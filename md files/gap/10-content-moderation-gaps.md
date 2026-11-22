# 10 — Content Moderation, NSFW & DMCA Gaps

**Source requirements:** `md files/completion_fixes/05_Content_Moderation_NSFW.md`, `md files/upgraded_docs/12_Security_Fixes.md` (FIX 4), `md files/documentation/11_Security/*`
**Related:** [03-search-api-gaps](03-search-api-gaps.md) · [07-data-corpus-pipeline-gaps](07-data-corpus-pipeline-gaps.md) · [11-admin-panel-gaps](11-admin-panel-gaps.md) · [09-security-gaps](09-security-gaps.md)

## Verified facts
- NSFW classification is a **real** CLIP zero-shot classifier (`backend/app/services/nsfw_service.py:35-75`), not a stub.
- It is used only by the admin endpoint `POST /moderation/classify` (`moderation.py:128`).
- User flagging exists (`moderation.py:20-49`); 5 flags auto-hide a meme.
- The DMCA CLI script `scripts/dmca_takedown.py` removes from the DB, Qdrant and R2.

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| MOD-01 | Classifier fails closed | Incorrectly implemented | `nsfw_service.py:54-55,79,96-99` return `(False, 0.0, "safe content")` when the model is missing or errors | Return `unknown` → `pending_review` | High |
| MOD-02 | NSFW filtered from search by default | Not implemented | `api/v1/search.py:16` filters only `moderation_status != "removed"`; `pending_review` is still served; the request `nsfw` flag is dropped ([03](03-search-api-gaps.md) API-01) | Filter `nsfw=true` unless opted in; exclude `pending_review` in both the SQL and the Qdrant filter | Critical |
| MOD-03 | Classify every meme at ingestion | Not implemented | No ingestion/index script imports `nsfw_service` | Pipeline step before indexing ([07](07-data-corpus-pipeline-gaps.md) DATA-06) | High |
| MOD-04 | Live third-party content is moderated | Not implemented | `giphy_service.py:89` pulls `meme-api.com/gimme/{sub}` (an unofficial Reddit proxy) into results with no NSFW/spoiler filter; Giphy rating not enforced (ASSUMPTION) | Filter `nsfw`/`spoiler`; Giphy `rating=pg-13`; or drop the live sources | High |
| MOD-05 | Flag abuse resistance | Incorrectly implemented | Anonymous flags, no dedupe; 5 flags hide any meme | Unique `(meme_id, reporter_hash)`; rate limit; hidden pending review, not removed | High |
| MOD-06 | Reporter privacy | Incorrectly implemented | `MemeFlag.reporter_ip` stores the raw IP (`database.py:~482`) | Hash/truncate; include in retention | Medium |
| MOD-07 | DMCA workflow (notice → takedown → counter-notice) | Partially implemented | CLI only; no API, no notice log, no CDN/Redis purge | Admin endpoint + `dmca_notices` table + cache purge + public DMCA contact page | Medium |
| MOD-08 | Moderation queue UI | Partially implemented | `frontend/src/components/AdminTab.tsx` has moderation actions but the backend rejects JWT admins ([11](11-admin-panel-gaps.md) ADM-01) | Working queue | High |
