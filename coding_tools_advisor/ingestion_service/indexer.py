import os
from dotenv import load_dotenv
from pinecone import Pinecone
from chunker import Chunk
from utils import batched


load_dotenv()

PC_API_KEY = os.getenv('PINECONE_API_KEY')
PC_INDEX = os.getenv('PINECONE_INDEX_NAME')
PC_NAMESPACE = os.getenv('PINECONE_NAMESPACE')

pc = Pinecone(api_key=PC_API_KEY)
index = pc.Index(PC_INDEX)

def build_records(chunks: list[Chunk], embeddings: list[list[float]]) -> list[dict]:
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Mismatched lengths: {len(chunks)} chunks vs {len(embeddings)} embeddings"
        )

    return [
        {
            "id": chunk.id,
            "values": embedding,
            "metadata": chunk.metadata,
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

def upsert_chunks(
    chunks: list[Chunk],
    embeddings: list[list[float]],
    index,
    namespace: str = "",
    batch_size: int = 100,
) -> int:
    records = build_records(chunks, embeddings)
    total_upserted = 0

    for batch in batched(records, batch_size):
        try:
            response = index.upsert(vectors=batch, namespace=namespace)
        except Exception as exc:
            first_id = batch[0]["id"]
            raise RuntimeError(
                f"Failed to upsert batch starting at record {first_id}"
            ) from exc

        total_upserted += response.upserted_count
        print(f"Upserted {total_upserted}/{len(records)} records")

    return total_upserted

