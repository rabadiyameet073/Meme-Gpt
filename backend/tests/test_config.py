"""Configuration Loading and Environment Setup Tests.
Specification: 01_Environment_Setup.md (Upgraded Docs)
"""

import os
import subprocess
import sys
from pathlib import Path

from scripts.verify_env import verify_environment

from app.config import get_settings


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
    # The concrete host is deployment-specific (production uses cdn.memegpt.com,
    # local development serves /static), so assert the contract instead.
    assert settings.CDN_BASE_URL.startswith("http://") or settings.CDN_BASE_URL.startswith("https://")
    assert " " not in settings.CDN_BASE_URL


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


def test_secret_key_problem_rejects_published_values():
    """Placeholder and short keys must be flagged before they sign any token."""
    from app.config import WEAK_SECRET_KEYS, secret_key_problem

    for weak in WEAK_SECRET_KEYS:
        assert secret_key_problem(weak) is not None
    assert secret_key_problem("") is not None
    assert secret_key_problem("short") is not None
    assert secret_key_problem("a" * 32) is None


def _import_config(env_overrides: dict):
    backend_dir = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, "-c", "import app.config"],
        cwd=str(backend_dir),
        env={**os.environ, **env_overrides},
        capture_output=True,
        text=True,
    )


def test_production_refuses_placeholder_secret_key():
    """APP_ENV=production with a published key must abort instead of warning."""
    result = _import_config({
        "APP_ENV": "production",
        "SECRET_KEY": "default_secret_key_change_in_production_memegpt_2026",
    })
    assert result.returncode != 0
    assert "Refusing to start with APP_ENV=production" in (result.stderr + result.stdout)


def test_production_starts_with_generated_secret_key():
    """A generated key must boot cleanly, so the guard is not a blanket failure."""
    result = _import_config({"APP_ENV": "production", "SECRET_KEY": "b" * 64})
    assert result.returncode == 0, result.stderr


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


def test_relative_sqlite_url_is_anchored_to_backend_dir():
    """A relative sqlite URL must not depend on the process working directory.

    ``.env`` ships ``DATABASE_URL=sqlite:///./memegpt.db``. Without anchoring,
    uvicorn started from ``backend/`` and the cron scripts in ``scripts/`` (run
    from the repo root by .github/workflows/cron.yml) open two different, and
    one empty, database — the jobs then report success over zero memes.
    """
    from app.config import BACKEND_DIR, DB_PATH, _anchor_sqlite_url

    anchored = _anchor_sqlite_url("sqlite:///./memegpt.db")
    assert anchored == f"sqlite:///{DB_PATH}"
    assert str(BACKEND_DIR) in anchored


def test_anchor_sqlite_url_leaves_absolute_and_memory_urls_alone():
    """Absolute paths, ``:memory:`` and non-sqlite URLs must pass through."""
    from app.config import _anchor_sqlite_url

    # An absolute POSIX path is already unambiguous: sqlite:/// + /opt/x.db.
    absolute = "sqlite:////opt/data/memegpt.db"
    assert _anchor_sqlite_url(absolute) == absolute
    assert _anchor_sqlite_url("sqlite:///:memory:") == "sqlite:///:memory:"
    assert _anchor_sqlite_url("sqlite://") == "sqlite://"
    postgres = "postgresql://user:pw@host:5432/db"
    assert _anchor_sqlite_url(postgres) == postgres
    # The sqlite+pysqlite driver alias is anchored too, not silently skipped.
    aliased = _anchor_sqlite_url("sqlite+pysqlite:///./x.db")
    assert aliased.startswith("sqlite+pysqlite:///")
    assert "./x.db" not in aliased
    assert aliased.endswith("backend\\x.db") or aliased.endswith("backend/x.db")


def test_database_url_is_cwd_independent():
    """Importing the app from the repo root must find the same database file."""
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "-c", "import app.config; print(app.config.DATABASE_URL)"],
        cwd=str(repo_root),
        env={
            **os.environ,
            "PYTHONPATH": str(repo_root / "backend"),
            "DATABASE_URL": "sqlite:///./memegpt.db",
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    resolved = result.stdout.strip().splitlines()[-1]
    assert resolved == f"sqlite:///{Path(__file__).resolve().parents[1] / 'memegpt.db'}"
    assert "backend" in resolved
