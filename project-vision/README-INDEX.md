# MemeGPT — Project Vision (Single Source of Truth)

> **Status:** Production reference. Consolidated from 206 legacy md files (removed) + code audit on 2026-10-14.
> **Code audited:** `backend/app` 148 files · `frontend/src` 62 · `services/api` 29 · `apps` 81 · `backend/tests` 139 · `scripts` 25.
> **Owner:** solo founder + OSS contributors. **Cost envelope:** $0/mo to 10k DAU (all free tiers).

## Map

| File | Covers | Primary reader |
|---|---|---|
| `01-vision-product.md` | Why, who, what, targets, scope, flows | Everyone (start here) |
| `02-architecture-stack.md` | System design, ADRs, data flows, stack, models, costs | Backend / DevOps / new devs |
| `03-backend-ai-data.md` | API contract, AI pipeline, scoring math, DB schema, data pipeline runbook | Backend / ML |
| `04-frontends-mobile.md` | Vite SPA, Next.js SEO site, Expo mobile: routes, components, state, perf/a11y | Frontend / mobile |
| `05-deploy-security-seo.md` | Local/prod runbooks, env matrix, CI/CD, monitoring, rollback, security, testing, growth, roadmap | DevOps / release |

## Quick start (Windows PowerShell)

```powershell
cd D:\memegpt\backend
pip install -r requirements.txt
python seed.py
python -m uvicorn app.main:app --reload --port 8000
# new terminal
cd D:\memegpt\frontend
npm install
npm run dev   # http://localhost:5173
```

## Production topology

```text
Users (web/mobile)
  → Vercel: memegpt.com (Next.js) + app.memegpt.com (Vite SPA)
  → Railway/Render: api.memegpt.com (FastAPI, backend/app/main.py)
  → Qdrant Cloud (vectors) · Supabase PG / SQLite-dev (relations)
    · Upstash Redis (cache + rate limit) · Cloudflare R2 (media CDN)
```

## Definition of done (any change)

1. `pytest -v` (backend) + `npm run build` + `vitest run` (frontend) green.
2. Manual smoke: search → results → preview → copy/download/share → vote → favorites → trending → admin CRUD.
3. No secrets committed (`.env` gitignored); new env vars added to `.env.example` + `05-deploy-security-seo.md`.
4. Docs updated in this folder (not scattered files).

## Ownership & review cadence
| Doc | Owner | Review |
|---|---|---|
| 01 vision/product | Founder | Quarterly or on scope change |
| 02 architecture/stack | Backend lead | On any ADR change |
| 03 backend/ai/data | Backend + ML | Monthly + after pipeline edits |
| 04 frontends/mobile | Frontend + mobile | Monthly + after route/component changes |
| 05 deploy/security/seo | DevOps | Before every release |
| implementation-report/* | Release captain | Re-scored every release; archive old overviews under `implementation-report/history/` (never delete a scored report — append-only history).
