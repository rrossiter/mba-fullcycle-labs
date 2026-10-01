# Pull, Otimização e Avaliação de Prompts com LangChain e LangFuse

# Estrutura do projeto

```
.
├── docker-compose.yml          ← Langfuse + Postgres
├── .env.example                ← Variáveis de ambiente necessárias
├── requirements.txt
├── datasets/
│   └── bug_to_user_story.jsonl ← Dataset de avaliação (20 exemplos)
├── prompts/
│   ├── bug_to_user_story_v1.yml  ← Prompt baseline
│   └── bug_to_user_story_v2.yml  ← Prompt otimizado (few-shot + CoT)
└── src/
    ├── pull_prompts.py     ← Envia prompts ao Langfuse
    ├── push_promts.py      ← Envia dataset ao Langfuse
    ├── evalueteV1.py       ← Avaliação pairwise v1
    ├── evalueteV1.py       ← Avaliação pairwise v2
    ├── metrics.py          ← 7 métricas LLM-as-Judge
    └── utils.py            ← Helpers (LLM factory, YAML, etc.)
```

## Configuração

### 1. Variáveis de Ambiente

Configure no `.env` na raiz do projeto:

```bash
# Langfuse Configuration
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="http://localhost:3000"  # ou https://cloud.langfuse.com

# OpenAI (para usar nos prompts)
OPENAI_API_KEY="sk-..."
```

### 2. Instalação

```bash
pip install -r requeriments.txt
```

### 3. Langfuse Server

**Docker (Recomendado para desenvolvimento)**
```bash
# Clone o repo oficial
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# Inicie com docker-compose
docker-compose up -d

# Acesse: http://localhost:3000
# Faça a configuração inicial antes de executar o passo a passo a seguir.
```

## Exemplo no CLI

```bash
# Executar o pull dos prompts ruins do LangFuse
python src/pull_prompts.py

# Executar avaliação inicial (prompts ruins)
python src/evaluateV1.py

# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação final (prompts otimizados)
python src/evaluateV2.py

## Testes Unitários
pytest -v
```