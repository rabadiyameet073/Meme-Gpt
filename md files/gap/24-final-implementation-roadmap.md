# 24 — Final Implementation Roadmap (dependency-aware)

**Inputs:** gap files [01](01-architecture-consolidation-gaps.md)–[23](23-data-privacy-retention-gaps.md) · **Overview:** [00](00-gap-analysis-overview.md)

## Decisions required from the owner (blocking)
| ID | Decision | Recommendation | Blocks |
|---|---|---|---|
| D-1 | Canonical web app | Keep **Vite `frontend/`** as the app (most complete) and **Next `apps/web/`** as marketing/SEO only; delete `apps/web/(app)/*` | FE, SEO, analytics, deploy (ARC-02, FE-01, DEP-07) |
| D-2 | Corpus target per phase | 1k MVP → 5k public launch → 10k+ SEO scale | DATA-01, SEO-01, DOC-04 |
| D-3 | Rate-limit tiers (docs vs code) | Adopt the doc numbers (Free 30/60, Dev 100/300, Pro 500/1000) | API-12 |
| D-4 | Keep the live Giphy/Reddit fetch in search? | Remove it from the hot path; ingest offline | PERF-01, MOD-04, INT-07 |
| D-5 | Provision accounts (Supabase, Upstash, Qdrant Cloud, R2, Groq, GIPHY, Reddit, Resend, Sentry, EAS) | User action; secrets go only into Railway/Vercel/EAS | Phase 2+ |

## Dependency graph (simplified)
```
D-1 ─┬─> Phase 1 consolidation ─┬─> Phase 3 correctness ─> Phase 4 product ─> Phase 5 launch
     │                          │
Phase 0 security ───────────────┤
                                └─> Phase 2 data/infra (needs D-2, D-5) ──┘
```

---

## Phase 0 — Security hot-fixes & CI unblock (≈ 3–5 days)
| Order | Work | Gap IDs |
|---|---|---|
| 0.1 | Remove/guard public email routes; server-side magic links; escape HTML | SEC-01, SEC-02, SEC-08, INT-01 |
| 0.2 | Lock down API-key issuance/list/revoke; remove the test-key prefix shortcut | AUTH-03, AUTH-04, AUTH-06 |
| 0.3 | OAuth `state`/PKCE; verified-email linking | AUTH-01, AUTH-02 |
| 0.4 | `require_admin` on purge; ownership proof for export/delete | SEC-03, PRIV-04 |
| 0.5 | Rate limiter: trusted-proxy XFF, invalid-key → IP bucket, sliding window | SEC-04, SEC-05 |
| 0.6 | Protect `/mobile/push-tokens`, `/health/sentry-test`; webhooks require auth + SSRF guard | SEC-11, BE-02, SEC-07 |
| 0.7 | Escape JSON-LD | SEC-09 |
| 0.8 | Promote `workflows-upgraded` → `workflows`; single deploy workflow; no secrets in PR CI | CI-01, CI-02, CI-03, SEC-13, SEC-14 |
| 0.9 | Add a negative security test for every item above | TEST-03 |

**Exit criteria:** every pen-test check in [09](09-security-gaps.md) passes; CI is green on a PR with no secrets.

## Phase 1 — Consolidation (≈ 1 week; needs D-1)
| Order | Work | Gap IDs |
|---|---|---|
| 1.1 | Delete `services/api/`, `prisma/`, dead shims, `rag_service`/`smart_search_service`, `landing.html` | ARC-01, ARC-03, ARC-04, ARC-08, DB-02, DB-08 |
| 1.2 | Remove the doc-manifest routers/services/tests from `api/v1/__init__.py` (or `/internal`, admin-only) | DOC-01, DOC-02, DOC-07, TEST-01, SEC-10 |
| 1.3 | Single `/api/v1` mount; dedupe the collections/download routers | ARC-05, ARC-06, API-07/08 (file 03) |
| 1.4 | Apply D-1: remove duplicate app routes; fix nav links, layout, footer | FE-01, FE-07, FE-08, FE-09 |
| 1.5 | One Dockerfile/railway.toml/vercel.json per app; fix compose env names; `APP_ENV` everywhere | DEP-01..03, DEP-06, BE-05 |
| 1.6 | One indexing pipeline + one `evaluate.py` | ARC-07, DATA-09, AI-10 |

**Exit:** OpenAPI lists each product route once; `find` shows a single backend; the build from a clean checkout succeeds.

## Phase 2 — Data & infrastructure (≈ 1–2 weeks; needs D-2, D-5)
| Order | Work | Gap IDs |
|---|---|---|
| 2.1 | Supabase Postgres + Alembic baseline + migrate SQLite data; GIN indexes | DB-01, DB-03, DB-04 |
| 2.2 | Safe seed (upsert); real backups + schedule + off-site encrypted copies | DB-05, DB-06, DB-07, PRIV-09 |
| 2.3 | Remote Qdrant + required Redis in prod; chat sessions in Redis → multi-worker | ARC-09, BE-07, SEC-06, PERF-05 |
| 2.4 | Pipeline: collect (Imgflip/Reddit/Giphy) → dedupe → NSFW (fail closed) → BLIP caption/alt → embed (abort if no model) → R2 upload + formats → index → verify | DATA-01..08, MOD-01, MOD-03, AI-03, INT-08, A11Y-05 |
| 2.5 | Scheduled refresh jobs (weekly ingest, hourly popularity sync), failing loudly | DATA-08, AI-09, FB-05 |

**Exit:** ≥ D-2 target memes indexed, 100% embedding/CDN coverage (`verify_index.py`, `verify_cdn_urls.py`), `pg_dump` artifact in off-site storage.

## Phase 3 — Backend & AI correctness (≈ 1–2 weeks)
| Order | Work | Gap IDs |
|---|---|---|
| 3.1 | Search contract: `nsfw`, categories, `limit`, response schema, validation bug, real confidence | API-01..07, MOD-02 |
| 3.2 | Async/cached Giphy (or removed per D-4); drop full-table loads; cache tier lookups | PERF-01..04, AI-07, INT-05 |
| 3.3 | Admin writes → embed + upsert + cache flush; deletions purge the cache | AI-08, BE-03, ADM-04 |
| 3.4 | Trending from real timestamps; aggregate SQL; remove fakes | TR-01..04 |
| 3.5 | Feedback idempotency, vote floor, store format | FB-01..03 |
| 3.6 | Truthful `/health` with dependency checks | BE-01, MON-05, DB-09 |
| 3.7 | CLIP text→image / combined-vector retrieval; merge the image services; personalised rerank | AI-01, AI-02, AI-04, AI-06 |
| 3.8 | RBAC (`User.role`, JWT admins), refresh-token revocation, one JWT lib, password policy + login limiter | AUTH-05, AUTH-07..09, ADM-01 |
| 3.9 | Per-endpoint rate limits, tiers per D-3 | API-11, API-12 |
| 3.10 | Privacy: one retention constant, full erasure cascade, hashed IPs | PRIV-01..05, MOD-06 |

**Exit:** contract tests for every documented field; golden-set P@5 baseline recorded; coverage ≥ 80% (manifest code excluded).

## Phase 4 — Product completeness (≈ 2–3 weeks)
| Area | Work | Gap IDs |
|---|---|---|
| Workflows | Favorites save, recents, edge cases, image copy, download headers, single feedback event, share `?ref=`, WebP, dynamic chips, empty states, server sync | WF-01..14, FB-04 |
| Frontend | Real routes, about/privacy pages, ISR trending, static meme pages, related memes, React Query, request cancel, live stats | FE-02..06, FE-10..16, PRIV-06, UX-02 |
| A11y/RWD | Accessible nav names, focus trap, aria-live, ARIA fixes, reduced motion, contrast audit, mobile drawer, 44px targets | A11Y-01..08, RWD-01..03 |
| SEO | Sitemap pagination/index, category hubs, real 404s, canonical, robots, metadataBase, BreadcrumbList, OG cards, `next/image`, ASO listing, blog decision | SEO-01..14 |
| Moderation/Admin | Flag dedupe, DMCA endpoint + log, admin audit log, role-gated tab, user mgmt | MOD-05, MOD-07, ADM-02, ADM-03, ADM-06, ADM-07 |
| Integrations | Real webhooks with retries; welcome/share emails; Giphy attribution; Expo push sender | INT-02, INT-03, INT-06, INT-09 |
| Analytics | KPI metrics API + admin dashboard; analytics events in all apps | RPT-01..04, MON-03, ADM-05 |
| Mobile | EAS config, projectId, deep links, prod API URL, parity screens, tests, permissions | MOB-01..11 |

## Phase 5 — Launch hardening (≈ 1 week)
| Order | Work | Gap IDs |
|---|---|---|
| 5.1 | Deploy backend (Railway) + app + marketing (Vercel); domains; env complete | DEP-07, DEP-08, ENV-01 |
| 5.2 | Post-deploy smoke tests; loud failure on missing secrets; rollback workflow | CI-04..07, DEP-09 |
| 5.3 | Uptime monitor on the real URL; Sentry rates; P95/error-rate alerts | MON-01, MON-02, MON-04 |
| 5.4 | Staging benchmark (≥200 samples) + Locust run with thresholds | PERF-06..08, TEST-09 |
| 5.5 | Container hardening; models baked into the image | DEP-04, DEP-05 |
| 5.6 | E2E Playwright smoke suite + mobile EAS build | TEST-07, TEST-08 |
| 5.7 | Update the docs: reset the master checklists, MVP status, scoring formula, tech stack, FAQ; mark old gap reports superseded | DOC-03..09 |

---

## Testing & verification criteria (per phase)
| Phase | Must be true |
|---|---|
| 0 | All security negative tests pass; anonymous abuse attempts return 401/429 |
| 1 | Single backend/app per role; no duplicate routes (startup assertion); CI green |
| 2 | Corpus ≥ target; 0 fake embeddings; 100% CDN URLs resolve; backup restore drill succeeds |
| 3 | Contract tests green; trending order changes over simulated time; health returns 503 when Redis is down; P@5 ≥ baseline |
| 4 | axe: 0 serious violations; Lighthouse SEO ≥ 95, a11y ≥ 90; sitemap lists every slug; KPI dashboard shows all 10 panels |
| 5 | p50 < 1s, p95 < 3s on staging; smoke tests green post-deploy; alerts fire in a test |

## Final production-readiness checklist
- [ ] D-1..D-5 decisions recorded
- [ ] All 33 Critical gaps closed (see [00](00-gap-analysis-overview.md) §3)
- [ ] No public routes that send email, purge data, or list tokens/keys without auth
- [ ] OAuth `state` + verified-email linking; RBAC with JWT admins
- [ ] Rate limiter: sliding window, Redis-backed, proxy-aware
- [ ] NSFW filtered by default; classifier fails closed; ingestion moderated
- [ ] Single backend, single canonical app, single schema (Alembic), single CI folder
- [ ] Postgres + Redis + remote Qdrant + R2 in production; backups scheduled and restore-tested
- [ ] Corpus ≥ launch target, 100% embedded and CDN-served
- [ ] Search contract honours `nsfw`, categories, `limit`
- [ ] Trending computed from real timestamps; feedback idempotent
- [ ] `/health` truthful; uptime + Sentry alerts live
- [ ] Coverage ≥ 80% on product code; security, contract and E2E suites in CI
- [ ] Sitemap complete; real 404s; canonical; robots fixed
- [ ] a11y (axe/Lighthouse) and responsive checks passed
- [ ] KPI dashboard live
- [ ] Mobile EAS build + push working
- [ ] Docs updated to match reality; doc-manifest API removed
- [ ] p50 < 1s / p95 < 3s measured on staging; load test passed
