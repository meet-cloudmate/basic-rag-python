import logging
import tempfile
from collections import defaultdict
from pathlib import Path

from langchain_core.documents import Document

from app.core.config import Settings
from app.rag.chain import build_rag_chain
from app.rag.document_loader import (
    load_documents_from_directory,
    load_documents_from_paths,
    split_documents,
)
from app.rag.vectorstore import add_documents, get_retriever
from app.schemas.documents import DocumentIngestResponse, DocumentSource
from app.schemas.query import QueryResponse, SourceChunk

logger = logging.getLogger(__name__)


class RAGService:
    """Orchestrates document ingestion and question answering."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def ingest_directory(self) -> DocumentIngestResponse:
        documents = load_documents_from_directory(self.settings.documents_dir)
        return self._ingest_documents(documents)

    def ingest_uploads(self, filenames: list[str], contents: list[bytes]) -> DocumentIngestResponse:
        documents: list[Document] = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for filename, content in zip(filenames, contents, strict=True):
                path = Path(tmpdir) / Path(filename).name
                path.write_bytes(content)
                documents.extend(load_documents_from_paths([path]))
        return self._ingest_documents(documents)

    def _ingest_documents(self, documents: list[Document]) -> DocumentIngestResponse:
        if not documents:
            return DocumentIngestResponse(
                message="No documents found to ingest",
                total_chunks=0,
                sources=[],
            )

        chunks = split_documents(documents, self.settings)
        total_chunks = add_documents(self.settings, chunks)

        chunks_by_source: dict[str, int] = defaultdict(int)
        for chunk in chunks:
            source = chunk.metadata.get("source", "unknown")
            chunks_by_source[str(source)] += 1

        sources = [
            DocumentSource(source=source, chunks_created=count)
            for source, count in sorted(chunks_by_source.items())
        ]
        return DocumentIngestResponse(
            message="Documents ingested successfully",
            total_chunks=total_chunks,
            sources=sources,
        )

    def query(self, question: str, *, top_k: int | None = None) -> QueryResponse:
        retriever = get_retriever(self.settings, top_k=top_k)
        retrieved_docs = retriever.invoke(question)
        chain = build_rag_chain(self.settings, top_k=top_k)
        answer = chain.invoke(question)

        sources = [
            SourceChunk(
                content=doc.page_content,
                source=doc.metadata.get("source"),
            )
            for doc in retrieved_docs
        ]
        return QueryResponse(question=question, answer=answer, sources=sources)
