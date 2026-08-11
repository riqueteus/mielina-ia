from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Lesao(BaseModel):
    localizacao: Optional[str] = None
    regiao: Optional[
        Literal[
            "periventricular",
            "juxtacortical",
            "infratentorial",
            "medular",
            "corpo caloso",
            "outra",
            "nao especificada",
        ]
    ] = "nao especificada"
    tamanho_mm: Optional[float] = None
    caracteristica: Optional[str] = None
    realce_contraste: Optional[bool] = None
    nova: Optional[bool] = None
    nota: Optional[str] = None


class LaudoExtraido(BaseModel):
    data_exame: Optional[date] = None
    tipo_exame: Optional[str] = None
    indicacao_clinica: Optional[str] = None
    tecnica: Optional[str] = None

    num_lesoes_total: Optional[int] = None
    lesoes: list[Lesao] = Field(default_factory=list)

    lesoes_periventriculares: Optional[int] = None
    lesoes_justacorticais: Optional[int] = None
    lesoes_infratentoriais: Optional[int] = None
    lesoes_medulares: Optional[int] = None

    lesoes_novas: Optional[int] = None
    lesoes_com_realce: Optional[int] = None
    lesao_maior_mm: Optional[float] = None

    atrofia_cerebral: Optional[bool] = None
    hidrocefalia: Optional[bool] = None

    atividade_doenca: Optional[
        Literal["ativa", "inativa", "duvidosa", "nao especificada"]
    ] = "nao especificada"
    diagnostico_principal: Optional[str] = None
    conclusao: Optional[str] = None
    observacoes_comparativas: Optional[str] = None

    campos_nao_encontrados: list[str] = Field(default_factory=list)