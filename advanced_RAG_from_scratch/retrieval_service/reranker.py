from shared.pinecone_client import PineconeClient

_client = PineconeClient()


def rerank(question: str, matches: list, keep: int) -> list:
    if len(matches) <= keep:
        return matches

    by_id = {m.id: m for m in matches}
    documents = [{"id": m.id, "text": m.metadata["text"]} for m in matches]

    ranked = _client.rerank(query=question, documents=documents, top_n=keep)
    return [by_id[row.document["id"]] for row in ranked.data]