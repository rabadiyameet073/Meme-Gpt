# 09 — Final .env with All Values (Production Checklist)
> **This is your master env file reference.**
> Fill in EVERY blank value below before going to production.

---

## ✅ Production .env — Complete File

Copy this to `d:\Meme GPT\.env` and fill in all empty values:

```env
# ══════════════════════════════════════════════════════════════════
# MemeGPT — PRODUCTION Environment Configuration
# ══════════════════════════════════════════════════════════════════

# ── APP ────────────────────────────────────────────────────────────
APP_NAME=MemeGPT
APP_ENV=production
APP_VERSION=1.0.0
APP_BASE_URL=https://your-app.railway.app
DEBUG=false
LOG_LEVEL=INFO

# ── DATABASE ───────────────────────────────────────────────────────
# For local dev: sqlite:///./memegpt.db
# For production (Railway PostgreSQL): auto-set by Railway plugin
DATABASE_URL=postgresql://user:password@host:5432/memegpt

# ── GROQ LLM (Intent Parsing) ─────────────────────────────────────
# GET FROM: https://console.groq.com → API Keys → Create Key
GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GROQ_MODEL=llama-3.1-8b-instant
GROQ_TIMEOUT=5
GROQ_MAX_TOKENS=200

# ── QDRANT (Vector Search) ─────────────────────────────────────────
# GET FROM: https://cloud.qdrant.io → Your Cluster → API Keys
QDRANT_URL=https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.us-east-1.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION=memes
QDRANT_TIMEOUT=10

# ── REDIS CACHE (Upstash) ──────────────────────────────────────────
# GET FROM: https://upstash.com → Your Database → Connection
REDIS_URL=redis://default:your_password@alive-xxx.upstash.io:6379
# Alternative REST API (use if TCP connection is blocked):
UPSTASH_REDIS_REST_URL=https://alive-xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_upstash_token_here
REDIS_CACHE_TTL=3600

# ── CLOUDFLARE R2 (Media CDN) ──────────────────────────────────────
# GET FROM: https://dash.cloudflare.com → R2 → Manage API Tokens
# Account ID: visible in Cloudflare Dashboard URL
R2_ENDPOINT=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_r2_access_key_id_here
R2_SECRET_KEY=your_r2_secret_access_key_here
R2_BUCKET=memegpt-memes
# Public URL (either custom domain or R2 free URL):
CDN_BASE_URL=https://pub-YOUR_PUBLIC_ID.r2.dev
# OR if custom domain: CDN_BASE_URL=https://cdn.memegpt.com

# ── GIPHY (GIF Collection) ──────────────────────────────────────────
# GET FROM: https://developers.giphy.com → Dashboard → Create App
GIPHY_API_KEY=your_giphy_api_key_here

# ── TENOR (Reaction GIFs) ───────────────────────────────────────────
# GET FROM: https://developers.google.com/tenor → Create API Key
TENOR_API_KEY=your_tenor_api_key_here

# ── REDDIT (Meme Collection) ────────────────────────────────────────
# GET FROM: https://www.reddit.com/prefs/apps → Create Script App
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=MemeGPT/1.0 by /u/your_username

# ── SECURITY ────────────────────────────────────────────────────────
# Generate: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=e83a7f85d92e4726b1c28f731a57e3bc48d91029e73fa248c8b671ef09a32c1b
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── CORS ─────────────────────────────────────────────────────────────
# Add your actual frontend domain here:
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://memegpt.vercel.app,https://app.memegpt.com,https://memegpt.com

# ── SENTRY (Error Tracking) ──────────────────────────────────────────
# GET FROM: https://sentry.io → New Project → Python → DSN
SENTRY_DSN=https://xxxxxxxxxxxxx@o000000.ingest.sentry.io/000000

# ── ML MODELS ────────────────────────────────────────────────────────
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMOTION_MODEL=j-hartmann/emotion-english-distilroberta-base
MODELS_CACHE_DIR=./model_cache

# ── RATE LIMITING ─────────────────────────────────────────────────────
RATE_LIMIT_ANONYMOUS=60
RATE_LIMIT_FREE=120
RATE_LIMIT_PRO=300
RATE_LIMIT_INTERNAL=1000

# ── GIPHY LIVE SEARCH (used in search_service for trending) ──────────
GIPHY_API_KEY=your_giphy_key_here

# ── APScheduler ───────────────────────────────────────────────────────
# Data retention: delete search logs older than 30 days
DATA_RETENTION_DAYS=30
```

---

## 📋 Status Checklist — Before Going Live

Run this script to check what's configured and what's missing:

```powershell
cd "d:\Meme GPT\backend"
python -c "
import os
from dotenv import load_dotenv
load_dotenv('../.env')

print('=== MemeGPT Environment Status ===\n')

checks = [
    ('GROQ_API_KEY', 'Groq LLM (intent parsing)'),
    ('QDRANT_URL', 'Qdrant (vector search)'),
    ('QDRANT_API_KEY', 'Qdrant API key'),
    ('REDIS_URL', 'Redis/Upstash (caching)'),
    ('R2_ENDPOINT', 'Cloudflare R2 (CDN)'),
    ('R2_ACCESS_KEY', 'R2 access key'),
    ('R2_SECRET_KEY', 'R2 secret key'),
    ('CDN_BASE_URL', 'CDN base URL'),
    ('SENTRY_DSN', 'Sentry (error tracking)'),
    ('GIPHY_API_KEY', 'Giphy API (meme collection)'),
    ('SECRET_KEY', 'JWT secret key'),
]

all_ok = True
for key, name in checks:
    val = os.getenv(key, '')
    if val and val != 'your_key_here' and 'XXXX' not in val:
        print(f'  ✅ {name}: SET')
    else:
        print(f'  ❌ {name}: MISSING — set {key} in .env')
        all_ok = False

print()
if all_ok:
    print('🎉 All environment variables are configured!')
else:
    print('⚠️  Fix the missing variables above before deploying.')
"
```

---

## 📋 Quick Connectivity Test

Run this to verify all services respond:

```powershell
cd "d:\Meme GPT\backend"
python -c "
from dotenv import load_dotenv
load_dotenv('../.env')

print('Testing service connections...\n')

# Test Qdrant
try:
    from app.services.search_service import get_qdrant_client
    client = get_qdrant_client()
    if client:
        cols = client.get_collections()
        print(f'✅ Qdrant: Connected ({len(cols.collections)} collections)')
    else:
        print('❌ Qdrant: Not connected (check QDRANT_URL)')
except Exception as e:
    print(f'❌ Qdrant: Error — {e}')

# Test Redis
try:
    from app.core.cache import get_redis_client
    redis = get_redis_client()
    if redis:
        redis.ping()
        print('✅ Redis: Connected')
    else:
        print('⚠️  Redis: Using in-memory fallback (set REDIS_URL for persistence)')
except Exception as e:
    print(f'❌ Redis: Error — {e}')

# Test R2
try:
    import os, boto3
    s3 = boto3.client('s3',
        endpoint_url=os.getenv('R2_ENDPOINT'),
        aws_access_key_id=os.getenv('R2_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('R2_SECRET_KEY'))
    s3.list_buckets()
    print('✅ Cloudflare R2: Connected')
except Exception as e:
    print(f'❌ R2: Error — {e}')

# Test Groq
try:
    import os
    from groq import Groq
    client = Groq(api_key=os.getenv('GROQ_API_KEY', ''))
    models = client.models.list()
    print(f'✅ Groq: Connected ({len(models.data)} models available)')
except Exception as e:
    print(f'❌ Groq: Error — {e}')

print('\nDone!')
"
```

---

## 🗺️ Implementation Order — Complete Reference

```
WEEK 1 — Make It Work Locally
  Day 1:  Fill .env → Run connectivity test above
  Day 1:  01_Qdrant_Setup_And_Indexing.md → Connect Qdrant
  Day 1:  02_Redis_Upstash_Setup.md → Connect Redis
  Day 1:  03_Cloudflare_R2_CDN_Setup.md → Connect R2
  Day 2:  04_Meme_Data_Pipeline.md → Collect + index 5K+ memes
  Day 3:  Test everything locally — search returns real results

WEEK 1 — Deploy
  Day 4:  06_Deployment_Railway_Vercel.md → Deploy backend + frontend
  Day 4:  07_CI_CD_GitHub_Actions.md → Set up CI/CD
  Day 5:  08_Monitoring_Sentry.md → Sentry + UptimeRobot

WEEK 2 — Mobile App
  Day 6-12: 05_Mobile_App_Completion.md → Build full mobile app

DONE — You have a production MemeGPT at 100%! 🎭
```

---

*This file + the 8 implementation guide files above = your complete roadmap from 65% to 100% completion.*
