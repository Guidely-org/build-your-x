import os
from dotenv import load_dotenv
from openai import OpenAI
from .utils import batched

load_dotenv()


class OpenAIClient:
    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("Missing OpenAI config. Check OPENAI_API_KEY.")

        self._client = OpenAI(api_key=api_key)

    def embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        model = os.getenv("OPENAI_EMBEDDING_MODEL")
        if not model:
            raise RuntimeError("Missing OpenAI config. Check OPENAI_EMBEDDING_MODEL.")

        embeddings = []

        for batch in batched(texts, batch_size):
            response = self._client.embeddings.create(
                model=model,
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

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        model = os.getenv("OPENAI_CHAT_MODEL")
        if not model:
            raise RuntimeError("Missing OpenAI config. Check OPENAI_CHAT_MODEL.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        try:
            return response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise ValueError("Response does not contain valid generated text") from exc
