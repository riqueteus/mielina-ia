from fastapi import FastAPI
from app.routers import ingest  

app = FastAPI(
    title="Mielina - RAG Service",
    description="Serviço de RAG (Retrieval-Augmented Generation) para o Mielina.",
    version="0.1.0",
)

app.include_router(ingest.router)

@app.get("/health")

def health_check():
    return {
        "status": "online",
        "service": "rag-service"
    }