from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "basic-rag-python"
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 4

    documents_dir: Path = Field(default=PROJECT_ROOT / "data" / "documents")
    chroma_persist_dir: Path = Field(default=PROJECT_ROOT / "data" / "chroma")

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in {"development", "dev", "local"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
