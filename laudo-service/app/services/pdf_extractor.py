import PyPDF2

def extrair_texto(arquivo_pdf):
    pdf = PyPDF2.PdfReader(arquivo_pdf)
    texto = ''
    for pagina in pdf.pages:
        texto += pagina.extract_text()
    return texto

