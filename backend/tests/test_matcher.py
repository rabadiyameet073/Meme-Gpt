import pytest
from app.rule_engine import run_rule_engine
from app.semantic_search import semantic_scores
from app.meme_matcher import match_memes, export_txt, export_markdown

TEST_MEMES = [
    {
        "id": "1",
        "name": "Bichwale Golmaal",
        "category": "coding",
        "dialogue": "Yeh humara department nahi hai",
        "explanation": "When asked to fix production code that isn't yours",
        "keywords": ["coding", "bug", "prod", "git"],
        "viralScore": 85,
        "usageCount": 120,
    },
    {
        "id": "2",
        "name": "Control Uday Control",
        "category": "funny",
        "dialogue": "Control Uday Control",
        "explanation": "Trying not to rage reply to client emails",
        "keywords": ["client", "rage", "angry", "meeting"],
        "viralScore": 90,
        "usageCount": 200,
    },
    {
        "id": "3",
        "name": "Mirzapur Risk",
        "category": "startup",
        "dialogue": "Risk hai to ishq hai",
        "explanation": "Deploying on Friday evening right before leaving",
        "keywords": ["startup", "deploy", "risk", "funding"],
        "viralScore": 75,
        "usageCount": 90,
    },
]

def test_rule_engine():
    res = run_rule_engine("My code bug crashed production server")
    assert "coding" in res.categories
    assert "coding" in res.tags

def test_semantic_search():
    scores = semantic_scores("production bug crash", TEST_MEMES)
    assert len(scores) == len(TEST_MEMES)
    assert scores["1"] > 0

def test_match_memes():
    result = match_memes("Client wants urgent feature delivery tomorrow morning", TEST_MEMES)
    assert result["primary"] is not None
    assert "id" in result["primary"]
    assert len(result["topFive"]) > 0
    assert result["latencyMs"] >= 0

def test_export_formats():
    result = match_memes("Test query", TEST_MEMES)
    txt = export_txt(result, "Test query")
    md = export_markdown(result, "Test query")
    assert "Situation: Test query" in txt
    assert "# MemeGPT Result" in md
