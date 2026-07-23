import os
from dotenv import load_dotenv
from openai import OpenAI
from utils import batched


load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai_embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL')

client = OpenAI()


def embed(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    embeddings = []

    for batch in batched(texts, batch_size):
        response = client.embeddings.create(
            model=openai_embedding_model,
            input=batch,
            encoding_format="float",
        )

        try:
            batch_embeddings = [item.embedding for item in response.data]
        except (AttributeError, TypeError) as exc:
            raise ValueError("Response does not contain valid embeddings") from exc

        embeddings.extend(batch_embeddings)

    return embeddings


def embed_query(text: str) -> list[float]:
    return embed([text])[0]
