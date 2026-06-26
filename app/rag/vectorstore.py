import logging

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings

from app.core.config import Settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "rag_documents"


def build_embeddings(settings: Settings) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key or None,
    )


def get_vectorstore(settings: Settings) -> Chroma:
    settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=build_embeddings(settings),
        persist_directory=str(settings.chroma_persist_dir),
    )


def get_retriever(
    settings: Settings,
    *,
    top_k: int | None = None,
) -> VectorStoreRetriever:
    vectorstore = get_vectorstore(settings)
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k or settings.retrieval_top_k},
    )


def add_documents(settings: Settings, documents: list[Document]) -> int:
    if not documents:
        return 0

    vectorstore = get_vectorstore(settings)
    vectorstore.add_documents(documents)
    logger.info("Indexed %d document chunks", len(documents))
    return len(documents)
