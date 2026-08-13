"""Schema estruturado de um laudo de RM (Esclerose Múltipla).

Modelo único ``LaudoEstruturado`` usado para validar o JSON extraído de UM
laudo pelo LLM. Campos ausentes ficam ``None`` (laudo não informa) e campos
``False`` significam que o laudo afirma explicitamente a ausência.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IdentificacaoProtocolo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data_exame: Optional[date] = None
    tipo_exame: Optional[str] = None
    regiao_examinada: Optional[str] = None
    indicacao_clinica: Optional[str] = None
    tecnica: Optional[str] = None


class AtividadeInflamatoria(BaseModel):
    model_config = ConfigDict(extra="forbid")

    realce_gadolinio: Optional[bool] = None
    quantidade_lesoes_com_realce: Optional[int] = None
    padrao_realce: Optional[str] = None
    evidencia: Optional[str] = None


class BiomarcadoresAvancados(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sinal_veia_central: Optional[bool] = None
    lesoes_anel_paramagnetico_prl: Optional[bool] = None
    evidencia: Optional[str] = None


class AtrofiaAchadosCronicos(BaseModel):
    model_config = ConfigDict(extra="forbid")

    atrofia_encefalica: Optional[bool] = None
    buracos_negros_t1: Optional[bool] = None
    evidencia: Optional[str] = None


class Lesao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    localizacao: Optional[str] = None
    regiao: Optional[str] = None
    tamanho_mm: Optional[float] = None
    caracteristica: Optional[str] = None
    realce_contraste: Optional[bool] = None
    evidencia: Optional[str] = None


class Conclusao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto: Optional[str] = None
    evidencia: Optional[str] = None


class LaudoEstruturado(BaseModel):
    """JSON estruturado extraído de um único laudo de RM anonimizado."""

    model_config = ConfigDict(extra="forbid")

    identificacao_protocolo: IdentificacaoProtocolo = Field(
        default_factory=IdentificacaoProtocolo
    )
    atividade_inflamatoria: AtividadeInflamatoria = Field(
        default_factory=AtividadeInflamatoria
    )
    biomarcadores_avancados: BiomarcadoresAvancados = Field(
        default_factory=BiomarcadoresAvancados
    )
    atrofia_achados_cronicos: AtrofiaAchadosCronicos = Field(
        default_factory=AtrofiaAchadosCronicos
    )
    lesoes: list[Lesao] = Field(default_factory=list)
    conclusao: Conclusao = Field(default_factory=Conclusao)