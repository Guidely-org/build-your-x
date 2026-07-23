import os
from fastapi import FastAPI

app = FastAPI(title="retrieval_service")


@app.get("/")
def read_root():
    return {"service": "retrieval_service", "status": "ok"}


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
from .retrieval import retrieve
from shared.embedder import EmbeddingClient

query = "What is the cost of Codex"

ec = EmbeddingClient()
vector = ec.embed_query(query)

results = retrieve(vector)

for hit in results:
    print(hit)
    print("\n")