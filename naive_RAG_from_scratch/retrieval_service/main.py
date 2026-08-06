from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .aug_gen import AugmentedGenerator


app = FastAPI(title="retrieval_service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

generator = AugmentedGenerator()  


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "retrieval_service"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        return generator.answer(request.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to answer the question") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("retrieval_service.main:app", host="0.0.0.0", port=8001, reload=True)