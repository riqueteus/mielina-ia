"""Testes do fallback determinístico de data do exame (app/services/data_exame.py)."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.data_exame import extrair_data_exame, normalizar_datas_para_iso


def test_extrai_data_apos_rotulo_data():
    texto = "Paciente: Maria Joaquina\nData: 24/07/2021\n\nACHADOS: sem lesões."
    assert extrair_data_exame(texto) == date(2021, 7, 24)


def test_extrai_data_iso():
    texto = "exame realizado em 2021-07-24."
    assert extrair_data_exame(texto) == date(2021, 7, 24)


def test_ignora_data_de_nascimento():
    texto = "Data de Nascimento: 23/04/1981\nSolicitante: Dra. Ana\nData: 14/07/2026"
    assert extrair_data_exame(texto) == date(2026, 7, 14)


def test_nascimento_nao_vira_data_do_exame():
    texto = "Data de Nascimento: 23/04/1981\nExame sem data no cabeçalho."
    assert extrair_data_exame(texto) is None


def test_sem_data_retorna_none():
    assert extrair_data_exame("Laudo sem nenhuma data no texto.") is None


def test_data_invalida_ignorada():
    assert extrair_data_exame("Data: 31/02/2021") is None


def test_normaliza_dd_mm_aaaa_para_iso():
    assert normalizar_datas_para_iso("Data: 24/07/2021") == "Data: 2021-07-24"


def test_normalizacao_preserva_texto_sem_data():
    texto = "Sem datas por aqui."
    assert normalizar_datas_para_iso(texto) == texto


def test_normalizacao_nao_quebra_data_invalida():
    assert normalizar_datas_para_iso("Data: 31/02/2021") == "Data: 31/02/2021"