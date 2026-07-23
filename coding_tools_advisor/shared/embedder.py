import os
from dotenv import load_dotenv
from openai import OpenAI
from .utils import batched

load_dotenv()


class EmbeddingClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        model = model or os.getenv("OPENAI_EMBEDDING_MODEL")

        if not api_key or not model:
            raise RuntimeError(
                "Missing OpenAI config. Check OPENAI_API_KEY and OPENAI_EMBEDDING_MODEL."
            )

        self._client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        embeddings = []

        for batch in batched(texts, batch_size):
            response = self._client.embeddings.create(
                model=self.model,
                input=batch,
                encoding_format="float",
            )

            try:
                batch_embeddings = [item.embedding for item in response.data]
            except (AttributeError, TypeError) as exc:
                raise ValueError("Response does not contain valid embeddings") from exc

            embeddings.extend(batch_embeddings)

        return embeddings

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]
