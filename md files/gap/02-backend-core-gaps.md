# 02 — Backend Core Gaps (health, caching, state, errors)

**Source requirements:** `md files/documentation/03_Backend/*` (Backend_Overview, Error_Handling, Logging, Services), `md files/upgraded_docs/04_Redis_Cache.md`, `md files/implementation_guides/02_Redis_Upstash_Setup.md`, `md files/documentation/12_Deployment/Monitoring.md`
**Related:** [03-search-api-gaps](03-search-api-gaps.md) · [09-security-gaps](09-security-gaps.md) · [17-reporting-analytics-monitoring-gaps](17-reporting-analytics-monitoring-gaps.md) · [21-performance-gaps](21-performance-gaps.md)

## Verified as fully implemented
| Item | Evidence |
|---|---|
| Redis → Upstash REST → in-memory cache fallback | `backend/app/core/cache.py:33-130` |
| Search cache keys are hashed (no raw query stored), 1h TTL | `core/cache.py:169-176`; `recommendation_service.py` `cache_set(..., ttl=3600)` |
| Structured JSON logging with PII hashing | `core/logging_config.py:15-44`; `setup_logging` at `main.py:41` |
| Security headers / HSTS in prod | `main.py:241-258` |
| Production refuses a weak `SECRET_KEY` | `config.py:162-167` |

## Gaps
| Gap ID | Requirement (source) | Status | Evidence | Expected behaviour | Required change | Priority |
|---|---|---|---|---|---|---|
| BE-01 | Health endpoint reflects dependency state (`Monitoring.md:73-92`) | Incorrectly implemented | `api/v1/health.py:37` always returns `"status":"ok"`; `:41` `"redis": "ok" if cache_stats.get("entries",0) >= 0`, which is always true; the response is flat, not nested under `services` | Returns `degraded`/503 when Redis, Qdrant, the DB or the models are unavailable; JSON shape as documented | Run real `PING`, a Qdrant `get_collection`, `SELECT 1` and a model-loaded flag; nest under `services`. The Railway healthcheck depends on this | High |
| BE-02 | Public endpoints only (`Error_Handling.md`) | Incorrectly implemented | `health.py:80` raises a deliberate 500; `/health/sentry-test` is public | Debug endpoints are only available in non-prod or to admins | Gate with `require_admin` or `APP_ENV != production` | Medium |
| BE-03 | Cache invalidation after data changes (`upgraded_docs/04`) | Not implemented | Admin create/update/delete (`admin.py:~95-178`) and feedback/votes don't clear `search:*`; a deleted meme can be served for up to 1h | Changes to a meme invalidate the affected cache entries | Call `cache_flush_pattern("search:*")` (or a versioned cache key) on admin writes | High |
| BE-04 | Cache survives deploys | Needs improvement | `main.py:57-58` `query_cache.clear()` flushes `search:*` on shared Redis at every boot | A deploy doesn't wipe the shared cache | Make it opt-in via an env flag | Low |
| BE-05 | Config consistency | Incorrectly implemented | `config.py:27` defines `APP_ENV`; `monitoring.py` falls back to `settings.ENVIRONMENT`; `docker-compose.yml` sets `ENVIRONMENT=development` | One env name | Standardise on `APP_ENV` everywhere | Medium |
| BE-06 | Hardcoded secret fallbacks removed (`upgraded_docs/12`) | Needs improvement | `core/auth.py:20` `"memegpt-super-secret-jwt-key-change-in-prod-2026"`, `services/jwt_service.py:9` `"change-me-in-production"`. Currently unreachable because `Settings.SECRET_KEY` always exists | No literal secrets in source | Delete the literals; read only from settings | Medium |
| BE-07 | Stateless app instances | Partially implemented | `_CHAT_SESSIONS` in memory (`chat_refinement_service.py:17`); in-memory rate-limit fallback grows without a bound (`core/rate_limit.py:17`) | State lives in Redis | Move both to Redis with a TTL; bound the fallback dict | Medium |
| BE-08 | No per-request DB lookups on the hot path | Needs improvement | `main.py:184-192` opens a DB session to look up the API-key tier on every keyed request; `search.py:77` `_memes_from_db(db)` loads **all** memes on every search | O(1) per request | Cache the tier lookups in Redis/LRU; drop the full-table load (Qdrant already holds the payloads) | High |
| BE-09 | Background jobs run reliably | ASSUMPTION – needs runtime validation | APScheduler retention job at `main.py:82-94`; with multiple workers or a restart it may run twice or not at all | Single scheduled runner | Move to a GitHub Actions cron or a dedicated worker once horizontal scaling is enabled | Low |

## Dependencies
BE-03 depends on the admin indexing fix ([11-admin-panel-gaps](11-admin-panel-gaps.md) ADM-04). BE-07 is required before ARC-09 (multi-worker).
