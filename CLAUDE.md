# CLAUDE.md — RAG Document Q&A Tool

<!-- .claude-governance-start -->
## .claude Governance (Mandatory)

**Do NOT start coding until this boot sequence is complete.**

1. Read `c:\Code\.claude\GOVERNANCE.md` -- rules, skill resolution, boundaries
2. Read `c:\Code\.claude\skills-registry.md` -- per-project skill mappings
3. Read `c:\Code\.claude\vault\CHANGELOG.md` -- what evolved since last session

For first session on this project, also read:
4. `c:\Code\.claude\vault\04-projects\06-rag-qa-tool.md` -- current phase, session log
5. Each SKILL.md listed below
6. `c:\Code\.claude\vault\03-patterns\` -- reusable patterns from earlier projects

All rules, skill resolution, evolution protocol, and session end protocol are in GOVERNANCE.md.
<!-- .claude-governance-end -->

## Skills to Read Before Starting
```
c:\Code\Skills\antigravity-awesome-skills\skills\rag-implementation\SKILL.md
c:\Code\Skills\antigravity-awesome-skills\skills\fastapi-pro\SKILL.md
c:\Code\Skills\antigravity-awesome-skills\skills\embedding-strategies\SKILL.md
```

## Phase 1 — Setup (~1hr)

**Goal:** FastAPI boots. ChromaDB persists locally. Sentence-transformers loads without error.

**Prompt:**
```
I'm building a RAG Document Q&A Tool — upload PDFs, ask questions, get cited answers grounded in the documents. No LangChain. Built from scratch.

Working directory: c:\Code\Portfolio\06-rag-qa-tool\

Phase 1: project setup only. No PDF ingestion yet.

Create:
1. `pyproject.toml` — Python 3.11+, dependencies: fastapi, uvicorn[standard], chromadb, sentence-transformers, pypdf, anthropic, python-dotenv, jinja2
2. `.env.example` — ANTHROPIC_API_KEY=
3. `src/__init__.py` (empty), `src/rag/__init__.py` (empty), `src/ui/__init__.py` (empty)
4. `src/app.py` — FastAPI init, loads .env, one route GET / returns {"status": "ok", "collections": []}
5. `src/rag/store.py` — ChromaDB client (persistent, stored in ./data/chroma/), creates or gets collection named "documents", exports `collection` object
6. `src/rag/embedder.py` — loads sentence-transformers model "all-MiniLM-L6-v2" on import, exports `embed(texts: list[str]) -> list[list[float]]` function

Startup test: `uvicorn src.app:app --reload` starts, ChromaDB creates ./data/chroma/ folder, no import errors.

Rules: no comments, no docstrings, no em dashes.
```

## Phase 2 — Ingest (~2hr)

**Goal:** PDF uploaded, chunked, embedded, stored. Metadata preserved: file name, page, chunk index.

**Prompt:**
```
Continue the RAG Q&A Tool. FastAPI boots, ChromaDB persists, embedder loads.

Working directory: c:\Code\Portfolio\06-rag-qa-tool\

Phase 2: PDF ingestion pipeline.

1. `src/rag/ingest.py` — function `ingest_pdf(pdf_path: str, collection) -> int`:
   - Parse PDF with pypdf, extract text per page
   - Chunk: 512-token chunks with 50-token overlap. Use simple word-split approximation (1 token ≈ 4 chars) since we want no extra dependencies.
   - Each chunk gets metadata: {"source": filename, "page": page_number, "chunk_index": i}
   - Embed all chunks with embedder.embed()
   - Upsert to ChromaDB collection with IDs like "filename_page_chunk"
   - Return number of chunks ingested

2. `src/app.py` — add route POST /ingest:
   - Accepts multipart/form-data with a PDF file
   - Saves file to ./data/uploads/ temporarily
   - Calls ingest_pdf
   - Returns {"status": "ingested", "chunks": N, "filename": name}

3. Add `tests/fixtures/test-doc.pdf` note — create a 2-page text-only PDF for testing (how?)

Rules: no comments, no docstrings, no em dashes.
```

## Phase 3 — Retrieve + Answer (~3hr)

**Goal:** Question in, cited answer out. "Not found" guardrail works.

**Prompt:**
```
Continue the RAG Q&A Tool. PDF ingestion works — chunks embedded and stored in ChromaDB.

Working directory: c:\Code\Portfolio\06-rag-qa-tool\

Phase 3: retrieval and answer synthesis.

1. `src/rag/retriever.py` — function `retrieve(query: str, collection, k: int = 5) -> list[dict]`:
   - Embed the query with embedder.embed([query])
   - Query ChromaDB for top-k similar chunks
   - Return list of dicts: {"text": chunk_text, "source": filename, "page": page_number, "distance": score}

2. `src/rag/answerer.py` — async function `answer(question: str, chunks: list[dict]) -> dict`:
   - If no chunks retrieved (or all distances > threshold): return {"answer": "Not found in the provided documents.", "sources": []}
   - Otherwise: call Claude API with system prompt: "Answer only from the provided context. If the answer is not in the context, say 'Not found in the provided documents.' Always cite the source page."
   - User message: includes question + formatted chunks
   - Return: {"answer": str, "sources": [{"source": str, "page": int}]}

3. `src/app.py` — add route POST /ask:
   - Body: {"question": str}
   - Calls retrieve then answer
   - Returns the answer dict

4. `src/ui/templates/index.html` — single page:
   - Upload PDF section (POST /ingest)
   - Q&A section (POST /ask)
   - Shows answer + source citations

Rules: no comments, no docstrings, no em dashes. Use claude-3-5-haiku for speed/cost.
```

## Phase 4 — Accuracy + Deploy (~2hr)

**Goal:** Accuracy measured (10+ Q&A pairs). HuggingFace Spaces deploy. README with score.

**Prompt:**
```
Final phase for the RAG Q&A Tool. Full pipeline works locally.

Working directory: c:\Code\Portfolio\06-rag-qa-tool\

1. `docs/ACCURACY.md` — test methodology:
   - Use a short, public-domain PDF (e.g., a Wikipedia article saved as PDF)
   - Ask 10 questions: 8 answerable from the doc, 2 that are NOT in the doc
   - Record: question, expected answer, actual answer, correct? (yes/no)
   - Report final score as "X/10 questions answered correctly"
   - Be honest — if accuracy is 7/10, say so and explain why

2. `tests/test_rag.py` — pytest tests:
   - test retriever returns the right number of chunks
   - test answerer returns "Not found" when given empty chunks
   - test answerer returns a dict with "answer" and "sources" keys on valid input
   - Mock ChromaDB and Claude API — no real calls

3. HuggingFace Spaces deploy:
   - What files does HuggingFace Spaces need for a FastAPI app?
   - Create `app.py` (entry point alias) if required
   - What are the memory/CPU constraints of the free tier, and does sentence-transformers fit?

4. `README.md`:
   - Line 1: "**Live demo:** [HuggingFace URL]" (placeholder)
   - Accuracy section: "X/10 on [document name] test set"
   - Architecture diagram (ASCII is fine)
   - Local setup + env vars

Rules: no em dashes, no AI vocabulary, no filler phrases.
```
