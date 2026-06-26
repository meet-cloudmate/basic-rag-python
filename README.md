# Basic RAG Python

A minimal Retrieval-Augmented Generation (RAG) service built with **LangChain**, **FastAPI**, and **uv**.

The API lets you ingest documents (`.txt`, `.md`, `.pdf`), store them in a local Chroma vector database, and ask natural-language questions grounded in your corpus.

## Architecture

```
Client → FastAPI (REST) → RAGService → LangChain
                              ├── Document loaders & text splitters
                              ├── OpenAI embeddings → Chroma (persistent)
                              └── OpenAI chat model (LCEL RAG chain)
```

See [docs/architecture.md](docs/architecture.md) for design decisions and component boundaries.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key (embeddings + chat)

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
├── api/v1/          # HTTP routes and versioning
├── core/            # Config, logging, dependencies
├── rag/             # RAG pipeline (load, split, embed, retrieve, generate)
├── schemas/         # Pydantic request/response models
└── main.py          # FastAPI application factory
data/
├── documents/       # Local document corpus (git-tracked samples)
└── chroma/          # Persistent vector store (gitignored)
docs/                # Architecture and getting-started guides
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
| `CHROMA_PERSIST_DIR` | `data/chroma` | Vector store path |

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
