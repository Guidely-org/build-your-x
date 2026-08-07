import json

from shared.openai_client import OpenAIClient


TOOLS = ["Claude", "Cursor", "Copilot", "Codex"]

ROUTER_PROMPT = """You classify questions about AI coding tools.

The available tools are: Claude, Cursor, Copilot, Codex.

Return JSON only, with no other text:
{{
  "type": "factual" | "comparison" | "out_of_scope",
  "tools": [],
  "doc_type": "pricing" | null
}}

Rules:
- "type" is "comparison" if the question compares tools, or asks which is
  best, cheapest, or most generous.
- "type" is "out_of_scope" if the question is not about one of the four
  tools listed above. A question about a different product is out of scope.
- "tools" lists every tool from the list above that the question is about.
  For a comparison with no tools named, list all four.
- "doc_type" is "pricing" only if the question is about cost, plans, tiers,
  or billing. Otherwise null.

Question: {question}"""


def _empty_route() -> dict:
    """Fallback: behave like the naive system rather than fail."""
    return {"type": "factual", "tools": [], "doc_type": None}


def route(question: str, client: OpenAIClient) -> dict:
    raw = client.generate(ROUTER_PROMPT.format(question=question))

    try:
        parsed = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
    except (json.JSONDecodeError, AttributeError):
        return _empty_route()

    tools = [t for t in parsed.get("tools", []) if t in TOOLS]
    doc_type = parsed.get("doc_type") if parsed.get("doc_type") == "pricing" else None
    route_type = parsed.get("type")

    if route_type not in ("factual", "comparison", "out_of_scope"):
        route_type = "factual"

    return {"type": route_type, "tools": tools, "doc_type": doc_type}