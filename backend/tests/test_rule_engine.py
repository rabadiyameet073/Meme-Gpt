"""Scoring Algorithm & Rule Engine Tests from 10_Testing/Backend_Tests.md."""

from app.services.smart_search_service import calculate_smart_search_composite_score


def calculate_keyword_score(query: str, keywords: list[str]) -> float:
    """Helper calculating keyword match ratio."""
    q_words = set(query.lower().split())
    matched = sum(1 for kw in keywords if kw.lower() in q_words)
    return matched / max(1, len(keywords))


def test_keyword_score_full_match():
    score = calculate_keyword_score("monday morning work", ["monday", "morning", "work"])
    assert score > 0.8


def test_keyword_score_no_match():
    score = calculate_keyword_score("cats playing", ["monday", "work"])
    assert score < 0.1


def test_composite_rule_scoring():
    # Composite score with cosine, primary emotion, and popularity
    score = calculate_smart_search_composite_score(
        cosine_similarity=0.75,
        primary_emotion_match=True,
        secondary_emotion_match=False,
        popularity_score=0.8,
        format_preference_match=True,
    )
    # 0.75 + 0.15 + (0.8*0.10) + 0.05 = 1.03 -> min(1.0, 1.03) = 1.0
    assert score == 1.0
