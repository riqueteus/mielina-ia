import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.services.anonimizador import anonimizar_texto
from app.services.extractor_ia import ErroExtracaoLaudo, extrair_laudo
from app.services.pdf_extractor import extrair_texto_pdf

router = APIRouter(prefix="/laudos", tags=["Extração de Laudos"])


@router.post("/extrair")
def extrair_laudo_de_pdf(arquivo: UploadFile):
    """Recebe um PDF de laudo de RM e devolve o laudo estruturado anonimizado."""
    texto_anonimizado = anonimizar_texto(_extrair_texto_do_pdf(arquivo))

    try:
        resultado = extrair_laudo(texto_anonimizado)
    except ErroExtracaoLaudo as erro:
        raise HTTPException(status_code=502, detail=str(erro))

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
