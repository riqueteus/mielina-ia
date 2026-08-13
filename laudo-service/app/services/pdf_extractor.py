import re

from pypdf import PdfReader


def extrair_texto_pdf(caminho_arquivo: str) -> str:
    """Extrai texto de um PDF usando PyPDF.

    Esta é a implementação mais simples para extração básica de texto,
    usada pelo pipeline principal de processamento de laudos.
    """
    pdf = PdfReader(caminho_arquivo)
    texto = ""
    for pagina in pdf.pages:
        texto += pagina.extract_text() or ""
    return texto
