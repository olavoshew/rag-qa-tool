import re
from pathlib import Path

from pypdf import PdfReader

from src.rag.embedder import embed
from src.rag.store import collection

CHUNK_SIZE = 2048
CHUNK_OVERLAP = 200


def _extract_pages(pdf_path: str) -> list[tuple[int, str]]:
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            pages.append((i + 1, text))
    return pages


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap

    return chunks


def ingest_pdf(pdf_path: str) -> int:
    filename = Path(pdf_path).name
    pages = _extract_pages(pdf_path)

    all_chunks = []
    all_ids = []
    all_metadatas = []

    chunk_index = 0
    for page_num, page_text in pages:
        chunks = _chunk_text(page_text)
        for chunk in chunks:
            safe_name = re.sub(r"[^a-zA-Z0-9]", "_", filename)
            chunk_id = f"{safe_name}_p{page_num}_c{chunk_index}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append({
                "source": filename,
                "page": page_num,
                "chunk_index": chunk_index,
                "type": "chunk",
            })
            chunk_index += 1

    if not all_chunks:
        return 0

    batch_size = 64
    for i in range(0, len(all_chunks), batch_size):
        batch_chunks = all_chunks[i:i + batch_size]
        batch_ids = all_ids[i:i + batch_size]
        batch_meta = all_metadatas[i:i + batch_size]
        batch_embeddings = embed(batch_chunks)

        collection.upsert(
            ids=batch_ids,
            documents=batch_chunks,
            embeddings=batch_embeddings,
            metadatas=batch_meta,
        )

    return len(all_chunks)
