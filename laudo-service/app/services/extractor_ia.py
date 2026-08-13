"""Extração estruturada de laudos de RM via Groq (LLM).

Recebe o texto ANONIMIZADO de um único laudo, envia ao Groq com
structured output (JSON Schema, modo estrito) e devolve um
``LaudoEstruturado`` validado pelo Pydantic.
"""

import json
import re
import time
from copy import deepcopy

from groq import APIStatusError, RateLimitError
from pydantic import ValidationError

from app.core.config import MODELO_GROQ
from app.core.groq_client import groq_client
from app.schemas import LaudoEstruturado


class ErroExtracaoLaudo(Exception):
    """Falha ao extrair o laudo via LLM (transporte ou resposta inválida)."""


MAX_TOKENS_SAIDA = 4096
MAX_TOKENS_SAIDA_MINIMO = 1024
MAX_TENTATIVAS_RATE_LIMIT = 3


def _max_tokens_para_request(erro: APIStatusError, max_tokens_atual: int) -> int:
    """Calcula o maior ``max_tokens`` que cabe no limite TPM, a partir do erro 413.

    A Groq informa ``Limit N, Requested M`` na mensagem do erro; o tamanho de
    entrada é ``M - max_tokens_atual``. Usa o restante do limite com uma margem
    de segurança. Se não der para calcular, reduz pela metade.
    """
    texto = str(erro)
    pedido = re.search(r"Requested (\d+)", texto)
    limite = re.search(r"Limit (\d+)", texto)
    if pedido and limite:
        tokens_entrada = int(pedido.group(1)) - max_tokens_atual
        novo = int(limite.group(1)) - tokens_entrada - 200
        if novo > MAX_TOKENS_SAIDA_MINIMO:
            return novo
    return max(max_tokens_atual // 2, MAX_TOKENS_SAIDA_MINIMO)


def _espera_apos_rate_limit(erro: RateLimitError, tentativa: int) -> float:
    """Usa o ``retry-after`` da Groq quando houver; senão, backoff exponencial."""
    cabecalhos = getattr(getattr(erro, "response", None), "headers", {}) or {}
    retry_after = cabecalhos.get("retry-after")
    try:
        return float(retry_after)
    except (TypeError, ValueError):
        return min(2 ** (tentativa - 1), 30)


PROMPT_SISTEMA = """Você é um especialista em extração estruturada de laudos de ressonância magnética (RM) para avaliação de esclerose múltipla. Você recebe o texto ANONIMIZADO de UM único laudo de RM e deve preenchê-lo no JSON conforme o schema fornecido.

REGRAS OBRIGATÓRIAS:
1. Extraia apenas informações presentes no texto. Não invente valores, números, medidas ou achados. Preencher uma região anatômica a partir da localização descrita NÃO é inventar: é parte da sua tarefa de extração estruturada.
2. Não realize diagnóstico, não classifique a doença e não sugira condutas.
3. Não compare exames e não determine progressão, regressão, estabilidade, NEDA ou disseminação no tempo. Se o laudo citar exame anterior, registre isso apenas como texto/evidência, nunca como conclusão de evolução.
4. Não rotule lesões como "nova".
5. Valores lógicos: use `true` se o texto descrever o achado, MESMO que como "questionável", "sugestivo", "provável" ou "possível"; use `false` apenas se o texto afirmar explicitamente a ausência (ex.: "sem lesões", "não há realce"); use `null` quando o texto não mencionar o assunto. Mantenha a incerteza descrita na `evidencia` e na `caracteristica`.
6. `evidencia` deve ser um trecho LITERAL curto do texto anonimizado que justifique o valor. Copie o texto exatamente como está, sem reescrever.
7. Não inclua dados pessoais no resultado (nomes, CPF, RG, telefone, e-mail, endereço, prontuário). O texto já vem anonimizado; apenas não os reconstrua.
8. Siga a estrutura e os nomes de campos do schema exatamente como fornecidos. Responda APENAS com o JSON válido, sem nenhum texto extra.

MAPA DAS REGIÕES (classificação anatômica das lesões):
- periventricular: lesões periventriculares, pericalosas/pericallosas, junto aos cornos ventriculares ou adjacentes ao corpo caloso.
- justacortical_cortical: lesões justacorticais/subcorticais, em contato ou próximas ao córtex cerebral.
- infratentorial: lesões no cerebelo, tronco cerebral ou fossa posterior.
- medula_espinhal: QUALQUER foco, área, lesão, placa ou imagem hiperintensa descrita na medula espinhal (cervical, torácica ou lombar), mesmo que "questionável", "sugestivo", "provável" ou "possível" (ex.: hipersinal medular, imagem ovalada hiperintensa em medula).
- nervo_optico: achados no nervo óptico ou neurite óptica.
Use o MAPA para classificar o campo `lesoes[].regiao` de cada lesão, com a melhor região que se enquadrar.

SIGNIFICADO DOS CAMPOS:
- identificacao_protocolo.data_exame: data do exame no formato AAAA-MM-DD. tipo_exame: título/nome do exame. regiao_examinada: região do exame (ex.: crânio/encéfalo, coluna cervical). indicacao_clinica: motivo clínico, se informado. tecnica: descreva a técnica/sequências citadas, mesmo que em prosa sem rótulo (ex.: parágrafo de abertura que descreve o protocolo).
- atividade_inflamatoria.realce_gadolinio: true se o laudo relatar lesões com realce pelo contraste; false se afirmar que não há realce; senão null. `quantidade_lesoes_com_realce` e `padrao_realce` (ex.: nodular, anelar) somente se citados.
- biomarcadores_avancados.sinal_veia_central e lesoes_anel_paramagnetico_prl: true/false/null conforme o laudo.
- atrofia_achados_cronicos.atrofia_encefalica e buracos_negros_t1: true/false/null conforme o laudo.
- lesoes: uma entrada para cada lesão de desmielinização/alteração de sinal do parênquima (substância branca cerebral ou medula espinhal) descrita no laudo. NÃO inclua achados degenerativos ou mecânicos da coluna: protrusão, abaulamento ou hérnia discal, espondilose, osteófitos, estenose, estreitamento foraminal, alterações de partes moles ou de discos — esses não são lesões e NÃO devem entrar em `lesoes`. Se o laudo citar um grupo sem individualizar cada lesão (ex.: "três justacorticais em região frontoparietal"), represente o grupo como UMA entrada, sem duplicar a mesma lesão. Use `regiao` conforme o MAPA quando a lesão se enquadrar (periventricular, justacortical, infratentorial, medular); caso contrário, use a melhor localização anatômica (corpo caloso, outra, etc.). `tamanho_mm` somente se o laudo citar medida (converta cm para mm, ex.: 0,6 cm = 6). `realce_contraste`: true se houver realce, false se o laudo afirmar ausência de realce, null se não mencionar.
- conclusao: resumo fiel do que o laudo conclui. `texto` pode ser o texto literal da conclusão/impressão."""


def _resolver_refs(no: dict, defs: dict):
    """Substitui ``$ref`` por sua definição, recursivamente."""
    if isinstance(no, dict):
        if "$ref" in no:
            ref = no["$ref"]
            if ref.startswith("#/$defs/"):
                nome = ref.split("/")[-1]
                resolvido = deepcopy(defs[nome])
                resolvido.update({k: v for k, v in no.items() if k != "$ref"})
                no = resolvido
        return {chave: _resolver_refs(valor, defs) for chave, valor in no.items()}
    if isinstance(no, list):
        return [_resolver_refs(item, defs) for item in no]
    return no


def _normalizar_esquema(no):
    """Torna o schema compatível com o modo estrito da Groq.

    - objetos com ``additionalProperties: false`` e todos os campos ``required``;
    - campos opcionais viram union ``["tipo", "null"]``;
    - remove títulos/descrições desnecessários.
    """
    if isinstance(no, dict):
        if "anyOf" in no:
            nao_nulo = [p for p in no["anyOf"] if p.get("type") != "null"]
            if len(nao_nulo) == 1 and isinstance(nao_nulo[0].get("type"), str):
                base = {k: v for k, v in nao_nulo[0].items() if k != "type"}
                base["type"] = [nao_nulo[0]["type"], "null"]
                return _normalizar_esquema(base)
        tipo = no.get("type")
        if tipo == "object":
            propriedades = no.get("properties", {})
            no["required"] = sorted(propriedades)
            no["additionalProperties"] = False
            no["properties"] = {
                chave: _normalizar_esquema(valor) for chave, valor in propriedades.items()
            }
        elif tipo == "array" and "items" in no:
            no["items"] = _normalizar_esquema(no["items"])
        for chave in ("title", "default", "description"):
            no.pop(chave, None)
        return no
    if isinstance(no, list):
        return [_normalizar_esquema(item) for item in no]
    return no


def _esquema_para_groq() -> dict:
    """JSON Schema do ``LaudoEstruturado`` inline e pronto para strict mode."""
    esquema = LaudoEstruturado.model_json_schema()
    defs = esquema.pop("$defs", {})
    return _normalizar_esquema(_resolver_refs(esquema, defs))


def extrair_laudo(texto_anonimizado: str) -> LaudoEstruturado:
    """Envia o texto anonimizado ao Groq e devolve um ``LaudoEstruturado`` validado."""
    if not texto_anonimizado or not texto_anonimizado.strip():
        raise ErroExtracaoLaudo("Texto do laudo está vazio.")

    tentativa = 0
    max_tokens_saida = MAX_TOKENS_SAIDA
    while True:
        try:
            resposta = groq_client.chat.completions.create(
                model=MODELO_GROQ,
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {
                        "role": "user",
                        "content": f"TEXTO DO LAUDO ANONIMIZADO:\n{texto_anonimizado}",
                    },
                ],
                temperature=0.0,
                max_tokens=max_tokens_saida,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "laudo_estruturado",
                        "strict": True,
                        "schema": _esquema_para_groq(),
                    },
                },
            )
            break
        except RateLimitError as erro:
            tentativa += 1
            if tentativa >= MAX_TENTATIVAS_RATE_LIMIT:
                raise ErroExtracaoLaudo(
                    f"Limite de uso do Groq atingido após {tentativa} tentativas: {erro}"
                ) from erro
            time.sleep(_espera_apos_rate_limit(erro, tentativa))
        except APIStatusError as erro:
            if erro.status_code == 413:
                max_tokens_saida = _max_tokens_para_request(erro, max_tokens_saida)
                tentativa += 1
                if tentativa >= MAX_TENTATIVAS_RATE_LIMIT:
                    raise ErroExtracaoLaudo(
                        f"Request grande demais para o Groq mesmo após reduzir a saída: {erro}"
                    ) from erro
                continue
            raise ErroExtracaoLaudo(f"Falha na chamada ao Groq: {erro}") from erro
        except Exception as erro:
            raise ErroExtracaoLaudo(f"Falha na chamada ao Groq: {erro}") from erro

    conteudo = getattr(resposta.choices[0].message, "content", None)
    if not conteudo:
        raise ErroExtracaoLaudo("O Groq retornou resposta vazia.")

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise ErroExtracaoLaudo(f"O Groq retornou JSON inválido: {erro}") from erro

    try:
        return LaudoEstruturado.model_validate(dados)
    except ValidationError as erro:
        raise ErroExtracaoLaudo(
            f"Resposta do Groq não compatível com LaudoEstruturado: {erro}"
        ) from erro
