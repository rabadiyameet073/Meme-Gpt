"""Configuration Loading Tests from 10_Testing/Backend_Tests.md."""

from app.core.config import get_settings


def test_settings_load():
    settings = get_settings()
    assert settings.APP_NAME == "MemeGPT"
    assert hasattr(settings, "QDRANT_URL")
    assert hasattr(settings, "REDIS_URL")
