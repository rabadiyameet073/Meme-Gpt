"""MemeGPT FastAPI backend — configuration.

Centralized settings loaded from environment variables with sensible defaults.
Matches specification from:
  - 01_Getting_Started/Environment_Variables.md
  - 02_Project_Architecture/Design_Principles.md
  - 01_Environment_Setup.md (Upgraded Docs)
"""
import json
import logging
import os
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env", override=False)

# ── App Info ──────────────────────────────────────────────────
APP_NAME = os.getenv("APP_NAME", "MemeGPT")
APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

# ── Paths & Database ──────────────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = BACKEND_DIR / "memegpt.db"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.json"

_env_db_url = os.getenv("DATABASE_URL", "").strip()
if not _env_db_url or _env_db_url.startswith("file:"):
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    DATABASE_URL = _env_db_url
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── Feature flags ──────────────────────────────────────────────
USE_TRANSFORMER_MODEL = True

# ── Groq LLM (Intent Parsing) ─────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "5"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "200"))

# ── ML Models ─────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384
EMOTION_MODEL = os.getenv("EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base")
MODELS_CACHE_DIR = os.getenv("MODELS_CACHE_DIR", "./model_cache")

# ── Qdrant (Vector Search) ────────────────────────────────────
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "memes")
QDRANT_TIMEOUT = int(os.getenv("QDRANT_TIMEOUT", "5"))

# ── Redis Cache (Upstash) ─────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", os.getenv("UPSTASH_REDIS_URL", ""))
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL", "")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", "3600"))

# ── Cloudflare R2 / CDN ───────────────────────────────────────
R2_ENDPOINT = os.getenv("R2_ENDPOINT", "")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY", "")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY", "")
R2_BUCKET = os.getenv("R2_BUCKET", "memegpt-memes")
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "https://cdn.memegpt.com")

# ── Giphy & Tenor ─────────────────────────────────────────────
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY", "")
TENOR_API_KEY = os.getenv("TENOR_API_KEY", "")

# ── Security & JWT ────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_in_production_memegpt_2026")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

if not SECRET_KEY or SECRET_KEY == "changeme" or len(SECRET_KEY) < 32:
    warnings.warn(
        "SECRET_KEY is not set or too short! JWT tokens will be insecure.",
        UserWarning,
    )

# ── CORS ──────────────────────────────────────────────────────
def _parse_cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    if raw.startswith("["):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    defaults = [
        "https://memegpt.com",
        "https://app.memegpt.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:19006",
    ]
    return [o.strip() for o in raw.split(",") if o.strip()] if raw else defaults

CORS_ORIGINS = _parse_cors_origins()

# ── Rate Limiting ─────────────────────────────────────────────
RATE_LIMIT_ANONYMOUS = int(os.getenv("RATE_LIMIT_ANONYMOUS", "60"))
RATE_LIMIT_FREE = int(os.getenv("RATE_LIMIT_FREE", "120"))
RATE_LIMIT_PRO = int(os.getenv("RATE_LIMIT_PRO", "300"))
RATE_LIMIT_INTERNAL = int(os.getenv("RATE_LIMIT_INTERNAL", "1000"))
RATE_LIMIT_PER_MINUTE = RATE_LIMIT_ANONYMOUS
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# ── Sentry ────────────────────────────────────────────────────
SENTRY_DSN = os.getenv("SENTRY_DSN", "")

# ── Logging ───────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class StructuredFormatter(logging.Formatter):
    """Structured JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_entry.update(record.extra_data)
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers = [handler]

    # Quiet noisy libs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)


# ── Settings Object Singleton ─────────────────────────────────
class Settings:
    APP_NAME: str = APP_NAME
    APP_ENV: str = APP_ENV
    APP_VERSION: str = APP_VERSION
    APP_BASE_URL: str = APP_BASE_URL
    DEBUG: bool = DEBUG
    DATABASE_URL: str = DATABASE_URL
    BACKEND_DIR: Path = BACKEND_DIR
    DATA_DIR: Path = DATA_DIR
    DB_PATH: Path = DB_PATH
    EMBEDDINGS_PATH: Path = EMBEDDINGS_PATH
    USE_TRANSFORMER_MODEL: bool = USE_TRANSFORMER_MODEL

    GROQ_API_KEY: str = GROQ_API_KEY
    GROQ_MODEL: str = GROQ_MODEL
    GROQ_TIMEOUT: int = GROQ_TIMEOUT
    GROQ_MAX_TOKENS: int = GROQ_MAX_TOKENS

    EMBEDDING_MODEL: str = EMBEDDING_MODEL
    EMBEDDING_DIM: int = EMBEDDING_DIM
    EMOTION_MODEL: str = EMOTION_MODEL
    MODELS_CACHE_DIR: str = MODELS_CACHE_DIR

    QDRANT_URL: str = QDRANT_URL
    QDRANT_API_KEY: str = QDRANT_API_KEY
    QDRANT_HOST: str = QDRANT_HOST
    QDRANT_PORT: int = QDRANT_PORT
    QDRANT_COLLECTION: str = QDRANT_COLLECTION
    QDRANT_TIMEOUT: int = QDRANT_TIMEOUT

    REDIS_URL: str = REDIS_URL
    UPSTASH_REDIS_REST_URL: str = UPSTASH_REDIS_REST_URL
    UPSTASH_REDIS_REST_TOKEN: str = UPSTASH_REDIS_REST_TOKEN
    REDIS_CACHE_TTL: int = REDIS_CACHE_TTL

    R2_ENDPOINT: str = R2_ENDPOINT
    R2_ACCESS_KEY: str = R2_ACCESS_KEY
    R2_SECRET_KEY: str = R2_SECRET_KEY
    R2_BUCKET: str = R2_BUCKET
    CDN_BASE_URL: str = CDN_BASE_URL

    GIPHY_API_KEY: str = GIPHY_API_KEY
    TENOR_API_KEY: str = TENOR_API_KEY

    SECRET_KEY: str = SECRET_KEY
    JWT_ALGORITHM: str = JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS: int = REFRESH_TOKEN_EXPIRE_DAYS

    CORS_ORIGINS: List[str] = CORS_ORIGINS

    RATE_LIMIT_ANONYMOUS: int = RATE_LIMIT_ANONYMOUS
    RATE_LIMIT_FREE: int = RATE_LIMIT_FREE
    RATE_LIMIT_PRO: int = RATE_LIMIT_PRO
    RATE_LIMIT_INTERNAL: int = RATE_LIMIT_INTERNAL
    RATE_LIMIT_PER_MINUTE: int = RATE_LIMIT_PER_MINUTE
    RATE_LIMIT_WINDOW: int = RATE_LIMIT_WINDOW

    SENTRY_DSN: str = SENTRY_DSN
    LOG_LEVEL: str = LOG_LEVEL

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV.lower() in ("development", "dev", "local")

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV.lower() in ("test", "testing")

    @property
    def has_groq(self) -> bool:
        return bool(self.GROQ_API_KEY and self.GROQ_API_KEY.strip())

    @property
    def has_qdrant(self) -> bool:
        return bool(self.QDRANT_URL and self.QDRANT_URL.strip())

    @property
    def has_redis(self) -> bool:
        return bool((self.REDIS_URL and self.REDIS_URL.strip()) or (self.UPSTASH_REDIS_REST_URL and self.UPSTASH_REDIS_REST_URL.strip()))

    @property
    def has_r2(self) -> bool:
        return bool(self.R2_ACCESS_KEY and self.R2_SECRET_KEY)

    @property
    def has_giphy(self) -> bool:
        return bool(self.GIPHY_API_KEY and self.GIPHY_API_KEY.strip())

    @property
    def has_sentry(self) -> bool:
        return bool(self.SENTRY_DSN and self.SENTRY_DSN.strip())


settings = Settings()


def get_settings() -> Settings:
    return settings
