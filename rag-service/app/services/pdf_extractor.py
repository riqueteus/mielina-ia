import os
import tempfile

from pypdf import PdfReader, PdfWriter

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

TAMANHO_LOTE = 5

opcoes = PdfPipelineOptions()

opcoes.do_ocr = False
opcoes.do_table_structure = True

# Libera páginas já processadas da memória.
opcoes.generate_parsed_pages = False
opcoes.images_scale = 0.5

# Recursos que não utilizaremos.
opcoes.do_formula_enrichment = False
opcoes.do_code_enrichment = False
opcoes.do_picture_classification = False


CONVERSOR = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=opcoes
        )
    }
)


def processar_lote(caminho_pdf: str) -> str:
    """Processa um PDF temporário utilizando o Docling."""
    resultado = CONVERSOR.convert(caminho_pdf)
    return resultado.document.export_to_markdown()


def extrair_texto_pdf(caminho_arquivo: str) -> str:
    """Extrai todo o texto de um PDF utilizando processamento em lotes."""

    leitor = PdfReader(caminho_arquivo)

    markdown_final = []

    total_paginas = len(leitor.pages)

    print(f"\nIniciando processamento de {total_paginas} páginas...\n")

    for inicio in range(0, total_paginas, TAMANHO_LOTE):

        fim = min(inicio + TAMANHO_LOTE, total_paginas)

        print(f"Processando páginas {inicio + 1} até {fim}...")

        escritor = PdfWriter()

        for pagina in range(inicio, fim):
            escritor.add_page(leitor.pages[pagina])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as arquivo_temp:

            escritor.write(arquivo_temp)
            caminho_temp = arquivo_temp.name

        try:

            markdown = processar_lote(caminho_temp)
            markdown_final.append(markdown)

        except Exception as erro:

            print(f"\nErro ao processar páginas {inicio + 1} até {fim}")
            raise erro

        finally:

            os.remove(caminho_temp)

    texto_final = "\n\n".join(markdown_final)

    print("\nProcessamento concluído!")
    print(f"Total de caracteres extraídos: {len(texto_final)}\n")

    return texto_final