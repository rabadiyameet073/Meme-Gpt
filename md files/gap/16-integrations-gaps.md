# 16 — Third-Party Integration Gaps (Giphy, Reddit, Imgflip, email, webhooks, push)

**Source requirements:** `md files/documentation/07_APIs/Webhooks.md`, `md files/completion_fixes/13_Monitoring_Analytics.md`, `06_Mobile_App_Completion.md`, `02_Meme_Database_Population.md`, `md files/implementation_guides/04_Meme_Data_Pipeline.md`
**Related:** [09-security-gaps](09-security-gaps.md) · [07-data-corpus-pipeline-gaps](07-data-corpus-pipeline-gaps.md) · [18-mobile-gaps](18-mobile-gaps.md) · [21-performance-gaps](21-performance-gaps.md)

## Verified as implemented
Real Giphy + Imgflip API clients; PRAW Reddit collector; Resend email client (`email_service.py:22-50`); webhook HMAC signing; push-token persistence (`api/v1/mobile.py:126-183`, `apps/mobile/hooks/usePushNotifications.ts:34`).

## Gaps
| Gap ID | Integration | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| INT-01 | Email: send only on system events | Incorrectly implemented | Public send routes (see [09](09-security-gaps.md) SEC-01/02) | Internal triggers only | Critical |
| INT-02 | Email: welcome/share emails on real events | Not implemented | Only `api/v1/email.py:55,84` call the senders; auth and collections never do | Call from the sign-up and collection-share services | Medium |
| INT-03 | Webhooks: real delivery with retries 5s/30s/300s (`Webhooks.md`) | Not implemented (stub) | `webhook_service.py:27` in-memory `_WEBHOOKS_DB`; `:122` "Simulate…" dispatch with hardcoded `"status":"delivered"` | DB model, httpx worker, retry queue, delivery log; emit `meme.trending`/`meme.new` | High |
| INT-04 | Webhooks: auth + SSRF guard | Incorrectly implemented | See [09](09-security-gaps.md) SEC-07 | — | High |
| INT-05 | Giphy: non-blocking, cached | Incorrectly implemented | Synchronous `requests.get` ×2, 5s timeouts each (`giphy_service.py:43,92`) on the search hot path | Async + cache + short timeout | High |
| INT-06 | Giphy attribution ("Powered by GIPHY") | Not implemented | Not found in `apps/` or `frontend/` | Add the badge where Giphy media is shown | Medium |
| INT-07 | Reddit content via official/moderated source | Incorrectly implemented | `meme-api.com/gimme/{sub}` unofficial proxy (`giphy_service.py:89`) | Use PRAW offline ingestion; drop the live proxy | High |
| INT-08 | Corpus collectors executed | Not implemented | No output; only Giphy is scheduled, with `continue-on-error` | See [07](07-data-corpus-pipeline-gaps.md) | Critical |
| INT-09 | Push notifications: sending | Not implemented | No Expo push sender (`exp.host`) anywhere; only registration | Sender service + trending trigger + opt-out | Medium |
| INT-10 | Push token listing protected | Incorrectly implemented | `GET /mobile/push-tokens` is public | Admin only | High |
| INT-11 | Tenor source (`completion_fixes/02`) | Not implemented | No Tenor client | Add or drop from the docs | Low |
