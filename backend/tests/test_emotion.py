"""Emotion Detection Tests from 10_Testing/Testing_Strategy.md."""

from app.rule_engine import detect_emotion


def test_joy_detection():
    result = detect_emotion("I just won the lottery!")
    assert result["primary"] in ("joy", "triumph")
    assert result["confidence"] >= 0.5


def test_sadness_detection():
    result = detect_emotion("My pet passed away yesterday")
    assert result["primary"] in ("sadness", "despair")


def test_anger_detection():
    result = detect_emotion("This bug is broken and I hate it!")
    assert result["primary"] in ("anger", "frustration")


def test_neutral_detection():
    result = detect_emotion("The weather is 72 degrees today")
    assert result["primary"] in ("neutral", "general", "funny")


def test_confidence_range():
    result = detect_emotion("anything")
    assert 0.0 <= result["confidence"] <= 1.0
