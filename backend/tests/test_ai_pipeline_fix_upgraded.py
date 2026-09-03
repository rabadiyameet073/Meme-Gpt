"""
Tests for 05_AI_Pipeline_Fix.md (Upgraded Docs).

Verifies:
- Stage A: Groq Intent Parsing with fallback chain, timeout, JSON extraction, and rule-based fallback
- Stage B: DistilRoBERTa Emotion Detection + MiniLM 384-dim Embedding + Rich Query Construction
- Stages C-F: Recommendation Pipeline Orchestrator with parallel asyncio.gather execution and caching
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services import llm_service
from app.services import embedding_service
from app.services import recommendation_service
from app.services import search_service
from app.core.cache import query_cache


@pytest.mark.asyncio
async def test_llm_service_rule_based_fallback_on_empty_api_key():
    """Verify parse_intent returns valid structured dict even when GROQ_API_KEY is empty."""
    with patch.object(llm_service.settings, "GROQ_API_KEY", ""):
        intent = await llm_service.parse_intent("I am so happy that our Friday deployment succeeded without any bug!")
        assert intent is not None
        assert isinstance(intent, dict)
        assert intent["emotion_hint"] == "joy"
        assert "coding" in intent["categories"] or "work" in intent["categories"]
        assert len(intent["keywords"]) > 0
        assert intent["meme_format"] == "reaction"
        assert intent["situation"] != ""


@pytest.mark.asyncio
async def test_llm_service_groq_parse_markdown_json():
    """Verify _groq_parse strips markdown code fences and validates intent schema."""
    import sys
    import types

    raw_mock_json = """```json
    {
        "situation": "Code deployed to production on Friday",
        "emotion_hint": "joy",
        "tone": "humorous",
        "keywords": ["deploy", "friday", "production"],
        "meme_format": "reaction",
        "intensity": 0.85,
        "categories": ["coding"]
    }
    ```"""

    mock_client = MagicMock()
    mock_chat = AsyncMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = raw_mock_json
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_chat.completions.create = AsyncMock(return_value=mock_response)
    mock_client.chat = mock_chat

    mock_groq_module = types.ModuleType("groq")
    mock_groq_module.AsyncGroq = MagicMock(return_value=mock_client)

    with patch.dict(sys.modules, {"groq": mock_groq_module}):
        parsed = await llm_service._groq_parse("deployed on friday", api_key="gsk_test_mock_key")
        assert parsed is not None
        assert parsed["situation"] == "Code deployed to production on Friday"
        assert parsed["emotion_hint"] == "joy"
        assert parsed["intensity"] == 0.85
        assert parsed["keywords"] == ["deploy", "friday", "production"]


@pytest.mark.asyncio
async def test_llm_service_groq_error_graceful_fallback():
    """Verify that if Groq raises an exception, parse_intent falls back to rule-based without raising."""
    import sys
    import types

    mock_groq_module = types.ModuleType("groq")
    mock_groq_module.AsyncGroq = MagicMock(side_effect=Exception("API rate limit reached"))

    with patch.dict(sys.modules, {"groq": mock_groq_module}):
        with patch.object(llm_service.settings, "GROQ_API_KEY", "gsk_test_mock_key"):
            intent = await llm_service.parse_intent("I am so angry at this broken server")
            assert intent is not None
            assert intent["emotion_hint"] == "anger"



def test_embedding_service_text_embedding_dimensions():
    """Verify embed_text returns 384-dimensional vector."""
    vec = embedding_service.embed_text("Deploying to production on Friday")
    assert isinstance(vec, list)
    assert len(vec) == 384
    # All vector elements are numeric
    assert all(isinstance(x, (float, int)) for x in vec)


def test_embedding_service_emotion_detection():
    """Verify detect_emotion returns primary, secondary, and confidence."""
    emotion_res = embedding_service.detect_emotion("I won the hackathon first prize!")
    assert isinstance(emotion_res, dict)
    assert "primary" in emotion_res
    assert emotion_res["primary"] == "joy"
    assert "confidence" in emotion_res
    assert emotion_res["confidence"] > 0.0


def test_embedding_service_build_rich_query_text():
    """Verify build_query_text combines user text, intent, and emotion fields."""
    user_text = "Boss cancelled the weekend meeting"
    intent = {
        "situation": "Weekend meeting cancelled by management",
        "tone": "excited",
        "keywords": ["boss", "meeting", "weekend"],
        "meme_format": "reaction",
    }
    emotion = {"primary": "joy", "secondary": "surprise"}

    rich_text = embedding_service.build_query_text(user_text, intent, emotion)
    assert "User said: Boss cancelled the weekend meeting" in rich_text
    assert "Situation: Weekend meeting cancelled by management" in rich_text
    assert "Primary emotion: joy" in rich_text
    assert "Secondary emotion: surprise" in rich_text
    assert "Tone: excited" in rich_text
    assert "Keywords: boss, meeting, weekend" in rich_text
    assert "Meme format: reaction" in rich_text


@pytest.mark.asyncio
async def test_recommendation_pipeline_execution():
    """Verify recommend_memes executes all 6 stages and returns structured response."""
    query_cache.clear()
    user_text = "When your unit tests all pass on the first run"

    result = await recommendation_service.recommend_memes(
        user_text=user_text,
        format_pref="gif",
        nsfw=False,
    )

    assert result is not None
    assert result.get("success") is True
    assert "queryId" in result
    assert "results" in result
    assert "primary" in result
    assert "topFive" in result
    assert "emotion" in result
    assert "latencyMs" in result
    assert result.get("cached") is False

    # Second call should return cached=True
    cached_result = await recommendation_service.recommend_memes(
        user_text=user_text,
        format_pref="gif",
        nsfw=False,
    )
    assert cached_result.get("cached") is True
