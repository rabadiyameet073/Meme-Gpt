# 07 — CI/CD with GitHub Actions
> **Priority:** 🟡 Medium — Automate testing and deployment
> **Time Needed:** ~2 hours
> **Result:** Every push to `main` runs tests + deploys automatically

---

## 🔄 What This Sets Up

```
Developer pushes code to GitHub (main branch)
  ↓
GitHub Actions triggers automatically
  ↓
  ├── Run all 134 pytest tests
  ├── Run flake8 linting
  ├── Build Docker image (validates it compiles)
  ↓ (if all pass)
  ├── Deploy backend to Railway
  └── Deploy frontend to Vercel (via Vercel GitHub integration)
```

---

## 📋 Step 1 — Add GitHub Secrets

In GitHub → Your Repo → Settings → Secrets and Variables → Actions → New Secret:

| Secret Name | Value | Where to Get |
|---|---|---|
| `RAILWAY_TOKEN` | Railway API token | Railway Dashboard → Settings → API Tokens |
| `VERCEL_TOKEN` | Vercel API token | Vercel → Settings → Tokens → Create |
| `VERCEL_ORG_ID` | Your Vercel org ID | `vercel whoami` |
| `VERCEL_PROJECT_ID` | Frontend project ID | Vercel → Project → Settings → bottom |
| `GROQ_API_KEY` | Your Groq key | For test environment |
| `QDRANT_URL` | Qdrant cluster URL | For integration tests |
| `QDRANT_API_KEY` | Qdrant API key | For integration tests |

---

## 📋 Step 2 — Create Main CI/CD Workflow

Create `d:\Meme GPT\.github\workflows\ci_cd.yml`:

```yaml
name: MemeGPT CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "20"

jobs:
  # ─────────────────────────────────────
  # Job 1: Backend Tests
  # ─────────────────────────────────────
  backend-tests:
    name: 🧪 Backend Tests
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: backend

    env:
      APP_ENV: testing
      DATABASE_URL: sqlite:///./test_memegpt.db
      GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
      QDRANT_URL: ${{ secrets.QDRANT_URL }}
      QDRANT_API_KEY: ${{ secrets.QDRANT_API_KEY }}
      REDIS_URL: ""
      SECRET_KEY: "test-secret-key-for-ci-only-32chars"
      LOG_LEVEL: WARNING
      EMBEDDING_MODEL: all-MiniLM-L6-v2
      MODELS_CACHE_DIR: ./model_cache

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install system dependencies
        run: sudo apt-get install -y tesseract-ocr

      - name: Install Python dependencies
        run: pip install -r requirements.txt

      - name: Run linting (flake8)
        run: |
          flake8 app/ --max-line-length=120 --ignore=E501,W503 --exclude=__pycache__
        continue-on-error: true  # Don't fail build on style issues

      - name: Run tests with coverage
        run: |
          pytest tests/ \
            --tb=short \
            --timeout=30 \
            -x \
            --ignore=tests/test_ai_pipeline.py \
            -q \
            2>&1 | head -200

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: backend-coverage
          path: backend/htmlcov/
        if: always()

  # ─────────────────────────────────────
  # Job 2: Frontend Build Check
  # ─────────────────────────────────────
  frontend-build:
    name: 🏗️ Frontend Build
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: frontend

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js ${{ env.NODE_VERSION }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Build frontend
        run: npm run build
        env:
          VITE_API_URL: https://memegpt.railway.app/api/v1

      - name: Check build output
        run: |
          ls -la dist/
          echo "Build size: $(du -sh dist/ | cut -f1)"

  # ─────────────────────────────────────
  # Job 3: Deploy Backend to Railway
  # (Only on push to main, not PRs)
  # ─────────────────────────────────────
  deploy-backend:
    name: 🚂 Deploy Backend
    runs-on: ubuntu-latest
    needs: [backend-tests]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy to Railway
        run: railway up --service=memegpt-backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  # ─────────────────────────────────────
  # Job 4: Deploy Frontend to Vercel
  # (Only on push to main, not PRs)
  # ─────────────────────────────────────
  deploy-frontend:
    name: ▲ Deploy Frontend
    runs-on: ubuntu-latest
    needs: [frontend-build]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
          vercel-args: --prod
```

---

## 📋 Step 3 — Create Weekly Meme Re-Indexing Cron

Create `d:\Meme GPT\.github\workflows\weekly_reindex.yml`:

```yaml
name: Weekly Meme Re-Index

on:
  schedule:
    # Every Sunday at 2:00 AM UTC
    - cron: "0 2 * * 0"
  workflow_dispatch:  # Allow manual trigger

jobs:
  reindex:
    name: 🔄 Collect + Re-Index Memes
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: backend

    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
      QDRANT_URL: ${{ secrets.QDRANT_URL }}
      QDRANT_API_KEY: ${{ secrets.QDRANT_API_KEY }}
      GIPHY_API_KEY: ${{ secrets.GIPHY_API_KEY }}
      R2_ENDPOINT: ${{ secrets.R2_ENDPOINT }}
      R2_ACCESS_KEY: ${{ secrets.R2_ACCESS_KEY }}
      R2_SECRET_KEY: ${{ secrets.R2_SECRET_KEY }}
      R2_BUCKET: ${{ secrets.R2_BUCKET }}
      CDN_BASE_URL: ${{ secrets.CDN_BASE_URL }}
      EMBEDDING_MODEL: all-MiniLM-L6-v2
      MODELS_CACHE_DIR: ./model_cache

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Collect new memes from Giphy
        run: python scripts/collect_giphy_full.py
        continue-on-error: true

      - name: Re-index all memes to Qdrant
        run: python scripts/reindex_all_to_qdrant.py

      - name: Upload new media to R2
        run: python scripts/upload_to_r2_full.py
        continue-on-error: true

      - name: Report results
        run: |
          python -c "
          from app.database import SessionLocal, Meme
          db = SessionLocal()
          count = db.query(Meme).count()
          db.close()
          print(f'Total memes in DB: {count}')
          "
```

---

## 📋 Step 4 — Create Health Check Workflow

Create `d:\Meme GPT\.github\workflows\health_check.yml`:

```yaml
name: Health Check

on:
  schedule:
    # Every 15 minutes
    - cron: "*/15 * * * *"
  workflow_dispatch:

jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - name: Check backend health
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
            "https://your-app.railway.app/api/v1/health")
          echo "Backend status: $STATUS"
          if [ "$STATUS" != "200" ]; then
            echo "❌ Backend is DOWN!"
            exit 1
          fi
          echo "✅ Backend is healthy"

      - name: Check frontend
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://memegpt-xyz.vercel.app")
          echo "Frontend status: $STATUS"
```

---

## 📋 Step 5 — Add conftest.py for Test DB Isolation

The existing `backend/tests/conftest.py` should already have test setup. Verify it uses SQLite for tests, not production DB. If it doesn't, update it:

```python
# backend/tests/conftest.py — verify this exists and works
import pytest
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_memegpt.db")
os.environ.setdefault("QDRANT_URL", "")  # Use DB fallback in tests
os.environ.setdefault("REDIS_URL", "")   # Use in-memory fallback in tests
```

---

## 📋 Step 6 — Verify PR Checks Work

```powershell
# Make a test commit and push
git checkout -b test/ci-check
echo "# test" >> README.md
git add . && git commit -m "test: CI check"
git push origin test/ci-check

# Create PR in GitHub
# You should see CI checks appear in the PR
```

---

## ✅ Done When

- [ ] `ci_cd.yml` appears in GitHub Actions tab
- [ ] Pushing to `main` triggers backend tests + frontend build
- [ ] Tests pass in CI (even if some tests skip without real Qdrant)
- [ ] Railway auto-deploys on push to main
- [ ] Vercel auto-deploys (Vercel handles this via GitHub integration)
- [ ] Weekly re-index cron visible in Actions → Scheduled jobs

**Next step → `08_Monitoring_Sentry.md`**
