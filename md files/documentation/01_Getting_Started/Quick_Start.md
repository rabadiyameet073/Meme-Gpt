# MemeGPT — Quick Start Guide

> **Get MemeGPT running in 5 minutes.**  
> **Last Updated:** 2026-08-02

---

## Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Node.js | 20+ | `node --version` |
| Python | 3.11+ | `python --version` |
| pnpm | 8+ | `pnpm --version` (install: `npm i -g pnpm`) |
| Git | Any recent | `git --version` |

---

## Quick Start Steps

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/memegpt.git
cd memegpt
pnpm install
```

This installs dependencies for all workspaces (frontend, backend, shared types) using Turborepo.

### 2. Set Up Backend

```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
cd ..
```

**Note:** The backend requires PyTorch (installed via requirements.txt). First install may take 2-5 minutes depending on your connection.

### 3. Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and set at minimum:

```env
DATABASE_URL="file:./memegpt.db"
```

For full AI features (recommended), also add:

```env
GROQ_API_KEY="your_groq_api_key"       # LLM intent parsing
QDRANT_URL="http://localhost:6333"       # Vector search (optional for dev)
```

### 4. Seed Database

```bash
pnpm run seed
```

This populates the SQLite database with ~50 sample memes and generates their vector embeddings using MiniLM. Expect ~30 seconds for the initial embedding generation.

### 5. Start Development Servers

```bash
pnpm run dev
```

Starts both backend and frontend concurrently:

| Service | URL | Description |
|---|---|---|
| Frontend | http://localhost:5173 | Vite dev server with HMR |
| Backend API | http://localhost:8000 | FastAPI with auto-reload |
| API Docs | http://localhost:8000/docs | Interactive Swagger UI |

### 6. Verify It Works

```bash
# In another terminal — health check
curl http://localhost:8000/health
# Expected: {"status":"ok","timestamp":"..."}

# Try a search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "when code works first try", "limit": 5}'
```

---

## What to Try First

1. Open http://localhost:5173 in your browser
2. Type "when your code works on first try" in the search box
3. Click "Find Meme" — results should appear in 1-3 seconds
4. Hover over a result to see copy/download options
5. Click a meme card to view details
6. Try different queries: "Monday morning", "success kid", "drake"

---

## Troubleshooting Quick Start

| Problem | Likely Cause | Fix |
|---|---|---|
| `pnpm: command not found` | pnpm not installed | `npm i -g pnpm` |
| `No module named torch` | Python venv not activated | Run `source venv/bin/activate` (or `.\venv\Scripts\Activate.ps1` on Windows) |
| `Connection refused` on port 8000 | Backend not running | Wait for `pnpm run dev` to finish starting both servers |
| Empty search results | Vector index not built | Run `pnpm run seed` |
| Slow first search (5s+) | Normal — MiniLM loads into memory | Subsequent searches will be faster (~500ms-1s) |

---

## Need More Detail?

- [Prerequisites.md](./Prerequisites.md) — Full software requirements
- [Installation.md](./Installation.md) — Detailed step-by-step installation
- [Environment_Variables.md](./Environment_Variables.md) — All configuration options
- [Development_Setup.md](./Development_Setup.md) — Advanced dev workflow
- [Project_Setup.md](./Project_Setup.md) — Repository structure and workspaces

---

> **Ready to go. Try searching for a meme now.**