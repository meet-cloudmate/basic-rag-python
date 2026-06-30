from functools import lru_cache

from app.core.config import get_settings
from app.rag.service import RAGService


@lru_cache
def get_rag_service() -> RAGService:
    settings = get_settings()
    return RAGService(settings)
