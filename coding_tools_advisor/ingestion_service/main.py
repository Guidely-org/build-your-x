from fastapi import FastAPI

app = FastAPI(title="ingestion_service")


@app.get("/")
def read_root():
    return {"service": "ingestion_service", "status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8001,
#         reload=True,
#     )

from parser import fetch_html, clean_html
from chunker import Document
from chunker import extract_text_to_embed
from shared.embedder import EmbeddingClient
from indexer import upsert_chunks


url = 'https://builtin.com/articles/claude-code-codex-cursor-github-copilot-comparison'
html = fetch_html(url)
md_text = clean_html(html)

doc = Document(markdown_text=md_text, source_url=url, tool='all', doc_type='')
chunks = doc.chunk_document()

strings = extract_text_to_embed(chunks)

ec = EmbeddingClient()
embeddings = ec.embed(strings)
upserted = upsert_chunks(chunks, embeddings)

print("\n")
print(f"Records Upserted: {upserted}")
print("\n")

