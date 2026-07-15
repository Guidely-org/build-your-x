import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai_embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL')

client = OpenAI()


def embed(chunk: str) -> list[float]:
    response = client.embeddings.create(
        model=openai_embedding_model,
        input=chunk,
        encoding_format="float"
    )
    
    try:
        embedding = response.data[0].embedding
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Response does not contain a valid embedding") from exc

    return embedding



# Testing area
from parser import fetch_html, clean_html
from chunker import Document

url = 'https://builtin.com/articles/claude-code-codex-cursor-github-copilot-comparison'
html = fetch_html(url)
md_text = clean_html(html)

doc = Document(markdown_text=md_text, source_url=url, tool='all', doc_type='')
chunks = doc.chunk_document()

embeddings = embed(chunks[10].text_to_embed)
print(embeddings)

