"""Testes da integração LLM (Groq) para extração do LaudoEstruturado.

O client Groq é mockado: nenhuma chamada real é feita. São usados dois
laudos fictícios anonimizados: um com várias lesões e um sem lesões.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import pytest
from groq import APIStatusError, RateLimitError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import MODELO_GROQ
from app.core.groq_client import groq_client
from app.schemas import LaudoEstruturado
from app.services.extractor_ia import (
    MAX_TOKENS_SAIDA,
    ErroExtracaoLaudo,
    _esquema_para_groq,
    extrair_laudo,
)


class _FakeMensagem:
    def __init__(self, conteudo):
        self.content = conteudo


class _FakeEscolha:
    def __init__(self, conteudo):
        self.message = _FakeMensagem(conteudo)


class _FakeResposta:
    def __init__(self, conteudo):
        self.choices = [_FakeEscolha(conteudo)]


def _mockar_groq(monkeypatch, conteudo_json):
    captura = {}

    def fake_create(**kwargs):
        captura["kwargs"] = kwargs
        return _FakeResposta(json.dumps(conteudo_json, ensure_ascii=False))

    monkeypatch.setattr(groq_client.chat.completions, "create", fake_create)
    return captura


def _mockar_groq_conteudo(monkeypatch, conteudo):
    def fake_create(**kwargs):
        return _FakeResposta(conteudo)

    monkeypatch.setattr(groq_client.chat.completions, "create", fake_create)


TEXTO_MULTIPLAS_LESOES = """RESSONÂNCIA MAGNÉTICA DO CRÂNIO

Paciente: [NOME]
[PRONTUARIO]
Solicitante: [NOME]
Data: 15/07/2026

INDICAÇÃO CLÍNICA: Parestesias em membros superiores. Avaliação de doença desmielinizante.

TÉCNICA: Sequências axiais e sagitais em T1, T2 e FLAIR, e axial T1 pós-contraste.

ACHADOS:
Múltiplas lesões desmielinizantes em substância branca supratentorial. Há cerca de oito lesões: três justacorticais em região frontoparietal direita e quatro periventriculares ao longo dos cornos occipitais. Uma placa desmielinizante no hemisfério cerebelar esquerdo. Uma lesão periventricular de 8 mm com realce pelo contraste. As demais lesões não apresentam realce.

Não há lesões medulares.

CONCLUSÃO: Múltiplas lesões desmielinizantes com atividade inflamatória em uma lesão."""

JSON_MULTIPLAS_LESOES = {
    "identificacao_protocolo": {
        "data_exame": "2026-07-15",
        "tipo_exame": "RESSONÂNCIA MAGNÉTICA DO CRÂNIO",
        "regiao_examinada": "Encéfalo",
        "indicacao_clinica": "Parestesias em membros superiores. Avaliação de doença desmielinizante.",
        "tecnica": "Sequências axiais e sagitais em T1, T2 e FLAIR, e axial T1 pós-contraste.",
    },
    "atividade_inflamatoria": {
        "realce_gadolinio": True,
        "quantidade_lesoes_com_realce": 1,
        "padrao_realce": "realce pelo contraste",
        "evidencia": "Uma lesão periventricular de 8 mm com realce pelo contraste",
    },
    "biomarcadores_avancados": {
        "sinal_veia_central": None,
        "lesoes_anel_paramagnetico_prl": None,
        "evidencia": None,
    },
    "atrofia_achados_cronicos": {
        "atrofia_encefalica": None,
        "buracos_negros_t1": None,
        "evidencia": None,
    },
    "lesoes": [
        {
            "localizacao": "região frontoparietal direita",
            "regiao": "justacortical",
            "tamanho_mm": None,
            "caracteristica": "lesões desmielinizantes",
            "realce_contraste": False,
            "evidencia": "três justacorticais em região frontoparietal direita",
        },
        {
            "localizacao": "cornos occipitais",
            "regiao": "periventricular",
            "tamanho_mm": None,
            "caracteristica": "lesões desmielinizantes periventriculares",
            "realce_contraste": False,
            "evidencia": "quatro periventriculares ao longo dos cornos occipitais",
        },
        {
            "localizacao": "hemisfério cerebelar esquerdo",
            "regiao": "infratentorial",
            "tamanho_mm": None,
            "caracteristica": "placa desmielinizante",
            "realce_contraste": False,
            "evidencia": "Uma placa desmielinizante no hemisfério cerebelar esquerdo",
        },
        {
            "localizacao": "periventricular",
            "regiao": "periventricular",
            "tamanho_mm": 8.0,
            "caracteristica": "lesão periventricular",
            "realce_contraste": True,
            "evidencia": "Uma lesão periventricular de 8 mm com realce pelo contraste",
        },
    ],
    "conclusao": {
        "texto": "Múltiplas lesões desmielinizantes com atividade inflamatória em uma lesão.",
        "evidencia": "Múltiplas lesões desmielinizantes com atividade inflamatória em uma lesão.",
    },
}

TEXTO_SEM_LESOES = """RESSONÂNCIA MAGNÉTICA DO CRÂNIO

Paciente: [NOME]
[PRONTUARIO]
Solicitante: [NOME]
Data: 20/07/2026

INDICAÇÃO CLÍNICA: Controle de paciente com suspeita de doença desmielinizante.

TÉCNICA: Sequências axiais FLAIR, T1 e T2.

ACHADOS:
Não há lesões na substância branca. Não há lesões periventriculares, justacorticais ou infratentoriais. Sem sinais de neurite óptica. Não há lesões com realce pelo gadolínio. Não há atrofia encefálica.

CONCLUSÃO: Sem lesões desmielinizantes no encéfalo."""

JSON_SEM_LESOES = {
    "identificacao_protocolo": {
        "data_exame": "2026-07-20",
        "tipo_exame": "RESSONÂNCIA MAGNÉTICA DO CRÂNIO",
        "regiao_examinada": "Encéfalo",
        "indicacao_clinica": "Controle de paciente com suspeita de doença desmielinizante.",
        "tecnica": "Sequências axiais FLAIR, T1 e T2.",
    },
    "atividade_inflamatoria": {
        "realce_gadolinio": False,
        "quantidade_lesoes_com_realce": None,
        "padrao_realce": None,
        "evidencia": "Não há lesões com realce pelo gadolínio",
    },
    "biomarcadores_avancados": {
        "sinal_veia_central": None,
        "lesoes_anel_paramagnetico_prl": None,
        "evidencia": None,
    },
    "atrofia_achados_cronicos": {
        "atrofia_encefalica": False,
        "buracos_negros_t1": None,
        "evidencia": "Não há atrofia encefálica",
    },
    "lesoes": [],
    "conclusao": {
        "texto": "Sem lesões desmielinizantes no encéfalo.",
        "evidencia": "Sem lesões desmielinizantes no encéfalo.",
    },
}


def test_extrai_laudo_com_varias_lesoes(monkeypatch):
    _mockar_groq(monkeypatch, JSON_MULTIPLAS_LESOES)
    laudo = extrair_laudo(TEXTO_MULTIPLAS_LESOES)

    assert isinstance(laudo, LaudoEstruturado)
    assert laudo.identificacao_protocolo.data_exame == date(2026, 7, 15)
    assert laudo.identificacao_protocolo.tipo_exame == "RESSONÂNCIA MAGNÉTICA DO CRÂNIO"
    assert "T2" in laudo.identificacao_protocolo.tecnica

    assert laudo.atividade_inflamatoria.realce_gadolinio is True
    assert laudo.atividade_inflamatoria.quantidade_lesoes_com_realce == 1

    assert len(laudo.lesoes) == 4
    assert laudo.lesoes[3].tamanho_mm == 8.0
    assert laudo.lesoes[3].realce_contraste is True


def test_extrai_laudo_sem_lesoes(monkeypatch):
    _mockar_groq(monkeypatch, JSON_SEM_LESOES)
    laudo = extrair_laudo(TEXTO_SEM_LESOES)

    assert laudo.lesoes == []

    assert laudo.atividade_inflamatoria.realce_gadolinio is False
    assert laudo.atrofia_achados_cronicos.atrofia_encefalica is False
    assert laudo.atrofia_achados_cronicos.buracos_negros_t1 is None


def test_evidencias_sao_trechos_literais_do_texto(monkeypatch):
    _mockar_groq(monkeypatch, JSON_MULTIPLAS_LESOES)
    laudo = extrair_laudo(TEXTO_MULTIPLAS_LESOES)

    evidencias = [
        laudo.atividade_inflamatoria.evidencia,
        laudo.conclusao.evidencia,
        *[lesao.evidencia for lesao in laudo.lesoes],
    ]
    for evidencia in evidencias:
        assert evidencia and evidencia in TEXTO_MULTIPLAS_LESOES


def test_sem_dados_pessoais_no_resultado(monkeypatch):
    _mockar_groq(monkeypatch, JSON_MULTIPLAS_LESOES)
    laudo = extrair_laudo(TEXTO_MULTIPLAS_LESOES)
    resultado = laudo.model_dump_json()

    assert not re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", resultado)
    assert not re.search(r"\(\d{2}\)\s?\d{4,5}-\d{4}", resultado)
    assert "@" not in resultado
    assert "[NOME]" not in resultado
    assert "[PRONTUARIO]" not in resultado


def test_informacoes_nao_mencionadas_ficam_nulas(monkeypatch):
    _mockar_groq(monkeypatch, JSON_SEM_LESOES)
    laudo = extrair_laudo(TEXTO_SEM_LESOES)

    assert laudo.biomarcadores_avancados.sinal_veia_central is None
    assert laudo.biomarcadores_avancados.lesoes_anel_paramagnetico_prl is None
    assert laudo.atividade_inflamatoria.quantidade_lesoes_com_realce is None
    assert laudo.atividade_inflamatoria.padrao_realce is None


def test_usa_structured_output_com_o_modelo_configurado(monkeypatch):
    captura = _mockar_groq(monkeypatch, JSON_MULTIPLAS_LESOES)
    extrair_laudo(TEXTO_MULTIPLAS_LESOES)

    kwargs = captura["kwargs"]
    assert kwargs["model"] == MODELO_GROQ
    assert kwargs["temperature"] == 0.0
    assert kwargs["max_tokens"] == MAX_TOKENS_SAIDA

    formato = kwargs["response_format"]
    assert formato["type"] == "json_schema"
    assert formato["json_schema"]["name"] == "laudo_estruturado"
    assert formato["json_schema"]["strict"] is True

    mensagens = kwargs["messages"]
    assert mensagens[0]["role"] == "system"
    assert "ressonância magnética" in mensagens[0]["content"].lower()
    assert TEXTO_MULTIPLAS_LESOES in mensagens[1]["content"]


def test_esquema_groq_inline_e_estrito():
    esquema = _esquema_para_groq()
    serializado = json.dumps(esquema)
    assert "$ref" not in serializado
    assert "$defs" not in serializado


def test_json_invalido_do_llm_levanta_erro(monkeypatch):
    _mockar_groq_conteudo(monkeypatch, "isto não é json {")
    with pytest.raises(ErroExtracaoLaudo):
        extrair_laudo(TEXTO_MULTIPLAS_LESOES)


def test_resposta_fora_do_schema_levanta_erro(monkeypatch):
    _mockar_groq(monkeypatch, {"campo_inventado": "x"})
    with pytest.raises(ErroExtracaoLaudo):
        extrair_laudo(TEXTO_MULTIPLAS_LESOES)


def test_resposta_vazia_levanta_erro(monkeypatch):
    _mockar_groq_conteudo(monkeypatch, None)
    with pytest.raises(ErroExtracaoLaudo):
        extrair_laudo(TEXTO_MULTIPLAS_LESOES)


def test_texto_vazio_levanta_erro(monkeypatch):
    with pytest.raises(ErroExtracaoLaudo):
        extrair_laudo("   ")


def _erro_rate_limit():
    import httpx

    resposta = httpx.Response(
        429,
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        headers={"retry-after": "0"},
    )
    return RateLimitError("rate limited", response=resposta, body={})


def test_retenta_quando_atinge_rate_limit(monkeypatch):
    chamadas = {"n": 0}

    def fake_create(**kwargs):
        chamadas["n"] += 1
        if chamadas["n"] < 3:
            raise _erro_rate_limit()
        return _FakeResposta(json.dumps(JSON_SEM_LESOES, ensure_ascii=False))

    monkeypatch.setattr(groq_client.chat.completions, "create", fake_create)
    monkeypatch.setattr("app.services.extractor_ia.time.sleep", lambda s: None)

    laudo = extrair_laudo(TEXTO_SEM_LESOES)

    assert isinstance(laudo, LaudoEstruturado)
    assert chamadas["n"] == 3


def _erro_413():
    import httpx

    resposta = httpx.Response(
        413,
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
    )
    mensagem = (
        "Request too large for model `openai/gpt-oss-120b` on tokens per minute "
        "(TPM): Limit 8000, Requested 8078, please reduce your message size and try again."
    )
    return APIStatusError(mensagem, response=resposta, body={})


def test_413_reduz_max_tokens_e_retenta(monkeypatch):
    chamadas = {"n": 0, "max_tokens": []}

    def fake_create(**kwargs):
        chamadas["n"] += 1
        chamadas["max_tokens"].append(kwargs["max_tokens"])
        if chamadas["n"] == 1:
            raise _erro_413()
        return _FakeResposta(json.dumps(JSON_SEM_LESOES, ensure_ascii=False))

    monkeypatch.setattr(groq_client.chat.completions, "create", fake_create)
    monkeypatch.setattr("app.services.extractor_ia.time.sleep", lambda s: None)

    laudo = extrair_laudo(TEXTO_SEM_LESOES)

    assert isinstance(laudo, LaudoEstruturado)
    assert chamadas["n"] == 2
    assert chamadas["max_tokens"] == [MAX_TOKENS_SAIDA, 3818]


def test_413_persistente_levanta_erro(monkeypatch):
    def fake_create(**kwargs):
        raise _erro_413()

    monkeypatch.setattr(groq_client.chat.completions, "create", fake_create)
    monkeypatch.setattr("app.services.extractor_ia.time.sleep", lambda s: None)

    with pytest.raises(ErroExtracaoLaudo):
        extrair_laudo(TEXTO_SEM_LESOES)


def test_rate_limit_esgotado_levanta_erro(monkeypatch):
    def fake_create(**kwargs):
        raise _erro_rate_limit()

    monkeypatch.setattr(groq_client.chat.completions, "create", fake_create)
    monkeypatch.setattr("app.services.extractor_ia.time.sleep", lambda s: None)

    with pytest.raises(ErroExtracaoLaudo):
        extrair_laudo(TEXTO_SEM_LESOES)
