import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.services.anonimizador import anonimizar_texto
from app.services.data_exame import extrair_data_exame, normalizar_datas_para_iso
from app.services.extractor_ia import ErroExtracaoLaudo, extrair_laudo
from app.services.pdf_extractor import extrair_texto_pdf

router = APIRouter(prefix="/laudos", tags=["Extração de Laudos"])


@router.post("/extrair")
def extrair_laudo_de_pdf(arquivo: UploadFile):
    """Recebe um PDF de laudo de RM e devolve o laudo estruturado anonimizado."""
    texto_bruto = _extrair_texto_do_pdf(arquivo)

    # Rede de segurança: a data do exame é extraída por regex do texto bruto,
    # pois o LLM às vezes devolve `null` mesmo com a data presente no laudo.
    data_exame_fallback = extrair_data_exame(texto_bruto)

    # Anonimiza e converte datas DD/MM/AAAA para AAAA-MM-DD antes do LLM,
    # facilitando a extração no formato que o schema espera.
    texto_anonimizado = anonimizar_texto(texto_bruto)
    texto_para_llm = normalizar_datas_para_iso(texto_anonimizado)

    try:
        resultado = extrair_laudo(texto_para_llm)
    except ErroExtracaoLaudo as erro:
        raise HTTPException(status_code=502, detail=str(erro))

    # Se o LLM não conseguiu extrair a data, usa a extraída por regex.
    if resultado.identificacao_protocolo.data_exame is None and data_exame_fallback is not None:
        resultado.identificacao_protocolo.data_exame = data_exame_fallback

    return {"resultado": resultado}


def _extrair_texto_do_pdf(arquivo: UploadFile) -> str:
    if not arquivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")

    try:
        conteudo = arquivo.file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Não foi possível ler o arquivo enviado.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(conteudo)
        caminho_temp = Path(f.name)

    try:
        return extrair_texto_pdf(str(caminho_temp))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha ao extrair texto do PDF: {e}")
    finally:
        caminho_temp.unlink(missing_ok=True)
