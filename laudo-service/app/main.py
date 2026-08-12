from fastapi import FastAPI

from app.router import router

app = FastAPI(
    title="Mielina - Laudo Service",
    description="Serviço de extração estruturada de laudos de RM para Esclerose Múltipla.",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "online", "service": "laudo-service"}