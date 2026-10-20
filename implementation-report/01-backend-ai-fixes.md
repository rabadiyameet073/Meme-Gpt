# 01 — Backend / AI / Data Fixes (production runbook)

## A. KEEP (verified, no action)
- `backend/` (148 files) is canonical. `services/api/` (29 files) is a real modular mirror — **do not delete**; update its Dockerfile/CI paths to build `backend/` if you unify.
- Full pipeline stages verified: `recommendation_service.py:47-185`, `llm_service.py:60-204`, `embedding_service.py:36-231`, `search_service.py:29-791`, `rerank_service`, `rule_engine.py`, `semantic_search.py`, `meme_matcher.py`, `image_processing_service.py:30-175`, `cdn_service.py`, `giphy_service.py`, `oauth_service.py`, `auth_service.py`, `core/{cache,rate_limit,auth,config,jobs,errors,logging_config,monitoring}.py`, `database.py` (WAL + `is_sqlite` swap + sanitize).

## B. WIRE-UP (commands in order)
### B1. Environment (30 min)
```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"  # → SECRET_KEY
```
Fill: `GROQ_API_KEY` (console.groq.com) · `QDRANT_URL/KEY` (cloud.qdrant.io) · `REDIS_URL` or `UPSTASH_*_REST_*` · `R2_ENDPOINT/KEY/SECRET/BUCKET` + `CDN_BASE_URL` · `DATABASE_URL` (local sqlite, prod Postgres plugin) · `CORS_ORIGINS` (exact domains, never `*`) · `SENTRY_DSN` · `GOOGLE_/GITHUB_*` (+ redirect URIs) · `GIPHY/TENOR/REDDIT_*`. Never commit `.env`.
### B2. Infra (30 min)
```powershell
docker-compose up -d
curl localhost:8000/api/v1/health                      # {"status":"ok"}
curl -X POST localhost:8000/api/v1/search -H "Content-Type: application/json" -d '{"query":"code works first try","limit":5}'
```
Pass = 5 results <1.5s; 2nd identical query ~15ms (`cached:true`); 61 rapid anon reqs → 429 + `retry_after` + `X-RateLimit-*`.
### B3. Qdrant collection + index (1–2 h first run)
```powershell
cd backend
python -c "from app.services.search_service import create_qdrant_collection, get_collection_info; create_qdrant_collection(); print(get_collection_info())"
python reindex_all_to_qdrant.py   # or scripts/index_qdrant.py, batch 50-100
python -c "from app.services.search_service import get_collection_info; print(get_collection_info())"  # points_count > 0
```
Expect named vectors `text:384/image:512/combined:896` cosine; filtered search honors `nsfw/format/categories/exclude_ids`; cascade 0.45→0.2 yields ≥3 hits; empty env → `_db_fallback_search` (by design, assert it triggers).
### B4. Image pipeline bulk (2–4 h, needs RAM ~4GB)
```powershell
cd backend
python generate_embeddings.py --limit 200   # pilot; then full
```
Assert per meme: BLIP `caption` non-empty on photos, OCR text on captioned templates, CLIP 512d finite (not all-zero), combined 896d L2-norm ≈1.0, `media URLs NOT NULL`, `emotions` is list.
### B5. Auth verification (1 h)
`GET /api/v1/auth/google|github/login` → consent URL · callback with code → JWT set → `POST /register|login` → `GET /me` → `PUT /me` prefs → `POST /api-keys` → use key → `GET /tier` shows raised limits → `DELETE /api-keys/{id}` revokes (401 after).
### B6. Moderation verification (30 min)
`POST /flag {meme_id, reason}` → `GET /queue` (admin) lists it → `POST /review {approve|remove}` → removed excluded from search → `POST /classify` returns scores (heuristic now; swap real CLIP-NSFW model P2).

## C. BUILD (small, coded plan)
1. **`prisma/seed.ts` (broken — imports nonexistent `server/`):** rewrite to `import { PrismaClient } from '@prisma/client'`, load `backend/data/memes.json`, upsert by `slug`; add `DATABASE_URL="file:./dev.db"`; run `npx prisma generate && npx prisma migrate dev && npx prisma db seed`.
2. **Retrain cron (optional P3):** weekly job votes→contrastive fine-tune MiniLM → publish `model_version` + eval delta in `/health/stats`.
3. **Ollama fallback (optional):** local LLM when Groq 429/offline; rule-fallback already covers MVP.

## Effort + rollback per step
| Step | Effort | Rollback if red |
|---|---|---|
| B1 env | 0.5h | `git checkout .env` (never committed); rotate leaked keys immediately |
| B2 compose | 0.5h | `docker-compose down -v` (local volumes only) |
| B3 Qdrant | 1–2h | `delete_collection` + re-index prior snapshot; fallback covers traffic |
| B4 images | 2–4h | Keep prior `embeddings.json`; re-index reverts vectors |
| B5 auth | 1h | Revoke test keys; disable OAuth routes via env flag |
| B6 moderation | 0.5h | Re-approve test flags; no user impact (queue is admin-only) |
| C1 Prisma seed | 1h | `migrate down` + restore dump |
