# Step-by-step: Basic RAG → Advanced RAG

This roadmap builds on what you already have (FastAPI, LangChain LCEL, Qdrant, OpenAI) without changing the core architecture. Work through the phases in order — each phase improves answer quality or production readiness.

---

## Phase 1: Measure before you optimize

You can't improve what you don't measure.

### Create a golden test set

- 30–100 real questions your users would ask
- Expected answers or "must mention" facts
- Tag each as easy / medium / hard

### Define metrics

- **Retrieval**: precision@k, recall@k, MRR (did the right chunk show up?)
- **Generation**: faithfulness (answer grounded in context?), relevance, completeness
- **End-to-end**: user satisfaction or human review score

### Add tracing

- LangSmith, Phoenix, or OpenTelemetry
- Log: query → retrieved chunks → prompt → answer → latency/cost

### Establish a baseline

- Run your golden set against the current system
- Record scores — this is your benchmark for every later change

> **Rule:** change one thing at a time and re-run the eval set.

---

## Phase 2: Improve document ingestion

Bad chunks = bad retrieval, no matter how good the LLM is.

### Better parsing

- Plain text / markdown: keep current loaders
- PDFs: use Unstructured, LlamaParse, or Docling for tables, headers, layout
- HTML, DOCX, code: add format-specific loaders

### Smarter chunking

Move from fixed character splits to:

- **Semantic chunking** (split on meaning boundaries)
- **Structure-aware** (by heading, section, page)
- **Parent–child**: small chunks for search, large parent for context

### Enrich metadata

Store per chunk: `source`, `page`, `section`, `title`, `doc_id`, `created_at`, `tags`

Enables filtered retrieval later ("only search policy docs from 2024").

### Deduplication & versioning

- Hash content to skip duplicate chunks
- Track `doc_id` + `version` so re-ingest updates instead of duplicating

### Incremental ingest

- Delete vectors by `doc_id` before re-indexing
- Support "ingest one file" without full rebuild

---

## Phase 3: Upgrade retrieval (highest ROI)

Most "advanced RAG" gains come from retrieval, not the LLM.

### Step 3.1 — Hybrid search

Combine:

- **Dense** (embeddings — you have this)
- **Sparse** (BM25 / keyword — Qdrant supports sparse vectors)

Good for: exact terms, IDs, product names, legal clauses.

### Step 3.2 — Query transformation

Before retrieval, rewrite the user question:

- **Multi-query**: generate 3–5 variants, merge results
- **HyDE**: generate a hypothetical answer, embed that
- **Step-back**: extract a broader question first
- **Conversation rewrite**: turn "What about pricing?" into a standalone question using chat history

### Step 3.3 — Re-ranking

After top-k retrieval (e.g. fetch 20), re-rank with a cross-encoder:

- Cohere Rerank
- `bge-reranker`
- Jina Reranker

Keep top 4–6 after re-ranking. This often beats increasing k alone.

### Step 3.4 — Metadata filters

Use Qdrant filters on ingest metadata:

- `department`, `date`, `document_type`, `tenant_id`
- Pre-filter or post-filter depending on use case

### Step 3.5 — Retrieval tuning

Experiment with:

- Chunk size (500 vs 1000 vs 1500)
- Overlap (10–20% of chunk size)
- `top_k` fetch vs final `top_k` after rerank
- MMR (maximal marginal relevance) for diversity

---

## Phase 4: Improve generation & trust

### Stronger prompt

- Require citations: "Answer using only context; cite [source:page]"
- Explicit refusal: "Say 'I don't know' if context is insufficient"
- Structured output (JSON with `answer`, `sources`, `confidence`)

### Context compression

- Long docs → compress retrieved chunks before sending to LLM
- Tools: LLMLingua, contextual retrieval (prepend chunk-specific context per Anthropic pattern)

### Answer validation (post-generation)

- **Faithfulness check**: does each claim appear in retrieved context?
- **Relevance check**: does the answer address the question?
- If validation fails → retry with expanded retrieval or return "uncertain"

### Citation mapping

- Return chunk IDs, page numbers, and highlighted spans
- Lets users verify answers in the UI

---

## Phase 5: Conversational & agentic RAG

Move from single Q&A to multi-turn and adaptive flows.

### Chat memory

- Store session history
- Rewrite follow-ups into standalone queries (Step 3.2)
- Optional: summarize old turns to save tokens

### Router

Classify intent:

- Needs retrieval → RAG path
- General chit-chat → direct LLM
- Action request → tools/API

### Corrective RAG (CRAG)

- After retrieval, grade relevance of chunks
- If poor → web search fallback or broader re-query
- If good → generate

### Agentic RAG

- Agent with tools: `search_docs`, `search_web`, `calculator`, `sql_query`
- Multi-step: retrieve → read → refine query → retrieve again → answer

### Graph RAG (for connected knowledge)

- Build entity/relation graph from documents
- Combine vector search + graph traversal for "how does X relate to Y?"

---

## Phase 6: Production hardening

### Async ingestion

- Upload → queue (Redis/Celery/SQS) → background index
- Return `job_id`; poll status endpoint

### Auth & multi-tenancy

- API keys or OAuth
- Separate Qdrant collections or payload filters per tenant
- Never mix tenant data in retrieval

### Caching

- Cache embeddings for repeated documents
- Cache frequent queries (with TTL)

### Rate limiting & cost controls

- Per-user limits
- Token budgets
- Cheaper model for rewrite/rerank; expensive model only for final answer

### Deployment

- Dockerize API + remote Qdrant
- Health checks for API and Qdrant
- CI: lint, test, eval on PR

### Security

- Scan uploads (size, type, malware)
- PII redaction before indexing
- Audit log: who queried what

---

## Phase 7: Continuous improvement loop

```
Deploy change → Run eval suite → Compare to baseline → Ship or rollback
        ↑                                                    |
        └────────────── collect user feedback ───────────────┘
```

- Log failed queries (low confidence, bad feedback)
- Add them to the golden set
- Monthly retrieval/generation tuning
- A/B test: hybrid vs dense-only, reranker on/off, chunk sizes

---

## Suggested priority order (practical)

| Priority | What to do | Why |
|----------|------------|-----|
| 1 | Eval set + tracing | Foundation for everything else |
| 2 | Metadata + better chunking | Cheap, big retrieval gains |
| 3 | Hybrid search + reranking | Biggest quality jump for most apps |
| 4 | Query rewriting | Helps vague/multi-turn questions |
| 5 | Answer validation + citations | Trust and enterprise readiness |
| 6 | Async ingest + auth | Production readiness |
| 7 | Agentic / Graph RAG | Only when simpler RAG hits a ceiling |

---

## How this maps to your project

Your architecture already has clear extension points:

| Advanced feature | Where it would plug in |
|------------------|------------------------|
| Hybrid search | `app/rag/vectorstores/qdrant.py` |
| New backends | `app/rag/vectorstores/factory.py` |
| Chunking / metadata | `app/rag/document_loader.py` |
| Reranking / query rewrite | New step before or after `get_retriever()` |
| Prompt / validation | `app/rag/chain.py` |
| Async jobs | `app/rag/service.py` + new worker |
| Eval / observability | New `app/eval/` or external tooling |

---

## What "advanced" looks like in practice

**Basic RAG (today):**

> User question → embed → top-4 similar chunks → LLM → answer

**Advanced RAG (target):**

> User question → rewrite query → hybrid retrieve (20) → rerank (5) → compress context → LLM with citations → validate faithfulness → return answer + sources + confidence
