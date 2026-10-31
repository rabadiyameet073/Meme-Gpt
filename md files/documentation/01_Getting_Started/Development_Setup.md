# MemeGPT — Development Setup

> **Document Version:** 1.0  
> **Last Updated:** 2026-08-01  
> **Related Documents:** [Installation.md](./Installation.md) · [Project_Setup.md](./Project_Setup.md)

---

## Purpose

This document covers the day-to-day development workflow: starting servers, making changes, testing locally, and debugging.

---

## Daily Development Workflow

### Starting Development

```bash
# From project root
npm run dev
```

This starts:
- **Backend** (FastAPI) at `http://localhost:8000` with `--reload` (auto-restart on Python file changes)
- **Frontend** (Vite) at `http://localhost:5173` with HMR (hot module replacement)

### Making Backend Changes

1. Edit files in `backend/app/`
2. Uvicorn auto-detects changes and restarts the server
3. Test via Swagger UI at `http://localhost:8000/docs`
4. Or use `curl` / Postman for API testing

### Making Frontend Changes

1. Edit files in `frontend/src/`
2. Vite applies changes instantly via HMR (no page reload needed)
3. View changes in browser at `http://localhost:5173`

---

## API Testing

### Using Swagger UI (Built-in)

FastAPI auto-generates interactive API documentation at `/docs`:

1. Open `http://localhost:8000/docs`
2. Click any endpoint to expand it
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. See the response

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Search memes
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "when code works first try", "limit": 5}'

# Get specific meme
curl http://localhost:8000/memes/1
```

### Using VS Code REST Client

Create a file `test.http`:

```http
### Health Check
GET http://localhost:8000/health

### Search Memes
POST http://localhost:8000/search
Content-Type: application/json

{
  "query": "Monday morning feeling",
  "limit": 5
}
```

---

## Database Management

### View Database Contents

```bash
cd backend
python -c "
from app.database import get_all_memes
memes = get_all_memes()
for m in memes[:5]:
    print(f'{m[\"id\"]}: {m[\"name\"]} ({m[\"category\"]})')
print(f'Total: {len(memes)} memes')
"
```

### Reset Database

```bash
# Delete and re-seed
rm backend/memegpt.db
npm run seed
```

### Re-generate Embeddings

```bash
npm run embeddings
```

---

## Hot Reload Behavior

| Component | Hot Reload | Mechanism | Trigger |
|---|---|---|---|
| Backend (Python) | ✅ Auto-restart | Uvicorn `--reload` flag | Any `.py` file change |
| Frontend (React) | ✅ HMR | Vite HMR | Any `.tsx`, `.css` change |
| Database schema | ❌ Manual | `npx prisma generate` | After `schema.prisma` change |
| Environment vars | ❌ Manual | Restart server | After `.env` change |

---

## Debugging

### Backend Debugging (VS Code)

Add this launch configuration to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Debug",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "DATABASE_URL": "file:./memegpt.db"
      }
    }
  ]
}
```

### Frontend Debugging (Browser DevTools)

1. Open Chrome DevTools (F12)
2. Go to Sources tab → `src/` folder
3. Set breakpoints in `.tsx` files
4. React DevTools extension shows component hierarchy

### Logging

Backend logs appear in the terminal running the dev server. Adjust verbosity:

```env
LOG_LEVEL=DEBUG    # Show all logs
LOG_LEVEL=INFO     # Default — show info and above
LOG_LEVEL=WARNING  # Show only warnings and errors
```

---

## Performance Profiling

### Backend

```bash
# Time an API request
curl -w "\n\nTime: %{time_total}s\n" \
  -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

### Frontend

Use Chrome DevTools → Performance tab → Record → Interact → Stop → Analyze.

Key metrics to watch:
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Total Blocking Time (TBT)

---

> **Related Documents:**
> - [09_Development/Coding_Standards.md](../09_Development/Coding_Standards.md) — Code style guide
> - [09_Development/Git_Workflow.md](../09_Development/Git_Workflow.md) — Branching and PR process
> - [10_Testing/Testing_Strategy.md](../10_Testing/Testing_Strategy.md) — How to write and run tests
