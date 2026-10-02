# RAG com PGVector — Desafio MBA Engenharia de Software com IA (Full Cycle)

Sistema de busca semântica com recuperação aumentada por geração (RAG) utilizando PostgreSQL com extensão pgvector, embeddings da OpenAI e LLM via LangChain.

---

## Visão Geral

```
PDF → ingest.py → PGVector (PostgreSQL)
                        ↓
      chat.py → search.py → similarity_search → LLM → resposta
```

O projeto possui dois fluxos principais:

- **Ingestão** (`ingest.py`): carrega um PDF, divide em chunks, gera embeddings e armazena no PostgreSQL.
- **Busca/Chat** (`search.py` + `chat.py`): recebe uma pergunta, busca os chunks mais relevantes por similaridade semântica e responde com base apenas no contexto recuperado.

---

## Estrutura do Projeto

```
├── docker-compose/
│   ├── docker-compose.yml   # PostgreSQL com pgvector
│   └── init.sql             # Habilita a extensão vector
├── src/
│   ├── docs/
│   │   └── document.pdf     # PDF a ser ingerido
│   ├── ingest.py            # Pipeline de ingestão do PDF
│   ├── search.py            # Busca semântica + resposta via LLM
│   └── chat.py              # Interface de chat em loop
└── README.md
```

---

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Chave de API da OpenAI

---

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

### 2. Crie o ambiente virtual e instale as dependências

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sk-...

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=documentos

OPENAI_EMBEDDING_MODEL=text-embedding-3-small

PDF_PATH=docs
PDF_NAME=document.pdf
```

---

## Execução

### 1. Suba o banco de dados

```bash
cd docker-compose
docker compose up -d
```

O `init.sql` habilita automaticamente a extensão `vector` no banco.

### 2. Ingira o PDF

Coloque o PDF em `src/docs/` e execute:

```bash
cd src
python ingest.py
```

O script irá:
1. Carregar o PDF
2. Dividir em chunks (tamanho: 1000, overlap: 150)
3. Gerar embeddings via OpenAI
4. Armazenar os vetores no PostgreSQL

### 3. Inicie o chat

```bash
cd src
python chat.py
```

```
=== Chat Iniciado ===
Digite 'sair' para encerrar.

Você: Qual o faturamento da empresa?
Assistente: ...

Você: sair
Encerrando o chat. Até mais!
```

Ou execute uma busca direta sem o loop de chat:

```bash
python search.py
```

![Diagrama do sistema](./exemplo.png)

---

## Dependências

| Pacote | Uso |
|---|---|
| `langchain` | Orquestração do pipeline |
| `langchain-openai` | `ChatOpenAI` e `OpenAIEmbeddings` |
| `langchain-postgres` | `PGVector` |
| `langchain-community` | `PyPDFLoader` |
| `langchain-text-splitters` | `RecursiveCharacterTextSplitter` |
| `langchain-core` | `PromptTemplate`, `Document` |
| `psycopg2-binary` | Driver PostgreSQL |
| `pgvector` | Extensão vetorial do PostgreSQL |
| `python-dotenv` | Leitura do `.env` |

---

## Regras de Resposta

O assistente responde **somente** com base no contexto recuperado do banco de dados. Caso a informação não esteja disponível, retorna:

> "Não tenho informações necessárias para responder sua pergunta."

Nunca utiliza conhecimento externo ou produz opiniões além do que está no documento.
