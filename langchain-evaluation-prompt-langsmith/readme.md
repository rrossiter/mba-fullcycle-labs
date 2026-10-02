# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

# Estrutura do projeto

```
desafio-prompt-engineer/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
│
├── prompts/
│   ├── bug_to_user_story_v1.yml       # Prompt inicial (após pull)
│   └── bug_to_user_story_v2.yml       # Seu prompt otimizado
│
├── datasets/
│   ├── bug_to_user_story.jsonl       # Data set a ser carregado
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith
│   ├── push_prompts.py       # Push ao LangSmith
│   ├── evaluate.py           # Avaliação automática
│   ├── metrics.py            # 4 métricas implementadas
│   └── utils.py              # Funções auxiliares
│
├── tests/
│   └── test_prompts.py       # Testes de validação
│
```

## Configuração

### 1. Variáveis de Ambiente

Configure no `.env` na raiz do projeto:

```bash
# Langsimth Configuration

OPENAI_API_KEY=''

# LangSmith Configuration
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=

# Publique um prompt no langsmith hub para gerar seu username, depois abra o prompt e vá no simbolo de cadeado.
USERNAME_LANGSMITH_HUB=

# Google Gemini Configuration
GOOGLE_API_KEY=

LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o

# OpenAI (para usar nos prompts)
OPENAI_API_KEY=""
```

### 2. Instalação

```bash
pip install -r requeriments.txt
```

## Exemplo no CLI

```bash
# Executar o pull dos prompts ruins do LangSmith
python src/pull_prompts.py

# Executar avaliação inicial (prompts ruins)
python src/evaluate.py

## Testes Unitários
pytest -v
```