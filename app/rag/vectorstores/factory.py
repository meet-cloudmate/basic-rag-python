import logging
from typing import Literal

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever

from app.core.config import Settings
from app.rag.vectorstores.qdrant import get_qdrant_vectorstore

logger = logging.getLogger(__name__)

VectorStoreBackend = Literal["qdrant"]


def get_vectorstore(settings: Settings) -> VectorStore:
    """Return the configured vector store backend.

    Add new backends here (e.g. pinecone, pgvector) and set VECTOR_STORE_BACKEND.
    """
    backend: VectorStoreBackend = settings.vector_store_backend
    if backend == "qdrant":
        return get_qdrant_vectorstore(settings)

    msg = f"Unsupported vector store backend: {backend}"
    raise ValueError(msg)


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
    logger.info("Indexed %d document chunks in %s", len(documents), settings.vector_store_backend)
    return len(documents)
