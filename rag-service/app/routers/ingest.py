import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File

from app.services.pdf_extractor import extrair_texto_pdf
from app.services.chunks import criar_chunks_documento

router = APIRouter(prefix="/ingest", tags=["Ingestão"])

@router.post("/pdf")
async def ingerir_pdf(arquivo: UploadFile = File(...)):
    # Cria o arquivo temporário para o extrator ler
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(arquivo.file, tmp)
        caminho_temp = tmp.name

    try:
        texto = extrair_texto_pdf(caminho_temp)
        
        chunks_resultado = criar_chunks_documento(arquivo.filename, texto)

        # Retorna a resposta estruturada com todos os chunks
        return {
            "nome_arquivo": arquivo.filename,
            "caracteres_extraidos": len(texto),
            "total_chunks_gerados": len(chunks_resultado),
            "chunks": chunks_resultado  
        }
        
    finally:
        # Garante a remoção do arquivo temporário do sistema
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)
