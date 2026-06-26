from langchain_openai import OpenAIEmbeddings

from app.core.config import Settings

# Known dimensions for common OpenAI embedding models (avoids a probe call at startup).
OPENAI_EMBEDDING_DIMENSIONS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


def build_embeddings(settings: Settings) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key or None,
    )


def resolve_embedding_dimensions(settings: Settings, embeddings: OpenAIEmbeddings) -> int:
    if settings.embedding_dimensions is not None:
        return settings.embedding_dimensions

    known = OPENAI_EMBEDDING_DIMENSIONS.get(settings.openai_embedding_model)
    if known is not None:
        return known

    return len(embeddings.embed_query("dimension_probe"))
