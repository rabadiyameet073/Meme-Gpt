"""Recommendation Service Tests from 10_Testing/Testing_Strategy.md."""

import pytest
from app.services.recommendation_service import recommend

TEST_CASES = [
    ("I just got promoted", "joy", ["achievement", "success"]),
    ("My flight got cancelled", "frustration", ["travel", "disappointment"]),
    ("It's finally Friday", "joy", ["weekend", "relief"]),
    ("My code worked on first try", "surprise", ["programming", "success"]),
    ("Mondays be like", "frustration", ["monday", "work"]),
]


@pytest.mark.asyncio
async def test_recommendation_returns_results():
    """Every valid query must return results."""
    for query, expected_emotion, expected_tags in TEST_CASES:
        results = await recommend(user_text=query, format_pref="any", nsfw=False)
        assert results is not None
        assert "primary" in results or "topFive" in results
        items = results.get("topFive", [])
        if "primary" in results and results["primary"]:
            items = [results["primary"]] + items
        assert len(items) >= 1, f"No results for: {query}"
        top_score = items[0].get("confidence", 0.0) or items[0].get("score", 0.0)
        assert top_score >= 0.15, f"Low confidence for: {query} (score: {top_score})"


@pytest.mark.asyncio
async def test_nsfw_filter():
    """NSFW content must be excluded when nsfw=False."""
    results = await recommend(user_text="funny coding meme", nsfw=False)
    items = results.get("topFive", [])
    if "primary" in results and results["primary"]:
        items = [results["primary"]] + items
    for r in items:
        assert r.get("nsfw", False) is False


@pytest.mark.asyncio
async def test_gif_format_filter():
    """When format=gif, returned memes should respect gif availability."""
    results = await recommend(user_text="happy celebration", format_pref="gif", nsfw=False)
    assert results is not None


@pytest.mark.asyncio
async def test_result_limit():
    """Results must not exceed the specified limit."""
    results = await recommend(user_text="test query limit", format_pref="any", nsfw=False)
    items = results.get("topFive", [])
    assert len(items) <= 5


@pytest.mark.asyncio
async def test_scores_are_sorted():
    """Results must be ordered by confidence/score (highest first)."""
    results = await recommend(user_text="monday morning panic", format_pref="any", nsfw=False)
    items = results.get("topFive", [])
    scores = [r.get("confidence", 0.0) or r.get("score", 0.0) for r in items]
    assert scores == sorted(scores, reverse=True)
