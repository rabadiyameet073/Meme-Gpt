# 05 — Trending & Feedback Business Logic Gaps

**Source requirements:** `md files/documentation/07_APIs/Trending_API.md`, `Feedback_API.md`, `md files/documentation/08_Features/Trending_System.md`, `Copy_Download.md` (signals), `md files/documentation/05_AI_System/Scoring_Logic.md`
**Related:** [04-ai-pipeline-gaps](04-ai-pipeline-gaps.md) · [13-user-workflow-gaps](13-user-workflow-gaps.md) · [17-reporting-analytics-monitoring-gaps](17-reporting-analytics-monitoring-gaps.md)

## Verified as fully implemented
- 8 feedback actions with weights, written in a background task; updates `usage_count`, upvotes and `viral_score` (`api/v1/feedback.py:76-108`).
- `/vote` deduplicates per session.
- Trending has a two-tier cache (1h); an hourly workflow `.github/workflows/trending.yml` exists.

## Gaps
| Gap ID | Requirement | Status | Evidence | Expected | Required change | Priority |
|---|---|---|---|---|---|---|
| TR-01 | Time-decayed trending score (`Trending_API.md`) | Incorrectly implemented | `trending_service.py:57-58,118` hardcode `hours_since_peak = 2.0`, `last_activity_hours = 1.0`, `days_on_trending = 2.0`, so decay is the same for every meme | Decay computed from real timestamps | Derive from `Feedback.created_at` (max/last activity per meme) | High |
| TR-02 | Trending reflects real activity | Incorrectly implemented | `trending_service.py:95-100` fabricates counts from `usage_count` (`downloads = int(base_usage*0.4)`) when there is no recent activity | No synthetic metrics | Return a "not enough data" ordering by `viral_score` and mark the response accordingly | High |
| TR-03 | Efficient computation | Needs improvement | `get_trending_catalog` loads every meme and runs 2 queries per meme | One aggregated query | `GROUP BY meme_id` over a 24h/7d window; precompute in `scripts/refresh_trending.py` | Medium |
| TR-04 | No fake trending items | Needs improvement | `search_service.get_trending_memes` (`:961-1003`) pads with "Trending Meme #N"; it is exported but unused | Removed | Delete | Low |
| FB-01 | Feedback can't be gamed | Not implemented | `/feedback` has no per-session/action dedupe; repeated `share` (+3.0) inflates `viral_score` without limit | Idempotent per (session, meme, action, window) | Unique window key in Redis; per-route rate limit | Medium |
| FB-02 | Correct vote arithmetic | Incorrectly implemented | `/vote` does `meme.upvotes -= 1` with no floor or NULL guard | Never negative | `max(0, coalesce(upvotes,0)-1)` | Low |
| FB-03 | Format feedback stored | Not implemented | The `fmt` field is accepted, never persisted | Stored for format preference learning | Add a column to `Feedback` | Low |
| FB-04 | Signals not double-counted by the client | Incorrectly implemented | `apps/web/components/meme/MemeCard.tsx:38-45` + `lib/hooks/useDownload.ts:37,52` both send `copy`/`download`; the detail page uses `session_id:'anonymous'` (`MemeDetailClient.tsx:36-56`); a `view` signal is sent for every result (`useMemeSearch.ts:102-108`) | One event per action, real session | Fix the client (see [13](13-user-workflow-gaps.md) WF-09) | High |
| FB-05 | Feedback influences ranking promptly | Partially implemented | Feedback doesn't invalidate the cache or the Qdrant payload (see [04](04-ai-pipeline-gaps.md) AI-09) | Popularity refresh at least hourly | Cron sync | Medium |

## Verification
- Unit tests with fixed `Feedback` timestamps show trending order changes as time advances.
- 100 identical `share` posts from one session raise `viral_score` once.
