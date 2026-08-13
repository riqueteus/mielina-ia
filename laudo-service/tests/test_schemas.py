"""Testes básicos do schema ``LaudoEstruturado``.

Cobrem os dois casos principais: um laudo preenchido (com lesões) e um
laudo sem lesões, além do comportamento quando o modelo não é informado.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from pydantic import ValidationError

from app.schemas import LaudoEstruturado

LAUDO_COMPLETO = {
    "identificacao_protocolo": {
        "data_exame": "2026-07-15",
        "tipo_exame": "RESSONÂNCIA MAGNÉTICA DO CRÂNIO",
        "regiao_examinada": "Encéfalo",
        "indicacao_clinica": "Parestesias em membros superiores. Avaliação de doença desmielinizante.",
        "tecnica": "Sequências axiais, sagitais e coronais, com e sem contraste.",
    },
    "atividade_inflamatoria": {
        "realce_gadolinio": True,
        "quantidade_lesoes_com_realce": 1,
        "padrao_realce": "Realce nodular homogêneo",
        "evidencia": "Uma lesão apresenta realce pelo gadolínio.",
    },
    "biomarcadores_avancados": {
        "sinal_veia_central": False,
        "lesoes_anel_paramagnetico_prl": False,
        "evidencia": "Não há sinal de veia central nem lesões com anel paramagnético.",
    },
    "atrofia_achados_cronicos": {
        "atrofia_encefalica": False,
        "buracos_negros_t1": False,
        "evidencia": "Não há atrofia encefálica nem buracos negros em T1.",
    },
    "lesoes": [
        {
            "localizacao": "Frontoparietal direita",
            "regiao": "justacortical",
            "tamanho_mm": 6.0,
            "caracteristica": "Lesão hiperintensa em T2/FLAIR, sem efeito de massa",
            "realce_contraste": False,
            "evidencia": "Lesão justacortical de cerca de 6 mm em região frontoparietal direita.",
        },
        {
            "localizacao": "Corno occipital esquerdo",
            "regiao": "periventricular",
            "tamanho_mm": 8.0,
            "caracteristica": "Lesão ovoide hiperintensa em T2/FLAIR",
            "realce_contraste": True,
            "evidencia": "Lesão periventricular com realce pelo contraste.",
        },
    ],
    "conclusao": {
        "texto": "Múltiplas lesões desmielinizantes com atividade inflamatória em uma lesão.",
        "evidencia": "O laudo descreve múltiplas lesões desmielinizantes, com uma apresentando realce.",
    },
}

LAUDO_SEM_LESOES = {
    "identificacao_protocolo": {
        "data_exame": "2026-07-20",
        "tipo_exame": "RESSONÂNCIA MAGNÉTICA DO CRÂNIO",
        "regiao_examinada": "Encéfalo",
        "indicacao_clinica": "Controle de paciente com suspeita de doença desmielinizante.",
        "tecnica": "Sequências axiais, sagitais e coronais.",
    },
    "atividade_inflamatoria": {
        "realce_gadolinio": False,
        "quantidade_lesoes_com_realce": None,
        "padrao_realce": None,
        "evidencia": "Não há lesões com realce pelo gadolínio.",
    },
    "biomarcadores_avancados": {
        "sinal_veia_central": None,
        "lesoes_anel_paramagnetico_prl": None,
        "evidencia": None,
    },
    "atrofia_achados_cronicos": {
        "atrofia_encefalica": False,
        "buracos_negros_t1": False,
        "evidencia": "Não há sinais de atrofia encefálica nem buracos negros em T1.",
    },
    "lesoes": [],
    "conclusao": {
        "texto": "Sem lesões desmielinizantes no encéfalo.",
        "evidencia": "Não foram identificadas lesões focais.",
    },
}


def test_laudo_completo_valido():
    laudo = LaudoEstruturado.model_validate(LAUDO_COMPLETO)

    assert laudo.identificacao_protocolo.data_exame.isoformat() == "2026-07-15"
    assert laudo.identificacao_protocolo.tipo_exame == "RESSONÂNCIA MAGNÉTICA DO CRÂNIO"
    assert laudo.identificacao_protocolo.regiao_examinada == "Encéfalo"

    assert laudo.atividade_inflamatoria.realce_gadolinio is True
    assert laudo.atividade_inflamatoria.quantidade_lesoes_com_realce == 1

    assert laudo.atrofia_achados_cronicos.atrofia_encefalica is False

    assert len(laudo.lesoes) == 2
    assert laudo.lesoes[0].regiao == "justacortical"
    assert laudo.lesoes[0].tamanho_mm == 6.0
    assert laudo.lesoes[1].realce_contraste is True

    assert laudo.conclusao.texto
    assert laudo.conclusao.evidencia


def test_laudo_sem_lesoes_valido():
    laudo = LaudoEstruturado.model_validate(LAUDO_SEM_LESOES)

    assert laudo.lesoes == []

    assert laudo.atividade_inflamatoria.realce_gadolinio is False
    assert laudo.atividade_inflamatoria.quantidade_lesoes_com_realce is None


def test_laudo_vazio_aceita_informacoes_ausentes():
    laudo = LaudoEstruturado()

    assert laudo.identificacao_protocolo.data_exame is None
    assert laudo.identificacao_protocolo.regiao_examinada is None
    assert laudo.lesoes == []
    assert laudo.atividade_inflamatoria.realce_gadolinio is None
    assert laudo.conclusao.texto is None


def test_campo_nova_nao_e_aceito():
    with pytest.raises(ValidationError):
        LaudoEstruturado.model_validate({"lesoes": [{"nova": True}]})


def test_campo_desconhecido_nao_e_aceito():
    with pytest.raises(ValidationError):
        LaudoEstruturado.model_validate({"diagnostico_principal": "esclerose múltipla"})
