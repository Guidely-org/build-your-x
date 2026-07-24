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

from .aug_gen import AugmentedGenerator
query = "Claude Code vs. Codex vs. Cursor vs. GitHub Copilot"

aug_gen = AugmentedGenerator()
response = aug_gen.answer(query)

answer, sources = response['answer'], response['sources']

print(answer)
print("\n")
print(sources)