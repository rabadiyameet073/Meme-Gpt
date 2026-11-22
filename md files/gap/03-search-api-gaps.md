# 03 — Search & Core API Contract Gaps

**Source requirements:** `md files/documentation/07_APIs/Search_API.md`, `Meme_API.md`, `Rate_Limiting.md`, `md files/upgraded_docs/07_Missing_API_Routes.md`, `md files/completion_fixes/12_Missing_API_Endpoints.md`
**Related:** [04-ai-pipeline-gaps](04-ai-pipeline-gaps.md) · [09-security-gaps](09-security-gaps.md) · [13-user-workflow-gaps](13-user-workflow-gaps.md) · [10-content-moderation-gaps](10-content-moderation-gaps.md)

## Verified as fully implemented
- All routes listed in `completion_fixes/12` / `upgraded_docs/07` are mounted under `/api/v1`: `/search`, `/trending`, `/feedback`, `/memes/{slug}`, `/memes/{slug}/download`, `/share`, `/users/me`, `/developer/usage`, `/admin/memes` (CRUD, `require_admin`), `/favorites`, `/favorites/toggle`, `/categories`, `/stats`.
- Input length caps and sanitisation: `models/search.py:38,52` (`max_length=2000`), `search.py:67` `sanitize_input`.
- Rate-limit headers and the 429 body match `Rate_Limiting.md`.

## Gaps
| Gap ID | Requirement | Status | Evidence | Expected (doc) | Required change | Priority |
|---|---|---|---|---|---|---|
| API-01 | `nsfw` flag controls explicit content | Incorrectly implemented | `models/search.py:45` accepts `nsfw`; `api/v1/search.py:83-87` calls `recommend(user_text, format_pref, memes_from_db)` without it, so it always defaults to `False`; the cache key also always uses `nsfw=False` | Opt-in NSFW, safe by default | Pass `body.nsfw` into `recommend` and into the cache key; combine with [10](10-content-moderation-gaps.md) MOD-04 | Critical |
| API-02 | `filters.categories` | Not implemented | `search_service.py:1134-1172` applies only `exclude_ids`; categories are echoed back unused | Results restricted to the chosen categories | Pass a Qdrant payload filter through `build_search_filter` / `vector_search` | High |
| API-03 | `limit` 1–20 | Partially implemented | `recommend` returns `final_results[:5]`; the endpoint returns that list | Up to `limit` results | Pass `limit` into `recommend`, set `top_k = max(15, limit*3)`, slice to `limit` | High |
| API-04 | Documented response schema | Partially implemented | `emotion_match` is a string, not an array (`search_service.py:1163`); `formats.mp4` vs documented `formats.video`; score falls back to a hardcoded `0.85` (`:1141`); duplicate camelCase and snake_case keys plus legacy `primary`/`topFive` | Schema as in `Search_API.md` | Define one Pydantic `response_model`; deprecate the legacy keys under a version flag | Medium |
| API-05 | Validation logic | Incorrectly implemented | `search.py:68` `if not is_valid_input(raw_query) and len(raw_query.strip()) == 0`, where `and` should be `or` | Invalid or empty input → 422 | Fix the boolean; add a test | Medium |
| API-06 | Accurate search logs | Incorrectly implemented | `search.py:134` logs `confidence=0.85` for every search | Real top score logged | Log `results[0].score` | Low |
| API-07 | Empty DB behaviour | Needs improvement | An empty DB returns 503 from `/search` | Graceful empty result + message | Return 200 with `results: []` and a `reason` field | Low |
| API-08 | Frontend sends the full contract | Incorrectly implemented | `apps/web/lib/api.ts:151-158` drops `limit`, `nsfw` and `session_id` passed by `useMemeSearch.ts:77-83` | All fields forwarded | Fix the client (see [12](12-frontend-web-gaps.md) FE-14) | High |
| API-09 | `/memes?limit=` supports sitemap generation | Partially implemented | `memes.py:67` clamps `limit` to 100; `apps/web/app/sitemap.ts:18` asks for 50000 | Every slug available for the sitemap | Add a paginated `/api/v1/sitemap/slugs` (see [15](15-seo-marketing-gaps.md) SEO-01) | Critical |
| API-10 | Unknown category → 404 | Incorrectly implemented | `memes.py:77-79` falls back to all memes when the filter is empty | 404 for an unknown category | Use a whitelist of categories; return 404 | High |
| API-11 | Per-endpoint rate limits (`Rate_Limiting.md`: `/search` 30/min, `/feedback` 120/min) | Not implemented | A single global limit in the middleware | Per-route budgets | Add a route-level limiter dependency | Medium |
| API-12 | Tier numbers (`Rate_Limiting.md`: Free 30/60, Dev 100/300, Pro 500/1000) | Incorrectly implemented | `config.py:240-243`: anon 60, free 120, pro 300, internal 1000 | Docs and code agree | Decide which is correct; update the other | Medium |
| API-13 | Image / reverse-image search (v2 feature, `05_AI_System/Image_Analysis.md`) | Not implemented | No `UploadFile` anywhere in `api/v1/` | `POST /search/image` | See [04](04-ai-pipeline-gaps.md) AI-08 | Medium (P2 in vision) |

## Verification criteria
- A contract test per documented field: `nsfw`, `filters.categories`, `limit=20`, plus a schema snapshot.
- `GET /memes?category=doesnotexist` → 404.
