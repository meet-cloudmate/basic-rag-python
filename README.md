# Basic RAG Python

A minimal Retrieval-Augmented Generation (RAG) service built with **LangChain**, **FastAPI**, **Qdrant**, and **uv**.

The API lets you ingest documents (`.txt`, `.md`, `.pdf`), store them in **Qdrant**, and ask natural-language questions grounded in your corpus.

## Architecture

```
Client → FastAPI (REST) → RAGService → LangChain
                              ├── Document loaders & text splitters
                              ├── OpenAI embeddings → Qdrant (local or remote)
                              └── OpenAI chat model (LCEL RAG chain)
```

See [docs/architecture.md](docs/architecture.md) for design decisions and component boundaries.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key (embeddings + chat)
- Qdrant runs **embedded locally by default** (no separate server required)

## Quick start

```bash
# Clone and enter the project
cd basic-rag-python

# Install dependencies (creates .venv automatically)
uv sync

# Configure environment
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

# Start the API server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Usage

### 1. Add documents

Place files in `data/documents/`, then ingest:

```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest
```

Or upload files directly:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "files=@data/documents/sample.txt"
```

### 2. Ask a question

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/documents/ingest` | Index files from `data/documents/` |
| `POST` | `/api/v1/documents/upload` | Upload and index files |
| `POST` | `/api/v1/query` | Ask a question against indexed docs |

## Project structure

```
app/
├── api/v1/              # HTTP routes and versioning
├── core/                # Config, logging, dependencies
├── rag/
│   ├── vectorstores/    # Pluggable backends (Qdrant today)
│   └── ...              # Load, split, chain, service
├── schemas/             # Pydantic request/response models
└── main.py              # FastAPI application factory
data/
├── documents/           # Local document corpus (git-tracked samples)
└── qdrant/              # Local Qdrant storage (gitignored)
docs/                    # Architecture and getting-started guides
```

## Configuration

All settings are driven by environment variables. See [.env.example](.env.example) for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required for embeddings and chat |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat model for answers |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_TOP_K` | `4` | Chunks retrieved per query |
| `DOCUMENTS_DIR` | `data/documents` | Local ingest directory |
| `VECTOR_STORE_BACKEND` | `qdrant` | Vector store backend |
| `QDRANT_MODE` | `local` | `local` (embedded) or `remote` (server) |
| `QDRANT_LOCAL_PATH` | `data/qdrant` | Path for local Qdrant storage |
| `QDRANT_URL` | `http://localhost:6333` | Remote Qdrant URL |
| `QDRANT_COLLECTION_NAME` | `rag_documents` | Qdrant collection name |

### Switching to a remote Qdrant server

```bash
QDRANT_MODE=remote
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=optional-api-key
```

Run Qdrant with Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## Development

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check .
```

More detail: [docs/getting-started.md](docs/getting-started.md).

## License

MIT
