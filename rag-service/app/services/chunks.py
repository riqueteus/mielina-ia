import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Mapeamento de tipos
TIPOS_DOCUMENTO = {
    "Atlas da EM": "material_educativo_geral",
    "Esclerose Múltipla Promoção de Saúde": "material_tecnico_reabilitacao",
    "Eu Tenho Esclerose Múltipla e Agora": "material_educativo_paciente",
    "Manual de apoio a vida com EM": "material_educativo_paciente",
    "PROTOCOLO CLÍNICO E DIRETRIZES TERAPÊUTICAS": "protocolo_oficial_ms",
}

def identificar_tipo(nome_arquivo: str) -> str:
    """Descobre a categoria do PDF analisando o nome do arquivo."""
    for chave, tipo in TIPOS_DOCUMENTO.items():
        if chave.lower() in nome_arquivo.lower():
            return tipo
    return "outro"

def dividir_com_contexto_de_secao(texto: str) -> list[tuple[str, str]]:
    """Separa o texto completo em blocos baseados nos títulos Markdown (#, ##, ###)."""
    linhas = texto.split("\n")
    blocos = []
    secao_atual = "Introdução"
    buffer = []

    for linha in linhas:
        # Detecta cabeçalhos Markdown de nível 1 a 3
        match = re.match(r"^(#{1,3})\s+(.*)", linha)
        if match:
            if buffer:
                blocos.append((secao_atual, "\n".join(buffer)))
                buffer = []
            secao_atual = match.group(2).strip()
        else:
            buffer.append(linha)

    if buffer:
        blocos.append((secao_atual, "\n".join(buffer)))

    # Configuração do fatiador do LangChain 
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " "]
    )

    resultado = []
    for secao, bloco_texto in blocos:
        for sub in splitter.split_text(bloco_texto):
            if sub.strip():
                resultado.append((secao, sub))

    return resultado

def criar_chunks_documento(nome_arquivo: str, texto_completo: str) -> list[dict]:
    """
    Transforma a string de texto extraída em uma lista de chunks estruturados
    com IDs únicos e metadados prontos para a validação ou indexação.
    """
    tipo = identificar_tipo(nome_arquivo)
    chunks_com_secao = dividir_com_contexto_de_secao(texto_completo)
    
    lista_chunks_estruturados = []
    
    for i, (secao, chunk) in enumerate(chunks_com_secao):
        # Injeta o contexto no topo do texto do chunk
        texto_final = f"[Seção: {secao}]\n{chunk}"
        
        lista_chunks_estruturados.append({
            "id": f"{nome_arquivo}_chunk_{i}",
            "texto": texto_final,
            "metadados": {
                "fonte": nome_arquivo,
                "tipo": tipo,
                "secao": secao
            }
        })
        
    return lista_chunks_estruturados
