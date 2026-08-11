"""
MemeGPT — Settings from .env
All environment variable defaults allow fully local development.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    API_VERSION: str = "v1"
    MAX_QUERY_LENGTH: int = 2000

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:19006,http://localhost:8081"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ── AI / LLM ──────────────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""

    # ── Vector DB (Qdrant) ────────────────────────────────────────────────────
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "memes"

    # ── PostgreSQL (Supabase in prod / SQLite in dev) ─────────────────────────
    DATABASE_URL: str = "file:./dev.db"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # ── Cache (Upstash Redis or local Redis) ──────────────────────────────────
    UPSTASH_REDIS_URL: str = "redis://localhost:6379"

    # ── File Storage (Cloudflare R2 in prod / local /public in dev) ───────────
    CLOUDFLARE_R2_ACCESS_KEY: str = ""
    CLOUDFLARE_R2_SECRET_KEY: str = ""
    CLOUDFLARE_R2_BUCKET: str = "memegpt-memes"
    CLOUDFLARE_R2_ACCOUNT_ID: str = ""
    CLOUDFLARE_R2_ENDPOINT: str = ""
    CDN_BASE_URL: str = "http://localhost:8000/static"

    # ── Data APIs ─────────────────────────────────────────────────────────────
    TENOR_API_KEY: str = ""
    IMGFLIP_USERNAME: str = ""
    IMGFLIP_PASSWORD: str = ""
    GIPHY_API_KEY: str = ""

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_DAY_ANON: int = 500
    RATE_LIMIT_PER_DAY_AUTH: int = 5000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
