"""Testes de anonimização usando os laudos mock (tests/mocks.py).

Cobrem o fluxo de texto (anonimizar_texto) e o fluxo de PDF
(extrair_texto_pdf + anonimizar_texto), verificando que os dados
sensíveis dos laudos nunca aparecem no resultado.
"""

import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.services.anonimizador import anonimizar_texto
from app.services.pdf_extractor import extrair_texto_pdf
from mocks import MOCKS

CPF_FORMATADO = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}")
CPF_PURO = re.compile(r"\d{11}")
EMAIL = re.compile(r"[\w.\-]+@[\w.\-]+")
TELEFONE_FORMATADO = re.compile(r"\(\d{2}\)\s?\d{4,5}-\d{4}")

MASCARA = [
    "[NOME]",
    "[CPF]",
    "[RG]",
    "[TELEFONE]",
    "[EMAIL]",
    "[DATA_NASCIMENTO]",
    "[PRONTUARIO]",
]

CAMPOS_SENSIVEIS = ["cpf", "rg", "telefone", "email", "nascimento", "prontuario"]


def _anonimizado(mock):
    return anonimizar_texto(mock["texto"])


def _gerar_pdf(texto: str) -> bytes:
    linhas = texto.split("\n")
    stream = "BT /F1 12 Tf 40 760 Td 16 TL\n"
    for linha in linhas:
        esc = linha.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream += f"({esc}) Tj T*\n"
    stream += "ET"
    conteudo = stream.encode("latin-1", errors="replace")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
            b"/Resources << /Font << /F1 5 0 R >> >> >>"
        ),
        (
            f"<< /Length {len(conteudo)} >>\nstream\n".encode("latin-1")
            + conteudo
            + b"\nendstream"
        ),
        (
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
            b"/Encoding /WinAnsiEncoding >>"
        ),
    ]
    saida = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objetos, 1):
        offsets.append(len(saida))
        saida += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(saida)
    saida += f"xref\n0 {len(objetos) + 1}\n".encode() + b"0000000000 65535 f \n"
    for off in offsets[1:]:
        saida += f"{off:010d} 00000 n \n".encode()
    saida += (
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(saida)


def _texto_do_pdf(mock):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(_gerar_pdf(mock["texto"]))
        caminho = f.name
    try:
        return extrair_texto_pdf(caminho)
    finally:
        Path(caminho).unlink(missing_ok=True)


# ---------------------------------------------------------------- nomes
def test_nenhum_nome_vaza():
    for nome, mock in MOCKS.items():
        anonimo = _anonimizado(mock)
        for pessoa in mock["nomes"]:
            assert pessoa.lower() not in anonimo.lower(), f"Nome vazou em {nome}: {pessoa}"


# ---------------------------------------------------------------- dados numéricos
def test_nenhum_cpf_vaza():
    for nome, mock in MOCKS.items():
        assert mock["cpf"] not in _anonimizado(mock), f"CPF vazou em {nome}"


def test_nenhum_rg_vaza():
    for nome, mock in MOCKS.items():
        assert mock["rg"] not in _anonimizado(mock), f"RG vazou em {nome}"


def test_nenhum_telefone_vaza():
    for nome, mock in MOCKS.items():
        assert mock["telefone"] not in _anonimizado(mock), f"Telefone vazou em {nome}"


def test_nenhum_email_vaza():
    for nome, mock in MOCKS.items():
        assert mock["email"] not in _anonimizado(mock), f"E-mail vazou em {nome}"


def test_nenhuma_data_de_nascimento_vaza():
    for nome, mock in MOCKS.items():
        assert mock["nascimento"] not in _anonimizado(mock), f"Nascimento vazou em {nome}"


def test_nenhum_prontuario_vaza():
    for nome, mock in MOCKS.items():
        assert mock["prontuario"] not in _anonimizado(mock), f"Prontuário vazou em {nome}"


def test_dados_sem_formatacao_nao_vazam():
    for nome, mock in MOCKS.items():
        anonimo = _anonimizado(mock)
        if mock["cpf"].isdigit():
            assert mock["cpf"] not in anonimo, f"CPF sem formatação vazou em {nome}"
        if mock["telefone"].isdigit():
            assert mock["telefone"] not in anonimo, f"Telefone sem formatação vazou em {nome}"


# ---------------------------------------------------------------- marcadores
def test_marcadores_presentes():
    for nome, mock in MOCKS.items():
        anonimo = _anonimizado(mock)
        for marcador in MASCARA:
            assert marcador in anonimo, f"Marcador {marcador} ausente em {nome}"


# ---------------------------------------------------------------- conteúdo preservado
def test_data_exame_preservada():
    for nome, mock in MOCKS.items():
        assert mock["data_exame"] in _anonimizado(mock), f"Data do exame perdida em {nome}"


def test_termos_medicos_preservados():
    for nome, mock in MOCKS.items():
        anonimo = re.sub(r"\s+", " ", _anonimizado(mock)).lower()
        for termo in mock["termos_medicos"]:
            assert re.sub(r"\s+", " ", termo).lower() in anonimo, (
                f"Termo médico perdido em {nome}: {termo}"
            )


# ---------------------------------------------------------------- padrões globais
def test_sem_cpf_formatado_no_resultado():
    for nome, mock in MOCKS.items():
        assert not CPF_FORMATADO.search(_anonimizado(mock)), f"CPF formatado em {nome}"


def test_sem_cpf_puro_no_resultado():
    for nome, mock in MOCKS.items():
        assert not CPF_PURO.search(_anonimizado(mock)), f"CPF puro (11 dígitos) em {nome}"


def test_sem_email_no_resultado():
    for nome, mock in MOCKS.items():
        assert not EMAIL.search(_anonimizado(mock)), f"E-mail residual em {nome}"


def test_sem_telefone_formatado_no_resultado():
    for nome, mock in MOCKS.items():
        assert not TELEFONE_FORMATADO.search(_anonimizado(mock)), f"Telefone residual em {nome}"


# ---------------------------------------------------------------- casos soltos no corpo
def test_cpf_solto_no_corpo_anonimizado():
    texto = "Laudo de RM. O paciente declarou CPF 123.456.789-00 durante o atendimento."
    anonimo = anonimizar_texto(texto)
    assert "123.456.789-00" not in anonimo
    assert "[CPF]" in anonimo


def test_telefone_solto_no_corpo_anonimizado():
    texto = "Contato informado pelo paciente: (11) 91234-5678."
    anonimo = anonimizar_texto(texto)
    assert "(11) 91234-5678" not in anonimo
    assert "[TELEFONE]" in anonimo


def test_ressonancia_magnetica_nao_e_tratada_como_nome():
    texto = "O exame de RESSONÂNCIA MAGNÉTICA evidenciou áreas de FLAIR no parênquima."
    anonimo = anonimizar_texto(texto)
    assert "RESSONÂNCIA MAGNÉTICA" in anonimo
    assert "[NOME]" not in anonimo


def test_sedacao_nao_e_tratada_como_nome():
    texto = "RESSONÂNCIA MAGNÉTICA DE CRÂNIO REALIZADA COM SEDAÇÃO."
    anonimo = anonimizar_texto(texto)
    assert "SEDAÇÃO" in anonimo
    assert "RESSONÂNCIA MAGNÉTICA" in anonimo
    assert "[NOME]" not in anonimo


# ---------------------------------------------------------------- fluxo via PDF
def test_pdf_extrai_texto_de_todos_os_mocks():
    for nome, mock in MOCKS.items():
        texto = _texto_do_pdf(mock)
        assert "RESSONÂNCIA" in texto, f"Não extraiu texto de {nome}"


def test_pdf_fica_anonimizado():
    for nome, mock in MOCKS.items():
        anonimo = anonimizar_texto(_texto_do_pdf(mock))
        for pessoa in mock["nomes"]:
            assert pessoa.lower() not in anonimo.lower(), f"Nome vazou via PDF em {nome}"
        for campo in CAMPOS_SENSIVEIS:
            assert mock[campo] not in anonimo, f"{campo} vazou via PDF em {nome}"
        assert "[NOME]" in anonimo, f"Marcador ausente via PDF em {nome}"


def test_pdf_preserva_conteudo_medico_e_data():
    for nome, mock in MOCKS.items():
        anonimo = anonimizar_texto(_texto_do_pdf(mock))
        assert mock["data_exame"] in anonimo, f"Data do exame perdida via PDF em {nome}"
        assert "RESSONÂNCIA" in anonimo, f"Conteúdo médico perdido via PDF em {nome}"
