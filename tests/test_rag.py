import pytest
from unittest.mock import MagicMock, patch


def test_retriever_returns_chunks():
    mock_result = {
        "ids": [["id1", "id2", "id3"]],
        "documents": [["text about AI", "text about ML", "text about data"]],
        "metadatas": [
            [
                {"source": "doc.pdf", "page": 1, "chunk_index": 0, "type": "chunk"},
                {"source": "doc.pdf", "page": 2, "chunk_index": 1, "type": "chunk"},
                {"source": "doc.pdf", "page": 3, "chunk_index": 2, "type": "chunk"},
            ]
        ],
        "distances": [[0.3, 0.6, 0.9]],
    }

    with patch("src.rag.retriever.embed", return_value=[[0.1] * 384]), \
         patch("src.rag.retriever.collection") as mock_col:
        mock_col.query.return_value = mock_result
        from src.rag.retriever import retrieve
        result = retrieve("what is AI?", k=3)

    assert len(result) == 3


@pytest.mark.asyncio
async def test_answerer_empty_chunks_returns_not_found():
    from src.rag.answerer import answer, NOT_FOUND

    result = await answer("anything?", [])

    assert result["answer"] == NOT_FOUND
    assert result["sources"] == []


@pytest.mark.asyncio
async def test_answerer_valid_input_returns_expected_keys():
    chunks = [
        {"text": "AI is machine intelligence.", "source": "doc.pdf", "page": 1, "distance": 0.3}
    ]

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="AI is machine intelligence.")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with patch("src.rag.answerer._client", mock_client):
        from src.rag.answerer import answer
        result = await answer("What is AI?", chunks)

    assert "answer" in result
    assert "sources" in result
    assert result["sources"][0]["source"] == "doc.pdf"
