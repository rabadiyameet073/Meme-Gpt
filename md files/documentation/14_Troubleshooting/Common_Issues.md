# MemeGPT — Common Issues & Troubleshooting

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Searchable troubleshooting guide — common errors, their causes, and step-by-step fixes organized by symptom.

---

## Quick Diagnostic Flowchart

```mermaid
flowchart TD
    START["Something isn't working"] --> H{"curl /health<br/>returns 200?"}
    H -->|No| S1["Backend is down<br/>→ Check Railway logs"]
    H -->|Yes| S2{"Search returns<br/>results?"}
    S2 -->|No| S3{"Qdrant<br/>connected?"}
    S2 -->|Yes| S4["✅ Backend is fine<br/>Check frontend"]
    S3 -->|No| S5["Check QDRANT_URL<br/>and QDRANT_API_KEY"]
    S3 -->|Yes| S6["Check score_threshold<br/>and collection count"]
```

---

## Error: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Cause:** Python dependencies not installed.

```bash
# Fix
cd services/api
pip install -r requirements.txt
```

---

## Error: "CORS error — blocked by CORS policy"

**Cause:** Frontend URL not in backend's CORS allow list.

```python
# Fix: Add your frontend URL to CORS origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",   # Next.js dev
    "http://localhost:5173",   # Vite dev
    "https://memegpt.com",    # Production
]
```

---

## Error: "Qdrant connection refused"

**Cause:** Qdrant not running locally, or wrong URL/API key.

```bash
# Fix 1: Start local Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Fix 2: Check .env
QDRANT_URL=http://localhost:6333  # Local
# or
QDRANT_URL=https://xxx.qdrant.io  # Cloud
QDRANT_API_KEY=your_key_here
```

---

## Error: "Redis connection refused"

**Cause:** Redis not running locally.

```bash
# Fix 1: Start local Redis
docker run -p 6379:6379 redis:7-alpine

# Fix 2: Use Upstash Redis (no local install needed)
UPSTASH_REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379
```

---

## Issue: "Search returns 0 results"

**Causes (in order of likelihood):**

| # | Cause | Fix |
|---|---|---|
| 1 | Qdrant collection is empty | Run `python scripts/index_qdrant.py` |
| 2 | score_threshold too high | Lower from 0.45 to 0.35 |
| 3 | NSFW filter excluding everything | Set `nsfw=True` temporarily to test |
| 4 | Wrong collection name | Verify `"memes"` in Qdrant |
| 5 | Embeddings not normalized | Add `normalize_embeddings=True` |

---

## Issue: "Search is slow (>3 seconds)"

| # | Cause | Fix |
|---|---|---|
| 1 | Groq API slow | Check Groq status page; fallback to raw query |
| 2 | ML models loading per-request | Use `lifespan` hook to load once at startup |
| 3 | Redis cache not working | Verify Redis connection; check cache TTL |
| 4 | Cold start after idle | Set minimum 1 instance on Railway |

---

## Issue: "Frontend build fails"

```bash
# Common fixes
cd apps/web
rm -rf node_modules .next
npm install
npm run build
```

---

## Issue: "Railway deploy fails"

```bash
# Check logs
railway logs --service api

# Common fixes:
# 1. Ensure Dockerfile has correct Python version
# 2. Check all env vars are set in Railway dashboard
# 3. Verify requirements.txt has all dependencies
```

---

## Best Practices for Debugging

1. **Check `/health` first** — if health fails, fix infrastructure
2. **Read the error message** — FastAPI gives detailed Pydantic errors
3. **Check `.env` file** — 90% of issues are missing/wrong env vars
4. **Test one service at a time** — backend, then frontend
5. **Check logs** — `railway logs` or `docker logs`

---

> **Related Documents:**
> - [Debug_Guide.md](./Debug_Guide.md) — Debugging procedures
> - [09_Development/Debugging_Guide.md](../09_Development/Debugging_Guide.md) — Dev debugging
> - [03_Backend/Error_Handling.md](../03_Backend/Error_Handling.md) — Error patterns
