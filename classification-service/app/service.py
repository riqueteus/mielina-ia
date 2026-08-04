import logging
import warnings
from pathlib import Path

import joblib
import numpy as np
from supabase import create_client

from app.core.config import (
    MODELO_NOME_ARQUIVO,
    SUPABASE_BUCKET,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)

logger = logging.getLogger(__name__)

CAMINHO_MODELO = Path(__file__).parent / "model" / MODELO_NOME_ARQUIVO


def _baixar_modelo():
    if CAMINHO_MODELO.exists():
        return

    logger.info("Baixando modelo do Supabase Storage...")
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    CAMINHO_MODELO.parent.mkdir(parents=True, exist_ok=True)

    dados = client.storage.from_(SUPABASE_BUCKET).download(MODELO_NOME_ARQUIVO)
    CAMINHO_MODELO.write_bytes(dados)
    logger.info("Modelo baixado: %s (%d bytes)", CAMINHO_MODELO, len(dados))


_baixar_modelo()

warnings.filterwarnings("ignore", category=UserWarning)
_pacote = joblib.load(CAMINHO_MODELO)
logger.info("Modelo carregado em memoria: %s", CAMINHO_MODELO)


def prever_risco(respostas: dict) -> dict:
    try:
        features = _pacote["features"]
        entrada = np.array([[respostas[col] for col in features]])

        if _pacote.get("usa_scaling"):
            entrada = _pacote["scaler"].transform(entrada)

        probabilidade = _pacote["modelo"].predict_proba(entrada)[0][1]
        return {"percentual_risco": round(probabilidade * 100, 1), "erro": False}
    except Exception as e:
        logger.exception("Erro ao processar previsao")
        return {"percentual_risco": 0.0, "erro": True, "mensagem": str(e)}
