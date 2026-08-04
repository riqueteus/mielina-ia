import os
from dotenv import load_dotenv

load_dotenv()


def _obrigatorio(nome_variavel: str, valor):
    if valor is None:
        raise RuntimeError(
            f"Variavel de ambiente obrigatoria '{nome_variavel}' nao esta definida no .env"
        )
    return valor


SUPABASE_URL = _obrigatorio("SUPABASE_URL", os.getenv("SUPABASE_URL"))
SUPABASE_SERVICE_ROLE_KEY = _obrigatorio(
    "SUPABASE_SERVICE_ROLE_KEY",
    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
)

SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "modelos-ia")
MODELO_NOME_ARQUIVO = os.getenv("MODELO_NOME_ARQUIVO", "Regressao_logistica_class_em.joblib")
