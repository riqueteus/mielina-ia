import shutil
import tempfile

from fastapi import APIRouter, UploadFile, File

from app.services.pdf_extractor import extrair_texto_pdf

router = APIRouter(prefix="/ingest", tags=["Ingestão"])


@router.post("/pdf")
async def ingerir_pdf(arquivo: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(arquivo.file, tmp)
        caminho_temp = tmp.name

    texto = extrair_texto_pdf(caminho_temp)

    return {
        "nome_arquivo": arquivo.filename,
        "caracteres_extraidos": len(texto),
        "preview": texto[:500]  
    }