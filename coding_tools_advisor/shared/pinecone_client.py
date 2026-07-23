import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()


class PineconeClient:
    def __init__(
        self,
        api_key: str | None = None,
        index_name: str | None = None,
        namespace: str | None = None,
    ):
        api_key = api_key or os.getenv("PINECONE_API_KEY")
        index_name = index_name or os.getenv("PINECONE_INDEX_NAME")
        namespace = namespace if namespace is not None else os.getenv("PINECONE_NAMESPACE", "")

        if not api_key or not index_name:
            raise RuntimeError(
                "Missing Pinecone config. Check PINECONE_API_KEY and PINECONE_INDEX_NAME."
            )

        self._pc = Pinecone(api_key=api_key)
        self.index = self._pc.Index(index_name)
        self.namespace = namespace

    def upsert_records(self, records: list[dict]) -> int:
        response = self.index.upsert(vectors=records, namespace=self.namespace)
        return response

    def query(self, vector: list[float], top_k: int = 4, filter: dict | None = None):
        return self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=self.namespace,
            filter=filter,
            include_metadata=True,
            include_values=False
        )