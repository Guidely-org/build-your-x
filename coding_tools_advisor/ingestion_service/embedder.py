import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai_embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL')

client = OpenAI()


def embed(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        response = client.embeddings.create(
            model=openai_embedding_model,
            input=batch,
            encoding_format="float",
        )

        try:
            batch_embeddings = [item.embedding for item in response.data]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("Response does not contain valid embeddings") from exc

        embeddings.extend(batch_embeddings)

    return embeddings

