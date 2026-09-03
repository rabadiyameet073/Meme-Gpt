"""
Unit tests for Vector Search Service from 14_Testing_Suite.md.
"""

from app.services.search_service import _cosine_similarity, vector_search


def test_cosine_similarity_identical():
    """Identical vectors → similarity = 1.0."""
    vec = [1.0, 0.0, 0.0, 1.0]
    result = _cosine_similarity(vec, vec)
    assert abs(result - 1.0) < 0.001


def test_cosine_similarity_orthogonal():
    """Orthogonal vectors → similarity = 0.0."""
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    result = _cosine_similarity(a, b)
    assert abs(result) < 0.001


def test_cosine_similarity_empty():
    """Empty vectors → 0.0 (no crash)."""
    assert _cosine_similarity([], []) == 0.0


def test_cosine_similarity_different_lengths():
    """Different length vectors → 0.0 (no crash)."""
    assert _cosine_similarity([1.0], [1.0, 2.0]) == 0.0


def test_vector_search_fallback_without_qdrant():
    """vector_search falls back gracefully when Qdrant is unavailable."""
    query_vector = [0.1] * 384
    results = vector_search(query_vector, top_k=5)
    # Should return a list (possibly empty) not raise
    assert isinstance(results, list)
