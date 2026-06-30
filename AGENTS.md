# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single product: **`basic-rag-python`**, a FastAPI + LangChain Retrieval-Augmented Generation (RAG) API backed by an embedded Qdrant vector store. There is one service to run — the FastAPI/Uvicorn app. Standard commands live in `README.md` and `docs/getting-started.md`; only the non-obvious notes are captured here.

### Tooling / running

- The project is managed by **`uv`** (Python `>=3.12`, pinned by `.python-version`). `uv` is installed at `~/.local/bin` (also added to `~/.bashrc`). The startup update script runs `uv sync`, so dependencies are already installed; you do not need to reinstall.
- Prefix commands with `uv run` so they use the project `.venv`: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`, `uv run pytest`, `uv run ruff check .`.
- Copy `.env.example` to `.env` before running the server (`.env` is gitignored). Qdrant defaults to **embedded local mode** (`data/qdrant/`), so no separate database/Docker is needed for default development.

### Non-obvious gotchas

- **Uvicorn `--reload` only watches `.py` files, not `.env`.** After editing `.env` (e.g. setting `OPENAI_API_KEY`), you must restart the server process for changes to take effect — settings are loaded once via an `lru_cache` at startup.
- **`OPENAI_API_KEY` is required for real RAG functionality.** `/api/v1/health` and the pytest suite work without it. `/api/v1/query` returns HTTP 503 (`OPENAI_API_KEY is not configured`) when the key is empty. If the key is set but invalid, ingest/query reach OpenAI and fail with a 401 surfaced as HTTP 500 — so a 500 here usually means a bad key, not a code bug.
- Both `/api/v1/documents/ingest` and `/api/v1/documents/upload` call OpenAI embeddings, so they also need a valid `OPENAI_API_KEY`.
- The actual application code lives on the `develop` branch (and feature branches off it); the `main` branch currently contains only a placeholder `README.md`. Base development work on `develop`.
