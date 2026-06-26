# Getting Started

Step-by-step guide to run the RAG API locally.

## 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

See the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/) for other platforms.

## 2. Install project dependencies

From the repository root:

```bash
uv sync
```

This creates a `.venv` virtual environment and installs locked dependencies from `uv.lock`.

## 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI key:

```
OPENAI_API_KEY=sk-...
```

Optional tuning:

```
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=4
OPENAI_CHAT_MODEL=gpt-4o-mini
```

## 4. Add sample documents

A starter file is included at `data/documents/sample.txt`. Add your own `.txt`, `.md`, or `.pdf` files to the same directory.

## 5. Start the server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 6. Ingest documents

**From the documents directory:**

```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest
```

**Or upload a file:**

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "files=@data/documents/sample.txt"
```

Expected response:

```json
{
  "message": "Documents ingested successfully",
  "total_chunks": 3,
  "sources": [
    {
      "source": "/path/to/data/documents/sample.txt",
      "chunks_created": 3
    }
  ]
}
```

## 7. Query the corpus

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main steps in a RAG pipeline?"}'
```

Example response:

```json
{
  "question": "What are the main steps in a RAG pipeline?",
  "answer": "The main steps are document loading, chunking, embedding, retrieval, and generation.",
  "sources": [
    {
      "content": "...",
      "source": "data/documents/sample.txt",
      "score": null
    }
  ]
}
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `OPENAI_API_KEY is not configured` | Set the key in `.env` and restart the server |
| Empty answers / "I don't know" | Run document ingest first; verify files exist in `data/documents/` |
| Chroma permission errors | Ensure `data/chroma/` is writable |
| PDF load failures | Confirm the PDF is text-based (not scanned images only) |

## Running tests

```bash
uv run pytest -v
```

Tests use FastAPI's `TestClient` and do not require a live OpenAI key for health checks.
