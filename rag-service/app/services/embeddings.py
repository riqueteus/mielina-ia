import time
from typing import Optional

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from app.core.config import EMBEDDING_MODEL_NAME, HF_TOKEN
from app.core.debug_memoria import log_memoria

CLIENTE: Optional[InferenceClient] = None


def get_cliente() -> InferenceClient:
    global CLIENTE

    if CLIENTE is None:
        log_memoria("antes de inicializar cliente HF")
        CLIENTE = InferenceClient(token=HF_TOKEN)
        log_memoria("depois de inicializar cliente HF")

    return CLIENTE


def gerar_embeddings(textos: list[str]) -> list[list[float]]:
    """
    Recebe uma lista de textos (os chunks) e devolve uma lista de
    embeddings — um vetor de 384 números para cada texto, na mesma ordem.
    Usa a Hugging Face Inference API via feature_extraction.
    """
    cliente = get_cliente()

    max_tentativas = 3
    tentativa = 0
    while True:
        tentativa += 1
        try:
            vetores = cliente.feature_extraction(
                text=textos,
                model=EMBEDDING_MODEL_NAME,
            )
            return vetores.tolist()

        except HfHubHTTPError as e:
            status = getattr(e, "response", None)
            status_code = getattr(status, "status_code", None) if status else None

            # 503 = modelo acordando; 429 = limite de requisições
            if status_code in {503, 429} and tentativa < max_tentativas:
                delay = 2 ** tentativa
                print(
                    f"[EMBEDDING] Erro {status_code} na HF (tentativa {tentativa}/{max_tentativas}). "
                    f"Aguardando {delay}s antes de tentar de novo..."
                )
                time.sleep(delay)
                continue

            # Outros erros HTTP ou excedeu tentativas: propaga o erro
            raise
