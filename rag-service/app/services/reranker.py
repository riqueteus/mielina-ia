# reordena os chunks candidatos pela relevância real em relação à pergunta, usando um cross-encoder.

from sentence_transformers import CrossEncoder

RERANKER = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")


def reordenar_por_relevancia(pergunta: str, candidatos: list[dict]) -> list[dict]:
    """
    Recebe a pergunta e uma lista de chunks candidatos (vindos da busca
    vetorial), devolve a MESMA lista reordenada da mais para a menos
    relevante, segundo o cross-encoder.
    """
    pares = [[pergunta, c["texto"]] for c in candidatos]
    scores = RERANKER.predict(pares)

    candidatos_com_score = list(zip(candidatos, scores))
    candidatos_com_score.sort(key=lambda item: item[1], reverse=True)

    return [c for c, score in candidatos_com_score]