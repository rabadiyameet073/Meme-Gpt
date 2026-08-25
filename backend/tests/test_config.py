"""Configuration Loading and Environment Setup Tests.
Specification: 01_Environment_Setup.md (Upgraded Docs)
"""

import os
from pathlib import Path
import pytest

from app.config import Settings, get_settings
from scripts.verify_env import verify_environment


def test_settings_load_core():
    """Verify core application configuration is correctly initialized."""
    settings = get_settings()
    assert settings.APP_NAME == "MemeGPT"
    assert settings.APP_VERSION == "1.0.0"
    assert isinstance(settings.DEBUG, bool)
    assert settings.DATABASE_URL.startswith("sqlite://") or settings.DATABASE_URL.startswith("postgresql://")


def test_groq_settings_step5():
    """Verify Groq LLM settings from Step 5."""
    settings = get_settings()
    assert hasattr(settings, "GROQ_API_KEY")
    assert settings.GROQ_MODEL == "llama-3.1-8b-instant"
    assert settings.GROQ_TIMEOUT == 5
    assert settings.GROQ_MAX_TOKENS == 200


def test_qdrant_settings_step5():
    """Verify Qdrant Vector DB settings from Step 5."""
    settings = get_settings()
    assert hasattr(settings, "QDRANT_URL")
    assert hasattr(settings, "QDRANT_API_KEY")
    assert settings.QDRANT_COLLECTION == "memes"
    assert settings.QDRANT_TIMEOUT == 5
    assert settings.QDRANT_PORT == 6333


def test_redis_cache_settings_step5():
    """Verify Upstash Redis cache settings from Step 5."""
    settings = get_settings()
    assert hasattr(settings, "REDIS_URL")
    assert hasattr(settings, "UPSTASH_REDIS_REST_URL")
    assert hasattr(settings, "UPSTASH_REDIS_REST_TOKEN")
    assert settings.REDIS_CACHE_TTL == 3600


def test_r2_cdn_settings_step5():
    """Verify Cloudflare R2 and CDN settings from Step 5."""
    settings = get_settings()
    assert hasattr(settings, "R2_ENDPOINT")
    assert hasattr(settings, "R2_ACCESS_KEY")
    assert hasattr(settings, "R2_SECRET_KEY")
    assert settings.R2_BUCKET == "memegpt-memes"
    assert "memegpt.com" in settings.CDN_BASE_URL or "r2.dev" in settings.CDN_BASE_URL


def test_giphy_and_sentry_settings_step5():
    """Verify Giphy, Tenor, and Sentry settings from Step 5."""
    settings = get_settings()
    assert hasattr(settings, "GIPHY_API_KEY")
    assert hasattr(settings, "TENOR_API_KEY")
    assert hasattr(settings, "SENTRY_DSN")


def test_ml_models_step5():
    """Verify ML Models configuration from Step 5."""
    settings = get_settings()
    assert settings.EMBEDDING_MODEL == "all-MiniLM-L6-v2"
    assert settings.EMBEDDING_DIM == 384
    assert settings.EMOTION_MODEL == "j-hartmann/emotion-english-distilroberta-base"
    assert settings.MODELS_CACHE_DIR == "./model_cache"


def test_rate_limits_step5():
    """Verify Rate Limiting tier specifications from Step 5."""
    settings = get_settings()
    assert settings.RATE_LIMIT_ANONYMOUS == 60
    assert settings.RATE_LIMIT_FREE == 120
    assert settings.RATE_LIMIT_PRO == 300
    assert settings.RATE_LIMIT_INTERNAL == 1000


def test_security_secret_key():
    """Verify SECRET_KEY meets cryptographic length and security guidelines."""
    settings = get_settings()
    assert settings.SECRET_KEY != "changeme"
    assert len(settings.SECRET_KEY) >= 32
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7


def test_cors_origins_parsing():
    """Verify CORS origins contains valid development and production origins."""
    settings = get_settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert any("localhost" in origin for origin in settings.CORS_ORIGINS)


def test_settings_helper_properties():
    """Verify convenience boolean properties on Settings."""
    settings = get_settings()
    assert settings.is_development is True or settings.is_production is True or settings.is_testing is True
    assert isinstance(settings.has_groq, bool)
    assert isinstance(settings.has_qdrant, bool)
    assert isinstance(settings.has_redis, bool)
    assert isinstance(settings.has_r2, bool)
    assert isinstance(settings.has_giphy, bool)
    assert isinstance(settings.has_sentry, bool)


def test_verify_environment_script():
    """Verify the environment verification routine executes cleanly."""
    status = verify_environment()
    assert status is True
