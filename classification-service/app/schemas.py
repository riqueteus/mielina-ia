from pydantic import BaseModel, Field
from typing import Literal

class RespostasQuestionario(BaseModel):
    Gender: Literal[1, 2]
    Age: int = Field(ge=0, le=120)
    Schooling: int = Field(ge=0, le=30)
    Breastfeeding: Literal[1, 2, 3]
    Varicella: Literal[1, 2, 3]
    Initial_Symptom: int = Field(ge=1, le=15)
    Mono_or_Polysymptomatic: Literal[1, 2, 3]
    Oligoclonal_Bands: Literal[0, 1]
    LLSSEP: Literal[0, 1]
    ULSSEP: Literal[0, 1]
    VEP: Literal[0, 1]
    BAEP: Literal[0, 1]
    Periventricular_MRI: Literal[0, 1]
    Cortical_MRI: Literal[0, 1]
    Infratentorial_MRI: Literal[0, 1]
    Spinal_Cord_MRI: Literal[0, 1]

class ResultadoPrevisao(BaseModel):
    percentual_risco: float
    erro: bool = False
    mensagem: str | None = None