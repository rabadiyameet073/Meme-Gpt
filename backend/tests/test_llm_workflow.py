"""Tests for Groq LLM Workflow from 05_AI_System/LLM_Workflow.md."""

import pytest
from app.services.llm_service import (
    parse_intent,
    _default_intent,
    GROQ_CONFIG,
)


def test_groq_config_parameters():
    assert "model" in GROQ_CONFIG
    assert "temperature" in GROQ_CONFIG
    assert GROQ_CONFIG["temperature"] <= 0.3
    assert "max_tokens" in GROQ_CONFIG
    assert GROQ_CONFIG["max_tokens"] <= 300
    assert "timeout" in GROQ_CONFIG
    assert GROQ_CONFIG["timeout"] <= 10.0


@pytest.mark.asyncio
async def test_parse_intent_fallback_schema():
    user_text = "When your code compiles on the first attempt without errors"
    intent = await parse_intent(user_text)

    assert isinstance(intent, dict)
    assert "emotion" in intent
    assert "situation" in intent
    assert "tone" in intent
    assert "keywords" in intent
    assert isinstance(intent["keywords"], list)
    assert len(intent["keywords"]) >= 1
    assert "meme_format" in intent


def test_default_intent_structure():
    user_text = "Late night deployment to production server"
    fallback = _default_intent(user_text)

    assert isinstance(fallback, dict)
    assert "situation" in fallback
    assert "emotion" in fallback
    assert "tone" in fallback
    assert "keywords" in fallback
    assert isinstance(fallback["keywords"], list)
    assert "categories" in fallback
