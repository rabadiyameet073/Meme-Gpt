# 06 — Deployment: Railway (Backend) + Vercel (Frontend)
> **Priority:** 🟠 High — App is localhost-only right now
> **Time Needed:** ~3 hours
> **Result:** Backend live at `https://memegpt-api.railway.app`, frontend at `https://memegpt.vercel.app`

---

## 🏗️ Architecture After Deployment

```
User (anywhere)
  ↓ HTTPS
Vercel (Frontend SPA)               ← frontend/ deployed here
  ↓ API calls
Railway.app (FastAPI Backend)       ← backend/ deployed here
  ↓ reads
Qdrant Cloud + Upstash Redis + Cloudflare R2
```

---

## PART A — Deploy Backend to Railway

### Step A1 — Railway Account Setup

```
1. Go to: https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub Repo"
4. Select your MemeGPT repo
5. Set "Root Directory" → backend
6. Railway auto-detects FastAPI from requirements.txt + Dockerfile
```

### Step A2 — Check/Update the Dockerfile

File: `d:\Meme GPT\backend\Dockerfile` — verify it looks like this:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system deps for Pillow, pytesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download ML models during build (optional — speeds up cold start)
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

If `Dockerfile` doesn't exist, create it at `d:\Meme GPT\backend\Dockerfile`.

### Step A3 — Set Environment Variables in Railway

In Railway dashboard → Your project → "Variables" tab, add ALL these:

```env
# App
APP_NAME=MemeGPT
APP_ENV=production
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# Database (Railway provides free PostgreSQL — add plugin)
DATABASE_URL=<auto-filled by Railway PostgreSQL plugin>

# Groq LLM
GROQ_API_KEY=gsk_XXXXXXXXXXXXXX
GROQ_MODEL=llama-3.1-8b-instant
GROQ_TIMEOUT=5

# Qdrant
QDRANT_URL=https://your-cluster.us-east-1.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION=memes

# Redis
REDIS_URL=redis://default:password@alive-xxx.upstash.io:6379

# Cloudflare R2
R2_ENDPOINT=https://ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=memegpt-memes
CDN_BASE_URL=https://pub-YOURPUBLICID.r2.dev

# Security
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
JWT_ALGORITHM=HS256

# CORS (your Vercel frontend URL)
CORS_ORIGINS=https://memegpt.vercel.app,https://memegpt.com,https://app.memegpt.com

# Sentry
SENTRY_DSN=https://xxx@sentry.io/xxx

# ML Models
EMBEDDING_MODEL=all-MiniLM-L6-v2
MODELS_CACHE_DIR=./model_cache

# Rate Limiting
RATE_LIMIT_ANONYMOUS=60
RATE_LIMIT_FREE=120
RATE_LIMIT_PRO=300
```

### Step A4 — Add PostgreSQL Plugin (Upgrade from SQLite)

In Railway → Your Project → "New" → "Database" → "PostgreSQL"

Railway automatically sets `DATABASE_URL` to the PostgreSQL connection string.

After adding PostgreSQL, run migrations:
```powershell
# This runs in Railway's shell (or locally with the production DATABASE_URL)
cd backend
python -c "from app.database import init_db; init_db()"
```

### Step A5 — Migrate Data from SQLite to PostgreSQL

```python
# d:\Meme GPT\backend\scripts\migrate_sqlite_to_postgres.py
"""Migrate all memes from local SQLite to Railway PostgreSQL."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv('../.env')

from sqlalchemy import create_engine
from app.database import Meme, Base

# Local SQLite
sqlite_engine = create_engine("sqlite:///./memegpt.db")

# Railway PostgreSQL (replace with your actual URL)
postgres_url = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")
postgres_engine = create_engine(postgres_url)

# Create tables in Postgres
Base.metadata.create_all(postgres_engine)

# Copy data
from sqlalchemy.orm import sessionmaker

SqliteSession = sessionmaker(bind=sqlite_engine)
PgSession = sessionmaker(bind=postgres_engine)

sqlite_db = SqliteSession()
pg_db = PgSession()

memes = sqlite_db.query(Meme).all()
print(f"Copying {len(memes)} memes...")

for meme in memes:
    pg_db.merge(meme)

pg_db.commit()
print("✅ Migration complete!")
sqlite_db.close()
pg_db.close()
```

### Step A6 — Verify Railway Deployment

After deploy, check:
- `https://your-app.railway.app/` → should return redirect or HTML
- `https://your-app.railway.app/api/v1/health` → should return `{"status": "healthy"}`
- Railway logs should show: `✅ Qdrant connected`, `✅ Sentry initialized`

---

## PART B — Deploy Frontend to Vercel

### Step B1 — Vercel Setup

```
1. Go to: https://vercel.com
2. Sign up with GitHub
3. Click "New Project"
4. Import your MemeGPT GitHub repo
5. Set:
   - Framework Preset: Vite
   - Root Directory: frontend
   - Build Command: npm run build (auto-detected)
   - Output Directory: dist (auto-detected)
```

### Step B2 — Set Environment Variables in Vercel

In Vercel → Project → Settings → Environment Variables:

```env
VITE_API_URL=https://your-app.railway.app/api/v1
```

### Step B3 — Check vercel.json

File `d:\Meme GPT\frontend\vercel.json` should exist. If not, create it:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ]
}
```

### Step B4 — Update API URL in Frontend

Open `d:\Meme GPT\frontend\src\api.ts` (or wherever the API base URL is set).
It likely uses `import.meta.env.VITE_API_URL`. Confirm this is set, or add it:

```typescript
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
```

### Step B5 — Deploy

```powershell
# Push to GitHub — Vercel auto-deploys on every push to main
git add .
git commit -m "chore: production deployment config"
git push origin main
```

Vercel will build and deploy. Check:
- `https://memegpt-xyz.vercel.app` — app loads
- Search works (calls Railway backend)

---

## PART C — Deploy Landing Page (Next.js) to Vercel

```
1. In Vercel → New Project → Import same repo
2. Root Directory: apps/web
3. Framework: Next.js (auto-detected)
4. Deploy
```

---

## PART D — Custom Domain Setup (Optional)

If you own `memegpt.com`:

```
Vercel → Project → Settings → Domains:
  Add: memegpt.com, www.memegpt.com, app.memegpt.com

Cloudflare DNS:
  A record: memegpt.com → 76.76.21.21 (Vercel IP)
  CNAME: www → cname.vercel-dns.com
  CNAME: app → cname.vercel-dns.com
  CNAME: cdn → pub-YOURR2ID.r2.dev (CDN subdomain)
```

---

## 📋 Post-Deployment Checklist

```powershell
# Test all critical endpoints on production
$BACKEND = "https://your-app.railway.app"

# Health check
Invoke-RestMethod "$BACKEND/api/v1/health"

# Search
Invoke-RestMethod -Uri "$BACKEND/api/v1/search" -Method POST -ContentType "application/json" `
  -Body '{"query":"monday morning feeling"}'

# Trending
Invoke-RestMethod "$BACKEND/api/v1/trending?limit=5"

# Categories
Invoke-RestMethod "$BACKEND/api/v1/categories"
```

---

## ✅ Done When

- [ ] `https://your-app.railway.app/api/v1/health` → `{"status": "healthy"}`
- [ ] `https://memegpt-xyz.vercel.app` → frontend loads
- [ ] Search from frontend returns results from Railway backend
- [ ] Railway logs show all services connected (Qdrant, Redis, R2)
- [ ] No CORS errors in browser console

**Next step → `07_CI_CD_GitHub_Actions.md`**
