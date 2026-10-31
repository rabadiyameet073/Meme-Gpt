# MemeGPT — Roadmap vs. Reality Gap Analysis

**Date:** 2026-10-31
**Supersedes:** `GAP-ANALYSIS-2026-10-30.md` (predates remediation rounds t01–t15; its 80/64/96 tally is stale)
**Baseline audit:** `AUDIT-REPORT-2026-10-30.md` (125 items → 62 fully / 49 partial / 14 not)
**Documentation corpus audited:** `md files/` — **206 Markdown files, 43,638 lines, 332 acceptance checkboxes**

---

## 1. Executive summary

MemeGPT is **green on engineering hygiene and red on product substance.**

| Dimension | Status | Evidence |
|---|---|---|
| Test suite | ✅ Green | `713 passed`, exit 0 (112 s); frontend 38/38; Next.js build 13/13 static pages |
| AI retrieval | ✅ Genuinely functional | Embedded Qdrant, 179 points, real ANN over MiniLM embeddings; top-1 verified at 0.54–0.64 cosine |
| Code volume | ✅ Large | 339 declared API routes across 35 modules; 139 backend test modules |
| Corpus size | ❌ 3.9 % of target | **195 memes** vs 5,000 target |
| Media pipeline | ❌ Never executed | `data/raw`, `data/processed`, `data/embeddings` contain only `.gitkeep` |
| Deployment | ❌ Not deployed | All 8 cloud credentials empty in `.env` |
| Mobile app | ❌ Unbuildable | `app.json` references 4 assets; `assets/` contains only `.gitkeep` |
| Documentation truthfulness | ❌ Broken | Master checklist claims **15/15 guides complete**; those same guides carry **96 unticked acceptance boxes, 0 ticked** |

**Headline number:** of 332 documented acceptance checkboxes across `md files/`, **17 are ticked (5.1 %)** — and every one of those 17 lives in `documentation/` or `basic things of project/`, not in the three implementation tracks that claim completion.

**The single most important finding:** `md files/completion_fixes/00_MASTER_FIX_CHECKLIST.md` marks all 15 fix guides `[x]`. The guides themselves contain 96 acceptance checkboxes with **zero** ticked. Both statements cannot be true. The checklist is an aspiration, not a status report — and it has been read as a status report.

---

## 2. Method

1. Read the baseline audit and the three master checklists (`completion_fixes/00`, `implementation_guides/00`, `upgraded_docs/00_INDEX`).
2. Re-derived the checkbox census programmatically across all 206 files (not trusting the prior document).
3. Verified each guide's claims against the live codebase, database, filesystem, and build/test output — never against another document.
4. Re-adjudicated all 16 audit defect IDs (D-1…D-12, S-1…S-4).
5. Recorded defects discovered during this pass that the original audit did not catch (§7).

Verification was read-only apart from this document.

---

## 3. Requirement inventory (recomputed)

```
track                                            [x]     [ ]   files    lines
documentation                                     10     117     151    21334
upgraded_docs                                      0      10      18     6693
completion_fixes                                   0      96      16     5103
basic things of project upgraded version (v2)      0      36       5     3766
implementation_guides                              0      40      10     3608
basic things of project                            7      16       5     2666
prompt.md                                          0       0       1      468
TOTAL                                             17     315     206    43638
```

Note: `completion_fixes/00` carries its completion claims as an **inline** `` `[x]` `` column inside a table (`15` occurrences), which is invisible to checkbox parsers — and therefore invisible to anyone or anything auditing the folder mechanically. The 96 real checkboxes in the 15 guides below it remain unticked.

---

## 4. Track A — `completion_fixes/` (15 guides)

| # | Guide | Checklist says | Reality | Verdict |
|---|---|---|---|---|
| 01 | Architecture Consolidation | `[x]` | `services/api/` **still present** — 26 files: own `Dockerfile`, `requirements.txt`, 5 routers, 3 models, 6 services, 5 scripts, 3 test modules | ❌ **NOT DONE** |
| 02 | Meme Database Population | `[x]` | 195 memes (145 `master_catalog` + 50 `manual`) vs 5,000 target = **3.9 %** | ❌ **NOT DONE** |
| 03 | BLIP + CLIP Image Pipeline | `[x]` | Services exist (`image_analysis_service`, `image_processing_service`, `nsfw_service`) but index was built with `--skip-images`; `data/raw` empty → **no image ever processed** | ⚠️ **CODE ONLY** |
| 04 | User Auth & OAuth | `[x]` | `auth.py`: `google/login|callback`, `github/login|callback`, `register`, `login`, `refresh`, `logout`, `me`; DB-backed tier + admin RBAC | ✅ **DONE** |
| 05 | Content Moderation & NSFW | `[x]` | `queue`/`review`/`classify` all `Depends(require_admin)`; `flag` rate-limited. **But Qdrant payload has no `moderation_status`** → see N-1 | ⚠️ **PARTIAL** |
| 06 | Mobile App Completion | `[x]` | `assets/` = `.gitkeep` only, while `app.json` references `icon.png`, `splash.png`, `adaptive-icon.png`, `favicon.png` → **EAS build fails**; `useOfflineCache`/`usePushNotifications` never invoked; `eas.json` submit has `your@email.com` / `YOUR_APP_ID` | ❌ **NOT DONE** |
| 07 | Next.js Web App Completion | `[x]` | `blog/[slug]`, `features`, `download`, `meme/[slug]`, `memes/[category]`, `robots.ts`, `sitemap.ts`, `og-image.jpg`, ImageObject JSON-LD all present. Missing `generateStaticParams` (D-12) | ⚠️ **MOSTLY** |
| 08 | Production Deployment | `[x]` | 8 cloud credentials empty; `CDN_BASE_URL=http://localhost:8000/static` but **`backend/static` does not exist**; two `railway.toml` disagree on healthcheck path | ❌ **NOT DONE** |
| 09 | SEO & Marketing | `[x]` | `robots.ts`, `sitemap.ts`, `api/v1/sitemap.py`, `aso_service` present. The "10,000 static pages" premise needs 10,000 memes; there are 195 | ⚠️ **PARTIAL** |
| 10 | Frontend Library Upgrades | `[x]` | `zustand ^5.0.3`, `@tanstack/react-query ^5.67.2`, `react-hook-form ^7.54.2` in `frontend/package.json`; plus `Sidebar`, `ThemeToggle`, `SkeletonCard`, `sw.js`, `manifest.json` | ✅ **DONE** |
| 11 | Accessibility & A11y | `[x]` | `scripts/backfill_alt_text.py` exists; 145/195 memes have `alt_text` (74 %); ARIA present in components. No axe/CI gate | ⚠️ **PARTIAL** |
| 12 | Missing API Endpoints | `[x]` | `/memes/{slug}/download`, `users/me` GET+PUT, `users/me/preferences` GET+PUT, `developer/usage`, `developer/status` all present. **No backend blog API** (blog is static in `apps/web`) | ⚠️ **PARTIAL** |
| 13 | Monitoring & Analytics | `[x]` | `core/monitoring.py` (backend) + `@sentry` (frontend) + `lib/analytics.ts` + `email_service` (Resend) wired. **`SENTRY_DSN` empty** → no events ever leave the process | ⚠️ **PARTIAL** |
| 14 | Testing & CI Gaps | `[x]` | 713 backend tests, 38 frontend tests, `benchmark_latency.py`, `evaluate_ai_search.py`, `data/eval/{golden,test}_queries.json`. **No `.coveragerc`/`codecov.yml`/coverage artifact**; no E2E; 4 overlapping CI workflows | ⚠️ **PARTIAL** |
| 15 | Non-Functional Requirements | `[x]` | No i18n (`*i18n*` → 0 hits). No retraining job (`backend/app/jobs/` = `retention.py` only). GDPR service + retention job **do** exist | ❌ **MOSTLY MISSING** |

**Track A score: 3 ✅ / 8 ⚠️ / 4 ❌** — against a checklist declaring 15/15 complete.

---

## 5. Track B — `upgraded_docs/` (17 guides)

| # | Guide | Reality | Verdict |
|---|---|---|---|
| 01 | Environment Setup | `GROQ_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `REDIS_URL`, `UPSTASH_REDIS_REST_URL`, `R2_ACCESS_KEY`, `GIPHY_API_KEY`, `SENTRY_DSN` — **all empty** | ❌ |
| 02 | Database Schema Migration | Live SQLite: `memes` **31 cols**, `users` **19 cols**, 10 tables incl. `meme_flags`, `favourite_memes`, `saved_memes`, `search_logs`, `api_keys`. Target met. **But `prisma/schema.prisma` has 6 models and is imported nowhere** (N-8) | ✅ / ⚠️ split |
| 03 | Qdrant Vector Search | Embedded client live at `backend/qdrant_storage`; **179 points**; ANN verified (0.54–0.64). Index stale vs 195 DB rows; text vector only | ✅ / ⚠️ |
| 04 | Redis Cache | `core/cache.py` implements redis-py **and** Upstash REST with graceful fallback. `REDIS_URL` empty → in-memory dict, lost on restart | ⚠️ |
| 05 | AI Pipeline Fix | `_cosine_similarity` correct; `_raw_vector_query` supports both `query_points` and legacy `search`; threshold cascade 0.35→0.2 implemented | ✅ |
| 06 | Meme Indexing Pipeline | "Download → OCR → BLIP → CLIP → Qdrant" — only the Qdrant leg ran, and only the text vector | ⚠️ |
| 07 | Missing API Routes | `/categories`, `/stats`, `/admin/memes`, `/favorites`, `/collections*` all registered | ✅ |
| 08 | Auth Middleware Fix | `lookup_api_key_tier(raw, db)` queries the `api_keys` table; no string matching | ✅ |
| 09 | CDN / R2 Setup | No bucket, no credentials, no `backend/static`; **15 memes hardcode `https://cdn.memegpt.com/...`** (N-2); **35 memes have NULL `image_url`** (N-3) | ❌ |
| 10 | Frontend Missing Features | ThemeToggle, Sidebar, Skeleton, PWA, search history all present | ✅ |
| 11 | Mobile App Completion | Share sheet / media-library / haptics dependencies installed; hooks unwired; assets absent; submit config placeholder | ❌ |
| 12 | Security Fixes | `nsfw` column, `data_privacy_service`, `jobs/retention.py`, `SECRET_KEY` 64 chars. **`config.py:104` still ships a default fallback secret and only warns** (N-9) | ⚠️ |
| 13 | SEO & Sitemap | `robots.ts`, `sitemap.ts`, `api/v1/sitemap.py`, per-meme JSON-LD, `og-image.jpg` all present | ✅ |
| 14 | Testing Suite | pytest + Vitest green; AI eval datasets present. No coverage measurement, no eval gate in CI | ⚠️ |
| 15 | Seed Data Expansion | 195 vs 5,000; the seeder **synthesises** `cdn.memegpt.com` URLs instead of resolving real media | ❌ |
| 16 | CI/CD Deployment | 9 workflows present; nothing deployed | ⚠️ |
| 17 | Landing Page | `frontend/public/landing.html` + `/landing` route (+ Vercel rewrite) | ✅ |

**Track B score: 6 ✅ / 6 ⚠️ / 5 ❌** against a `00_INDEX.md` Definition of Done with 10 unchecked boxes.

---

## 6. Track C — `implementation_guides/` (9 guides)

| # | Guide | Blocker | Reality | Verdict |
|---|---|---|---|---|
| 01 | Qdrant Setup & Indexing | BLOCKER 1 | Embedded local Qdrant works; **no cloud cluster** (`QDRANT_URL` empty). 179/195 indexed | ⚠️ **50 %** |
| 02 | Redis / Upstash | BLOCKER 3 | Code complete, not connected | ❌ |
| 03 | Cloudflare R2 + thumbnails | BLOCKER 4 | Nothing configured; `generate_thumbnails*.py` never run | ❌ |
| 04 | Meme Data Pipeline (50K+) | BLOCKER 2 | 195 memes; `data/raw` empty | ❌ **0.4 %** |
| 05 | Mobile App Completion | — | Unbuildable (§4 #06) | ❌ |
| 06 | Deployment Railway + Vercel | — | Config files present; never deployed; configs mutually inconsistent (N-7) | ❌ |
| 07 | CI/CD GitHub Actions | — | Workflows present but `ci.yml`, `ci_cd.yml`, `test.yml`, `deploy.yml` overlap (N-10) | ⚠️ |
| 08 | Monitoring Sentry | — | Code wired, `SENTRY_DSN` empty; no UptimeRobot config committed | ⚠️ |
| 09 | Environment Variables Final | — | 8 of 8 cloud keys empty | ❌ |

**Track C Definition of Done (23 boxes): 4 satisfied, 5 partial, 14 unsatisfied.**

---

## 7. Defect re-audit — D-1…D-12, S-1…S-4

| ID | Original finding | Current state | Verdict |
|---|---|---|---|
| **D-1** | Seeder discards `memes.json` on `KeyError: 'category'` → 62 instead of 145 | Seeder now maps `categories`/`image_url`/`gif_url`; DB holds **145 `master_catalog` rows** (exactly the expected count). `except Exception` still swallows (lines 619/661/805) | ✅ **FIXED** (residual: silent excepts) |
| **D-2** | Root `railway.toml` does `cd backend` inside a backend-rooted image | `startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2"` — no `cd` | ✅ **FIXED** |
| **D-3** | `ci.yml` runs non-existent root `npm run lint`/`build` | `ci.yml` + `test.yml` use `working-directory: backend` and `APP_ENV: test` | ✅ **FIXED** |
| **D-4** | `prisma/seed.ts` imports non-existent `../server/*` | Still `import { prisma } from "../server/src/lib/database/prisma.js"` | ❌ **OPEN** |
| **D-5** | Mobile `assets/` empty while `app.json` references icon/splash | `apps/mobile/assets/` = `.gitkeep` **only** | ❌ **OPEN** |
| **D-6** | 9 tests hardcode `d:/Meme GPT/...` | Zero live matches; only a docstring in `tests/paths.py` explaining the fix | ✅ **FIXED** |
| **D-7** | Prisma schema covers 6 of 10 models | Still 6: `Meme`, `MemeVote`, `MemeUsage`, `Feedback`, `SavedMeme`, `SearchLog`. No `User`, `ApiKey`, `MemeFlag` | ❌ **OPEN** |
| **D-8** | Chat tab single-shot; `/chat/refine` orphaned | `ChatTab.tsx` calls `api.refineChat(q, sessionId, …)` and `api.resetChat(sessionId)` | ✅ **FIXED** |
| **D-9** | Collections UI localStorage-only; 18 endpoints orphaned | `FavoritesTab.tsx` calls `api.favorites`, `api.listCollections`, `api.createCollection`, `api.deleteCollection` | ✅ **FIXED** |
| **D-10** | Offline cache + push hooks unused by screens | `useOfflineCache` and `usePushNotifications` defined; **only** reference is a *type-only* import in `MemeCard.tsx:13` | ❌ **OPEN** |
| **D-11** | Unpinned `fastapi>=0.111` breaks internal route verifier | Verifier fixed (`_iter_registered_paths` recurses `_IncludedRouter`). `requirements.txt` still `fastapi>=0.111.0,<1.0.0`, `uvicorn>=0.30.0,<1.0.0`, `pydantic>=2.7.0,<3.0.0` | ⚠️ **HALF** |
| **D-12** | `/meme/[slug]` renders dynamically, not SSG | No `generateStaticParams` in `apps/web/app/meme/[slug]/page.tsx` | ❌ **OPEN** |
| **S-1** | `_STATIC_DEV_KEYS` grants admin from a hardcoded key, always active | `_load_bootstrap_keys()` gated on `_DEV_ENVIRONMENTS`; keys sourced from env only | ✅ **FIXED** |
| **S-2** | Moderation endpoints unauthenticated | `queue`, `review`, `classify` all `Depends(require_admin)`; `flag` rate-limited | ✅ **FIXED** |
| **S-3** | `.env.example` contains a real `SECRET_KEY` | `SECRET_KEY=changeme_generate_with_secrets_token_hex_32` | ✅ **FIXED** |
| **S-4** | `GET /admin/memes` uses `get_api_tier` | `AuthContext = Depends(require_admin)` | ✅ **FIXED** |

**Result: 9 fixed, 1 half-fixed, 6 open** (D-4, D-5, D-7, D-10, D-12 + D-11 partial).

---

## 8. New defects discovered in this pass

Not in the original audit. All verified against live code/data.

### N-1 — Qdrant payload lacks `moderation_status` *(P1, correctness)*
`search_service.build_point()` (lines 297–317) emits `meme_id, name, slug, categories, emotions, keywords, dialogue, explanation, image_url, gif_url, mp4_url, thumb_url, webp_url, has_gif, has_video, nsfw, popularity_score, viral_score, source`. There is **no `moderation_status`**, so `build_search_filter()` cannot express "exclude removed memes". The DB-fallback path *does* filter (`_db_fallback_search` → `MemeModel.moderation_status != "removed"`), so **the two retrieval paths disagree about whether moderated content is visible.** Any meme removed after indexing stays ANN-retrievable until a full reindex.

### N-2 — 15 memes point at a CDN that does not exist *(P1)*
`scripts/seed_master_catalog.py:657–658` synthesises `https://cdn.memegpt.com/images/{name}.jpg`. `cdn.memegpt.com` is not configured, `R2_ACCESS_KEY`/`R2_SECRET_KEY` are empty, and `backend/static` (the configured `CDN_BASE_URL` target) does not exist. These 15 images are guaranteed 404s.

### N-3 — 35 / 195 memes have no image at all *(P2)*
`image_url IS NULL or ''` → 35. The `upgraded_docs/00_INDEX.md` DoD line "Meme images load from real CDN URLs (not NULL)" is false for 18 % of the corpus.

### N-4 — `indexed_at` is never written *(P2)*
`SELECT count(*) FROM memes WHERE indexed_at IS NOT NULL` → **0**, while Qdrant holds 179 points. Index bookkeeping is dead metadata; there is no way to answer "which memes are unindexed?" without cross-querying Qdrant.

### N-5 — Three divergent corpus counts *(P1, integrity)*
`backend/memegpt.db` = **195** · `backend/data/embeddings.json` = **142** · `backend/qdrant_storage` = **179**. No single source of truth. `requirements.txt` declares `qdrant-client` but it was **not installed locally**, meaning every search silently degraded to the in-process fallback until it was installed during remediation.

### N-6 — 70 % of the API surface is documentation, not product *(P0, architectural)*
Of 339 declared routes across 35 modules, only **16 modules touch the database**. Documentation-serving modules (`deployment` 43, `marketing` 35, `testing` 24, `development` 19, `appendix` 18, `project_management` 18, `security` 15, `troubleshooting` 15, `references` 14, `mobile` 11, `faq` 9, `validation` 7, `rate_limiting` 6, `features` 3, `developer` 2) total **~239 endpoints** that return hardcoded narrative JSON describing the project to itself. `deployment.py` serves `/manifest`, `/posture`, `/ci-cd/practices`; `testing.py` serves `/coverage-targets`, `/inventory`. **56 of 139 test modules (40 %) test these services.** This is why 713 tests pass while the product ships 195 memes.

### N-7 — 91 hardcoded green attestations *(P0, integrity)*
Across 16 service modules: **16 × `"passed": True`**, **17 × `"verified": True`**, **58 × `"status": "COMPLETED"/"VERIFIED"`**. Examples:
- `deployment_overview_service.py:201–210` — 8-item pre-deploy security checklist, all `"VERIFIED"/True`, including **"Single worker in production (--workers 1 for memory safety)"** while both `railway.toml` files use `--workers 2`.
- `security_overview_service.py:208–221` — 12 items all `"COMPLETED", verified: True`, including **"Dependency scanning configured"** while no `dependabot.yml`, `.pre-commit-config.yaml`, `codeql.yml`, pip-audit, safety, or bandit exists anywhere in the repo.

### N-8 — `prisma/` is dead code *(P2)*
6 models, seed imports a non-existent `../server/*` path, and **`@prisma/client` is imported nowhere in `apps/web`** — the Next.js app reads the REST API instead. There is no working path to the Postgres mirror the deployment docs describe.

### N-9 — Insecure default secret fallback *(P2, security)*
`config.py:104`: `SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_in_production_memegpt_2026")`. Lines 109–111 log a warning when the value is short or `changeme` but **never raise**. A misconfigured deployment boots with a publicly known JWT signing key.

### N-10 — Overlapping CI workflows *(P3)*
`ci.yml`, `ci_cd.yml`, `test.yml`, `deploy.yml`, plus `index.yml`, `cron.yml`, `trending.yml`, `weekly_reindex.yml`, `health_check.yml`. Four of these arbitrate "run the tests"; duplication invites drift and wasted minutes.

### N-11 — Image and combined vectors are empty *(P1)*
The index was built with `--skip-images`. `COLLECTION_NAME` declares three named vectors — `text:384`, `image:512`, `combined:896` — but only `text` has data. `format_pref="gif"/"video"` filtering works (payload fields), but image-similarity and combined retrieval are non-functional despite being advertised.

### N-12 — Sitemap degrades silently to zero meme pages *(P3, SEO)*
`apps/web/app/sitemap.ts:41–43` catches every fetch error and returns `memePages = []`. If the API is unreachable during a Vercel build, the site publishes a sitemap containing only static routes — with no warning and no non-zero exit.

---

## 9. Prioritized action plan

Ordered by "unblocks the most declared intent per day". Effort is solo-developer estimate.

### P0 — Stop the documentation from lying, and make the product real (≈6 days)

| # | Action | Files | Effort | Why first |
|---|---|---|---|---|
| P0-1 | Replace the hardcoded attestations with live probes. `deployment_overview_service` / `security_overview_service` must **compute** each item (read `railway.toml`, glob for `dependabot.yml`, call `shutil.which('bandit')`), and report `"status": "UNVERIFIABLE"` when it cannot prove a thing | `backend/app/services/{deployment_overview,security_overview,ci_cd,data_privacy}_service.py` | 1.5 d | 91 false greens currently mislead every downstream reader, including audits |
| P0-2 | Fix `--workers 1` **or** the attestation. Decide the memory story, then make `railway.toml` ×2 agree on both workers and healthcheck path (`/health` exists; `/api/v1/health` exists; pick one) | `railway.toml`, `backend/railway.toml` | 0.25 d | Two configs that disagree will eventually be deployed in the wrong one |
| P0-3 | Add `moderation_status` to `build_point()` payload **and** to `build_search_filter()` as a `must_not: removed` condition; reindex | `backend/app/services/search_service.py` | 0.5 d | Removed content is currently retrievable — a live correctness + safety bug |
| P0-4 | Make the corpus real: run the collectors to ≥5,000 memes, resolve true `image_url` for all of them, delete the `cdn.memegpt.com` synthesis, and set `indexed_at` on every upserted row | `scripts/seed_master_catalog.py` (657–658), `backend/app/api/v1/memes.py`, indexer | 2 d + overnight run | Every downstream claim (SEO 10k pages, "10 memes per search", CDN) is gated on this |
| P0-5 | Reconcile the corpus counts: make `embeddings.json` a derived cache with a hash guard, not a parallel store; add a `--verify` mode that fails when DB ≠ Qdrant | `backend/generate_embeddings.py`, `backend/scripts/index_to_qdrant.py` | 0.75 d | Silent drift is why "179 indexed" and "195 memes" coexisted unnoticed |
| P0-6 | Reset the completion_fixes checklist to reality: untick all 15, and convert the index column from `` `[x]` `` to a status field derived from the guides' own 96 boxes | `md files/completion_fixes/00_MASTER_FIX_CHECKLIST.md` | 0.25 d | A roadmap that reports 100 % when the body says 0 % is worse than no roadmap |

### P1 — Close the open defects that break builds or guarantees (≈4.5 days)

| # | Action | Files | Effort |
|---|---|---|---|
| P1-1 | **D-5** — generate `icon.png` 1024², `adaptive-icon.png` 1024², `splash.png` 1284×2778, `favicon.png` 48² into `apps/mobile/assets/`; verify `expo prebuild` | `apps/mobile/assets/*` | 0.5 d |
| P1-2 | **D-10** — call `useOfflineCache` in `(tabs)/index.tsx` + `(tabs)/library.tsx`, `usePushNotifications` in `app/_layout.tsx`; register `expo-notifications` plugin + `projectId` in `app.json` | `apps/mobile/**` | 1 d |
| P1-3 | **N-2/N-3** — replace 15 synthetic and 35 NULL `image_url`s; only after R2 exists (P1-5) | `scripts/seed_master_catalog.py`, DB migration | 0.5 d |
| P1-4 | **D-4/D-7/N-8** — either delete `prisma/` or regenerate `schema.prisma` from the live schema (add `User`, `ApiKey`, `MemeFlag`, `FavouriteMeme`; fix `seed.ts` to read `backend/data/memes.json`). Deleting is the cheaper correct answer today | `prisma/*` | 0.5 d |
| P1-5 | Provision R2: bucket, credentials, `CDN_BASE_URL`, run `upload_to_r2.py` + `generate_thumbnails_full.py`, create `backend/static` **or** repoint `CDN_BASE_URL` | `.env`, `scripts/upload_to_r2.py`, `backend/static/` | 1 d |
| P1-6 | **N-11** — run the indexer **without** `--skip-images` once BLIP/CLIP can run on CPU, so the `image`/`combined` vectors exist; or delete those vectors from the collection definition and stop advertising them | `scripts/full_index_pipeline.py`, `search_service.py` | 0.5 d |
| P1-7 | **N-9** — raise instead of warn when `SECRET_KEY` is the default/short, unless `APP_ENV in {"test","development"}` | `backend/app/config.py:104–111` | 0.1 d |

### P2 — Deployment and operational truth (≈4 days, needs credentials)

| # | Action | Effort |
|---|---|---|
| P2-1 | Fill the 8 cloud keys (§5 #01). Until then, every "deployed" claim is aspirational | 0.5 d |
| P2-2 | Deploy backend → Railway, frontend → Vercel, `apps/web` → Vercel; verify `healthcheckPath` responds from outside | 0.5 d |
| P2-3 | **D-12** — `generateStaticParams()` on `/meme/[slug]` + `dynamicParams = true`, then re-measure TTFB | 0.5 d |
| P2-4 | **N-12** — make `sitemap.ts` fail the build (or log loudly + emit a `/sitemap-health` marker) when the meme fetch fails | 0.1 d |
| P2-5 | **D-11 residual** — pin exact versions (`fastapi==0.115.x` etc.) or adopt `pip-compile` lockfiles | 0.5 d |
| P2-6 | **N-10** — collapse `ci.yml` / `ci_cd.yml` / `test.yml` / `deploy.yml` into `ci.yml` + `deploy.yml` with `paths` filters | 0.5 d |
| P2-7 | Redis: set `REDIS_URL` and assert cache survives a restart (the entire point of BLOCKER 3) | 0.25 d |
| P2-8 | Sentry: set `SENTRY_DSN`, fire `/health/sentry-error`, confirm the event lands | 0.25 d |

### P3 — Architectural debt with the highest long-term cost (≈4 days)

| # | Action | Effort |
|---|---|---|
| P3-1 | **N-6** — retire the documentation-serving API surface. Move `appendix`, `deployment`, `development`, `faq`, `features`, `marketing`, `mobile`, `project_management`, `rate_limiting`, `references`, `security`, `testing`, `troubleshooting`, `validation` endpoints out of the shipped OpenAPI (a `DOCS_ENABLED` flag, default off in production), and move their 56 test modules to a `tests/docs/` tier that does not inflate the product coverage signal | 2 d |
| P3-2 | **Track A #01** — delete `services/api/` after diffing it against `backend/` for any unique asset (its `scripts/download_datasets.py` etc. are referenced by older docs) | 0.5 d |
| P3-3 | **Track A #15** — add i18n (`next-intl` for `apps/web`, `react-i18next` for `frontend`) and a `jobs/retrain.py` stub with a documented cadence, or delete those requirements from the docs | 1 d |
| P3-4 | **Track A #14** — add `pytest-cov` + `coverage.json` artifact + E2E (`playwright` against `frontend` + `apps/web`) with a threshold gate | 0.5 d |

### P4 — Verify, don't assert (≈1 day)

| # | Action |
|---|---|
| P4-1 | Add `tests/test_docs_truthfulness.py`: for every numeric claim the master checklists make (meme count, worker count, coverage, deployed URLs, asset existence), assert the codebase value. A checklist that cannot fail is not a checklist |
| P4-2 | Add `scripts/verify_readiness.py` that exits non-zero unless: memes ≥ target, `indexed_at` ≈ indexed points, 0 NULL `image_url`, `SENTRY_DSN` set, `REDIS_URL` set, `QDRANT_URL` set, assets present |
| P4-3 | Re-run this gap analysis against the resulting state and re-tick the 332 boxes from evidence |

---

## 10. Dependency graph for the plan

```
P0-4 corpus (5,000 memes + real images)
   ├──▶ P1-3 fix image_urls ──▶ P1-5 R2/CDN ──▶ P2-2 deploy
   ├──▶ P1-6 image vectors ──▶ P0-5 count reconciliation
   └──▶ Track A #09 SEO 10k pages ──▶ P2-3 SSG

P0-1 live attestations ──▶ P4-1 docs-truthfulness tests ──▶ P4-3 re-tick boxes
P0-3 moderation in payload ──▶ P0-5 reindex consistency
P1-1 assets ──▶ P1-2 mobile hooks ──▶ Track A #06 store submission
```

**Three gating decisions, needed before P0-4:**

1. **Single worker or two?** `--workers 2` with a 384-d MiniLM plus CLIP resident may exceed a small Railway instance. Decide, then make `railway.toml` and `deployment_overview_service` say the same thing.
2. **Prisma or delete?** Nothing imports it. Deleting removes D-4 and D-7 outright and shrinks the surface by 2 defect IDs.
3. **Is the documentation-API surface a product feature?** If yes, say so and stop counting it as coverage. If no, gate it behind `DOCS_ENABLED=false` (P3-1) and the 40 % test-overhead disappears with it.

---

## 11. What is genuinely done — do not regress it

Confirmed working, verified this pass:

- **Real vector retrieval.** Embedded Qdrant, 179 points, real MiniLM embeddings, both `qdrant-client` API generations supported, threshold cascade, semantic fallback that does not silently sort by popularity.
- **CORS correctness.** Additive canonical+configured origins (a bug that made every browser preflight 400 in development).
- **API-key auth.** DB-backed tier lookup, `require_admin` RBAC, OAuth for Google and GitHub, JWT access/refresh.
- **Test + build hygiene.** 713 backend tests, 38 frontend tests, `npm run build` for both frontends — all green, exit 0.
- **CI correctness.** Backend-scoped `working-directory`, `APP_ENV=test`, index workflow pointing at scripts that actually exist.
- **DB schema.** 31-column `memes`, 19-column `users`, 10 tables — richer than the docs demand.
- **Frontend completeness.** zustand / TanStack Query / RHF; ThemeToggle, Sidebar, Skeletons, PWA `sw.js` + `manifest.json`, search history, collections and chat-refine wired to the backend.
- **Shutdown correctness.** `reset_qdrant_client()` in lifespan plus both indexer entrypoints — the `QdrantClient.__del__ → ImportError: sys.meta_path is None` fatal teardown is gone.

---

## 12. Verification commands

```powershell
# test + build truth
cd backend; python -m pytest tests/ -q
cd ..; npm run build            # frontend (vite)
cd apps/web; npm run build      # next

# corpus / index truth
@'
import sqlite3; c = sqlite3.connect("backend/memegpt.db")
print("memes", c.execute("select count(*) from memes").fetchone()[0])
print("indexed_at", c.execute("select count(*) from memes where indexed_at is not null").fetchone()[0])
print("null image", c.execute("select count(*) from memes where image_url is null or image_url=''").fetchone()[0])
'@ | python -
cd backend; python scripts/index_to_qdrant.py --skip-images    # prints upserts + backend

# attestation census
@'
import os,re; tot=0
for f in os.listdir("app/services"):
    s=open("app/services/"+f,encoding="utf-8").read()
    tot+=len(re.findall(r'"passed"\s*:\s*True',s))+len(re.findall(r'"verified"\s*:\s*True',s))
print("hardcoded greens:", tot)
'@ | python -

# mobile build blocker
Get-ChildItem apps/mobile/assets -Force     # expect only .gitkeep today
```

---

*Companion to `AUDIT-REPORT-2026-10-30.md`. Where this document and any checklist disagree, this document wins — every claim above was read from code, a database row, a filesystem listing, or a build log on 2026-10-31.*
