# 01 — Architecture Consolidation Gaps

**Source requirements:** `md files/completion_fixes/01_Architecture_Consolidation.md`, `md files/documentation/02_Project_Architecture/*`, `md files/documentation/04_Frontend/Frontend_Overview.md`, `Routing.md`
**Related:** [12-frontend-web-gaps](12-frontend-web-gaps.md) · [20-ci-cd-deployment-gaps](20-ci-cd-deployment-gaps.md) · [06-database-gaps](06-database-gaps.md) · [22-documentation-and-stub-endpoint-gaps](22-documentation-and-stub-endpoint-gaps.md)

> Every gap below was verified by reading the code (no runtime execution). Items marked **ASSUMPTION** need runtime validation.

## Summary
The docs call for **one backend, one main web app, one marketing/SEO site, one mobile app**. The repo actually has **two backends** (`backend/`, `services/api/`), **two user-facing web apps** (`frontend/` Vite, `apps/web/` Next.js), plus a static `frontend/public/landing.html`, **two ORMs/schemas** (SQLAlchemy and Prisma), **three script trees**, **three Dockerfiles** and **two GitHub workflow folders**. This duplication is the root cause of many gaps elsewhere, so fixing it is a **Phase 0** prerequisite.

| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| ARC-01 | Single backend (`completion_fixes/01`) | Incorrectly implemented | `services/api/app/` is a second FastAPI app (5 routers, its own embedding/LLM/rerank, `core/demo_data.py` 388 lines with `DEMO_MEMES` fallback at `services/api/app/services/search_service.py:69-71`). `services/api/Dockerfile:16,23` does `COPY ../../backend/...`, which is outside the build context and can never build | Delete or archive `services/api/`; keep `backend/` as the only API | Critical |
| ARC-02 | Clear frontend ownership (`completion_fixes/01:13,166-167`: Vite = app, Next = marketing/SEO) | Incorrectly implemented | `apps/web/app/(app)/{app,search,trending,library}` duplicate Vite features with weaker implementations; MemeCard, FormatSelector, SuggestionChips, SearchInput, API client and analytics exist twice. `Frontend_Overview.md`/`Routing.md` still describe a single Next.js 14 app | Make a product decision (see the roadmap, decision D-1): either (a) remove `apps/web/(app)/*` and link to the Vite app, or (b) port the Vite features to Next.js and retire `frontend/`. Then update the docs | Critical |
| ARC-03 | One landing page | Needs improvement | `frontend/public/landing.html` (static, `/landing` rewrite in root `vercel.json`) and `apps/web/app/(marketing)/page.tsx` | Keep the Next.js marketing page; delete `landing.html` | Low |
| ARC-04 | One schema source of truth | Incorrectly implemented | `prisma/schema.prisma` (6 models, sqlite) is unused (no `PrismaClient` import anywhere); `prisma/seed.ts:1` imports a missing `../server/` folder. SQLAlchemy in `backend/app/database.py` has 11 tables | Delete `prisma/` or regenerate it from SQLAlchemy (details: [06](06-database-gaps.md) DB-02) | High |
| ARC-05 | One API mount point | Needs improvement | `backend/app/main.py:367-370` mounts `v1_router` at `/api/v1`, `/api`, `/v1` and `/`, roughly 4×342 routes, plus ad-hoc handlers at `main.py:375-444` | Keep `/api/v1` (plus a deprecated `/api` alias with a sunset date); remove the root and `/v1` mounts | Medium |
| ARC-06 | Unique routes | Incorrectly implemented | `collections.py` is registered before `collections_full.py`, so the latter's `GET/POST /collections` are shadowed; `memes.py:169` shadows `download.py:22` | Merge into one router per resource; add a startup assertion that no two routes share a method and path | Medium |
| ARC-07 | One indexing/data pipeline | Needs improvement | `scripts/index_qdrant.py`, `scripts/full_index_pipeline.py`, `backend/scripts/index_to_qdrant.py`, `backend/scripts/reindex_all_to_qdrant.py`, `services/api/scripts/index_qdrant.py` | Pick `scripts/full_index_pipeline.py` (or similar) as canonical and delete the rest (see [07](07-data-corpus-pipeline-gaps.md)) | Medium |
| ARC-08 | Dead shims / duplicate services | Needs improvement | `services/llm.py`, `embedding.py` and `recommendation.py` are `import *` shims; `rag_service.rag_recommend` and `smart_search_service` have no endpoint callers; there are two image services (`image_processing_service.py`, `image_analysis_service.py`) | Delete the shims; merge the image services; delete the unused pipelines | Medium |
| ARC-09 | Stateless horizontal scaling (`02_Project_Architecture/High_Level_Architecture`) | Partially implemented | Chat sessions live in process memory (`chat_refinement_service.py:17 _CHAT_SESSIONS = {}`); embedded Qdrant takes a file lock, which forces `--workers 1` (`railway.toml`) | Store chat sessions in Redis; use remote Qdrant in production | Medium |
| ARC-10 | Single CI and deploy definition | Incorrectly implemented | `.github/workflows/` vs `.github/workflows-upgraded/`; 3 Dockerfiles; 2 `railway.toml`; 3 `vercel.json` | See [20](20-ci-cd-deployment-gaps.md) | Critical |

## Dependencies & considerations
- ARC-02 is a **business decision** that blocks FE, SEO, analytics and the deploy target. Decide first.
- Deleting `services/api` is safe: nothing deploys it (all Docker, Railway and compose files reference `backend/`). Verified by reading the files.
- After consolidation, re-run the test suite. Some tests (e.g. `services/api/tests/*`, which are 9-line stubs) will disappear.

## Verification criteria
- `find . -name main.py -path '*app*'` returns only `backend/app/main.py`.
- OpenAPI shows each path once.
- Only one `.github/workflows` folder, one Dockerfile per service and one `vercel.json` per deployed app.
