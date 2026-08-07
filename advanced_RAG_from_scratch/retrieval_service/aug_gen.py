import re

from shared.openai_client import OpenAIClient
from shared.pinecone_client import PineconeClient
from .router import route


SYSTEM_PROMPT = """Answer the question using only the numbered context below.
For every claim you make, cite the number it came from, like [1].
If the context does not contain the answer, say you do not have that information."""

_CITATION_RE = re.compile(r"\s?\[(\d+)\]")


class AugmentedGenerator:
    def __init__(
        self,
        openai_client: OpenAIClient | None = None,
        pinecone_client: PineconeClient | None = None,
        top_k: int = 4,
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

        matches = self._retrieve(question, route_info)

        print(f"\n{matches}")
        if not matches:
            return {
                "answer": "I don't have information about that in my knowledge base.",
                "sources": [],
            }

        context, citation_map = self._build_context_and_citations(matches)
        raw_answer = self._generate(question, context)
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
            context_blocks.append(f"[{i}] {metadata['text']}")
            citation_map[i] = metadata["source_url"]

        return "\n".join(context_blocks), citation_map

    def _generate(self, question: str, context: str) -> str:
        prompt = f"""Context:{context}

        Question: {question}"""
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