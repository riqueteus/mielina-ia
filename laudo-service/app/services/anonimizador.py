import re

import spacy

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("pt_core_news_sm")
    return _nlp


CAMPOS_NOME = re.compile(
    r"\b(?P<campo>NOME|SOLICITANTE|PACIENTE|M[ÉE]DICO RESPONS[ÁA]VEL|"
    r"M[ÉE]DICO EXECUTANTE|RADIOLOGISTA)\s*:\s*"
    r"(?P<valor>[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ\s\.]{2,}?)"
    r"(?=\s+(?:PRONTU[ÁA]RIO|AN\b|CPF|RG|TELEFONE|DATA|SOLICITANTE|PACIENTE|RESSON|$))",
    re.IGNORECASE,
)

CAMPOS_VALOR_NUMERICO = [
    (re.compile(r"\bPRONTU[ÁA]RIO\s*:?\s*([A-Za-z0-9\-]+)", re.IGNORECASE), "[PRONTUARIO]"),
    (re.compile(r"\bAN\s*:?\s*(\d{4,})", re.IGNORECASE | re.UNICODE), "[PRONTUARIO]"),
    (re.compile(r"\bCPF\s*:?\s*([\d.\-]+)", re.IGNORECASE), "[CPF]"),
    (re.compile(r"\bRG\s*:?\s*([\d.\-]+)", re.IGNORECASE), "[RG]"),
    (re.compile(r"\bTELEFONE\s*:?\s*([\d\s()\-]{8,})", re.IGNORECASE), "[TELEFONE]"),
    (re.compile(r"\bDATA DE NASCIMENTO\s*:?\s*([\d/]{6,})", re.IGNORECASE), "[DATA_NASCIMENTO]"),
    (re.compile(r"\bE-?MAIL\s*:?\s*([\w.\-]+@[\w.\-]+)", re.IGNORECASE), "[EMAIL]"),
]

PADROES_SOLTOS = [
    (re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"), "[CPF]"),
    (re.compile(r"\b\d{11}\b"), "[NUMERO_LONGO]"),
    (re.compile(r"\(\d{2}\)\s?\d{4,5}-\d{4}"), "[TELEFONE]"),
    (re.compile(r"\b[\w.\-]+@[\w.\-]+\.[A-z]{2,}\b"), "[EMAIL]"),
]

TERMOS_MEDICOS = {
    "RESSONÂNCIA", "RESSONANCIA", "MAGNÉTICA", "MAGNETICA", "MAGNÉTICO", "MAGNETICO",
    "CRÂNIO", "CRANIO", "ENCÉFALO", "ENCEFALO", "CEREBRAL", "COLUNA", "CERVICAL",
    "TORÁCICA", "TORACICA", "LOMBAR", "SACRAL", "SACRO", "ÓRBITAS", "ORBITAS",
    "TOMOGRAFIA", "RADIOGRAFIA", "MAMOGRAFIA", "ANGIOGRAFIA", "ULTRASSONOGRAFIA",
    "DOPPLER", "FLAIR", "CONTRASTE", "GADOLÍNIO", "GADOLINIO", "SAGITAL", "AXIAL",
    "CORONAL", "SEDAÇÃO", "SEDACAO", "PÉLVICA", "PELVICA", "PELVE", "ABDÔMEN",
    "ABDOMEN", "PRÓSTATA", "PROSTATA", "MAMAS",
}


def _eh_termo_medico(entidade) -> bool:
    palavras = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", entidade.text.upper())
    return any(palavra in TERMOS_MEDICOS for palavra in palavras)


def _aplicar_campos_numericos(texto: str) -> str:
    resultado = texto
    for padrao, substituto in CAMPOS_VALOR_NUMERICO:
        resultado = padrao.sub(substituto, resultado)
    return resultado


def _mascarar_nomes_rotulados(texto: str) -> str:
    def _sub(match):
        campo = match.group("campo")
        return f"{campo}: [NOME]"

    return CAMPOS_NOME.sub(_sub, texto)


def _anonimizar_nomes_livres(texto: str) -> str:
    doc = _get_nlp()(texto)
    spans = sorted(
        [
            e
            for e in doc.ents
            if e.label_ == "PER"
            and len(e.text.strip()) >= 3
            and " " in e.text.strip()
            and not _eh_termo_medico(e)
        ],
        key=lambda e: -e.start_char,
    )
    for ent in spans:
        texto = texto[: ent.start_char] + "[NOME]" + texto[ent.end_char :]
    return texto


def anonimizar_texto(texto: str) -> str:
    resultado = _mascarar_nomes_rotulados(texto)
    resultado = _aplicar_campos_numericos(resultado)
    for padrao, substituto in PADROES_SOLTOS:
        resultado = padrao.sub(substituto, resultado)
    resultado = _anonimizar_nomes_livres(resultado)
    return resultado.strip()
