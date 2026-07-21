import os
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
from embedder import embed
from indexer import build_records, upsert_chunks
from dotenv import load_dotenv
from pinecone import Pinecone



load_dotenv()

PC_API_KEY = os.getenv('PINECONE_API_KEY')
PC_INDEX = os.getenv('PINECONE_INDEX_NAME')
PC_NAMESPACE = os.getenv('PINECONE_NAMESPACE')

pc = Pinecone(api_key=PC_API_KEY)
index = pc.Index(PC_INDEX)

url = 'https://builtin.com/articles/claude-code-codex-cursor-github-copilot-comparison'
html = fetch_html(url)
md_text = clean_html(html)

doc = Document(markdown_text=md_text, source_url=url, tool='all', doc_type='')
chunks = doc.chunk_document()

strings = extract_text_to_embed(chunks)
embeddings = embed(strings)
upserted = upsert_chunks(chunks, embeddings, index, PC_NAMESPACE)

print("\n")
print(f"Records Upserted: {upserted}")
print("\n")

