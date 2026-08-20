"""Tests for Future AI improvements from 05_AI_System/Future_AI.md."""

from app.services.rerank_service import (
    personalized_rerank,
    calculate_viral_velocity,
    match_meme_template,
)


def test_personalized_rerank_formula():
    candidates = [
        {"id": "m1", "score": 0.5, "meme": {"category": "reaction", "name": "Meme 1"}},
        {"id": "m2", "score": 0.5, "meme": {"category": "sports", "name": "Meme 2"}},
    ]
    # User likes 'reaction' (weight 1.8) and skips 'sports' (weight 0.6)
    category_weights = {
        "reaction": 1.8,
        "sports": 0.6,
    }
    reranked = personalized_rerank(candidates, category_weights)

    # Formula: final_score = base_score * (1 + 0.15 * weight)
    # m1: 0.5 * (1 + 0.15 * 1.8) = 0.5 * 1.27 = 0.635
    # m2: 0.5 * (1 + 0.15 * 0.6) = 0.5 * 1.09 = 0.545
    assert reranked[0]["id"] == "m1"
    assert reranked[0]["score"] == 0.635
    assert reranked[1]["id"] == "m2"
    assert reranked[1]["score"] == 0.545


def test_personalized_rerank_clamping():
    candidates = [
        {"id": "m1", "score": 0.5, "meme": {"category": "reaction"}},
    ]
    # Extreme weights should be clamped to [0.5, 2.0]
    reranked_high = personalized_rerank(candidates, {"reaction": 5.0})
    assert reranked_high[0]["personalized_weight"] == 2.0

    reranked_low = personalized_rerank(candidates, {"reaction": 0.1})
    assert reranked_low[0]["personalized_weight"] == 0.5


def test_calculate_viral_velocity_and_priority_flag():
    # High velocity post: (100*1 + 50*2 + 20*3) / 2 hours = 260 / 2 = 130/hr > 50/hr
    res_high = calculate_viral_velocity(upvotes=100, comments=50, share_count=20, hours_since_post=2.0)
    assert res_high["velocity"] == 130.0
    assert res_high["is_priority_indexing"] is True

    # Low velocity post: (10*1 + 2*2 + 0*3) / 5 hours = 14 / 5 = 2.8/hr <= 50/hr
    res_low = calculate_viral_velocity(upvotes=10, comments=2, share_count=0, hours_since_post=5.0)
    assert res_low["velocity"] == 2.8
    assert res_low["is_priority_indexing"] is False


def test_match_meme_template():
    caption = "When the project is on fire but I stay calm"
    matches = match_meme_template(caption)
    assert len(matches) >= 1
    # Should match 'This is Fine' template with fire/crisis keywords
    top_match = matches[0]
    assert "fine" in top_match["name"].lower() or top_match["id"] == "T002"
