from app.core.supabase_client import supabase


def buscar_chunks_similares(embedding_pergunta: list[float], n_candidatos: int = 20) -> list[dict]:
    """
    Recebe o embedding já calculado da pergunta do usuário e devolve
    os 'n_candidatos' chunks mais parecidos, vindos do Supabase.
    """
    resposta = supabase.rpc("match_documents", {
        "query_embedding": embedding_pergunta,
        "match_count": n_candidatos,
    }).execute()

    return resposta.data  