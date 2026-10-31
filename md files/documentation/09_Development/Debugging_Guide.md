# MemeGPT — Debugging Guide

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Step-by-step debugging guide for common development issues — organized by service (backend, frontend, AI, database, deployment).

---

## Debugging by Service

### Backend (FastAPI)

| Problem | Diagnosis | Fix |
|---|---|---|
| `ModuleNotFoundError` | Missing dependency | `pip install -r requirements.txt` |
| Model loading fails | Wrong Python version | Ensure Python 3.11+ |
| `ConnectionRefusedError` on Redis | Redis not running | `docker-compose up redis` |
| Groq API 429 | Rate limit exceeded | Wait 1 minute, or use Ollama fallback |
| Qdrant connection timeout | Wrong URL or API key | Check `QDRANT_URL` in `.env` |
| CORS error from frontend | Origin not in allow list | Add `http://localhost:5173` to CORS |

### Frontend (Next.js)

| Problem | Diagnosis | Fix |
|---|---|---|
| `fetch` returns CORS error | Backend CORS misconfigured | Add frontend URL to CORS origins |
| Images not loading | CDN URL incorrect | Check `R2_ENDPOINT` in env |
| Hydration mismatch | Server/client state differs | Use `'use client'` for dynamic components |
| Build fails with type error | TypeScript strict mode | Fix type annotations |
| Slow page load | Large JS bundle | Check `npm run build` output for size |

### AI Pipeline

| Problem | Diagnosis | Fix |
|---|---|---|
| Low search quality | Embeddings not normalized | Add `normalize_embeddings=True` |
| Emotion detection wrong | Short input text | Ensure >10 characters for accuracy |
| Groq returns gibberish | Temperature too high | Lower to `0.1` for structured output |
| Qdrant returns 0 results | Score threshold too high | Lower from 0.45 to 0.35 |
| CLIP model OOM | Insufficient RAM | Only load CLIP during indexing, not runtime |

### Database

| Problem | Diagnosis | Fix |
|---|---|---|
| SQLite locked | Concurrent writes | Use single writer or switch to PostgreSQL |
| Migration fails | Schema conflict | `npx prisma migrate reset` (dev only!) |
| Slow queries | Missing index | Add index on searched columns |

---

## Quick Debug Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Test search endpoint
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# Check Qdrant
curl http://localhost:6333/collections/memes

# Check Redis
redis-cli ping

# Check environment variables
python -c "from app.core.config import get_settings; print(get_settings().dict())"
```

---

## Log Inspection

```bash
# View FastAPI logs (with uvicorn --reload)
# Logs appear in terminal automatically

# Search for errors
grep -i "error" logs/memegpt.log | tail -20

# View Qdrant logs
docker logs qdrant-container 2>&1 | tail -20
```

---

## Best Practices

1. **Check health endpoint first** — if `/health` fails, fix infrastructure
2. **Read error messages carefully** — FastAPI gives detailed Pydantic errors
3. **Test in isolation** — test one service at a time (backend, then frontend)
4. **Use `--reload` flag** — auto-restart on code changes
5. **Check `.env` first** — 90% of "it doesn't work" issues are missing env vars

---

> **Related Documents:**
> - [14_Troubleshooting/Common_Issues.md](../14_Troubleshooting/Common_Issues.md) — Common issues
> - [03_Backend/Error_Handling.md](../03_Backend/Error_Handling.md) — Error handling
> - [Development_Workflow.md](./Development_Workflow.md) — Daily workflow
