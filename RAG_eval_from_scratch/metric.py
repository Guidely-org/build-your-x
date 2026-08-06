from .dataset import TOOL_ALIASES

_REFUSAL_MARKERS = [
    "do not have", "don't have", "no information",
    "cannot find", "can't find", "not covered",
]


def is_abstention(answer: str) -> bool:
    if not answer.strip():
        return True
    lowered = answer.lower()
    return any(marker in lowered for marker in _REFUSAL_MARKERS)


def named_tools(answer: str) -> set[str]:
    lowered = answer.lower()
    return {
        tool for tool, aliases in TOOL_ALIASES.items()
        if any(alias in lowered for alias in aliases)
    }


def score(case: dict, result: dict) -> dict:
    abstained = is_abstention(result["answer"])

    row = {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "latency_s": result["latency_s"],
        "error": result["error"],
        "answer": result["answer"],
        "sources": result["sources"],
    }

    if case["category"] == "out_of_scope":
        row["abstained_correctly"] = abstained
        return row

    # In scope from here on: declining is a failure.
    row["false_abstention"] = abstained

    if expected := case.get("expected_source"):
        row["source_correct"] = expected in result["sources"]

    if case["category"] == "comparison":
        expected = set(case["expected_tools"])
        found = named_tools(result["answer"]) & expected
        row["tool_coverage"] = round(len(found) / len(expected), 2)
        row["tools_missing"] = sorted(expected - found)

    return row