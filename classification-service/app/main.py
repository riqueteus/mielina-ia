from fastapi import FastAPI

from app.router import router

app = FastAPI(
    title="Mielina - Classification Service",
    description="Serviço de classificação para previsão de risco de Esclerose Múltipla.",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "online", "service": "classification-service"}
