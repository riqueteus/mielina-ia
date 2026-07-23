import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File

from app.services.pdf_extractor import extrair_texto_pdf
from app.services.chunks import criar_chunks_documento
from app.services.vector_store import salvar_chunks  

router = APIRouter(prefix="/ingest", tags=["Ingestão"])


@router.post("/pdf")
async def ingerir_pdf(arquivo: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(arquivo.file, tmp)
        caminho_temp = tmp.name

    try:
        texto = extrair_texto_pdf(caminho_temp)
        chunks_resultado = criar_chunks_documento(arquivo.filename, texto)

        total_salvo = salvar_chunks(chunks_resultado)

        return {
            "nome_arquivo": arquivo.filename,
            "caracteres_extraidos": len(texto),
            "total_chunks_gerados": len(chunks_resultado),
            "total_chunks_salvos_supabase": total_salvo,
        }

    finally:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)