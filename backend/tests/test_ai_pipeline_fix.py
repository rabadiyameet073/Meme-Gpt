"""
Tests for AI Pipeline Fix from 05_AI_Pipeline_Fix.md.
"""

import sys
import pytest
import math
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.llm_service import (
    parse_intent,
    _groq_parse,
    _rule_based_intent,
    INTENT_SCHEMA,
    _extract_json_block,
)
from app.services.embedding_service import (
    embed_text,
    detect_emotion,
    _rule_based_emotion,
    build_query_text,
    load_models,
    _fallback_embed,
)
from app.services.recommendation_service import recommend


def test_intent_schema_and_rule_based_emotions():
    res_joy = _rule_based_intent("yay we finally got promoted and won the hackathon!")
    assert res_joy["emotion_hint"] == "joy"
    assert res_joy["emotion"] == "joy"
    assert "work" in res_joy["categories"] or "general" in res_joy["categories"]
    assert res_joy["intensity"] >= 0.5

    res_anger = _rule_based_intent("i hate this terrible annoying bug in my code")
    assert res_anger["emotion_hint"] == "anger"
    assert "coding" in res_anger["categories"]

    res_fear = _rule_based_intent("panic deadline tomorrow for university exam")
    assert res_fear["emotion_hint"] == "fear"
    assert "college" in res_fear["categories"] or "work" in res_fear["categories"]


def test_extract_json_block():
    raw_markdown = "```json\n{\"situation\": \"bug in prod\", \"emotion_hint\": \"panic\"}\n```"
    cleaned = _extract_json_block(raw_markdown)
    assert cleaned == "{\"situation\": \"bug in prod\", \"emotion_hint\": \"panic\"}"

    plain = "{\"situation\": \"clean json\"}"
    assert _extract_json_block(plain) == plain


@pytest.mark.asyncio
async def test_groq_parse_with_mock():
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '```json\n{"situation": "working late", "emotion_hint": "sadness", "tone": "sarcastic", "keywords": ["overtime", "night"], "categories": ["work"]}\n```'
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    mock_groq_module = MagicMock()
    mock_groq_module.AsyncGroq.return_value = mock_client

    with patch.dict(sys.modules, {"groq": mock_groq_module}):
        parsed = await _groq_parse("working late on friday", "fake_key_123")
        assert parsed is not None
        assert parsed["situation"] == "working late"
        assert parsed["emotion_hint"] == "sadness"
        assert parsed["tone"] == "sarcastic"
        assert "overtime" in parsed["keywords"]


def test_embedding_vector_dimensions_and_norm():
    vec = embed_text("Deploying to production on Friday afternoon")
    assert isinstance(vec, list)
    assert len(vec) == 384

    # Calculate norm
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 0.05  # Normalized to unit length


def test_detect_emotion_rule_based():
    emo_joy = _rule_based_emotion("I am so happy and excited today!")
    assert emo_joy["primary"] == "joy"
    assert emo_joy["confidence"] >= 0.6

    emo_neutral = _rule_based_emotion("the quick brown fox jumps over the lazy dog")
    assert emo_neutral["primary"] == "neutral"


def test_build_query_text():
    intent = {
        "situation": "Broken build on main branch",
        "tone": "frustrated",
        "keywords": ["ci/cd", "github", "build"],
        "meme_format": "reaction",
    }
    emotion = {
        "primary": "anger",
        "secondary": "fear",
    }
    query_text = build_query_text("Git push broke the entire CI pipeline", intent, emotion)
    assert "User said:" in query_text
    assert "Situation: Broken build on main branch" in query_text
    assert "Primary emotion: anger" in query_text
    assert "Secondary emotion: fear" in query_text
    assert "Tone: frustrated" in query_text
    assert "Keywords: ci/cd, github, build" in query_text


@pytest.mark.asyncio
async def test_recommendation_pipeline_parallel_flow():
    user_query = "when you spend 4 hours debugging only to find a missing semicolon"
    memes_db = [
        {
            "id": "meme_dbg_01",
            "name": "Semicolon Debugging",
            "slug": "semicolon-debugging",
            "category": "coding",
            "categories": ["coding"],
            "emotions": ["anger", "surprise"],
            "dialogue": "4 hours for a semicolon",
            "keywords": ["coding", "debugging", "semicolon"],
            "gif_url": "https://cdn.memegpt.com/semicolon.gif",
            "image_url": "https://cdn.memegpt.com/semicolon.jpg",
            "viral_score": 85,
            "usage_count": 120,
        }
    ]

    response = await recommend(user_query, format_pref="gif", memes_from_db=memes_db)
    assert response["success"] is True
    assert "queryId" in response
    assert "emotion" in response
    assert "detectedCategories" in response
    assert "results" in response
    assert len(response["results"]) >= 1
    assert response["latencyMs"] >= 0
