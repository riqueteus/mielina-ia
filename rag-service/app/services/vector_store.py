# vector_store.py — responsável por salvar chunks (com embeddings) no Supabase.

from app.core.supabase_client import supabase
from app.services.embeddings import gerar_embeddings

TAMANHO_LOTE_SUPABASE = 50  


def salvar_chunks(chunks: list[dict]) -> int:
    """
    Recebe a lista de chunks (já vinda do chunks.py, cada um com
    'id', 'texto' e 'metadados'), gera os embeddings e insere tudo
    no Supabase em lotes.
    Devolve quantos chunks foram salvos.
    """
    textos = [chunk["texto"] for chunk in chunks]
    embeddings = gerar_embeddings(textos)

    linhas = []
    for chunk, embedding in zip(chunks, embeddings):
        linhas.append({
            "id": chunk["id"],
            "texto": chunk["texto"],
            "fonte": chunk["metadados"]["fonte"],
            "tipo": chunk["metadados"]["tipo"],
            "secao": chunk["metadados"]["secao"],
            "embedding": embedding,
        })

    for i in range(0, len(linhas), TAMANHO_LOTE_SUPABASE):
        lote = linhas[i:i + TAMANHO_LOTE_SUPABASE]
        supabase.table("chunks").upsert(lote).execute()

    return len(linhas)