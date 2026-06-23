from fastapi import FastAPI

app = FastAPI(title="ingestion_service")


@app.get("/")
def read_root():
    return {"service": "ingestion_service", "status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)