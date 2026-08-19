"""Extrai a data do exame de forma determinística (regex) a partir do texto bruto.

O LLM (Groq) é ótimo para estruturar o laudo, mas às vezes retorna ``data_exame``
como ``null`` mesmo com a data presente no texto (ex.: ``Data: 24/07/2021``).
Como a data é estruturalmente simples, um fallback por regex é determinístico,
barato e confiável.

Também expõe ``normalizar_datas_para_iso``, que converte datas DD/MM/AAAA para
AAAA-MM-DD no texto enviado ao LLM — facilitando a vida do modelo, que já é
instruído a devolver a data nesse formato.
"""

import re
from datetime import date
from typing import Iterator, Optional, Tuple

_PADRAO_DDMMYYYY = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")
_PADRAO_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

_MARCADORES_NASCIMENTO = re.compile(
    r"\b(NASCIMENTO|NASC|NASCIDO)\b",
    re.IGNORECASE,
)


def _para_data(dia: int, mes: int, ano: int) -> Optional[date]:
    try:
        return date(ano, mes, dia)
    except ValueError:
        return None


def _datas_validas(texto: str) -> Iterator[Tuple[int, date]]:
    """Itera pelas datas válidas no texto, em ordem de aparição (posição)."""
    for m in _PADRAO_DDMMYYYY.finditer(texto):
        d = _para_data(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if d:
            yield m.start(), d
    for m in _PADRAO_ISO.finditer(texto):
        d = _para_data(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        if d:
            yield m.start(), d


def normalizar_datas_para_iso(texto: str) -> str:
    """Converte datas DD/MM/AAAA para AAAA-MM-DD no texto.

    Ajuda o LLM: o prompt já pede a data em AAAA-MM-DD, então ele encontra o
    valor já no formato esperado. Datas inválidas (ex.: 31/02/2021) são
    preservadas como estavam.
    """
    def _sub(m: re.Match) -> str:
        d = _para_data(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return d.isoformat() if d else m.group(0)

    return _PADRAO_DDMMYYYY.sub(_sub, texto)


def extrair_data_exame(texto: str) -> Optional[date]:
    """Busca a data do exame no texto bruto do PDF (fallback determinístico).

    Estratégia:
    1. Prefere a data que aparece logo após um rótulo "DATA" (ex.: "Data: 24/07/2021").
    2. Senão, usa a primeira data válida que NÃO seja de nascimento.
    """
    if not texto:
        return None

    for pos, d in _datas_validas(texto):
        contexto = texto[max(0, pos - 30):pos]
        if re.search(r"\bDATA\b", contexto, re.IGNORECASE) and not _MARCADORES_NASCIMENTO.search(contexto):
            return d

    for pos, d in _datas_validas(texto):
        contexto = texto[max(0, pos - 25):pos]
        if _MARCADORES_NASCIMENTO.search(contexto):
            continue
        return d

    return None