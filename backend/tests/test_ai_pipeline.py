"""
Integration tests for AI Pipeline from 14_Testing_Suite.md.
"""

import pytest
import asyncio


@pytest.mark.asyncio
async def test_rule_based_intent_always_returns_dict():
    """Rule-based intent extraction never returns None."""
    from app.services.llm_service import _rule_based_intent

    result = _rule_based_intent("my boss is so annoying today")
    assert isinstance(result, dict)
    assert "emotion_hint" in result
    assert "keywords" in result
    assert result["emotion_hint"] in ["joy", "anger", "sadness", "surprise", "fear", "disgust", "neutral"]


@pytest.mark.asyncio
async def test_parse_intent_without_groq():
    """parse_intent returns dict even when GROQ_API_KEY is empty."""
    from app.services.llm_service import parse_intent

    result = await parse_intent("when the coffee machine is broken on Monday")
    assert isinstance(result, dict)
    assert result is not None


def test_embed_text_returns_384_dim():
    """embed_text always returns 384-dim vector."""
    from app.services.embedding_service import embed_text

    vector = embed_text("hello world")
    assert isinstance(vector, list)
    assert len(vector) == 384


def test_detect_emotion_returns_dict():
    """detect_emotion always returns valid dict."""
    from app.services.embedding_service import detect_emotion

    result = detect_emotion("I am so angry!")
    assert "primary" in result
    assert result["primary"] in ["joy", "anger", "sadness", "surprise", "fear", "disgust", "neutral"]
