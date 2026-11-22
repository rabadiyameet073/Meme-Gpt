# 17 — Reporting, Analytics & Monitoring Gaps

**Source requirements:** `md files/project-vision/01-vision-product.md` §1.9 (KPI dashboard), `md files/documentation/12_Deployment/Monitoring.md`, `md files/completion_fixes/13_Monitoring_Analytics.md`, `md files/implementation_guides/08_Monitoring_Sentry.md`, `Roadmap.md` (P2c)
**Related:** [11-admin-panel-gaps](11-admin-panel-gaps.md) · [02-backend-core-gaps](02-backend-core-gaps.md) · [21-performance-gaps](21-performance-gaps.md) · [20-ci-cd-deployment-gaps](20-ci-cd-deployment-gaps.md)

## Verified as implemented
Sentry init with PII off (`backend/app/core/monitoring.py:43-52`); structured JSON logs; Umami in apps/web gated on `NEXT_PUBLIC_UMAMI_WEBSITE_ID` (`layout.tsx:67-76`); Vite analytics wrapper (`frontend/src/lib/analytics.ts:16-28`) used in `MemeCard.tsx`; `SearchLog` stores `response_time_ms` and `result_count` (data exists for KPIs).

## KPI coverage (vision §1.9)
| KPI | Data captured? | Exposed? |
|---|---|---|
| Searches/day | ✅ `SearchLog` | ⚠️ total only (`/stats`) |
| Latency P50/P95 | ✅ `response_time_ms` | ❌ |
| Cache-hit % | ⚠️ in-memory counters | ❌ |
| Copy/download/share counts | ✅ `Feedback` (double-counted, see [05](05-trending-feedback-gaps.md)) | ❌ |
| Thumbs-up % | ✅ | ❌ |
| Zero-result % | ✅ `result_count` | ❌ |
| Top-20 queries | ❌ only the hash is stored (by design, for GDPR) | ❌, needs an anonymised aggregate design |
| DAU/WAU, D7 retention | ⚠️ session IDs only | ❌ |
| Error rate | Sentry | ❌ alerting |

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| RPT-01 | KPI metrics API | Not implemented | `categories.py:57-81` `/stats` = 3 totals; `/health/stats` (`health.py:84-88`) claims latency stats but only proxies `/stats` | `/admin/metrics` aggregating the table above | High |
| RPT-02 | Admin analytics dashboard (Roadmap P2c) | Not implemented | `AdminTab.tsx` has no metrics | Charts on RPT-01 | Medium |
| RPT-03 | Analytics events in both apps | Partially implemented | `frontend/index.html:45-46` hardcodes `data-website-id="memegpt-app"` (not a UUID); apps/web `trackEvent` has no callers; mobile has none | Env-driven ID; instrument search, chip, copy, download, share, favorite and chat | High |
| RPT-04 | Top-queries reporting without raw PII | Not implemented | Queries are hashed only | Design: k-anonymous aggregate of normalised queries (e.g. ≥5 occurrences) | Low |
| MON-01 | Uptime monitoring | Incorrectly implemented | `.github/workflows/health_check.yml:15` uses `https://your-app.railway.app`; a non-200 only `echo`s | Real URL, `exit 1`; UptimeRobot (external) | High |
| MON-02 | Sentry sample rates (`Monitoring.md:36-45`: traces 0.1) | Partially implemented | Traces 0.2 in prod / 1.0 elsewhere; reads `ENVIRONMENT`, not `APP_ENV` | Align | Low |
| MON-03 | Latency/cache metrics (`Monitoring.md:59-69`) | Not implemented | No `/metrics` or histogram; `deployment.py:318` returns a dashboard spec as data | Timing middleware → p50/p95, cache-hit counters | Medium |
| MON-04 | Alerts: P95 > 3s, error rate > 2% | Not implemented | No alert config in the repo (Sentry console rules unverifiable, ASSUMPTION) | Define rules; document them as code or a checklist | Medium |
| MON-05 | Truthful health status | Incorrectly implemented | See [02](02-backend-core-gaps.md) BE-01 | — | High |
