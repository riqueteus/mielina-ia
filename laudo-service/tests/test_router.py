"""Teste de integração: rota /laudos/extrair usa o fallback de data por regex.

Simula o LLM devolvendo ``data_exame: null`` (caso real observado) e verifica
que a data do exame extraída por regex do texto bruto é preenchida no resultado.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


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


def test_data_exame_preenchido_quando_llm_retorna_null(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app
    from app.schemas import LaudoEstruturado

    def fake_extrair_laudo(texto):
        # LLM "não encontrou" a data de propósito.
        return LaudoEstruturado(
            identificacao_protocolo={
                "tipo_exame": "RESSONÂNCIA MAGNÉTICA DO CRÂNIO",
                "data_exame": None,
            },
            conclusao={"texto": "Sem alterações."},
        )

    monkeypatch.setattr("app.router.extrair_laudo", fake_extrair_laudo)

    texto = (
        "RESSONÂNCIA MAGNÉTICA DO CRÂNIO\n"
        "Paciente: Maria Joaquina da Silva\n"
        "Data de Nascimento: 23/04/1981\n"
        "Data: 24/07/2021\n\n"
        "Exame sem alterações significativas."
    )

    cliente = TestClient(app)
    resposta = cliente.post(
        "/laudos/extrair",
        files={"arquivo": ("laudo.pdf", _gerar_pdf(texto), "application/pdf")},
    )

    assert resposta.status_code == 200
    resultado = resposta.json()["resultado"]
    assert resultado["identificacao_protocolo"]["data_exame"] == "2021-07-24"


def test_data_exame_do_llm_prevalece_quando_existe(monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app
    from app.schemas import LaudoEstruturado

    def fake_extrair_laudo(texto):
        return LaudoEstruturado(
            identificacao_protocolo={
                "tipo_exame": "RESSONÂNCIA MAGNÉTICA DO CRÂNIO",
                "data_exame": "2026-07-15",
            },
            conclusao={"texto": "Sem alterações."},
        )

    monkeypatch.setattr("app.router.extrair_laudo", fake_extrair_laudo)

    texto = "RESSONÂNCIA MAGNÉTICA DO CRÂNIO\nData: 24/07/2021\n\nExame normal."
    cliente = TestClient(app)
    resposta = cliente.post(
        "/laudos/extrair",
        files={"arquivo": ("laudo.pdf", _gerar_pdf(texto), "application/pdf")},
    )

    assert resposta.status_code == 200
    resultado = resposta.json()["resultado"]
    assert resultado["identificacao_protocolo"]["data_exame"] == "2026-07-15"