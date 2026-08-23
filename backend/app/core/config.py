from app.config import *
from typing import List


class Settings:
    """Application settings class."""
    APP_NAME: str = "MemeGPT"
    DATABASE_URL: str = DATABASE_URL
    QDRANT_URL: str = QDRANT_URL
    REDIS_URL: str = REDIS_URL
    GROQ_API_KEY: str = GROQ_API_KEY
    GROQ_MODEL: str = GROQ_MODEL
    EMBEDDING_MODEL: str = EMBEDDING_MODEL
    EMBEDDING_DIM: int = EMBEDDING_DIM
    CORS_ORIGINS: List[str] = CORS_ORIGINS
    LOG_LEVEL: str = LOG_LEVEL


_settings_instance = Settings()


def get_settings() -> Settings:
    """Get active Settings singleton."""
    return _settings_instance

