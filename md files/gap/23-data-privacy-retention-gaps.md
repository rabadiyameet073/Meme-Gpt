# 23 — Data Management, Privacy & Retention Gaps

**Source requirements:** `md files/documentation/11_Security/Data_Privacy.md`, `md files/upgraded_docs/12_Security_Fixes.md` (FIX 2), `md files/completion_fixes/15_Non_Functional_Requirements.md`, `md files/documentation/06_Database/Backup.md`
**Related:** [06-database-gaps](06-database-gaps.md) · [09-security-gaps](09-security-gaps.md) · [10-content-moderation-gaps](10-content-moderation-gaps.md) · [07-data-corpus-pipeline-gaps](07-data-corpus-pipeline-gaps.md)

## Verified as implemented
Search queries hashed before storage (`database.py:596,611-616`); 30-day retention job scheduled via APScheduler (`jobs/retention.py:12`, `main.py:82-94`; whether it fires is ASSUMPTION); PII hashing in logs; Sentry `send_default_pii=False`.

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| PRIV-01 | One retention period (30 days) | Incorrectly implemented | `privacy.py:30` `PurgeRequest` defaults to 90 days vs 30 in `retention.py` | One constant in config | Medium |
| PRIV-02 | Retention covers every PII table | Partially implemented | Ignores `meme_flags.reporter_ip` and `meme_usage` | Extend | Medium |
| PRIV-03 | GDPR erasure is complete | Partially implemented | `privacy.py:124-160` skips api_keys, device_tokens, favourite_memes, meme_flags; matches search logs by `session_id == user_id` (likely the wrong key) | Cascade across all user-linked tables; fix the key | High |
| PRIV-04 | Erasure/export require proof of identity | Incorrectly implemented | Any `session_id` accepted (see [09](09-security-gaps.md) SEC-03) | Authenticated user or signed session | Critical |
| PRIV-05 | Raw IPs not stored | Incorrectly implemented | `MemeFlag.reporter_ip` raw | Hash/truncate | Medium |
| PRIV-06 | Privacy policy page | Not implemented (apps/web) | No `/privacy` route (Vite has a `PrivacyView`) | Publish on the canonical site | High |
| PRIV-07 | Cookie/analytics consent | ASSUMPTION – needs review | Umami is cookieless (OK); no consent UI found | Confirm by jurisdiction; document it | Low |
| PRIV-08 | i18n (`completion_fixes/15`) | Not implemented | No i18n library in either frontend | Defer to the P2 roadmap; fix the checklist | Low |
| PRIV-09 | Backup encryption + retention policy | Not implemented | See [06](06-database-gaps.md) DB-06 | — | High |
