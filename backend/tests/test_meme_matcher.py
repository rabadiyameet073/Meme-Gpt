"""Pipeline Orchestrator Tests from 10_Testing/Backend_Tests.md."""

from app.meme_matcher import match_memes


def test_meme_matcher_empty_query():
    # Empty query should return result dict
    results = match_memes("")
    assert isinstance(results, dict)
    assert "primary" in results
    assert "topFive" in results


def test_meme_matcher_valid_search():
    results = match_memes("confused math calculation")
    assert isinstance(results, dict)
    assert "primary" in results
    assert "topFive" in results
    assert len(results["topFive"]) <= 5
    assert "confidence" in results["primary"]
    assert "name" in results["primary"]

