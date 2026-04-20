# PROJECT.md — RAG Document Q&A Tool

## Concept
Upload any PDF or set of documents and ask questions. Answers are grounded in the actual document content with source citations — no hallucination.

## Target User / Problem
Anyone who needs to query dense documents (contracts, manuals, technical specs, reports) without reading cover to cover. Classic RAG pipeline, built from scratch, with real error handling.

## Key Features
- Upload one or multiple PDFs via simple web UI
- Documents chunked, embedded, stored in ChromaDB
- Questions answered by Claude with source attribution (page number + excerpt)
- Hallucination guardrail: if answer not found in docs, returns "not found in documents"
- Accuracy metric in README (measured on test documents before shipping)

## Tech Stack
- Python 3.11+
- Anthropic SDK (`anthropic`) — Claude for answer synthesis
- ChromaDB (local vector store)
- `sentence-transformers` (embeddings — free, local, no API cost)
- `pypdf` (PDF parsing)
- FastAPI + Jinja2 (web UI)
- Deployed: Hugging Face Spaces (free, supports Python + Gradio/FastAPI)

## File Structure
```
src/
  app.py             FastAPI app
  rag/
    ingest.py        PDF parsing + chunking
    embedder.py      Sentence transformer embeddings
    store.py         ChromaDB operations
    retriever.py     Similarity search + re-ranking
    answerer.py      Claude API synthesis + citation
  ui/
    templates/       HTML templates
tests/
  test_rag.py
  fixtures/
    test-doc.pdf     Short test document
docs/
  ACCURACY.md        Measured accuracy on test docs (pre-ship)
```

## Environment Variables
```
ANTHROPIC_API_KEY=
```

## Chunking Strategy
- Chunk size: 512 tokens with 50-token overlap
- Metadata stored per chunk: source file, page number, chunk index
- Top-k retrieval: 5 chunks, re-ranked by relevance

## Definition of Done
- [ ] Local: upload a PDF, ask a question, get back answer with source citation
- [ ] Hallucination test: ask about something NOT in the doc — returns "not found"
- [ ] Deployed on HuggingFace Spaces — live URL
- [ ] ACCURACY.md documents test results (at least 10 Q&A pairs measured)
- [ ] Source on GitHub

## Why This Impresses Recruiters
RAG is the single most in-demand AI engineering skill going into 2026. A working, deployed RAG pipeline with real accuracy metrics signals production instincts and real engineering depth.

## Stand Out Further
Add a "confidence score" per answer. Show it going low when the question is ambiguous and high when the evidence is clear. Explain this in the README — it shows you understand LLM limitations.
