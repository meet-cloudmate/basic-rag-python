# Architecture

This document describes the system design for **basic-rag-python** — a small but production-minded RAG service.

## Goals

- **Separation of concerns**: HTTP layer, configuration, and RAG logic are isolated.
- **Local-first development**: Qdrant embedded mode persists vectors on disk without a separate server.
- **Swappable components**: Embeddings, vector store backend, and LLM are wired through LangChain abstractions.
- **Explicit API contracts**: Pydantic schemas define every request and response.

## High-level flow

```mermaid
flowchart LR
    Client[HTTP Client]
    API[FastAPI /api/v1]
    Svc[RAGService]
    Load[Document Loader]
    Split[Text Splitter]
    VS[(Qdrant Vector Store)]
    Emb[OpenAI Embeddings]
    Ret[Retriever]
    LLM[OpenAI Chat Model]

    Client --> API --> Svc
    Svc --> Load --> Split --> Emb --> VS
    Svc --> Ret --> VS
    Ret --> LLM
    Svc --> LLM
```

### Ingestion path

1. Documents arrive via **directory ingest** (`data/documents/`) or **file upload**.
2. `document_loader` selects the correct LangChain loader by extension (`.txt`, `.md`, `.pdf`).
3. `RecursiveCharacterTextSplitter` chunks text with configurable size and overlap.
4. Chunks are embedded with OpenAI and stored in a Qdrant collection.

### Query path

1. The user question is embedded and used for **similarity search** in Qdrant.
2. Top-k chunks are formatted into a prompt context.
3. An LCEL chain passes context + question to the chat model.
4. The API returns the generated answer plus the retrieved source chunks.

## Layer responsibilities

| Layer | Location | Responsibility |
|-------|----------|----------------|
| API | `app/api/v1/` | Routing, validation, HTTP errors |
| Schemas | `app/schemas/` | Request/response models |
| Core | `app/core/` | Settings, logging, DI |
| RAG | `app/rag/` | Document processing, vector store, chain |
| Vector stores | `app/rag/vectorstores/` | Backend-specific Qdrant wiring + factory |
| Data | `data/` | Raw documents and local Qdrant persistence |

## Key design choices

### LangChain LCEL for the RAG chain

The retrieval chain uses LangChain Expression Language (LCEL) instead of legacy `RetrievalQA` chains. This keeps the pipeline composable and aligns with LangChain 1.x patterns.

### Qdrant for vector storage

[Qdrant](https://qdrant.tech/) is used via the official `langchain-qdrant` integration. Two deployment modes are supported:

| Mode | Config | Use case |
|------|--------|----------|
| **Local** (default) | `QDRANT_MODE=local` | Development — embedded client, data in `data/qdrant/` |
| **Remote** | `QDRANT_MODE=remote` | Production — connect to a Qdrant server or cloud cluster |

Collections are created automatically on first ingest with cosine distance and the correct embedding dimension.

### Pluggable vector store factory

`app/rag/vectorstores/factory.py` selects the backend via `VECTOR_STORE_BACKEND`. Today only `qdrant` is implemented; add new modules (e.g. `pinecone.py`, `pgvector.py`) and extend the factory without changing API routes or `RAGService`.

### OpenAI for embeddings and generation

`text-embedding-3-small` balances cost and quality. `gpt-4o-mini` handles answer generation with low latency. Both are configurable via environment variables.

### FastAPI dependency injection

`RAGService` is provided through `get_rag_service()` so routes stay thin and the service can be mocked in tests.

### API versioning

Routes are mounted under `/api/v1` to allow future breaking changes without disrupting existing clients.

## Extension points

| Need | Where to extend |
|------|-----------------|
| New file types | `app/rag/document_loader.py` |
| Different vector DB | `app/rag/vectorstores/` + `factory.py` |
| Custom prompt | `app/rag/chain.py` |
| Auth / rate limits | FastAPI middleware or dependencies |
| Async ingestion | Background tasks or a job queue in `RAGService` |

## Security considerations

- **API keys** must be set via environment variables, never committed.
- **Upload size** is capped at 10 MB per file in the documents endpoint.
- **No authentication** is included by design; add API keys or OAuth before exposing publicly.

## Future improvements

- Hybrid search (Qdrant sparse + dense vectors)
- Re-ranking retrieved chunks
- Conversation memory / multi-turn chat
- Observability (LangSmith, OpenTelemetry)
- Container image and CI pipeline
