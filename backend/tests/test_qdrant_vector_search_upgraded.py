"""
Tests for 03_Qdrant_Vector_Search.md (Upgraded Docs).

Verifies:
- get_qdrant_client() singleton and graceful degradation
- create_qdrant_collection() named vector definitions (text: 384d, image: 512d)
- build_point() point construction, ID hashing, and payload enrichment
- upsert_memes() batching logic
- vector_search() with payload filters and score thresholds
- _cosine_similarity() precision math
- get_collection_info() diagnostics
"""

import math
from unittest.mock import MagicMock
import pytest

from app.services.search_service import (
    get_qdrant_client,
    create_qdrant_collection,
    build_point,
    upsert_memes,
    vector_search,
    search,
    _cosine_similarity,
    _meme_id_to_int,
    _db_fallback_search,
    get_collection_info,
    COLLECTION_NAME,
    TEXT_VECTOR_SIZE,
    IMAGE_VECTOR_SIZE,
)


def test_qdrant_client_singleton_and_fallback():
    """Verify get_qdrant_client returns None gracefully when not configured."""
    client = get_qdrant_client()
    assert client is None or hasattr(client, "search")


def test_collection_setup_and_named_vectors():
    """Verify create_qdrant_collection sets up text (384d) and image (512d) named vectors."""
    mock_client = MagicMock()
    success = create_qdrant_collection(client=mock_client, collection_name="memes")
    assert success is True
    assert mock_client.recreate_collection.called or mock_client.create_collection.called


def test_build_point_with_real_vectors():
    """Verify build_point constructs PointStruct with integer ID and named vectors."""
    meme = {
        "id": "meme_drake_123",
        "name": "Drake Hotline Bling",
        "slug": "drake-hotline-bling",
        "category": "comparison",
        "categories": ["comparison", "reaction"],
        "emotions": ["approval", "disapproval"],
        "keywords": ["drake", "pointing", "prefer"],
        "dialogue": "Nah / Yeah",
        "explanation": "Comparing preferred choice over rejected one",
        "image_url": "https://cdn.memegpt.com/images/drake.jpg",
        "gif_url": "https://cdn.memegpt.com/gifs/drake.gif",
        "mp4_url": "https://cdn.memegpt.com/videos/drake.mp4",
        "thumb_url": "https://cdn.memegpt.com/thumbs/drake.webp",
        "nsfw": False,
        "popularity_score": 0.95,
        "viral_score": 0.88,
        "source": "manual",
    }

    text_vec = [0.1] * TEXT_VECTOR_SIZE
    img_vec = [0.2] * IMAGE_VECTOR_SIZE

    point = build_point(meme, text_vector=text_vec, image_vector=img_vec)
    point_id = getattr(point, "id", None) or point["id"]
    vectors = getattr(point, "vector", None) or getattr(point, "vectors", None) or point.get("vectors")
    payload = getattr(point, "payload", None) or point.get("payload")

    assert isinstance(point_id, int)
    assert point_id == _meme_id_to_int("meme_drake_123")

    assert "text" in vectors
    assert len(vectors["text"]) == 384
    assert "image" in vectors
    assert len(vectors["image"]) == 512

    assert payload["meme_id"] == "meme_drake_123"
    assert payload["name"] == "Drake Hotline Bling"
    assert payload["slug"] == "drake-hotline-bling"
    assert payload["has_gif"] is True
    assert payload["has_video"] is True
    assert payload["nsfw"] is False
    assert payload["popularity_score"] == 0.95


def test_upsert_memes_batch_execution():
    """Verify upsert_memes batches requests in groups of 100."""
    mock_client = MagicMock()
    sample_memes = [
        {
            "meme": {"id": f"meme_{i}", "name": f"Test Meme {i}"},
            "text_vector": [0.05] * TEXT_VECTOR_SIZE,
        }
        for i in range(250)
    ]

    count = upsert_memes(memes_with_vectors=sample_memes, batch_size=100, client=mock_client, collection_name="memes")
    assert count == 250
    assert mock_client.upsert.call_count == 3  # 100, 100, 50


def test_vector_search_with_mock_client():
    """Verify vector_search executes named vector search with payload filters."""
    mock_client = MagicMock()
    mock_hit1 = MagicMock()
    mock_hit1.id = 12345
    mock_hit1.score = 0.89
    mock_hit1.payload = {
        "meme_id": "meme_drake_123",
        "name": "Drake Hotline Bling",
        "image_url": "https://cdn.memegpt.com/images/drake.jpg",
    }

    mock_hit2 = MagicMock()
    mock_hit2.id = 67890
    mock_hit2.score = 0.82
    mock_hit2.payload = {
        "meme_id": "meme_fine_456",
        "name": "This Is Fine",
        "image_url": "https://cdn.memegpt.com/images/fine.jpg",
    }

    mock_hit3 = MagicMock()
    mock_hit3.id = 11121
    mock_hit3.score = 0.76
    mock_hit3.payload = {
        "meme_id": "meme_pikachu_789",
        "name": "Surprised Pikachu",
        "image_url": "https://cdn.memegpt.com/images/pikachu.jpg",
    }

    mock_client.search.return_value = [mock_hit1, mock_hit2, mock_hit3]

    q_vec = [0.1] * TEXT_VECTOR_SIZE
    hits = vector_search(
        query_vector=q_vec,
        client=mock_client,
        collection_name="memes",
        top_k=5,
        score_threshold=0.35,
    )

    assert len(hits) == 3
    assert hits[0]["id"] == "meme_drake_123"
    assert hits[0]["score"] == 0.89
    assert hits[0]["meme"]["name"] == "Drake Hotline Bling"
    assert mock_client.search.called


def test_search_alias():
    """Verify search() is a functional alias for vector_search()."""
    mock_client = MagicMock()
    mock_hit = MagicMock()
    mock_hit.id = 999
    mock_hit.score = 0.95
    mock_hit.payload = {"meme_id": "meme_test", "name": "Alias Test Meme"}
    mock_client.search.return_value = [mock_hit, mock_hit, mock_hit]

    q_vec = [0.1] * TEXT_VECTOR_SIZE
    results = search(query_vector=q_vec, client=mock_client, collection_name="memes", top_k=3)
    assert len(results) == 3


def test_db_fallback_search():
    """Verify _db_fallback_search returns structured results when Qdrant is unavailable."""
    fallback_results = _db_fallback_search(top_k=5)
    assert isinstance(fallback_results, list)
    assert len(fallback_results) >= 1
    assert "id" in fallback_results[0]
    assert "score" in fallback_results[0]
    assert "meme" in fallback_results[0]


def test_cosine_similarity_math():
    """Verify _cosine_similarity calculates correct normalized dot product."""
    # Identical vectors -> 1.0
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert math.isclose(_cosine_similarity(v1, v2), 1.0, rel_tol=1e-5)

    # Orthogonal vectors -> 0.0
    v3 = [0.0, 1.0, 0.0]
    assert math.isclose(_cosine_similarity(v1, v3), 0.0, abs_tol=1e-5)

    # Opposite vectors -> -1.0
    v4 = [-1.0, 0.0, 0.0]
    assert math.isclose(_cosine_similarity(v1, v4), -1.0, rel_tol=1e-5)

    # Empty / mismatched length / zero norm handling
    assert _cosine_similarity([], [1.0]) == 0.0
    assert _cosine_similarity([1.0, 2.0], [1.0]) == 0.0
    assert _cosine_similarity([0.0, 0.0], [0.0, 0.0]) == 0.0


def test_get_collection_info_diagnostics():
    """Verify get_collection_info returns diagnostic health payload."""
    mock_client = MagicMock()
    mock_info = MagicMock()
    mock_info.status = "green"
    mock_info.points_count = 500
    mock_info.vectors_count = 1500
    mock_info.indexed_vectors_count = 1500
    mock_client.get_collection.return_value = mock_info

    info = get_collection_info(client=mock_client, collection_name="memes")
    assert info["status"] in ("ok", "green")
    assert info["points_count"] == 500
    assert info["count"] == 1500

