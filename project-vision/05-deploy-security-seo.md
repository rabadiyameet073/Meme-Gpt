# 05 — Deploy, Security, Testing, SEO & Roadmap (production reference)

## 5.1 Local runbook
```powershell
# Backend (FastAPI :8000 + docs at /docs)
cd D:\memegpt\backend
pip install -r requirements.txt
python seed.py                      # ~145 memes SQLite (grow to 5k+: see §5.2)
python generate_embeddings.py       # optional MiniLM pre-cache
python -m uvicorn app.main:app --reload --port 8000
# Frontend (Vite :5173)
cd D:\memegpt\frontend
npm install; npm run dev
# Full stack deps (optional Qdrant :6333 + Redis :6379)
cd D:\memegpt; docker-compose up
# Mobile (LAN backend!)
cd D:\memegpt\apps\mobile
$env:EXPO_PUBLIC_API_URL="http://<YOUR-LAN-IP>:8000"; npx expo start
```
Verify: `curl localhost:8000/api/v1/health` → `{"status":"ok"}`; `POST /api/v1/search {"query":"code works first try"}` → 5 results <1.5s; frontend search + copy + vote + favorites persist.

## 5.2 Environment matrix (`.env.example`, 113 lines — never commit `.env`)
| Group | Vars | Dev | Prod |
|---|---|---|---|
| App | `APP_NAME/APP_ENV/VERSION/BASE_URL/DEBUG/LOG_LEVEL` | debug true | `memegpt.com`, debug false |
| DB | `DATABASE_URL` | `sqlite:///./memegpt.db` | Railway Postgres plugin |
| LLM | `GROQ_API_KEY/MODEL=llama-3.1-8b-instant/TIMEOUT=5/MAX_TOKENS` | key required | same + quota alerts |
| Vectors | `QDRANT_URL/KEY/COLLECTION=memes/TIMEOUT` | local :6333 or empty (fallback) | Qdrant Cloud |
| Cache | `REDIS_URL` / `UPSTASH_*_REST_*`, `REDIS_CACHE_TTL=3600` | local :6379 or in-mem | Upstash |
| Media | `R2_ENDPOINT/KEY/SECRET/BUCKET`, `CDN_BASE_URL` | local `/static` | R2 + custom `cdn.*` |
| Sources | `GIPHY/TENOR_API_KEY`, `REDDIT_ID/SECRET/USER_AGENT` | optional | all set for 5k+ seeding |
| Auth | `SECRET_KEY (secrets.token_hex(32))`, `JWT_*`, `GOOGLE_/GITHUB_*` | generated local | rotated, per-env |
| CORS | `CORS_ORIGINS` | `localhost:5173,localhost:3000` | + prod domains, never `*` |
| Obs. | `SENTRY_DSN`, Umami, `MODELS_CACHE_DIR` | optional | all on |
Generate: `python -c "import secrets; print(secrets.token_hex(32))"`. Rotate on any leak; use anon (not service_role) keys.

## 5.3 Prod deploy
- **Backend (Railway):** `railway login/init/up` + Postgres (+Redis) plugins → set all env → `ENV=prod` → custom `api.memegpt.com` → `Dockerfile` (py3.11-slim + tesseract + model pre-download, single worker) → `railway logs` clean. `railway.toml` + `backend/railway.toml` present.
- **Frontends (Vercel):** Vite (`VITE_API_URL=https://api.memegpt.com`, `app.*`) + Next.js (`NEXT_PUBLIC_API_URL`, `memegpt.com`); copy root `vercel.json` into `apps/web/` per spec; SSL + `curl -I` 200.
- **Data cutover:** `migrate_sqlite_to_postgres.py` → `verify_index` → `evaluate.py` gate.
- **CDN/DNS:** Cloudflare CNAME `memegpt/api/cdn`; R2 bucket `memegpt-media` + CORS; assets `Cache-Control: max-age=1y immutable`; meme pages `s-maxage=1h + SWR`.

## 5.4 CI/CD (`.github/workflows/` ×9: ci, ci_cd, test, deploy, cron, health_check, trending, weekly_reindex, index)
- PR: lint (ruff/black/flake8/eslint) → backend `pytest` → frontend `build + vitest` → perf/latency bench.
- `main`: auto-deploy Railway + Vercel ×2; hourly trending refresh; weekly Qdrant re-index; 15-min health ping. Secrets in GitHub/Railway/Vercel dashboards (never in repo).

## 5.5 Observability & rollback
- **Monitor:** UptimeRobot `/api/v1/health` (keyword `ok`) + warm ping (cold-start guard); Sentry BE+FE (`SENTRY_DSN`, `sentry-test` route); `/health/stats` (latency histogram, cache-hit %, Qdrant count); Railway metrics + Vercel Analytics + Umami events (search/copy/download/share).
- **Rollback tree:** FE → Vercel promote-previous deployment; BE → Railway redeploy prior commit; DB → migration down script; Qdrant → re-index from `data/processed/` (~30min); R2 → source-of-truth `data/raw/`. Blue-green planned P4.

## 5.6 Security & privacy
5-layer: HTTPS/Cloudflare DDoS → strict CORS + security headers + tiered rate-limit → Pydantic + sanitize (HTML-strip/null-kill/NFKC/2000cap) + JSON-only LLM containment (prompt-injection) → hashed keys (`SHA256`), MD5 query hashes, no PII logs, Prisma-parameterized (no raw SQL), React escaping → env vault + Dependabot + pre-launch secret scan. GDPR: minimization, `privacy.py` purge endpoint, 30-day APScheduler retention (`retention.py`), cookie policy. NSFW: boolean field + search filter + `/flag|queue|review|classify` (CLIP-assisted, human-reviewed).

## 5.7 Testing
- Backend `tests/` 139 pytest (endpoint/AI-pipeline/search-service/schema/security/rate-limit/perf, mocked Qdrant/Redis/Groq, `conftest.py` isolation) + `.coverage` history.
- Frontend Vitest + Testing Library (8 suites) + `vitest.config.ts` + jsdom.
- `locustfile.py` (100 concurrent users, staging 10/2s + `:8089` UI); `test_performance.py` gates P50<1s P95<3s; `evaluate.py` P@3/R@10/NDCG@5 + online 👍CTR/download/copy/zero-result<5% + failure review.

## 5.8 Growth (SEO/ASO/content)
- 10k+ `/meme/[slug]` long-tail (e.g. Drake 8K/mo), `/memes/[category]` hubs (work 12K, monday 8K), weekly LLM auto-blog cron (`generate_weekly_blog_post`), `sitemap.ts` popularity-priority + GSC submit, `robots.ts`, OG 1200×630 + JSON-LD `ImageObject`, `next/image` CWV pass.
- Funnel: SEO 50% / ASO 25% / WoM 15% / content+API 10%, $0. Launch: Product Hunt Tuesday top-5 + Reddit (SideProject/InternetIsBeautiful/webdev/ProgrammerHumor) + HN + Twitter `@memegpt` + demo video. ASO (`docs/ASO_Store_Listing.md` + `16_SEO_Marketing/`): exact titles/subtitles/keyword strings/screenshot storyboards/rating prompts (after 3rd search, max 1/30d, never on error).

## 5.9 Roadmap & risks
- **Done P1 (M1–4):** search, emotion, multiformat, copy/download, trending, feedback, SEO shells, deploys configs.
- **P2 Growth (M5–8):** OAuth verify, API tiers, favorites sync, analytics, moderation — mostly coded, needs live-key verification.
- **P3 Scale:** Expo parity + submit, chat refinement, image search, personalization, i18n.
- **P4 2027:** creation tool, $9 premium, enterprise API, realtime, AI generation.
- **Risks (12-register top):** R3 search quality (mitigate: 1k human curation + weekly evals) · Groq pricing/limits (rule-fallback + cache) · free-tier removals (fallbacks coded) · DMCA (takedown CLI) · cold starts (warm ping) · breach (no-PII design). Full matrix in legacy Risk_Register (deleted; key rows preserved here).
- **Debug ladder:** `/health` → `POST /search` minimal → Qdrant count → threshold 0.45→0.35 → Groq key → embeddings norm≈1.0 → `LOG_LEVEL=DEBUG` → `prisma studio` / sqlite count → `railway logs`.

## 5.10 SLOs & alerts
| SLO | Target | Alert |
|---|---|---|
| Search P95 | <1.5s (7d window) | Page on 15-min breach |
| Search availability | 99.5% (excl. planned) | Page on 5-min 5xx>2% |
| Cache-hit rate | >50% | Warn <40% for 1 h |
| Zero-result rate | <5% | Warn >7% daily |
| CDN image p95 | <200ms | Warn on R2 4xx spike |
| CI main green | 100% (no red merges) | Block merge on red |

## 5.11 Incident playbook (search down)
1. Check `/health` + `/health/stats`: note failing layer (qdrant/redis/llm/db).
2. If Qdrant: confirm fallback engaged (`degraded:true` in responses); restart/recreate collection; re-index from `data/processed/` (~30min/10k).
3. If Groq: confirm rule-fallback (`intent_source:rules`); rotate key; reduce `MAX_TOKENS`.
4. If Redis: flush hot keys? No — fallback is in-memory; restart Upstash endpoint binding.
5. If DB locked (SQLite): check WAL mode + `busy_timeout`; cut to Postgres per §3.6.
6. Post-mortem within 48h: timeline, root cause, fix, regression test added, doc updated here.

## 5.12 Backup & restore
| Layer | Backup | Restore | RTO |
|---|---|---|---|
| Postgres (prod) | Daily auto (7d free / 30d pro) + pre-release `pg_dump` | Point-in-time / dump replay | ~5 min |
| Qdrant | Nightly snapshot API + `data/processed/` source | Recreate + `reindex_all_to_qdrant.py` | ~30 min/10k |
| R2 media | Source-of-truth `data/raw/` + versioned bucket | Re-upload script | ~1 h/10k |
| Redis | Ephemeral (no backup) | Cold rebuild via traffic | N/A |
| Secrets | Vault + sealed per-env copies | Rotate + redeploy | ~15 min |
