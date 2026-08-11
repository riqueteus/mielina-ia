from pypdf import PdfReader


def extrair_texto(arquivo_pdf: str) -> str:
    pdf = PdfReader(arquivo_pdf)
    texto = ""
    for pagina in pdf.pages:
        texto += pagina.extract_text() or ""
    return texto