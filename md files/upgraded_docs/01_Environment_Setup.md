# 01 — Environment Setup
# Every API Key, Every Env Var, Exactly What To Set

> **Gap Source:** Section 11 of GAP_ANALYSIS_FULL.md  
> **Priority:** P0 — Do this FIRST before any code changes  
> **Files to edit:** `d:\Meme GPT\.env`

---

## WHY THIS MATTERS

Without these env vars set correctly, the following features are DEAD:
- `GROQ_API_KEY` empty → LLM intent parsing disabled, only rule-based fallback
- `QDRANT_URL` missing → Vector search does DB limit scan, not cosine similarity
- `REDIS_URL` missing → Cache is in-memory dict, resets on every restart
- `SECRET_KEY` missing → JWT tokens can't be signed → auth broken
- `R2_*` missing → All meme images are NULL, no CDN

---

## STEP 1 — Get All Required API Keys

### 1a. Groq API Key (LLM Intent Parsing)
- URL: https://console.groq.com
- Sign up free → API Keys → Create Key
- Model used: `llama-3.1-8b-instant`
- Free tier: 6,000 requests/day — sufficient for MVP
- Key format: `gsk_...`

### 1b. Qdrant Cloud (Vector Search)
- URL: https://cloud.qdrant.io
- Sign up free → Create Cluster → Copy URL + API Key
- Free tier: 1 cluster, 1GB storage
- URL format: `https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.us-east4-0.gcp.cloud.qdrant.io:6333`
- Key format: `eyJ0...` (JWT token)

### 1c. Upstash Redis (Cache)
- URL: https://upstash.com
- Sign up free → Create Database → REST API → Copy URL
- Free tier: 10,000 commands/day
- URL format: `rediss://default:xxxx@xxx.upstash.io:6379`

### 1d. Cloudflare R2 (Media Storage)
- URL: https://dash.cloudflare.com → R2
- Create bucket named `memegpt-memes`
- Go to Manage R2 API Tokens → Create Token with Read+Write
- Get: Account ID, Access Key ID, Secret Access Key
- Endpoint: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`

### 1e. Giphy API Key (Live GIFs)
- URL: https://developers.giphy.com
- Sign in → Create App → API Key
- Free tier: 100 requests/hour

### 1f. Sentry DSN (Error Tracking)
- URL: https://sentry.io
- Create project → FastAPI → Copy DSN
- Free tier: 5,000 events/month

---

## STEP 2 — Complete `.env` File

Replace `d:\Meme GPT\.env` with this (fill in your values):

```env
# ══════════════════════════════════════════════════
# MemeGPT — Environment Configuration
# Updated: 2026-08-23 (based on Gap Analysis)
# ══════════════════════════════════════════════════

# ── APP ─────────────────────────────────────────
APP_NAME=MemeGPT
APP_ENV=development
APP_VERSION=1.0.0
APP_BASE_URL=http://localhost:8000
DEBUG=true
LOG_LEVEL=INFO

# ── DATABASE ─────────────────────────────────────
# SQLite (dev) — change to postgres URL for production
DATABASE_URL=sqlite:///./memegpt.db

# ── GROQ LLM (Intent Parsing) ────────────────────
# GET FROM: https://console.groq.com → API Keys
GROQ_API_KEY=gsk_YOUR_KEY_HERE
GROQ_MODEL=llama-3.1-8b-instant
GROQ_TIMEOUT=5
GROQ_MAX_TOKENS=200

# ── QDRANT (Vector Search) ────────────────────────
# GET FROM: https://cloud.qdrant.io
QDRANT_URL=https://YOUR-CLUSTER.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJ0YOUR_QDRANT_KEY_HERE
QDRANT_COLLECTION=memes
QDRANT_TIMEOUT=5

# ── REDIS CACHE (Upstash) ─────────────────────────
# GET FROM: https://upstash.com → Redis → REST URL
REDIS_URL=rediss://default:YOUR_PASSWORD@YOUR-DB.upstash.io:6379
# OR use HTTP REST URL for Upstash:
UPSTASH_REDIS_REST_URL=https://YOUR-DB.upstash.io
UPSTASH_REDIS_REST_TOKEN=YOUR_TOKEN_HERE
REDIS_CACHE_TTL=3600

# ── CLOUDFLARE R2 (Media CDN) ────────────────────
# GET FROM: https://dash.cloudflare.com → R2 → API Tokens
R2_ENDPOINT=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY=YOUR_ACCESS_KEY_ID
R2_SECRET_KEY=YOUR_SECRET_ACCESS_KEY
R2_BUCKET=memegpt-memes
CDN_BASE_URL=https://cdn.memegpt.com
# If no custom domain yet, use R2 public URL:
# CDN_BASE_URL=https://pub-XXXX.r2.dev

# ── GIPHY (Live GIF Search) ───────────────────────
# GET FROM: https://developers.giphy.com
GIPHY_API_KEY=YOUR_GIPHY_KEY_HERE
TENOR_API_KEY=YOUR_TENOR_KEY_HERE

# ── SECURITY ──────────────────────────────────────
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=YOUR_64_CHAR_HEX_SECRET_HERE
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── CORS ─────────────────────────────────────────
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000

# ── SENTRY (Error Tracking) ───────────────────────
# GET FROM: https://sentry.io → Project → DSN
SENTRY_DSN=https://YOUR_KEY@oXXXXXX.ingest.sentry.io/XXXXXXX

# ── ML MODELS ────────────────────────────────────
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMOTION_MODEL=j-hartmann/emotion-english-distilroberta-base
MODELS_CACHE_DIR=./model_cache

# ── RATE LIMITING ─────────────────────────────────
RATE_LIMIT_ANONYMOUS=60
RATE_LIMIT_FREE=120
RATE_LIMIT_PRO=300
RATE_LIMIT_INTERNAL=1000
```

---

## STEP 3 — Generate SECRET_KEY

Run in PowerShell:
```powershell
cd "d:\Meme GPT\backend"
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as `SECRET_KEY=` in `.env`.

---

## STEP 4 — Verify Setup

Run this verification script from `d:\Meme GPT\backend`:
```bash
python -c "
from app.config import settings
print('GROQ:', 'SET' if settings.GROQ_API_KEY else 'MISSING ❌')
print('QDRANT URL:', 'SET' if settings.QDRANT_URL else 'MISSING ❌')
print('QDRANT KEY:', 'SET' if settings.QDRANT_API_KEY else 'MISSING ❌')
print('REDIS:', 'SET' if settings.REDIS_URL else 'MISSING ❌')
print('SECRET:', 'SET' if settings.SECRET_KEY else 'MISSING ❌')
print('R2:', 'SET' if settings.R2_ACCESS_KEY else 'MISSING ❌')
print('GIPHY:', 'SET' if settings.GIPHY_API_KEY else 'MISSING ❌')
"
```

All should print `SET`.

---

## STEP 5 — Add Missing Config Fields

Edit `d:\Meme GPT\backend\app\config.py` — add these missing fields to the `Settings` class:

```python
# Add these fields that are missing from current config.py:

# Groq settings
GROQ_MODEL: str = "llama-3.1-8b-instant"
GROQ_TIMEOUT: int = 5
GROQ_MAX_TOKENS: int = 200

# Qdrant settings
QDRANT_COLLECTION: str = "memes"
QDRANT_TIMEOUT: int = 5

# Redis settings
UPSTASH_REDIS_REST_URL: str = ""
UPSTASH_REDIS_REST_TOKEN: str = ""
REDIS_CACHE_TTL: int = 3600

# R2 / CDN settings
R2_ENDPOINT: str = ""
R2_ACCESS_KEY: str = ""
R2_SECRET_KEY: str = ""
R2_BUCKET: str = "memegpt-memes"
CDN_BASE_URL: str = "https://cdn.memegpt.com"

# ML models
MODELS_CACHE_DIR: str = "./model_cache"

# Rate limits
RATE_LIMIT_ANONYMOUS: int = 60
RATE_LIMIT_FREE: int = 120
RATE_LIMIT_PRO: int = 300
RATE_LIMIT_INTERNAL: int = 1000

# Giphy
GIPHY_API_KEY: str = ""
TENOR_API_KEY: str = ""

# Sentry
SENTRY_DSN: str = ""
```

---

## PRODUCTION ENV VARS (Railway)

When deploying to Railway, add all the same vars in:
**Railway Dashboard → Project → Variables**

Additional production-only vars:
```env
APP_ENV=production
APP_BASE_URL=https://api.memegpt.com
DEBUG=false
DATABASE_URL=postgresql://USER:PASS@HOST:5432/memegpt
CORS_ORIGINS=https://app.memegpt.com,https://memegpt.com
```
