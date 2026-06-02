import os
from dotenv import load_dotenv


from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

prompt = PromptTemplate.from_template(
"""
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

PERGUNTA DO USUÁRIO: {pergunta}
"""
)

def init_chat(question=None):
    return input(f"{question}: ")

def search_postgres(question: str) -> str:
    """Busca contexto relevante no PostgreSQL vector store."""
    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    )
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    results = store.similarity_search_with_score(question, k=10)

    if not results:
        return "Nenhum resultado encontrado."

    output = []
    for i, (doc, score) in enumerate(results, start=1):
        output.append(f"[Resultado {i} | Score: {score:.2f}]")
        output.append(doc.page_content.strip())
        output.append("")
    
    return "\n".join(output)

# Para executar diretamente, sem usar o chat.py
def main():
    question = init_chat("Faça sua pergunta")
    contexto = search_postgres(question)

    llm = ChatOpenAI(model="gpt-4o-mini", disable_streaming=True)

    response = prompt | llm
    resposta_final = response.invoke({
        "pergunta": question,
        "contexto": contexto
    })

    print(resposta_final.content)
    return resposta_final.content

if __name__ == "__main__":
    main()
    
# Para usar via chat.py
def search_prompt(question: str) -> str | None:
    """Busca contexto e retorna resposta do LLM."""
    try:
        contexto = search_postgres(question)
        llm = ChatOpenAI(model="gpt-4o-mini", disable_streaming=True)
        chain = prompt | llm
        resposta = chain.invoke({"pergunta": question, "contexto": contexto})
        return resposta.content
    except Exception as e:
        print(f"Erro ao processar pergunta: {e}")
        return None
    
# llm = ChatOpenAI(model="gpt-4o-mini", disable_streaming=True)

# # Pipeline: prompt | llm
# chain = prompt | llm

# # Execução
# question = init_chat("Faça sua pergunta")
# contexto = search_postgres(question)

# response = chain.invoke({
#     "pergunta": question,
#     "contexto": contexto
# })

# print(response.content)