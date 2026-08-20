"""Tests for Prompt Engineering from 05_AI_System/Prompt_Engineering.md."""

from app.services.llm_service import (
    clean_llm_json,
    generate_alt_text,
    INTENT_PROMPT,
    TAG_PROMPT,
    ALT_TEXT_PROMPT,
    BLOG_PROMPT,
    VALID_EMOTIONS,
    VALID_TONES,
    VALID_MEME_FORMATS,
)


def test_prompt_constants_exist_and_format():
    # 1. Intent prompt
    formatted_intent = INTENT_PROMPT.format(user_text="testing prompt")
    assert "testing prompt" in formatted_intent
    assert "emotion" in formatted_intent

    # 2. Tag prompt
    formatted_tag = TAG_PROMPT.format(meme_name="Dog Fire", ocr_text="this is fine", caption="dog sitting in fire")
    assert "Dog Fire" in formatted_tag
    assert "this is fine" in formatted_tag

    # 3. Alt text prompt
    formatted_alt = ALT_TEXT_PROMPT.format(meme_name="Distracted Boyfriend", caption="man looking back", ocr_text="")
    assert "Distracted Boyfriend" in formatted_alt

    # 4. Blog prompt
    formatted_blog = BLOG_PROMPT.format(topic="Coding", topic_lower="coding", meme_summary="- Meme 1")
    assert "Coding" in formatted_blog


def test_clean_llm_json_markdown_stripping():
    # Markdown wrapped JSON
    raw_markdown = "```json\n{\n  \"emotion\": \"joy\",\n  \"keywords\": [\"fun\", \"happy\"]\n}\n```"
    cleaned = clean_llm_json(raw_markdown)
    assert isinstance(cleaned, dict)
    assert cleaned.get("emotion") == "joy"
    assert cleaned.get("keywords") == ["fun", "happy"]


def test_clean_llm_json_text_preamble():
    # LLM output with extra text before/after JSON
    raw_preamble = "Here is the intent analysis:\n{\"situation\": \"studying late\", \"tone\": \"resigned\"}\nHope this helps!"
    cleaned = clean_llm_json(raw_preamble)
    assert isinstance(cleaned, dict)
    assert cleaned.get("situation") == "studying late"
    assert cleaned.get("tone") == "resigned"


def test_generate_alt_text_fallback():
    alt = generate_alt_text("Distracted Boyfriend", caption="Man looking back at another woman")
    assert isinstance(alt, str)
    assert len(alt) > 0
    assert "Distracted Boyfriend" in alt


def test_valid_enum_constraints():
    assert "joy" in VALID_EMOTIONS
    assert "frustration" in VALID_EMOTIONS
    assert "sarcastic" in VALID_TONES
    assert "reaction" in VALID_MEME_FORMATS
