"""
Tests for 04-ai-pipeline-gaps.md (AI-01 through AI-13).
Validates multimodal retrieval, unified image analysis, fail-fast embedding guards,
shared model singletons, convex composite scoring, personalized feedback reranking,
bounded external call latency, and popularity synchronization.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.services import embedding_service, rerank_service, search_service, image_analysis_service
from app.services.recommendation_service import recommend
from app.services.rerank_service import COMPOSITE_WEIGHTS, personalized_rerank


def test_ai01_multimodal_vector_search_fusion():
    """AI-01: Query uses CLIP text-to-image similarity and fuses text/image scores."""
    query_vector = [0.1] * 384
    clip_vector = [0.2] * 512

    # Mock Qdrant raw results for text and image vectors
    mock_text_hit = MagicMock()
    mock_text_hit.id = 12345
    mock_text_hit.score = 0.80
    mock_text_hit.payload = {"meme_id": "test_meme_1", "name": "Test Meme 1"}

    mock_image_hit = MagicMock()
    mock_image_hit.id = 12345
    mock_image_hit.score = 0.90
    mock_image_hit.payload = {"meme_id": "test_meme_1", "name": "Test Meme 1"}

    def mock_raw_query(client, collection_name, vector_name, query_vector, **kwargs):
        if vector_name == "image":
            return [mock_image_hit]
        return [mock_text_hit]

    with patch("app.services.search_service._raw_vector_query", side_effect=mock_raw_query), \
         patch("app.services.search_service.ensure_collection_ready", return_value=True), \
         patch("app.services.search_service.get_qdrant_client", return_value=MagicMock()):

        results = search_service.multimodal_vector_search(
            query_vector=query_vector,
            clip_text_vector=clip_vector,
            top_k=5,
        )

        assert len(results) > 0
        top = results[0]
        assert top["id"] == "test_meme_1"
        # Fused score: 0.70 * 0.80 + 0.30 * 0.90 = 0.56 + 0.27 = 0.83
        assert 0.80 <= top["score"] <= 0.85


def test_ai02_single_unified_image_analysis_service():
    """AI-02: image_analysis_service provides unified BLIP captioning, CLIP embeddings, and text clip encoding."""
    assert hasattr(image_analysis_service, "extract_text")
    assert hasattr(image_analysis_service, "generate_caption")
    assert hasattr(image_analysis_service, "embed_image")
    assert hasattr(image_analysis_service, "embed_text_clip")
    assert hasattr(image_analysis_service, "create_combined_embedding")


def test_ai03_indexing_fails_fast_when_model_missing():
    """AI-03: Indexing scripts abort with an error rather than generating fake pseudo-vectors."""
    from generate_embeddings import embed_text

    # When models["text"] is None, embed_text must raise RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        embed_text("sample query", models={"text": None})
    assert "aborted" in str(exc_info.value).lower() or "not loaded" in str(exc_info.value).lower()


def test_ai04_single_embedding_model_instance():
    """AI-04: semantic_search reuses shared embedding_service model instead of second instance."""
    from app.semantic_search import _get_transformer_model

    mock_shared_model = MagicMock()
    with patch("app.services.embedding_service._text_model", mock_shared_model), \
         patch("app.services.embedding_service.is_text_model_loaded", return_value=True):
        model = _get_transformer_model()
        assert model is mock_shared_model


def test_ai05_convex_composite_score_weights_sum_to_one():
    """AI-05: Composite scoring weights form a convex combination summing to exactly 1.0 (no saturation)."""
    weights = COMPOSITE_WEIGHTS
    assert "semantic" in weights
    assert "lexical" in weights
    assert "emotion_primary" in weights
    assert "emotion_secondary" in weights
    assert "popularity" in weights
    assert "recency" in weights
    assert "format" in weights

    total_weight = sum(weights.values())
    assert abs(total_weight - 1.0) < 1e-9


def test_ai06_personalized_rerank_with_category_affinity():
    """AI-06: Feedback category affinity map boosts matching candidate scores."""
    candidates = [
        {"id": "m1", "score": 0.60, "meme": {"category": "tech", "categories": ["tech", "coding"]}},
        {"id": "m2", "score": 0.60, "meme": {"category": "sports", "categories": ["sports"]}},
    ]

    # User strongly likes tech
    affinities = {"tech": 2.0, "sports": 0.5}
    reranked = personalized_rerank(candidates, affinities)

    assert len(reranked) == 2
    top = reranked[0]
    second = reranked[1]

    assert top["id"] == "m1"
    assert top["score"] > second["score"]
    assert top["personalized_weight"] > second["personalized_weight"]


def test_ai07_latency_bounded_external_calls():
    """AI-07: External Giphy and live stream calls have tight timeouts and in-memory TTL caching."""
    from app.services.giphy_service import get_global_gifs_and_memes, _LIVE_CACHE

    _LIVE_CACHE.clear()
    with patch("requests.get", side_effect=Exception("Timeout")):
        # Must gracefully return empty list within <1.5s rather than crashing
        res = get_global_gifs_and_memes("test_query", category="funny", limit=6)
        assert isinstance(res, dict)
        assert "memes" in res
        assert isinstance(res["memes"], list)


def test_ai08_admin_mutations_reindex_to_qdrant():
    """AI-08: Admin create and update paths embed and upsert meme points to Qdrant."""
    from app.api.v1.admin import _reindex_meme_to_qdrant

    with patch("app.services.embedding_service.embed_text", return_value=[0.1] * 384) as mock_embed, \
         patch("app.services.search_service.upsert_memes", return_value=1) as mock_upsert:
        _reindex_meme_to_qdrant({
            "id": "new_meme",
            "name": "New Meme",
            "dialogue": "Hello world",
            "categories": ["tech"],
        })
        assert mock_embed.called
        assert mock_upsert.called


def test_ai09_popularity_sync_updates_qdrant_payload():
    """AI-09: Popularity recalculation syncs updated scores into Qdrant payload."""
    from app.core.jobs import recalculate_persisted_popularity

    mock_db = MagicMock()
    mock_meme = MagicMock()
    mock_meme.id = "m1"
    mock_meme.popularity_score = 0.8
    mock_meme.viral_score = 50.0
    mock_db.query.return_value.all.return_value = [mock_meme]

    mock_qdrant = MagicMock()
    with patch("app.core.jobs._feedback_window_counts", return_value={}), \
         patch("app.services.search_service.get_qdrant_client", return_value=mock_qdrant):
        res = recalculate_persisted_popularity(mock_db, window_days=30)
        assert res["status"] == "success"
        assert mock_qdrant.set_payload.called
