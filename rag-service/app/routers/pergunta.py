import os 
import re

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.embeddings import gerar_embeddings
from app.services.vector_search import buscar_chunks_similares
from app.services.reranker import reordenar_por_relevancia
from app.core.groq_client import groq_client

router = APIRouter(prefix="/pergunta", tags=["Pergunta"])

class PerguntaRequest(BaseModel):
    pergunta: str

def limpar_nome_fonte(nome_arquivo: str) -> str:
    """
    BOA PRÁTICA: Função utilitária posicionada antes das rotas.
    Remove a extensão do arquivo (.pdf) e sufixos duplicados
    tipo " (1)" que o Windows/navegador adiciona em downloads repetidos.
    """
    nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
    nome_limpo = re.sub(r"\s*\(\d+\)\s*$", "", nome_sem_extensao)
    return nome_limpo.strip()


@router.post("")
async def responder_pergunta(request: PerguntaRequest):
    pergunta = request.pergunta

    embedding_pergunta = gerar_embeddings([pergunta])[0]

    candidatos = buscar_chunks_similares(embedding_pergunta, n_candidatos=20)

    chunks_relevantes = reordenar_por_relevancia(pergunta, candidatos)[:5]

    contexto = "\n\n---\n\n".join(
        f"[Fonte: {c['fonte']} | Tipo: {c['tipo']}]\n{c['texto']}"
        for c in chunks_relevantes
    )

    prompt = f"""Você é um assistente que responde perguntas sobre Esclerose Múltipla
com base APENAS no contexto abaixo, extraído de documentos sobre a doença.

REGRAS DE CONTEÚDO:
- Priorize sempre informações de tipo "protocolo_oficial_ms" sobre "material_tecnico_reabilitacao", "material_educativo_paciente" ou "material_educativo_geral" quando o assunto for indicação, dose ou contraindicação de medicamentos.
- "material_tecnico_reabilitacao" é uma boa fonte para perguntas sobre fisioterapia, exercícios, avaliação funcional e disfunções (urinárias, respiratórias, de fala, deglutição), mas não tem autoridade sobre indicação medicamentosa.
- Estudos e capítulos técnicos podem descrever contexto ou metodologia, o que não é o mesmo que recomendação clínica direta. Não confunda as duas coisas.
- Se as fontes parecerem conflitantes, diga isso explicitamente na resposta em vez de escolher uma versão sozinho.
- Se não tiver certeza ou a informação não estiver clara no contexto, diga isso.
- Não invente informações médicas.

REGRAS DE FORMATO (siga rigorosamente):
- Responda em texto corrido, direto e objetivo, em 1 a 3 frases sempre que possível.
- Não use markdown: sem títulos (#), sem negrito (**), sem listas com marcadores.
- Não inclua nenhum aviso legal, disclaimer ou recomendação de "consulte um médico" — isso é tratado separadamente pela aplicação.
- Não inclua marcações de fonte dentro do texto (ex: 【fonte: ...】, [1], etc.) — as fontes já são exibidas separadamente pelo sistema.


CONTEXTO:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""

    resposta = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    texto_resposta = resposta.choices[0].message.content

    fontes_usadas = list(dict.fromkeys(
        limpar_nome_fonte(c["fonte"]) for c in chunks_relevantes
    ))

    return {
        "resposta": texto_resposta,
        "fontes": fontes_usadas,
    }