# MemeGPT — Gap Analysis: Roadmap vs Implementation

**Date:** 2026-10-30
**Baseline:** [`AUDIT-REPORT-2026-10-30.md`](file:///d:/memegpt/AUDIT-REPORT-2026-10-30.md) (commit `34d9c62`)
**Scope:** all 206 Markdown files in `md files/` (34,767 lines, 1,392 KB) — `completion_fixes`, `implementation_guides`, `upgraded_docs`, `documentation`, `basic things of project` (v1 + v2)
**Method:** mechanical extraction of every checkbox in the corpus, then each item resolved against the audit baseline and re-verified in code where the audit was silent.

---

## 0. How to read this

The `md files/` tree is not one document — it is **four generations of the same roadmap** layered on top of each other:

| Generation | Folder | What it is |
|---|---|---|
| v1 | `basic things of project/` | Original product vision + backlog |
| v2 | `basic things of project upgraded version (v2)/` | Rewritten roadmap, adds launch gates |
| v3 | `completion_fixes/`, `implementation_guides/`, `upgraded_docs/` | The "make it actually work" task specs |
| v4 | `documentation/` (00–17) | Full reference manual with embedded checklists |

Items overlap across generations. Where two docs specify the same thing, this analysis counts it **once**, at the strictest definition.

---

## 1. Headline

### 1.1 The corpus contains 332 checkboxes. Seventeen are ticked.

| Metric | Value |
|---|---|
| Markdown files | 206 |
| Files containing checkboxes | 39 |
| Total checkbox items | **332** |
| Open (`- [ ]`) | **315** |
| Ticked (`- [x]`) | **17** |
| Files with **zero** ticks | **37 of 39** |
| Ticked items, by file | `documentation/11_Security/Security_Overview.md` (10) · `basic things of project/01_PRODUCT_AND_FEATURES.md` (7) |

The two files with ticks are the *oldest* in the corpus. **No checklist created during the `completion_fixes` / `implementation_guides` / `upgraded_docs` phase was ever updated**, even though large parts of those specs were in fact built. The roadmap's own progress tracking has been dead since August.

### 1.2 Of the 315 open items, 240 are real requirements

| Class | Count | Examples |
|---|---|---|
| Process / PR / runbook checklists | **75** | `Code_Review.md` PR template (32), `Migrations.md` (7), `Recovery.md` (7), `Development_Workflow.md` (6), `MVP_Phases.md` (6), `Prerequisites.md` (6), `Vision.md` business goals (6), `Git_Workflow.md` (3), `Security_Overview.md` TODOs (2) |
| **Requirement-bearing** | **240** | everything that describes a thing to build, configure, verify, or ship |

The 75 process items cannot be "implemented" — they are templates for future work. They are excluded from scoring and listed in §6.

### 1.3 Roadmap completion: 80 / 240 met (33%)

| Status | Count | Share |
|---|---|---|
| **Met** — implemented and verified | **80** | 33.3% |
| **Partial** — exists but incomplete, unwired, or unverified | **64** | 26.7% |
| **Not met** — absent, broken, or never executed | **96** | 40.0% |

### 1.4 Three different completion numbers, all defensible

| Source | Figure | Definition used |
|---|---|---|
| `implementation-report/` self-report | **81%** | "code exists and the path was checked" |
| Audit (2026-10-30) | **49.6% fully** | "executed and worked on this machine" |
| **This gap analysis** | **33% met** | "the roadmap's own checklist item is satisfied" |

The gap widens with each definition because the roadmap asks for *outcomes* (500 memes indexed, store listing live, P95 measured), while the codebase delivers *capability*. That distinction is the entire finding.

---

## 2. Gap matrix by track

### 2.1 `completion_fixes/` — 96 items → 39 met / 30 partial / 27 not

| Doc | Met | Part | Not | What is actually still missing |
|---|---|---|---|---|
| `01_Architecture_Consolidation` | 7 | 1 | 0 | Only `docker-compose up` unrun (Docker not installed). `mobile/` deleted ✓, `services/api/Dockerfile` builds from `backend/` ✓, no workflow references `services/api` ✓, all four `dev:*` scripts exist ✓ |
| `02_Meme_Database_Population` | 1 | 0 | 6 | **Worst track.** `data/raw/memes_master.json`, `data/processed/`, `data/embeddings/` **do not exist**; DB has 62 rows; no Qdrant collection; no R2 |
| `03_BLIP_CLIP_Image_Pipeline` | 1 | 3 | 2 | Service file exists; BLIP/CLIP/OCR **never executed**; no 3-vector-space collection; quality delta unmeasured |
| `04_User_Authentication_OAuth` | 2 | 5 | 0 | `User` model + migration ✓; all OAuth paths coded but need client IDs; JWT verify coded |
| `05_Content_Moderation_NSFW` | 3 | 4 | 0 | `MemeFlag` + flag + auto-queue ✓; **queue/review have no auth**; **removed memes still reachable via the fallback retrieval path** (§4.6) |
| `06_Mobile_App_Completion` | 4 | 3 | 1 | Share + camera roll + detail screen ✓; offline cache and push hooks never imported; **EAS build impossible — `assets/` empty** |
| `07_NextJS_Web_App_Completion` | **8** | 0 | 0 | **The only fully-closed track.** metadata, JSON-LD, category pages, blog, og-image, `apps/web/vercel.json`, `npm run build`, Framer Motion — all verified present |
| `08_Production_Deployment` | 0 | 1 | 7 | No domain resolves; nothing deployed |
| `09_SEO_Marketing_Completion` | 0 | 4 | 3 | GSC/CWV/indexing all unrun; blog has 6 hardcoded slugs; store listings have copy but no assets |
| `10_Frontend_Library_Upgrades` | **5** | 0 | 0 | Zustand `persist` ✓ (`store.ts:55,88`), TanStack Query ✓, RHF ✓, DevTools ✓, 38 tests green ✓ |
| `11_Accessibility_A11y` | 5 | 3 | 2 | `alt_text` column with `f"Meme: {name}"` fallback ✓, tablist ✓, focus trap ✓, Escape ✓, skip link ✓; but no axe run, no contrast measurement, no Lighthouse score |
| `12_Missing_API_Endpoints` | 1 | 3 | 0 | Download redirect verified; preferences / collection CRUD coded but not exercised |
| `13_Monitoring_Analytics` | 1 | 1 | 2 | `/health` ✓; Umami script present in `index.html:45` + `layout.tsx:73` but needs a live website ID; no Sentry DSN; no SMTP |
| `14_Testing_CI_Gaps` | 1 | 0 | 2 | Frontend tests ✓ 38 green; AI eval and latency SLA never run |
| `15_Non_Functional_Requirements` | 0 | 2 | 2 | GDPR delete coded but unauth-adjacent; multilingual query behaviour untested; DMCA + rerank-optimizer never run |

**Read this track as:** the *coding* tasks are largely done (07, 10, 01, 11 are ≥60% met). The *data, credential, and deployment* tasks are almost entirely undone (02 is 1/7, 08 is 0/8).

### 2.2 `implementation_guides/` — 40 items → 4 met / 8 partial / 28 not

These are all provisioning runbooks — they require external accounts.

| Guide | Met | Part | Not | Blocking dependency |
|---|---|---|---|---|
| `01_Qdrant_Setup_And_Indexing` | 0 | 1 | 4 | Qdrant Cloud URL + API key; collection never created |
| `02_Redis_Upstash_Setup` | 0 | 1 | 3 | Upstash REST URL + token; in-memory fallback in use |
| `03_Cloudflare_R2_CDN_Setup` | 0 | 0 | 5 | R2 bucket, keys, `CDN_BASE_URL`; `image_url` still local |
| `05_Mobile_App_Completion` | 4 | 3 | 2 | Screens/hooks coded; `expo start` never run; EAS never run |
| `06_Deployment_Railway_Vercel` | 0 | 0 | 5 | No Railway/Vercel project exists |
| `07_CI_CD_GitHub_Actions` | 0 | 2 | 4 | 9 workflows exist; `ci.yml` cannot pass (references nonexistent root `lint`/`build`); zero Actions runs in repo history |
| `08_Monitoring_Sentry` | 0 | 1 | 5 | `SENTRY_DSN`; UptimeRobot monitor; Vercel Analytics |

**None of these 40 items can be closed without credentials or a cloud account.** They are the single largest bucket of "not met" in the project (28 items) and the reason the number cannot move by coding alone.

### 2.3 `upgraded_docs/00_INDEX.md` — 10 acceptance criteria → 3 met / 4 partial / 3 not

| # | Criterion | Status |
|---|---|---|
| 1 | Sentence in → 5 real AI-matched memes with images | **Met** (verified live, query-sensitive) |
| 2 | Response < 1.5 s P50 | **Met** (4–12 ms local) |
| 3 | Images load from real CDN URLs, not NULL | **Not** — no CDN; local `/static` is empty |
| 4 | All frontend buttons work (copy/download/share/vote) | Partial — coded, interactions never driven |
| 5 | API keys validated from DB by tier | Partial — DB lookup exists, but static keys short-circuit it (§4.3) |
| 6 | Redis caches results across restarts | Partial — falls back to in-process cache; restart loses it |
| 7 | Qdrant does real cosine similarity | **Not** — `qdrant: db_fallback` |
| 8 | Mobile share sheet + camera roll | Partial — code correct, app never built |
| 9 | `robots.txt` and `sitemap.xml` exist | **Met** |
| 10 | Tests > 80% coverage | **Not** — no coverage artifact exists anywhere |

Criterion 10 is notable: **there is no coverage data in the repository at all** — no `.coverage`, no `htmlcov/`, no `coverage.xml`. The 80% target has never been measured, in either direction.

### 2.4 Roadmap phases — v2 (36) + v1 backlog (16)

**v2 `01_FEATURES_AND_PRODUCT` — 18 phase items → 11 met / 3 partial / 4 not**

Met: web search · PNG+GIF download · copy · dark UI · MP4 support · user accounts + saved library · share link with OG · trending · individual meme SEO pages · developer API · (deployed ×) —
Not met: **5,000-meme database** · deployed to Vercel+Railway · app store submission · browser extension · multi-language.
Partial: mobile app (code, unbuilt) · blog (6 hardcoded posts) · analytics dashboard (`/stats` only).

**v2 `05_SEO_DEPLOYMENT_AND_LAUNCH` — 18 launch gates → 2 met / 6 partial / 10 not**

Met: download works for PNG+GIF · rate limiting configured.
Not met: 5,000 indexed · 50 test queries verified · NSFW filter tested · mobile tested on devices · Sentry · GSC verified · sitemap submitted · 10 blog posts · 500 meme SEO pages · HTTPS everywhere.
Partial: P95 measured · OG renders · store listings (copy only) · FAQ page · Privacy/ToS · copy across 3 browsers.

**v1 `01_PRODUCT_AND_FEATURES` — 16 backlog items → 5 met / 2 partial / 9 not**

Met: collections/favourites · direct share · API access · trending · video support.
Not met: voice input · multi-language input · meme templates · Discord bot · Telegram bot · Chrome extension · user-submitted memes · team workspaces · white-label API.

### 2.5 Feature specs in `documentation/` — 42 items → 16 met / 11 partial / 15 not

| Doc | Met | Part | Not | Notable |
|---|---|---|---|---|
| `08_Features/Chat_Refinement` (4) | 1 | 2 | 1 | **"Session state management (Redis)" is false** — an in-process dict is used (§4.2) |
| `11_Security/API_Security` (12) | 9 | 2 | 1 | Good coverage; **"No secrets in codebase" fails** (§4.3) |
| `12_Deployment/Deployment_Overview` (8) | 4 | 3 | 1 | **"All API keys in env vars (not hardcoded)" fails** |
| `16_SEO_Marketing/Launch_Strategy` (18) | 2 | 4 | 12 | Entirely a launch-day checklist; nothing shipped |

---

## 3. Where the roadmap and the code disagree most

Ranked by how much rework the disagreement implies.

| # | Disagreement | Cost to reconcile |
|---|---|---|
| 1 | Roadmap assumes **5,000 memes**; reality is **145** (62 seeded). Four separate checklists depend on this number | 2–3 days + API keys |
| 2 | Roadmap assumes **`data/raw/`, `data/processed/`, `data/embeddings/`** exist; **none do**. The repo uses `backend/data/memes.json` and a flat `embeddings.json` | 0.5 day — pick one layout |
| 3 | Roadmap treats **Qdrant + Redis + R2 as configured**; all three are unconfigured, and every code path degrades silently | 1–2 days + accounts |
| 4 | Three services **hardcode "VERIFIED / passed: true"** for checks that are false (§4.1) | 0.5 day |
| 5 | `docs/` is a one-file folder while `md files/` holds 206 — the manual and the roadmap are in different places | 0.5 day |

---

## 4. Discrepancy register — documentation claims vs code reality

### 4.1 The API serves hardcoded "all green" compliance attestations — **P1**

`deployment_overview_service.py` returns an 8-point pre-deploy checklist in which **every item is hardcoded**:

```python
PRE_DEPLOY_SECURITY_CHECKLIST = [
    {"id": 1, "item": "All API keys in environment variables (not hardcoded)", "status": "VERIFIED", "passed": True},
    {"id": 4, "item": "HTTPS enforced (HTTP -> HTTPS 301 redirect)",            "status": "VERIFIED", "passed": True},
    ...
]
```

Item 1 is **provably false** — `backend/app/core/auth.py` ships `_STATIC_DEV_KEYS` containing an admin key. Item 4 describes a production redirect on a stack that has never been deployed.

The same pattern recurs: `security_overview_service.py` marks 13 controls `"COMPLETED", "verified": True` including *"HTTPS enforced in production"* and *"Rate limiting enabled on all endpoints"*. Across `backend/app/services/` there are **16 `"passed": True` literals and 40 `"VERIFIED"/"COMPLETED"` markers**, most of them static.

The endpoint reports `compliance_percentage: 100.0` while the audit measured two P1 security gaps. **Anyone trusting this endpoint is misinformed by the software itself.**

### 4.2 Chat sessions are documented as Redis-backed; they are an in-process dict — **P2**

`documentation/08_Features/Chat_Refinement.md` requires "Session state management (Redis)" and "Conversation history storage". `chat_refinement_service.py:19`:

```python
_CHAT_SESSIONS: Dict[str, Dict[str, Any]] = {}
SESSION_TTL_SECONDS = 3600
```

Consequences: conversation state dies on restart, is not shared across workers, and is lost behind any load balancer. Combined with the frontend never calling `/chat/refine` (audit D-8), the entire chat-refinement feature is unreachable *and* non-durable.

### 4.3 "No secrets in codebase" and "API keys validated from DB by tier" are both false — **P1**

Two roadmap items demand these. `core/auth.py:52-57` hardcodes three keys including `memegpt_admin_secret_key` → `is_admin: True`, and `.env.example` ships a real 64-hex `SECRET_KEY`. The DB-tier path exists but the static map is consulted first and always active.

### 4.4 "Tests > 80% coverage" has never been measured — **P2**

No coverage artifact exists. `pytest` is configured with `--cov` in the roadmap's own commands but no report has ever been produced or committed.

### 4.5 The data pipeline described in four documents does not exist on disk — **P1**

`completion_fixes/02` checks for `data/raw/memes_master.json` (5,000+), `data/processed/memes_processed.json`, `data/embeddings/`. All three paths are absent; the collector scripts that would build them are present and never executed. The seeder additionally discards 57% of the 145 curated memes (audit **D-1**).

### 4.6 "Removed memes are excluded from search results" is only half true — **P2**

`api/v1/search.py:14-17` correctly builds a moderation-filtered candidate set, and `/api/v1/memes` and `trending_service` filter too. But `search_service._db_fallback_search()` queries `Meme` with **no moderation filter**:

```python
memes = db.query(MemeModel).order_by(MemeModel.popularity_score.desc(), ...).limit(top_k).all()
```

When Qdrant is unavailable — the current state — the degraded retrieval path can re-introduce a moderated-away meme. Moderation "remove" is therefore not authoritative on the primary surface under degradation.

### 4.7 Offline cache and push notifications are documented as features, not present as behaviour — **P2**

`completion_fixes/06` and `implementation_guides/05` both require them. `useOfflineCache.ts` and `usePushNotifications.ts` exist and are **imported by no screen** — verified by grep across `apps/mobile/`. The store listing additionally advertises "Offline Camera Roll Cache".

### 4.8 "EAS build succeeds" is unreachable — **P2**

`app.json` references `./assets/icon.png`, `./assets/splash.png`, `./assets/adaptive-icon.png`, `./assets/favicon.png`. `apps/mobile/assets/` contains **only `.gitkeep`**. `eas.json` submit block still has `appleId: "your@email.com"`, `ascAppId: "YOUR_APP_ID"`.

### 4.9 Checklist discipline collapsed — **P3, but it caused the rest**

315 of 332 items are unticked, including items that *were* completed (07 is 8/8 done, 0/8 ticked). This is why the self-report could claim 81% while the roadmap tracked 0%: nobody updated the source of truth, so a second narrative grew beside it.

---

## 5. Prioritized action plan

Effort assumes one developer, local-first, no waiting on store review.

### P0 — Truth and safety (2 working days)

| # | Action | Closes | Effort |
|---|---|---|---|
| 1 | Fix seeder schema mapping (`categories[0]`, `image_url`, `gif_url`) and fail loudly | D-1, `cf/02`, v2 phases | 3 h |
| 2 | Delete `_STATIC_DEV_KEYS` or gate on `APP_ENV == "development"` | S-1, §4.3 | 1 h |
| 3 | Add `require_admin` to `moderation/queue` and `moderation/review`; rate-limit `flag` | S-2, `cf/05` items 5-6 | 2 h |
| 4 | Add `moderation_status != "removed"` to `_db_fallback_search` and the Qdrant filter | §4.6, `cf/05` item 7 | 1 h |
| 5 | Rotate `SECRET_KEY` in `.env.example` to a placeholder | S-3 | 15 m |
| 6 | Replace hardcoded `VERIFIED`/`passed: True` blocks with computed checks, or label them `"status": "asserted"` | §4.1 | 3 h |
| 7 | Swap `GET /admin/memes` to `require_admin` | S-4 | 15 m |

**Why first:** these are the items that make the product *lie* — to users, to operators, and to whoever reads the compliance endpoint. They are all single-file changes.

### P1 — Make the AI pipeline real (3 working days, needs accounts)

| # | Action | Closes | Effort | Blocked by |
|---|---|---|---|---|
| 8 | Provision Qdrant Cloud; create `memes` collection with the 3 named vectors; index all memes | `ig/01`, `ud/03`, `ud/07`, §4.5 | 1 d | Qdrant account |
| 9 | Install `torch` + `transformers` + tesseract; regenerate `embeddings.json`; run BLIP/CLIP/OCR over the dataset | `cf/03`, §4.4 of audit | 1 d | compute |
| 10 | Provision Upstash Redis; verify cache survives restart; verify rate limits survive restart | `ig/02`, `ud/06` | 0.5 d | Upstash account |
| 11 | Decide the data layout: adopt `data/raw|processed|embeddings/` or rewrite `completion_fixes/02` to match `backend/data/` | §3.2 | 0.5 d | decision |
| 12 | Fix `ci.yml` to run `frontend` and `apps/web` scripts explicitly; get one green run | D-3, `ig/07` | 0.5 d | — |

### P2 — Get it deployed (3 working days)

| # | Action | Closes | Effort |
|---|---|---|---|
| 13 | Fix root `railway.toml` `startCommand` (remove `cd backend`) | D-2 | 15 m |
| 14 | Deploy API to Railway + Vite SPA + Next.js to Vercel; point DNS; verify all 8 URLs in `cf/08` | `cf/08` (8 items), `ig/06` | 1 d |
| 15 | Provision R2, upload images, rewrite `image_url` to CDN | `ig/03`, `ud/03` | 0.5 d |
| 16 | Set `SENTRY_DSN`, add UptimeRobot; confirm a real error lands in Sentry | `ig/08`, `cf/13` | 0.5 d |
| 17 | Scale dataset 145 → 500 (achievable now) then toward 5,000 via collectors | `cf/02`, v2 gates | 1 d |

### P3 — Ship to stores (4 days + review)

| # | Action | Closes | Effort |
|---|---|---|---|
| 18 | Generate icon/splash/adaptive-icon/favicon into `apps/mobile/assets/` | D-5, §4.8 | 2 h |
| 19 | Wire `useOfflineCache` + `usePushNotifications` into the tab screens | D-10, `cf/06` items 3,6 | 3 h |
| 20 | `eas build` for both platforms; fix what breaks | `cf/06` item 8 | 1 d |
| 21 | Produce the graphic set the ASO doc specifies — **with the corrected 9:16 ratio** (audit G-3) and iPad set (G-4) | `cf/09`, `af` | 0.5 d |
| 22 | Correct store copy: "thousands of GIFs" → actual count; drop "offline cache" until item 19 lands; drop "no invasive permissions" or remove `WRITE_EXTERNAL_STORAGE` | G-5 | 1 h |
| 23 | Submit | v2 gates | review time |

### P4 — Hygiene that prevents the drift recurring (1.5 days)

| # | Action | Closes | Effort |
|---|---|---|---|
| 24 | Measure coverage; publish the real number (do not target 80% first — establish a baseline) | `ud/10`, §4.4 | 2 h |
| 25 | Add Playwright smoke: search → copy → download → vote → favourite | audit §12 | 1 d |
| 26 | Replace 9 hardcoded `d:/Meme GPT/...` test paths with `Path(__file__).parents[2]` | D-6 | 1 h |
| 27 | Add `dependabot.yml` + secret scanning | `Security_Overview` TODO | 1 h |
| 28 | Delete or archive the 3 hardcoded-attestation services' static data; point manifest `file_path`s at `project-vision/` not the pruned `md files/` | audit G-2 | 2 h |
| 29 | Tick the checklists you actually closed — or delete `md files/` and keep `project-vision` as the single source | §4.9 | 2 h |

**Total: ~13.5 working days**, of which ~5 days need no external account.

---

## 6. Items to stop tracking (75)

These appear as unchecked boxes but are templates or non-goals. Recommended: move to a `templates/` folder, or mark `n/a` — do not carry them in a completion percentage.

| File | Items | Why excluded |
|---|---|---|
| `documentation/09_Development/Code_Review.md` | 32 | PR review template, applied per-PR |
| `documentation/06_Database/Migrations.md` | 7 | Per-migration checklist |
| `documentation/06_Database/Recovery.md` | 7 | Incident runbook, used only during an outage |
| `documentation/09_Development/Development_Workflow.md` | 6 | Per-commit checklist |
| `documentation/13_Project_Management/MVP_Phases.md` | 6 | Per-release gate |
| `documentation/01_Getting_Started/Prerequisites.md` | 6 | Machine setup (4 of 6 satisfied locally) |
| `documentation/00_Project_Overview/Vision.md` | 6 | Business outcomes (>4.5 rating, 10k reviews) — not implementable |
| `documentation/09_Development/Git_Workflow.md` | 3 | Per-commit checklist |
| `documentation/11_Security/Security_Overview.md` | 2 | Genuine TODOs — fold into P4 #27 |

---

## 7. Dependency graph

```
P0 (truth/safety)  ──►  P1 (AI real)  ──►  P2 (deploy)  ──►  P3 (stores)
   no deps              needs accounts        needs P1        needs P2
        │
        └──► P4 (hygiene) — can run in parallel from day 1
```

Three decisions gate the largest chunks and should be made before any of it:

1. **Is `md files/` restored and authoritative, or is `project-vision/` the source of truth?** Right now both exist and disagree. This determines whether P4 #29 is "tick the boxes" or "delete the tree".
2. **Which data layout is canonical?** `backend/data/memes.json` or `data/raw|processed|embeddings/`? Four checklists assume the latter.
3. **Is the 5,000-meme target still real?** If not, rewrite `completion_fixes/02` and both v2 launch gates — they currently make the project un-completable by definition.

---

## 8. Appendix — checkbox census by file

39 files carry checkboxes; the rest are prose. Met/Partial/Not are for requirement-bearing items only.

| File | Open | Ticked | Met | Part | Not |
|---|---|---|---|---|---|
| `basic things/project/01_PRODUCT_AND_FEATURES` | 16 | 7 | 5 | 2 | 9 |
| `basic things/...v2/01_FEATURES_AND_PRODUCT` | 18 | 0 | 11 | 3 | 4 |
| `basic things/...v2/05_SEO_DEPLOYMENT_AND_LAUNCH` | 18 | 0 | 2 | 6 | 10 |
| `completion_fixes/01` … `15` | 96 | 0 | 39 | 30 | 27 |
| `documentation/08_Features/Chat_Refinement` | 4 | 0 | 1 | 2 | 1 |
| `documentation/11_Security/API_Security` | 12 | 0 | 9 | 2 | 1 |
| `documentation/12_Deployment/Deployment_Overview` | 8 | 0 | 4 | 3 | 1 |
| `documentation/16_SEO_Marketing/Launch_Strategy` | 18 | 0 | 2 | 4 | 12 |
| `documentation/11_Security/Security_Overview` | 2 | 10 | — | — | — |
| `implementation_guides/01,02,03,05,06,07,08` | 40 | 0 | 4 | 8 | 28 |
| `upgraded_docs/00_INDEX` | 10 | 0 | 3 | 4 | 3 |
| 9 process files (§6) | 75 | — | excluded | excluded | excluded |
| **Total** | **315** | **17** | **80** | **64** | **96** |

---

*Companion to `AUDIT-REPORT-2026-10-30.md`. Requirement inventory extracted mechanically from `md files/` (332 checkboxes across 39 of 206 files); each item resolved against the audit baseline and re-verified in code where the audit was silent. No source files were modified.*
