import os
from dotenv import load_dotenv

load_dotenv()


def _obrigatorio(nome_variavel: str, valor):
    """Lança erro claro se uma variável obrigatória não estiver definida."""
    if valor is None:
        raise RuntimeError(
            f"Variável de ambiente obrigatória '{nome_variavel}' não está definida no .env"
        )
    return valor


def _get_bool(nome_variavel: str) -> bool:
    """Lê uma variável booleana do .env. Falta da variável = erro."""
    valor = os.getenv(nome_variavel)
    _obrigatorio(nome_variavel, valor)
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(nome_variavel: str) -> int:
    """Lê uma variável inteira do .env. Falta da variável = erro."""
    valor = os.getenv(nome_variavel)
    _obrigatorio(nome_variavel, valor)
    return int(valor)


SUPABASE_URL = _obrigatorio("SUPABASE_URL", os.getenv("SUPABASE_URL"))
SUPABASE_SERVICE_ROLE_KEY = _obrigatorio(
    "SUPABASE_SERVICE_ROLE_KEY",
    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
)
GROQ_API_KEY = _obrigatorio("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
HF_TOKEN = _obrigatorio("HF_TOKEN", os.getenv("HF_TOKEN"))

EMBEDDING_MODEL_NAME = _obrigatorio(
    "EMBEDDING_MODEL_NAME",
    os.getenv("EMBEDDING_MODEL_NAME"),
)

ENABLE_INGEST_ROUTE = _get_bool("ENABLE_INGEST_ROUTE")
LOG_MEMORY = _get_bool("LOG_MEMORY")
LOG_STEP_TIMINGS = _get_bool("LOG_STEP_TIMINGS")

N_CANDIDATOS = _get_int("N_CANDIDATOS")
TOP_K = _get_int("TOP_K")
