import re
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
    row["incorrect_refusal_rate"] = abstained

    if expected := case.get("expected_source"):
        row["expected_source"] = expected
        row["source_correct"] = expected in result["sources"]

    if case["category"] == "comparison":
        expected = set(case["expected_tools"])
        found = named_tools(result["answer"]) & expected
        row["tool_coverage"] = round(len(found) / len(expected), 2)
        row["tools_missing"] = sorted(expected - found)
    
    if expected := case.get("expected_prices"):
        paragraphs = [p for p in result["answer"].split("\n") if p.strip()]
        wrong = {}

        for tool, accepted in expected.items():
            para = next((p for p in paragraphs if tool.lower() in p.lower()), "")
            matched = any(
                re.search(rf"{re.escape(price)}\b", para) for price in accepted
            )
            if not matched:
                found = re.findall(r"\$\d[\d,]*", para) or ["no price"]
                wrong[tool] = f"said {', '.join(found)}, expected {' or '.join(accepted)}"

        row["price_accuracy"] = round(1 - len(wrong) / len(expected), 2)
        row["wrong_prices"] = wrong

    return row


def failure_reason(row: dict) -> str | None:
    """Explain why a scored row counts as a failure, or None if it passed."""
    if row["error"]:
        return f"request failed: {row['error']}"

    if row.get("source_correct") is False:
        expected = row["expected_source"]
        cited = row["sources"]
        if not cited:
            return f"cited no sources; expected {expected}"
        return f"cited {', '.join(cited)}; expected {expected}"

    if row.get("tool_coverage") is not None and row["tool_coverage"] < 1.0:
        missing = ", ".join(row["tools_missing"])
        pct = int(row["tool_coverage"] * 100)
        return f"named only {pct}% of the tools; missing {missing}"

    if row.get("abstained_correctly") is False:
        return "answered instead of declining an out-of-scope question"

    if row.get("incorrect_refusal_rate") is True:
        return "declined an in-scope question it should have answered"
    
    if row.get("wrong_prices"):
        details = [f"\n        {t}: {msg}" for t, msg in row["wrong_prices"].items()]
        return "wrong single-developer price:" + "".join(details)

    return None