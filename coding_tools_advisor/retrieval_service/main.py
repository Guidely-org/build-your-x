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
from dotenv import load_dotenv
from pinecone import Pinecone
from .retrieval import retrieve
from ingestion_service.embedder import embed_query



load_dotenv()

PC_API_KEY = os.getenv('PINECONE_API_KEY')
PC_INDEX = os.getenv('PINECONE_INDEX_NAME')
PC_NAMESPACE = os.getenv('PINECONE_NAMESPACE')

pc = Pinecone(api_key=PC_API_KEY)
index = pc.Index(PC_INDEX)

query = "Tell me about Claude code's pricing plan"
vector = embed_query(query)

results = retrieve(index, PC_NAMESPACE, vector)

for hit in results:
    print(hit)
    print("\n")