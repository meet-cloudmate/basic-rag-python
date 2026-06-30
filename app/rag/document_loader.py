import logging
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import Settings

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def _loader_for_path(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return TextLoader(str(path), encoding="utf-8")
    if suffix == ".md":
        return UnstructuredMarkdownLoader(str(path))
    if suffix == ".pdf":
        return PyPDFLoader(str(path))
    raise ValueError(f"Unsupported file type: {suffix}")


def load_documents_from_paths(paths: list[Path]) -> list[Document]:
    documents: list[Document] = []
    for path in paths:
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{path.suffix}'. "
                f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
        loader = _loader_for_path(path)
        documents.extend(loader.load())
        logger.info("Loaded %s", path.name)
    return documents


def load_documents_from_directory(directory: Path) -> list[Document]:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        return []

    documents: list[Document] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        documents.extend(_loader_for_path(path).load())
        logger.info("Loaded %s", path.name)
    return documents


def split_documents(documents: list[Document], settings: Settings) -> list[Document]:
    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        add_start_index=True,
    )
    return splitter.split_documents(documents)
