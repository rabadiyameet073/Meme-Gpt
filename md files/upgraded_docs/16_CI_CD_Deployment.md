# 16 — CI/CD & Deployment
# GitHub Actions, Railway (Backend), Vercel (Frontend), Sentry, UptimeRobot

> **Gap Source:** Section 12 of GAP_ANALYSIS_FULL.md  
> **Priority:** P2  
> **Target:** Fully automated deploy pipeline

---

## ARCHITECTURE

```
GitHub Push → GitHub Actions CI:
  ├── Test (pytest + vitest)
  ├── Lint (ruff + eslint)
  └── Build Docker image
         ↓
     Railway Deploy (backend + FastAPI)
         ↓
     Vercel Deploy (frontend + Vite SPA)
         ↓
     Sentry Error Tracking
     UptimeRobot Health Monitoring
```

---

## FILE 1 — GitHub Actions: Full CI/CD Pipeline

**Create** `.github/workflows/deploy.yml` (create directories if needed):

```yaml
name: MemeGPT — CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "20"

jobs:
  # ─────────────────────────────────────────
  # JOB 1: Backend Tests
  # ─────────────────────────────────────────
  test-backend:
    name: Backend Tests (pytest)
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests with coverage
        env:
          DATABASE_URL: sqlite:///./test.db
          SECRET_KEY: test_secret_key_for_ci_only
          GROQ_API_KEY: ""      # Tests must work without real keys
          QDRANT_URL: ""
          REDIS_URL: ""
        run: |
          pytest tests/ -v \
            --cov=app \
            --cov-report=term-missing \
            --cov-fail-under=70 \
            -x

      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        with:
          directory: backend/

  # ─────────────────────────────────────────
  # JOB 2: Frontend Tests
  # ─────────────────────────────────────────
  test-frontend:
    name: Frontend Tests (Vitest)
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test -- --run --reporter=verbose

      - name: Build (production check)
        run: npm run build

  # ─────────────────────────────────────────
  # JOB 3: Deploy Backend to Railway
  # ─────────────────────────────────────────
  deploy-backend:
    name: Deploy Backend → Railway
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - uses: actions/checkout@v4

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          cd backend
          railway up --service memegpt-api --detach

      - name: Run DB migration on Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          railway run --service memegpt-api python migrate.py

  # ─────────────────────────────────────────
  # JOB 4: Deploy Frontend to Vercel
  # ─────────────────────────────────────────
  deploy-frontend:
    name: Deploy Frontend → Vercel
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install Vercel CLI
        run: npm install -g vercel

      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          cd frontend
          vercel --prod --token $VERCEL_TOKEN \
            --env VITE_API_URL=https://api.memegpt.com
```

---

## FILE 2 — Railway Setup (`railway.toml`)

**Create** `d:\Meme GPT\backend\railway.toml`:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
healthcheckPath = "/health"
healthcheckTimeout = 30

[[services]]
name = "memegpt-api"
```

---

## FILE 3 — Vercel Config (`vercel.json`)

**Create** `d:\Meme GPT\frontend\vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm ci",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/((?!api/).*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    },
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

---

## FILE 4 — Sentry Integration

### Backend Sentry

In `d:\Meme GPT\backend\app\main.py`, add Sentry initialization:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_dsn = getattr(settings, "SENTRY_DSN", "")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,   # 10% of requests traced
        profiles_sample_rate=0.1,
        environment=getattr(settings, "APP_ENV", "development"),
        release=getattr(settings, "APP_VERSION", "1.0.0"),
    )
    logger.info("✅ Sentry initialized")

# Add to requirements.txt:
# sentry-sdk[fastapi]>=1.40.0
```

### Frontend Sentry

```bash
cd "d:\Meme GPT\frontend"
npm install @sentry/react @sentry/vite-plugin
```

In `d:\Meme GPT\frontend\src\main.tsx`:

```tsx
import * as Sentry from "@sentry/react";

const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: 0.1,
    environment: import.meta.env.MODE,
  });
}
```

---

## STEP — Add GitHub Secrets

In GitHub repo → Settings → Secrets → Actions, add:

| Secret Name | Value | Where to Get |
|---|---|---|
| `RAILWAY_TOKEN` | Railway token | railway.app → Account → Tokens |
| `VERCEL_TOKEN` | Vercel token | vercel.com → Settings → Tokens |
| `VERCEL_ORG_ID` | Org ID | `vercel env pull` output |
| `VERCEL_PROJECT_ID` | Project ID | `vercel env pull` output |

---

## UptimeRobot Setup

1. Go to https://uptimerobot.com → Create Monitor
2. Monitor Type: **HTTP(s)**
3. URL: `https://api.memegpt.com/health`
4. Monitoring Interval: **5 minutes**
5. Alert Contacts: Your email

### Health Endpoint Verification

```bash
curl https://api.memegpt.com/health
# Should return:
{
  "status": "ok",
  "version": "1.0.0",
  "qdrant": "ok",
  "redis": "ok",
  "db": "ok"
}
```

---

## MANUAL DEPLOYMENT (Without GitHub Actions)

### Backend to Railway:
```bash
npm install -g @railway/cli
railway login
cd "d:\Meme GPT\backend"
railway up
```

### Frontend to Vercel:
```bash
npm install -g vercel
cd "d:\Meme GPT\frontend"
vercel --prod
```

---

## ENVIRONMENT VARIABLES ON RAILWAY

Set all production env vars in Railway dashboard:
- **Railway** → Your Project → Variables → Add All vars from `.env`
- KEY production-specific ones:
  - `APP_ENV=production`
  - `DATABASE_URL=postgresql://...` (Railway PostgreSQL addon)
  - `DEBUG=false`
  - `APP_BASE_URL=https://api.memegpt.com`
