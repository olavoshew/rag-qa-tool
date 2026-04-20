from src.rag.embedder import embed
from src.rag.store import collection

DISTANCE_THRESHOLD = 1.5


def retrieve(query: str, k: int = 5) -> list[dict]:
    query_embedding = embed([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        if distance > DISTANCE_THRESHOLD:
            continue
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "page": results["metadatas"][0][i]["page"],
            "distance": distance,
        })

    return chunks
