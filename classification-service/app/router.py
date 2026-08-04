from fastapi import APIRouter
from app.schemas import RespostasQuestionario, ResultadoPrevisao
from app.service import prever_risco

router = APIRouter(prefix="/classification", tags=["Classificação EM"])

@router.post("/prever", response_model=ResultadoPrevisao)
def prever(respostas: RespostasQuestionario):
    return prever_risco(respostas.model_dump())