# MemeGPT — Environment Configuration

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete guide to MemeGPT's runtime environments — development, staging, and production — including environment-specific settings, feature flags, and switching behavior.

---

## Background

MemeGPT runs in three distinct environments. Each has different service dependencies, performance characteristics, and security requirements. Understanding these differences prevents "works on my machine" bugs and ensures safe deployments.

---

## Environment Matrix

| Setting | Development | Staging | Production |
|---|---|---|---|
| **Frontend URL** | `http://localhost:5173` | `https://staging.memegpt.com` | `https://memegpt.com` |
| **Backend URL** | `http://localhost:8000` | `https://api-staging.memegpt.com` | `https://api.memegpt.com` |
| **Database** | SQLite (local file) | Supabase (staging project) | Supabase (prod project) |
| **Vector DB** | Qdrant (localhost:6333) | Qdrant Cloud (staging) | Qdrant Cloud (prod) |
| **Cache** | Redis (localhost:6379) | Upstash Redis (staging) | Upstash Redis (prod) |
| **LLM** | Ollama (local) or Groq | Groq API | Groq API |
| **CDN** | Local static files | Cloudflare R2 (staging) | Cloudflare R2 (prod) |
| **Debug Mode** | `True` | `True` | **`False`** |
| **CORS Origins** | `localhost:*` | `staging.memegpt.com` | `memegpt.com` |
| **Rate Limiting** | Disabled | 120 req/min | 60 req/min |
| **HTTPS** | No (HTTP) | Yes | **Yes (enforced)** |
| **Swagger Docs** | Visible (`/docs`) | Visible | **Hidden** |
| **Log Level** | DEBUG | INFO | WARNING |

---

## Environment Detection

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Core
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # URLs
    FRONTEND_URL: str = "http://localhost:5173"
    API_URL: str = "http://localhost:8000"
    
    # Database
    DATABASE_URL: str = "file:./dev.db"  # SQLite for dev
    
    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    
    # Cache
    UPSTASH_REDIS_URL: str = "redis://localhost:6379"
    
    # AI Services
    GROQ_API_KEY: str = ""
    OLLAMA_URL: str = "http://localhost:11434"
    
    # Storage
    R2_ENDPOINT: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET: str = "memegpt-dev"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## `.env` File Template

```bash
# ============================================
# MemeGPT Environment Variables
# Copy this file to .env and fill in values
# ============================================

# ── Core ──────────────────────────────────
APP_ENV=development          # development | staging | production
DEBUG=true
API_VERSION=v1

# ── URLs ──────────────────────────────────
FRONTEND_URL=http://localhost:5173
API_URL=http://localhost:8000

# ── Database (Supabase) ──────────────────
DATABASE_URL=file:./dev.db
# Production: postgresql://user:pass@host:5432/db

# ── Vector Database (Qdrant) ─────────────
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
# Production: https://xxx.qdrant.io

# ── Cache (Redis / Upstash) ──────────────
UPSTASH_REDIS_URL=redis://localhost:6379

# ── AI Services ──────────────────────────
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
# Get free key: https://console.groq.com

# ── Storage (Cloudflare R2) ──────────────
R2_ENDPOINT=
R2_ACCESS_KEY=
R2_SECRET_KEY=
R2_BUCKET=memegpt-dev

# ── Monitoring ───────────────────────────
SENTRY_DSN=
UMAMI_WEBSITE_ID=
```

---

## Docker Compose (Local Development)

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./services/api
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./services/api:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

---

## Switching Environments

```bash
# Development (default)
cp .env.development .env
npm run dev

# Staging
cp .env.staging .env
npm run build && npm run start

# Production
# Environment variables set via Railway/Vercel dashboard
# Never commit .env.production to Git!
```

---

## Security Rules

| Rule | Development | Production |
|---|---|---|
| `.env` in `.gitignore` | ✅ Yes | ✅ Yes |
| API keys in code | ❌ Never | ❌ Never |
| Debug mode | ✅ Allowed | ❌ Must be false |
| Swagger UI visible | ✅ Allowed | ❌ Must be hidden |
| HTTPS required | ❌ Optional | ✅ Mandatory |
| CORS wildcard `*` | ❌ Never | ❌ Never |

---

## Best Practices

1. **Never hardcode API keys** — always use environment variables
2. **Keep `.env` in `.gitignore`** — commit `.env.example` instead
3. **Use different API keys per environment** — dev keys ≠ production keys
4. **Set `DEBUG=false` in production** — prevents stack trace leaks
5. **Validate all env vars at startup** — fail fast if missing critical values
6. **Use `pydantic-settings`** — type-safe config with validation

---

> **Related Documents:**
> - [Environment_Variables.md](./Environment_Variables.md) — Complete `.env` reference
> - [Development_Setup.md](./Development_Setup.md) — Local dev setup
> - [Production_Setup.md](./Production_Setup.md) — Production deployment
