# 03 — Data / Infra / Release Fixes (ship runbook)

## 3.1 Data volume — the #1 gap (145 / 5,000)
| Step | Command / action | Done when |
|---|---|---|
| Imgflip (easiest, templates) | `python backend/scripts/collect_imgflip_full.py` (+ `scrape_imgflip.py`) | Top-100 templates with HQ images stored `data/raw/` |
| Giphy (GIFs) | `python backend/scripts/collect_giphy_full.py` (100 search terms, ≤100 req/hr, backoff on 429) | ~2–5k GIF records + `gif_url` |
| Reddit (relatable) | `python backend/scripts/collect_reddit_full.py` (PRAW, r/memes+dankmemes, `.gifv→.gif` normalize) | ~2–5k posts + `ocr_text` source |
| Clean | `python scripts/preprocess_memes.py` (NSFW skip, 5KB–10MB, pHash dedup) | `data/processed/memes.json` ≥5000 unique |
| Enrich | `python backend/generate_embeddings.py` (BLIP + OCR + MiniLM + CLIP, batch 50) | `embeddings.json` count == memes count |
| Index | `python backend/scripts/reindex_all_to_qdrant.py` | `get_collection_info().points_count` ≥5000 |
| Host | `python backend/scripts/upload_to_r2*.py` + `generate_thumbnails*.py` | Spot-check 20 URLs: 200 + `<200ms` + WebP thumbs |
| Seed | `python backend/seed.py` (+ `seed_extended.py` / `build_huge_dataset.py`) | `GET /api/v1/stats` meme count ≥5000 |
| Quality | `python evaluate.py` + `backend/scripts/evaluate.py` (P@3/R@10/NDCG@5) | P@5>0.70, zero-result<5%; add `golden_queries.json` CI gate |

## 3.2 Deploy runbook
- [ ] **Railway BE:** `railway login && railway init && railway up` + Postgres (+Redis) plugins → all env vars → `APP_ENV=production` → custom domain `api.memegpt.com` → deploy `backend/Dockerfile` → `curl https://api.memegpt.com/api/v1/health` ok → `POST /search` <1.5s → `railway logs` clean.
- [ ] **Vercel Vite:** `VITE_API_URL=https://api.memegpt.com` → deploy `frontend/` → `app.*` → smoke §3.4.
- [ ] **Vercel Next:** `NEXT_PUBLIC_API_URL` → deploy `apps/web/` → `memegpt.com` → sitemap + OG checks (§02).
- [ ] **R2/CDN:** bucket `memegpt-media` + token + CORS → upload → `CDN_BASE_URL` → 20-URL spot check → `Cache-Control: max-age=1y immutable`.
- [ ] **DNS:** Cloudflare CNAME `memegpt`/`api`/`cdn` → `curl -I` 200 + SSL valid.
- [ ] **DB cutover:** `migrate_sqlite_to_postgres.py` → Prisma migrate → reseed → verify counts match.

## 3.3 Observability
- [ ] UptimeRobot: `/api/v1/health` keyword `ok` every 15 min + warm ping every 10 min (cold-start guard).
- [ ] Sentry BE+FE with `SENTRY_DSN` (test via `/health/sentry-test` + FE button); alert to email.
- [ ] Dashboard: `/api/v1/stats` + Umami events (search/copy/download/share/signup) reviewed weekly; latency histogram P50/P95 + cache-hit% + Qdrant count in release notes.

## 3.4 Release gate (all must pass, none committed/pushed until you approve)
- [ ] `cd backend && python -m pytest tests/ -v` green (139 files).
- [ ] `cd frontend && npm run build && npx vitest run` green.
- [ ] `cd apps/web && npm run build` green.
- [ ] Live smoke: search 5 queries (EN + Hindi Hinglish) → results relevant → copy works → download saves bytes → vote persists → favorites survive reload → trending loads → admin add+delete meme → export TXT/JSON/MD downloads.
- [ ] Perf: 5 searches P50<1s/P95<3s on prod; CDN images <200ms; Locust staging 100u no 5xx.
- [ ] SEO/legal: GSC sitemap submitted; OG card renders; `/privacy` + GDPR delete verified; DMCA CLI documented (`privacy.py` + takedown script).

## Ship timeline (solo, 10–12 working days)
| Days | Focus | Exit criteria |
|---|---|---|
| 1–2 | B1–B3 env + compose + Qdrant live | Health ok, cache-hit proven, 429 proven |
| 3–5 | Data volume to 5k + R2 + thumbs | Counts ≥5000, 20-URL check green |
| 6 | B4–B6 images + auth + moderation | Round-trips recorded |
| 7–8 | Frontend acceptance + Next OG/SEO | Checklists ticked |
| 9–10 | Mobile LAN + EAS build + CI green | Builds green, submit filed |
| 11–12 | Release gate + buffer | Gate §3.4 all ticked; store review pending is the only open item |
