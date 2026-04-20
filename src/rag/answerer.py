import os

from anthropic import Anthropic

NOT_FOUND = "Not found in the provided documents."

SYSTEM_PROMPT = (
    "Answer only from the provided context. "
    "If the answer is not in the context, say exactly: "
    f"'{NOT_FOUND}' "
    "Always cite the source file name and page number."
)

_client: Anthropic | None = None


def _get_client() -> Anthropic | None:
    global _client
    if _client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if key:
            _client = Anthropic(api_key=key)
    return _client


def _format_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks):
        parts.append(
            f"[Source: {chunk['source']}, Page {chunk['page']}]\n{chunk['text']}"
        )
    return "\n\n---\n\n".join(parts)


async def answer(question: str, chunks: list[dict]) -> dict:
    if not chunks:
        return {"answer": NOT_FOUND, "sources": []}

    if not _get_client():
        return {"answer": "ANTHROPIC_API_KEY not configured.", "sources": []}

    context = _format_context(chunks)
    user_message = f"Context:\n\n{context}\n\nQuestion: {question}"

    response = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    sources = []
    seen = set()
    for chunk in chunks:
        key = (chunk["source"], chunk["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"source": chunk["source"], "page": chunk["page"]})

    return {
        "answer": response.content[0].text,
        "sources": sources,
    }
