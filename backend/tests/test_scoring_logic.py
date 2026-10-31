"""Tests for Composite Scoring Formula and Popularity from 05_AI_System/Scoring_Logic.md."""

from app.services.rerank_service import (
    calculate_composite_score,
    calculate_popularity_score,
    calculate_trending_score,
    recalculate_all_popularity_scores,
    format_score_display,
)


def test_calculate_composite_score_formula_and_capping():
    """The composite is a convex blend whose weights sum to exactly 1.0.

    This replaces the previous additive ``base + bonuses`` contract. Bonuses
    stacked on top of an already-high cosine drove most candidates to the 0.99
    clip, so ordering degenerated into ties and the most relevant meme often
    was not returned first (AUDIT-REPORT AI-2).
    """
    # relevance = 0.34*cosine + 0.30*lexical + 0.14*primary + 0.06*secondary
    #           + 0.08*popularity + 0.03*recency + 0.05*format
    #           = 0.34*0.60 + 0.14 + 0.06 + 0.08*0.50 + 0.03*0.50 + 0.05
    score = calculate_composite_score(
        cosine_similarity=0.60,
        meme_emotions=["frustration", "irony"],
        user_emotion_primary="frustration",
        user_emotion_secondary="irony",
        popularity_score=0.50,
        format_match=True,
    )
    assert score == 0.509

    # A universally favourable candidate still cannot exceed 1.0: the weights
    # are normalised, so no clipping is required.
    best_case = calculate_composite_score(
        cosine_similarity=1.0,
        meme_emotions=["joy"],
        user_emotion_primary="joy",
        user_emotion_secondary="joy",
        popularity_score=1.0,
        format_match=True,
        lexical_score=1.0,
        recency_score=1.0,
    )
    assert best_case == 1.0


def test_calculate_composite_score_preserves_ordering():
    """A stronger lexical/semantic match must outrank emotion and popularity."""
    on_topic = calculate_composite_score(
        cosine_similarity=0.82,
        meme_emotions=["humor"],
        user_emotion_primary="sadness",
        popularity_score=0.1,
        lexical_score=0.9,
    )
    off_topic = calculate_composite_score(
        cosine_similarity=0.55,
        meme_emotions=["sad"],
        user_emotion_primary="sadness",
        popularity_score=1.0,
        lexical_score=0.0,
    )
    assert on_topic > off_topic


def test_emotion_families_map_classifier_labels_to_meme_vocabulary():
    """Different detected emotions must resolve to different meme tags."""
    from app.services.rerank_service import _family

    assert "happy" in _family("joy")
    assert "celebratory" in _family("joy")
    assert "panic" in _family("fear")
    assert "frustrated" in _family("anger")
    assert "sad" in _family("sadness")
    # And the families must stay disjoint enough to differentiate scenarios.
    assert not (_family("anger") & _family("sadness"))


def test_calculate_popularity_score_30_day_weights():
    # 30-day feedback simulation:
    # 1000 views * 0.1 = 100
    # 200 clicks * 0.5 = 100
    # 100 copies * 1.0 = 100
    # 50 downloads * 2.0 = 100
    # 20 shares * 3.0 = 60
    # 30 thumbs_up * 2.0 = 60
    # 10 thumbs_down * -1.0 = -10
    # Total raw = 510. Normalized / 10000 = 0.051
    feedback = {
        "view_count": 1000,
        "click_count": 200,
        "copy_count": 100,
        "download_count": 50,
        "share_count": 20,
        "thumbs_up": 30,
        "thumbs_down": 10,
    }
    pop_score = calculate_popularity_score(feedback)
    assert pop_score == 0.051


def test_calculate_trending_score_24_hour_velocity():
    # 24-hr feedback:
    # 500 views * 0.1 = 50
    # 50 downloads * 2.0 = 100
    # 20 shares * 3.0 = 60
    # 20 thumbs_up * 2.0 = 40
    # Total raw = 250. Normalized / 1000 = 0.25
    feedback_24h = {
        "view_count": 500,
        "download_count": 50,
        "share_count": 20,
        "thumbs_up": 20,
    }
    trend_score = calculate_trending_score(feedback_24h)
    assert trend_score == 0.25


def test_recalculate_all_popularity_scores():
    memes = [
        {"id": "m1", "name": "Meme 1", "feedback": {"download_count": 1000}},
        {"id": "m2", "name": "Meme 2", "feedback": {"view_count": 500}},
    ]
    updated = recalculate_all_popularity_scores(memes)
    assert len(updated) == 2
    assert updated[0]["popularity_score"] == 0.2  # 1000 * 2.0 / 10000 = 0.2
    assert updated[1]["popularity_score"] == 0.005  # 500 * 0.1 / 10000 = 0.005


def test_format_score_display_ranges_and_colors():
    high = format_score_display(0.94)
    assert high["display"] == "🎯 94% match"
    assert high["color"] == "#22C55E"
    assert high["is_visible"] is True

    medium = format_score_display(0.78)
    assert medium["display"] == "🎯 78% match"
    assert medium["color"] == "#F59E0B"
    assert medium["is_visible"] is True

    fair = format_score_display(0.62)
    assert fair["display"] == "🎯 62% match"
    assert fair["color"] == "#FB923C"
    assert fair["is_visible"] is True

    low = format_score_display(0.42)
    assert low["is_visible"] is False
