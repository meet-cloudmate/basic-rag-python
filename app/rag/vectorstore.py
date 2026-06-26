"""Vector store public API.

Implementation details live in app.rag.vectorstores; this module keeps imports stable
for the rest of the application.
"""

from app.rag.vectorstores.embeddings import build_embeddings
from app.rag.vectorstores.factory import add_documents, get_retriever, get_vectorstore

__all__ = [
    "add_documents",
    "build_embeddings",
    "get_retriever",
    "get_vectorstore",
]
