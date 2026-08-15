"""MemeGPT FastAPI backend — configuration.

Centralized settings loaded from environment variables with sensible defaults.
Matches specification from:
  - 01_Getting_Started/Environment_Variables.md
  - 02_Project_Architecture/Design_Principles.md
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import os
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env", override=False)

# ── Paths & Database ──────────────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = BACKEND_DIR / "memegpt.db"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.json"

# Database URL: defaults to local SQLite, or uses cloud PostgreSQL if provided
_env_db_url = os.getenv("DATABASE_URL", "").strip()
if not _env_db_url or _env_db_url.startswith("file:"):
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    DATABASE_URL = _env_db_url
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── Feature flags ──────────────────────────────────────────────
USE_TRANSFORMER_MODEL = True   # Try loading sentence-transformers; fallback to TF-IDF

# ── AI / ML Model Configuration ───────────────────────────────
# Groq LLM API (free tier: 6K req/day)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "10"))

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384

# Emotion detection model
EMOTION_MODEL = os.getenv("EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base")

# ── Vector Database — Qdrant ──────────────────────────────────
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "memes")

# ── Cache — Redis / Upstash ───────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", os.getenv("UPSTASH_REDIS_URL", ""))

# ── CDN / Object Storage ─────────────────────────────────────
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "https://cdn.memegpt.com")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://memegpt.com")

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
        "http://localhost:19006",
    ]
    return [o.strip() for o in raw.split(",") if o.strip()] if raw else defaults

CORS_ORIGINS = _parse_cors_origins()

# ── Rate Limiting ─────────────────────────────────────────────
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# ── Logging ───────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class StructuredFormatter(logging.Formatter):
    """Structured JSON log formatter from 03_Backend/Logging.md."""

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
