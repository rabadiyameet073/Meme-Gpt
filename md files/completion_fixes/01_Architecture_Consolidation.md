# 01 — Architecture Consolidation Guide
> Fix the dual backend + dual frontend + duplicate mobile codebase confusion.

---

## Problem Statement

The project currently has **duplicated structures** that cause confusion:

| What | Location 1 (Active) | Location 2 (Skeleton) | Decision |
|------|---------------------|----------------------|----------|
| Backend | `backend/` (full working code, 82 services, 134 tests) | `services/api/` (Dockerfile + stubs) | Keep `backend/`, retire `services/api/` |
| Frontend (Web App) | `frontend/` (Vite SPA, full working UI) | `apps/web/` (Next.js skeleton) | Keep both — `frontend/` = Vite SPA, `apps/web/` = Next.js SEO/landing |
| Mobile | `apps/mobile/` (Expo, active) | `mobile/` (abandoned scaffold) | Keep `apps/mobile/`, delete `mobile/` |

---

## Step 1: Consolidate Backend

The `services/api/` directory is a skeleton that was supposed to mirror `backend/`. Since `backend/` has the complete implementation, make `services/api/` properly reference it.

### 1.1 Update `services/api/Dockerfile` to point to backend

**File:** `services/api/Dockerfile`

```dockerfile
# This Dockerfile builds the actual backend from the backend/ directory.
# It exists here for docker-compose compatibility.

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      tesseract-ocr \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the real backend
COPY ../../backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download ML models during build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" || true
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base')" || true

# Copy the actual backend code
COPY ../../backend/ .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

### 1.2 Update `docker-compose.yml` to use `backend/`

**File:** `docker-compose.yml`

Replace the `api` service `build.context`:

```yaml
services:
  api:
    build:
      context: ./backend           # ← Changed from ./services/api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - qdrant
      - redis
    volumes:
      - ./backend:/app             # ← Changed from ./services/api
      - ./data:/data
    env_file:
      - .env

  qdrant:
    image: qdrant/qdrant:v1.7.4
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  qdrant_storage:
```

### 1.3 Update `railway.toml` at project root

**File:** `railway.toml`

```toml
[build]
builder = "dockerfile"
dockerfilePath = "backend/Dockerfile"
watchPatterns = ["backend/**"]

[deploy]
startCommand = "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

### 1.4 Update CI/CD workflow paths

**File:** `.github/workflows/ci_cd.yml`

In every step that references `services/api`, change to `backend/`:

```yaml
# BEFORE:
- name: Install dependencies
  run: |
    cd services/api
    pip install -r requirements.txt

# AFTER:
- name: Install dependencies
  run: |
    cd backend
    pip install -r requirements.txt
```

Do this for `test.yml`, `ci.yml`, `deploy.yml` as well.

---

## Step 2: Clean Up Duplicate Mobile

### 2.1 Remove `mobile/` directory at project root

The `mobile/` folder at the root is an earlier scaffold. The active mobile app is at `apps/mobile/`.

```powershell
# From project root
Remove-Item -Recurse -Force "d:\Meme GPT\mobile"
```

### 2.2 Update `.gitignore` if it references `mobile/`

Make sure `.gitignore` doesn't have entries that would ignore `apps/mobile/`.

---

## Step 3: Define the Frontend Strategy

You have two frontend apps, and both serve different purposes:

| App | Framework | Purpose | URL |
|-----|-----------|---------|-----|
| `frontend/` | Vite + React SPA | **The main web application** (search, chat, trending, favorites, admin) | `app.memegpt.com` |
| `apps/web/` | Next.js 14 | **Landing site + SEO pages** (homepage, meme pages, blog, download page) | `memegpt.com` |

### 3.1 Add README to each frontend

**File:** `frontend/README.md`
```markdown
# MemeGPT Web Application (Vite SPA)

The main web application — ChatGPT-style meme search interface.

## Tech Stack
- React 19 + TypeScript
- Vite 6
- Framer Motion
- Lucide React icons

## Run locally
```bash
npm install
npm run dev  # http://localhost:5173
```

## Deploy
Deployed to Vercel as `app.memegpt.com`
```

**File:** `apps/web/README.md`
```markdown
# MemeGPT Landing Site & SEO Pages (Next.js)

Marketing site + 10,000+ SEO-indexed meme pages.

## Tech Stack
- Next.js 14 (App Router)
- Tailwind CSS
- SSG/SSR for SEO

## Run locally
```bash
npm install
npm run dev  # http://localhost:3000
```

## Deploy
Deployed to Vercel as `memegpt.com`
```

### 3.2 Update the Vite frontend to use the correct API URL

**File:** `frontend/src/lib/api.ts`

Ensure the API base URL reads from environment:
```typescript
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

**File:** `frontend/.env.development`
```env
VITE_API_URL=http://localhost:8000
```

**File:** `frontend/.env.production`
```env
VITE_API_URL=https://api.memegpt.com
```

---

## Step 4: Create a Unified Start Script

**File (create new):** `package.json` (project root — update)

```json
{
  "name": "memegpt",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev:backend": "cd backend && uvicorn app.main:app --reload --port 8000",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:web": "cd apps/web && npm run dev",
    "dev:mobile": "cd apps/mobile && npx expo start",
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "test:backend": "cd backend && python -m pytest tests/ -v",
    "test:frontend": "cd frontend && npm test",
    "build:frontend": "cd frontend && npm run build",
    "build:web": "cd apps/web && npm run build"
  },
  "devDependencies": {
    "concurrently": "^8.2.2"
  }
}
```

Install concurrently:
```powershell
cd "d:\Meme GPT"
npm install
```

---

## Verification Checklist

- [ ] `docker-compose up` starts the API from `backend/` directory
- [ ] `npm run dev:backend` starts FastAPI at `localhost:8000`
- [ ] `npm run dev:frontend` starts Vite at `localhost:5173`
- [ ] `npm run dev:web` starts Next.js at `localhost:3000`
- [ ] `mobile/` directory is deleted
- [ ] `services/api/` Dockerfile references `backend/`
- [ ] All CI/CD workflows reference `backend/` not `services/api/`
- [ ] Both frontends can reach the backend API
