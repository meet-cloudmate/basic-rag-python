import logging

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import Settings
from app.rag.vectorstores.embeddings import build_embeddings, resolve_embedding_dimensions

logger = logging.getLogger(__name__)


def build_qdrant_client(settings: Settings) -> QdrantClient:
    if settings.qdrant_mode == "local":
        settings.qdrant_local_path.mkdir(parents=True, exist_ok=True)
        logger.debug("Using local Qdrant storage at %s", settings.qdrant_local_path)
        return QdrantClient(path=str(settings.qdrant_local_path))

    logger.debug("Connecting to remote Qdrant at %s", settings.qdrant_url)
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )


def ensure_collection(
    client: QdrantClient,
    *,
    collection_name: str,
    vector_size: int,
) -> None:
    if client.collection_exists(collection_name):
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )
    logger.info("Created Qdrant collection '%s' (dim=%d)", collection_name, vector_size)


def get_qdrant_vectorstore(settings: Settings) -> QdrantVectorStore:
    client = build_qdrant_client(settings)
    embeddings = build_embeddings(settings)

    ensure_collection(
        client,
        collection_name=settings.qdrant_collection_name,
        vector_size=resolve_embedding_dimensions(settings, embeddings),
    )

    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection_name,
        embedding=embeddings,
        validate_embeddings=False,
        validate_collection_config=False,
    )
