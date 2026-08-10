import re

from shared.openai_client import OpenAIClient
from shared.pinecone_client import PineconeClient
from .router import route, TOOLS


SYSTEM_PROMPT = """Answer the question using only the numbered context below.
For every claim you make, cite the number it came from, like [1].
If the context does not contain the answer, say you do not have that information."""


COMPARISON_SYSTEM_PROMPT = """Answer the question using only the numbered context below.
Each context item is labelled with the tool it describes.

Structure your answer as one short paragraph per tool, in this order:
Claude, Cursor, Copilot, Codex. Only include tools the question asks about.
Start each paragraph with the tool name. State what the context says about
that tool, with a citation like [1]. If the context contains nothing relevant
for a tool, write one line saying so for that tool.

After covering every tool, add a final short paragraph with your conclusion.

Never conclude that a tool lacks a feature simply because you did not notice
it in the context."""


_CITATION_RE = re.compile(r"\s?\[(\d+)\]")

# How many chunks to fetch per tool when decomposing a comparison question.
# Four tools at 3 chunks each gives 12, comparable to the single-search top_k.
_PER_TOOL_K = 3


class AugmentedGenerator:
    def __init__(
        self,
        openai_client: OpenAIClient | None = None,
        pinecone_client: PineconeClient | None = None,
        top_k: int = 10,
    ):
        self.openai_client = openai_client or OpenAIClient()
        self.pinecone_client = pinecone_client or PineconeClient()
        self.top_k = top_k

    def answer(self, question: str) -> dict:
        route_info = route(question, self.openai_client)

        print(f"{question} \n")
        print(route_info)

        if route_info["type"] == "out_of_scope":
            return {
                "answer": "I don't have information about that in my knowledge base.",
                "sources": [],
            }

        if route_info["type"] == "comparison":
            matches = self._retrieve_per_tool(question, route_info)
        else:
            matches = self._retrieve(question, route_info)

        print(f"\n{matches}")
        if not matches:
            return {
                "answer": "I don't have information about that in my knowledge base.",
                "sources": [],
            }

        context, citation_map = self._build_context_and_citations(matches)
        raw_answer = self._generate(question, context, route_info)
        print(f"\n{raw_answer}")
        return self._build_response(raw_answer, citation_map)

    def _retrieve(self, question: str, route_info: dict):
        query_vector = self.openai_client.embed_query(question)
        pinecone_filter = self._build_filter(route_info)
        results = self.pinecone_client.query(
            query_vector,
            top_k=self.top_k,
            filter=pinecone_filter,
        )
        return results.matches
    
    def _retrieve_per_tool(self, question: str, route_info: dict):
        """Run one filtered retrieval per tool, so every tool is represented.

        A single search has no mechanism to reserve slots per tool, so a
        comparison question can come back with chunks about one tool only.
        Searching per tool guarantees each one contributes.
        """
        tools = route_info["tools"] or TOOLS

        matches = []
        for tool in tools:
            sub_question = f"{tool}: {question}"
            query_vector = self.openai_client.embed_query(sub_question)

            results = self.pinecone_client.query(
                query_vector,
                top_k=_PER_TOOL_K,
                filter={"tool": tool},
            )
            matches.extend(results.matches)

        # Comparison articles carry tool="comparison", so the per-tool filter
        # above excludes them. For non-pricing comparisons they are often the
        # only source that discusses tools against each other, so fetch some.
        if route_info["doc_type"] != "pricing":
            query_vector = self.openai_client.embed_query(question)
            results = self.pinecone_client.query(
                query_vector,
                top_k=_PER_TOOL_K,
                filter={"doc_type": "comparison"},
            )
            matches.extend(results.matches)

        return matches

    @staticmethod
    def _build_filter(route_info: dict) -> dict | None:
        conditions = {}

        # Only constrain by tool when exactly one tool is in play.
        # Comparison articles are stored with tool="comparison", so filtering
        # to a single tool excludes them. That is correct for pricing questions
        # and wrong for capability questions, which is why doc_type matters below.
        if len(route_info["tools"]) == 1 and route_info["doc_type"] == "pricing":
            conditions["tool"] = route_info["tools"][0]
            conditions["doc_type"] = "pricing"

        return conditions or None

    @staticmethod
    def _build_context_and_citations(matches) -> tuple[str, dict]:
        context_blocks = []
        citation_map = {}

        for i, match in enumerate(matches, start=1):
            metadata = match.metadata
            tool = metadata.get("tool", "")
            heading = " > ".join(metadata.get("heading_path", []))

            label = f"[{i}]"
            if tool and tool != "comparison":
                label += f" ({tool}"
                if heading:
                    label += f" — {heading}"
                label += ")"
            elif heading:
                label += f" ({heading})"

            context_blocks.append(f"{label} {metadata['text']}")
            citation_map[i] = metadata["source_url"]

        return "\n".join(context_blocks), citation_map

    def _generate(self, question: str, context: str, route_info: dict) -> str:
        if route_info["type"] == "comparison":
            tools = route_info["tools"] or TOOLS
            prompt = f"""Context: {context}

                Question: {question}

                Cover these tools, each in its own paragraph: {", ".join(tools)}
            """
            
            return self.openai_client.generate(prompt, system_prompt=COMPARISON_SYSTEM_PROMPT)

        prompt = f"""Context:
            {context}

            Question: {question}
        """
        return self.openai_client.generate(prompt, system_prompt=SYSTEM_PROMPT)

    @staticmethod
    def _build_response(answer: str, citation_map: dict) -> dict:
        cited_numbers = {int(n) for n in _CITATION_RE.findall(answer)}
        clean_text = _CITATION_RE.sub("", answer).strip()

        seen_urls = set()
        sources = []
        for n in sorted(cited_numbers):
            url = citation_map.get(n)
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append(url)

        return {"answer": clean_text, "sources": sources}