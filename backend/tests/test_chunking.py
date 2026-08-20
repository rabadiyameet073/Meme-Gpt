"""Tests for text chunking and composition strategies from 05_AI_System/Chunking.md."""

from app.services.text_composer import compose_meme_text, compose_query_text


def test_compose_meme_text_ordering_and_fields():
    meme = {
        "name": "This Is Fine",
        "blip_caption": "a cartoon dog sitting in a burning room",
        "ocr_text": "THIS IS FINE",
        "emotions": ["frustration", "denial", "acceptance", "crisis"],
        "situations": ["ignoring problems", "pretending everything is ok", "crisis at work"],
        "categories": ["work", "stress", "relatable"],
        "keywords": ["fine", "fire", "calm", "denial"],
    }
    composed = compose_meme_text(meme)

    # Check that name comes first
    assert composed.startswith("Meme: This Is Fine.")
    # Check visual caption
    assert "Shows: a cartoon dog sitting in a burning room." in composed
    # OCR is duplicate of name in case-insensitive, so check deduplication
    # Emotions present
    assert "Emotions: frustration, denial, acceptance, crisis." in composed
    # Situations present
    assert "Used when: ignoring problems, pretending everything is ok, crisis at work." in composed
    # Categories present
    assert "Categories: work, stress, relatable." in composed
    # Keywords present
    assert "Keywords: fine, fire, calm, denial." in composed


def test_compose_meme_text_deduplication():
    # If OCR text is identical to name, it should not duplicate
    meme = {
        "name": "Distracted Boyfriend",
        "ocr_text": "Distracted Boyfriend",
        "blip_caption": "man looking at another woman",
    }
    composed = compose_meme_text(meme)
    assert "Meme: Distracted Boyfriend." in composed
    assert "Text in image:" not in composed


def test_compose_meme_text_max_length():
    meme = {
        "name": "Long Meme",
        "blip_caption": "A" * 3000,
        "keywords": ["tag" * 100],
    }
    composed = compose_meme_text(meme)
    assert len(composed) <= 2048


def test_compose_query_text():
    user_text = "My code crashed right before the client demo"
    intent = {
        "situation": "Code crashing before production demo",
        "tone": "panic and stress",
        "keywords": ["crash", "demo", "panic"],
        "meme_format": "reaction",
    }
    emotion = {
        "primary": "fear",
        "secondary": "frustration",
    }
    query_text = compose_query_text(user_text, intent, emotion)
    assert "User said: My code crashed right before the client demo" in query_text
    assert "Situation: Code crashing before production demo" in query_text
    assert "Emotion: fear, frustration" in query_text
    assert "Tone: panic and stress" in query_text
    assert "Keywords: crash, demo, panic" in query_text
    assert "Meme type needed: reaction" in query_text
