import json
import statistics
from pathlib import Path

from .client import ask
from .dataset import DATASET
from .metrics import score

RESULTS = Path(__file__).parent / "results"
BASELINE = "baseline-naive"


def _rate(rows, key):
    values = [r[key] for r in rows if key in r]
    return round(sum(float(v) for v in values) / len(values), 2) if values else None


def summarise(rows: list[dict]) -> dict:
    return {
        "source_accuracy": _rate(rows, "source_correct"),
        "tool_coverage": _rate(rows, "tool_coverage"),
        "abstention": _rate(rows, "abstained_correctly"),
        "false_abstention": _rate(rows, "false_abstention"),
        "median_latency_s": statistics.median([r["latency_s"] for r in rows]),
        "errors": sum(1 for r in rows if r["error"]),
    }


def run(url: str, label: str):
    rows = []
    for case in DATASET:
        result = ask(url, case["question"])
        row = score(case, result)
        rows.append(row)
        mark = "!" if row["error"] else " "
        print(f"{mark} {row['id']:3} {row['latency_s']:>5.1f}s  {case['question'][:52]}")

    summary = summarise(rows)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"{label}.json").write_text(
        json.dumps({"label": label, "summary": summary, "cases": rows}, indent=2)
    )

    print(f"\n{label}")
    baseline_path = RESULTS / f"{BASELINE}.json"
    show_baseline = baseline_path.exists() and label != BASELINE
    baseline = json.loads(baseline_path.read_text())["summary"] if show_baseline else {}

    for key, value in summary.items():
        if value is None:
            continue
        line = f"  {key:20} {value:>6}"
        if (before := baseline.get(key)) is not None:
            delta = round(value - before, 2)
            sign = "+" if delta > 0 else ""
            line += f"   (baseline {before}, {sign}{delta})"
        print(line)

    # Surface what is still broken.
    failures = [
        r["id"] for r in rows
        if r.get("source_correct") is False
        or r.get("tool_coverage") == 0.0
        or r.get("abstained_correctly") is False
        or r.get("false_abstention") is True
    ]
    if failures:
        print(f"\n  still failing: {', '.join(failures)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8001")
    parser.add_argument("--label", required=True)
    run(*vars(parser.parse_args()).values())