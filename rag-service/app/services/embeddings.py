from sentence_transformers import SentenceTransformer

MODELO = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def gerar_embeddings(textos: list[str]) -> list[list[float]]:
    """
    Recebe uma lista de textos (os chunks) e devolve uma lista de
    embeddings — um vetor de 384 números para cada texto, na mesma ordem.
    """
    vetores = MODELO.encode(textos, show_progress_bar=False)
    return vetores.tolist()