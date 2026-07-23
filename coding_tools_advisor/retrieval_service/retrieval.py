from shared.pinecone_client import PineconeClient


def retrieve(query_vector: list[float]) -> list[dict]:
    pc = PineconeClient()
    results = pc.query(vector=query_vector, top_k=5)
    return results['matches']