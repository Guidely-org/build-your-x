import time
import httpx


def ask(base_url: str, question: str, timeout: float = 60.0) -> dict:
    started = time.perf_counter()
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}/query",
            json={"question": question},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        answer, sources, error = payload.get("answer", ""), payload.get("sources", []), None
    except Exception as exc:
        answer, sources, error = "", [], f"{type(exc).__name__}: {exc}"

    return {
        "answer": answer,
        "sources": sources,
        "latency_s": round(time.perf_counter() - started, 2),
        "error": error,
    }