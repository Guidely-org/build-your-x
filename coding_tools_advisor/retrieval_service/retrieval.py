

def retrieve(index: str, namespace: str, query_vector: list[float]) -> list[dict]:
    results = index.query(
        namespace=namespace,
        vector=query_vector, 
        top_k=5,
        include_metadata=True,
        include_values=False
    )
    return results['matches']