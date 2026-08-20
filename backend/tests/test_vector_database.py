"""Tests for Qdrant Vector Database Architecture from 05_AI_System/Vector_Database.md."""

from unittest.mock import MagicMock
from app.services.search_service import (
    create_qdrant_collection,
    build_point,
    index_memes,
    verify_vector_index,
)


def test_build_point_named_vectors_and_payload():
    meme = {
        "id": "meme_success_kid_001",
        "name": "Success Kid",
        "emotions": ["joy", "pride"],
        "situations": ["when code compiles on first try"],
        "keywords": ["success", "kid", "first try"],
        "meme_type": "reaction",
        "source": "reddit",
        "image_url": "https://cdn.memegpt.com/memes/success.jpg",
        "gif_url": "https://cdn.memegpt.com/memes/success.gif",
        "mp4_url": "https://cdn.memegpt.com/memes/success.mp4",
        "thumb_url": "https://cdn.memegpt.com/memes/success-thumb.jpg",
        "nsfw": False,
        "score": 8500,
    }

    point = build_point(meme)

    # Int ID check: abs(hash(meme_id)) % 10**18
    assert isinstance(point.id if hasattr(point, "id") else point["id"], int)

    vectors = point.vectors if hasattr(point, "vectors") else point["vectors"]
    assert "text" in vectors
    assert len(vectors["text"]) == 384
    assert "image" in vectors
    assert len(vectors["image"]) == 512
    assert "combined" in vectors
    assert len(vectors["combined"]) == 896

    payload = point.payload if hasattr(point, "payload") else point["payload"]
    assert payload["meme_id"] == "meme_success_kid_001"
    assert payload["name"] == "Success Kid"
    assert payload["has_gif"] is True
    assert payload["has_video"] is True
    assert payload["nsfw"] is False
    assert payload["popularity_score"] == 8500.0


def test_create_qdrant_collection_mock():
    mock_client = MagicMock()
    success = create_qdrant_collection(client=mock_client, collection_name="test_memes")
    assert success is True
    assert mock_client.recreate_collection.called
    call_kwargs = mock_client.recreate_collection.call_args[1]
    assert call_kwargs["collection_name"] == "test_memes"
    assert "text" in call_kwargs["vectors_config"]
    assert "image" in call_kwargs["vectors_config"]
    assert "combined" in call_kwargs["vectors_config"]
    assert call_kwargs["vectors_config"]["text"].size == 384
    assert call_kwargs["vectors_config"]["image"].size == 512
    assert call_kwargs["vectors_config"]["combined"].size == 896


def test_index_memes_batching():
    mock_client = MagicMock()
    memes = [{"id": f"m_{i}", "name": f"Meme {i}"} for i in range(25)]

    indexed = index_memes(memes=memes, batch_size=10, client=mock_client, collection_name="test_memes")
    assert indexed == 25
    # 25 items with batch size 10 -> 3 upsert calls (10, 10, 5)
    assert mock_client.upsert.call_count == 3


def test_verify_vector_index():
    mock_client = MagicMock()
    mock_info = MagicMock()
    mock_info.status = "green"
    mock_info.points_count = 1250
    mock_info.vectors_count = 3750
    mock_client.get_collection.return_value = mock_info

    diag = verify_vector_index(client=mock_client, collection_name="test_memes")
    assert diag["is_connected"] is True
    assert diag["status"] == "green"
    assert diag["points_count"] == 1250
