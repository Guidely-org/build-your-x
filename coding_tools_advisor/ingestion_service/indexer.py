from chunker import Chunk
from utils import batched


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

