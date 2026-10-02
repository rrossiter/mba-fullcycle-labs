import os
from pathlib import Path
from dotenv import load_dotenv


from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

chunk_size = 1000
chunk_overlap = 150
load_dotenv()

for k in ("OPENAI_API_KEY", "DATABASE_URL","PG_VECTOR_COLLECTION_NAME"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

def ingest_pdf():
    docs = load_pdf()
    splits = split_documents(docs)

    validate_splits(splits)

    enriched = enrich_documents(splits)

    create_vector_store_openai().add_documents(
        documents=enriched,
        ids=generate_ids(enriched)
    )

def load_pdf():
    PDF_PATH = os.getenv("PDF_PATH")
    PDF_NAME = os.getenv("PDF_NAME")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_file = os.path.join(base_dir, PDF_PATH, PDF_NAME)
    return PyPDFLoader(pdf_file).load()

def split_documents(docs):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=False
    ).split_documents(docs)

def validate_splits(splits):
    if not splits:
        print("Nenhum chunk encontrado no PDF")
        raise SystemExit(0)
    
def enrich_documents(documents):
    return [
        Document(
            page_content=doc.page_content,
            metadata={
                k: v
                for k, v in doc.metadata.items()
                if v not in ("", None)
            }
        )
        for doc in documents
    ]

def generate_ids(documents):
    return [f"doc-{i}" for i in range(len(documents))]

def create_vector_store_openai():    
    return PGVector(
        embeddings=OpenAIEmbeddings(
            model=os.getenv(
                "OPENAI_EMBEDDING_MODEL",
                "text-embedding-3-small"
            )
        ),
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )
    
def create_vector_store_google():    
    return PGVector(
        embeddings=GoogleGenerativeAIEmbeddings(
            model=os.getenv(
                "GOOGLE_EMBEDDING_MODEL",
                "embedding-001"
            )
        ),
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )
    
if __name__ == "__main__":
    ingest_pdf()
    

