# Mielina — IA para apoio a pacientes com Esclerose Múltipla

Plataforma com **3 microsserviços em Python** que ajuda pacientes com Esclerose Múltipla (EM) a entenderem laudos de ressonância magnética (RM), tirarem dúvidas sobre a doença e estimarem o risco clínico — tudo com privacidade: dados pessoais são anonimizados antes de qualquer processamento por IA.

> Projeto de portfólio/estudo, com arquitetura de microsserviços, testes automatizados e deploy em nuvem.

---

## Como funciona (visão geral)

```
                    ┌─────────────────────┐
  Usuário sobe PDF  │   laudo-service     │  Extrai o laudo estruturado
  de laudo de RM ──▶│  (extração por IA)  │  (lesões, atividade, etc.)
                    └─────────────────────┘
                    ┌─────────────────────┐
  Usuário pergunta  │    rag-service      │  Busca na base de documentos
  sobre a doença ──▶│  (pergunta e resposta)│  e responde com fontes citadas
                    └─────────────────────┘
                    ┌─────────────────────┐
  Usuário responde  │classification-service│  Prevê % de risco de EM com
  questionário ────▶│ (regressão logística) │  modelo treinado
                    └─────────────────────┘
```

Os três serviços são **stateless** e conversam com serviços externos em nuvem (Groq para o LLM e Supabase para banco/embeddings/storage). Cada um roda no seu próprio container Docker.

---

## Serviços

| Serviço | Porta | Função | Destaque técnico |
|---|---|---|---|
| **laudo-service** | 7862 | Recebe o PDF do laudo de RM, anonimiza e extrai um laudo estruturado (lesões, região anatômica, realce por contraste, biomarcadores, conclusão) via LLM com saída estruturada (JSON Schema estrito) | Anonimização com **spaCy (NER pt)**, fallback determinístico por regex para a data do exame, retry automático em rate-limit da Groq |
| **rag-service** | 7860 | Responde perguntas sobre EM usando RAG: embeddings → busca vetorial (**pgvector** no Supabase) → resposta da LLM citando fontes | PDFs convertidos para Markdown com **Docling**; embeddings via **Hugging Face Inference API**; prioriza fontes oficiais e sinaliza quando não há resposta no contexto |
| **classification-service** | 7861 | Calcula o **percentual de risco de EM** a partir das respostas de um questionário | Modelo de **regressão logística** (joblib) treinado, baixado do Supabase Storage no startup |

---

## Stack

- **Linguagem:** Python 3.14
- **APIs:** FastAPI + Pydantic (validação e schemas) + Uvicorn
- **IA:** Groq (`openai/gpt-oss-120b`) para geração; Hugging Face Inference API para embeddings; spaCy para NER em português
- **Documentos:** Docling (PDF → Markdown com estrutura de tabelas) · LangChain (divisão de chunks)
- **ML:** scikit-learn / joblib (regressão logística)
- **Dados:** Supabase (PostgreSQL + pgvector + Storage)
- **Container & deploy:** Docker · Render (cloud)
- **Qualidade:** pytest (53 testes no laudo-service), tipagem com Pydantic

---

## Estrutura do repositório

```
mielina-ia/
├── laudo-service/          # Extração estruturada de laudos de RM
│   ├── app/
│   │   ├── services/       # pdf, anonimização, data do exame, extração via Groq
│   │   ├── core/           # config central de variáveis de ambiente
│   │   └── schemas.py      # LaudoEstruturado (Pydantic)
│   └── tests/              # 53 testes (mocks da Groq, anonimização, router)
├── rag-service/            # RAG: pergunta e resposta com fontes
│   └── app/
│       ├── routers/        # /pergunta e /ingest
│       └── services/       # extração (Docling), embeddings, chunks, busca vetorial
└── classification-service/ # Previsão de risco de EM
    └── app/
        ├── service.py      # regressão logística (joblib)
        └── model/          # modelo treinado (baixado do Storage)
```

---

## Como rodar localmente

Cada serviço é independente. Com **Docker**:

```bash
cd laudo-service
docker build -t laudo-service .
docker run -p 7862:7862 --env-file .env laudo-service
```

Sem Docker (ex.: laudo-service):

```bash
cd laudo-service
python -m venv .venv
.\.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m spacy download pt_core_news_sm
uvicorn app.main:app --port 7862
```

Crie um `.env` na raiz de cada serviço (veja a tabela abaixo).

### Variáveis de ambiente

| Variável | Onde é usada | Descrição |
|---|---|---|
| `GROQ_API_KEY` | laudo e rag | Chave da API Groq |
| `MODELO_GROQ` | laudo | Modelo LLM (padrão: `openai/gpt-oss-120b`) |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | rag e classification | Conexão com o Supabase |
| `PORT` | todos | Porta do servidor (o Render injeta automaticamente) |

> **Segurança:** os arquivos `.env` estão no `.gitignore` e nunca são commitados. As chaves ficam apenas no ambiente (local ou painel do Render).

---

## Testes

```bash
cd laudo-service
python -m pytest tests -q
```

A suíte cobre extração com **Groq mockada** (sem chamadas reais), anonimização, fallback de data e o endpoint HTTP — **53 testes passando**.

---

## Deploy

Cada serviço tem seu `Dockerfile` e `.dockerignore`, prontos para o Render (todos podem rodar no **plano gratuito**, que oferece 512 MB de RAM).

1. Conecte o repositório no Render e defina o **Root Directory** (`laudo-service`, `rag-service` ou `classification-service`).
2. Defina as variáveis de ambiente no painel.
3. Deploy automático a cada `push` na `main`.

---

## Aprendizados no caminho

**Arquitetura**
- **Custo × qualidade:** LLM em nuvem (Groq) em vez de modelo local, o que mantém os serviços leves (o laudo-service mediu ~232 MB de pico) e aptos para o plano gratuito do Render.
- **Monorepo com microsserviços:** cada serviço com config central única, testes próprios e Docker próprio.

**laudo-service (extração estruturada)**
- **Saída estruturada de LLM:** uso de `response_format` com JSON Schema estrito (Groq) + validação com Pydantic para garantir resposta confiável, sem parsing frágil.
- **Privacidade por design:** anonimização com NER antes do texto chegar ao LLM.
- **Rede de segurança determinística:** regex como fallback quando o LLM falha em campos simples (ex.: data do exame).
- **Anonimização para o português:** spaCy (NER `pt_core_news_sm`) + regex para PII brasileiras (CPF, RG, telefone, e-mail, prontuário) — nomes de paciente e médico mascarados antes de qualquer envio.
- **Prompt como "contrato" com o modelo:** mapa anatômico para classificar a região das lesões e regra de `evidencia` exigindo trecho literal do laudo — cada campo extraído aponta o texto que o justifica (rastreável e auditável).
- **Lidando com os limites da API:** retry com backoff em rate-limit e, em erro 413, redução automática do `max_tokens` de saída reaproveitando o limite informado pela própria Groq.
- **Testar IA sem custo:** a suíte mocka o client da Groq (53 testes) — determinismo nos testes e zero gasto de API no CI.
- **Modelo carregado sob demanda:** o spaCy só carrega na 1ª request — cold start leve e pico de memória (~232 MB) que cabe no plano gratuito.

**RAG (documentos e busca)**
- **Extração de PDF de alta fidelidade:** Docling converte PDFs em Markdown preservando títulos e tabelas — muito superior à extração de texto puro para gerar chunks com contexto de seção (também ajudou a otimizar memória processando em lotes de páginas).
- **Embeddings sem hospedar modelo:** a Hugging Face Inference API (`feature_extraction`, vetores de 384 dims) evita rodar modelo de embeddings localmente, com retry automático em 429/503 (modelo acordando na plataforma).
- **Experimentar e descartar:** comecei com um reranker local e o **removi** ao migrar os embeddings para a API da HF — menos infraestrutura para manter com resultado equivalente.

**Classification (ML)**
- **Do dataset ao deploy:** treinei e comparei diferentes algoritmos sobre um dataset clínico de EM; a **regressão logística** venceu por simplicidade e interpretabilidade. O modelo (joblib) fica no Supabase Storage e é baixado no startup — deploy sem acoplar o modelo ao repositório.
- **Ficha de características clínicas:** o questionário combina dados demográficos, exames (bandas oligoclonais, potenciais evocados) e achados de RM (periventricular, cortical, infratentorial, medular) para estimar o risco com `predict_proba`.