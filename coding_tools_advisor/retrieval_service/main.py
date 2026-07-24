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
from shared.openai_client import OpenAIClient

query = "What is the cost of Codex"

oc = OpenAIClient()
vector = oc.embed_query(query)

results = retrieve(vector)

for hit in results:
    print(hit)
    print("\n")