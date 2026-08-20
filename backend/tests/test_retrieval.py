"""Tests for Qdrant Vector Retrieval and Filter System from 05_AI_System/Retrieval.md."""

from app.services.search_service import (
    build_search_filter,
    search,
    adaptive_vector_search,
    get_trending_memes,
)


def test_build_search_filter_must_and_must_not():
    # Filter with format, categories, and exclude_ids
    filter_obj = build_search_filter(
        nsfw=False,
        format_pref="gif",
        categories=["coding", "office"],
        exclude_ids=["m_001", "m_002"],
    )

    if hasattr(filter_obj, "must"):
        # Qdrant Filter object
        assert filter_obj.must is not None
        assert filter_obj.must_not is not None
        assert len(filter_obj.must) >= 2  # nsfw + has_gif + categories
        assert len(filter_obj.must_not) == 2  # exclude_ids
    else:
        # Dictionary fallback
        assert filter_obj["nsfw"] is False
        assert filter_obj["format_pref"] == "gif"
        assert "coding" in filter_obj["categories"]
        assert "m_001" in filter_obj["exclude_ids"]


def test_search_named_vector_dispatch():
    # Synthetic 384-dim query vector
    query_vector = [0.05] * 384
    results = search(query_vector=query_vector, vector_name="text", top_k=5)

    assert isinstance(results, list)
    assert len(results) <= 5
    if results:
        assert "id" in results[0]
        assert "score" in results[0]
        assert "meme" in results[0]


def test_adaptive_vector_search_cascade():
    # Should always return candidates through threshold degradation or trending fallback
    query_vector = [0.0] * 384
    results = adaptive_vector_search(
        query_vector=query_vector,
        vector_name="text",
        top_k=5,
    )
    assert isinstance(results, list)
    assert len(results) >= 1
    assert "meme" in results[0]


def test_get_trending_memes_fallback():
    trending = get_trending_memes(limit=4)
    assert isinstance(trending, list)
    assert len(trending) == 4
    assert trending[0].get("is_trending_fallback") is True
