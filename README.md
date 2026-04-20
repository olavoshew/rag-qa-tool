---
title: RAG Document Q&A
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

**Live demo:** [huggingface.co/spaces/zehsnuts/rag-qa-tool](https://huggingface.co/spaces/zehsnuts/rag-qa-tool)

# RAG Document Q&A Tool

Upload a PDF. Ask questions. Get answers grounded in the document with page citations.

Built from scratch without LangChain to demonstrate real understanding of the retrieval pipeline.

## Accuracy

**8/10** on a public-domain Wikipedia article test set (8 answerable questions, 2 control questions not in the document).

See [docs/ACCURACY.md](docs/ACCURACY.md) for the full question/answer breakdown.

## Architecture

```
PDF Upload
    |
    v
pypdf (text extraction per page)
    |
    v
Chunker (2048 char chunks, 200 char overlap)
    |
    v
sentence-transformers/all-MiniLM-L6-v2 (embeddings)
    |
    v
ChromaDB (vector store, persistent per session)
    |
    v
Question -> embed -> similarity search (top 5) -> filter by distance
    |
    v
Claude 3.5 Haiku (answer synthesis with source citation)
    |
    v
{"answer": "...", "sources": [{"source": "doc.pdf", "page": 3}]}
```

## Stack

- **FastAPI** - web framework
- **ChromaDB** - vector store (ephemeral on HuggingFace free tier, persists locally)
- **sentence-transformers** - `all-MiniLM-L6-v2`, 384 dims, runs on CPU
- **Claude 3.5 Haiku** - answer synthesis
- **pypdf** - PDF text extraction

## Local Setup

```bash
git clone https://github.com/olavoshew/rag-qa-tool
cd rag-qa-tool

python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -e .

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

uvicorn src.app:app --reload
# Open http://localhost:8000
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude 3.5 Haiku |

## Notes

- ChromaDB storage is ephemeral on HuggingFace Spaces free tier. Documents reset on cold start. For a persistent demo, re-upload the PDF after a cold start.
- No GPU required. Embeddings run on CPU in under 100ms per query.
- "Not found" guardrail prevents hallucination when the question is outside the document.
