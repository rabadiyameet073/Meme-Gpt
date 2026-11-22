# 09 — Security Gaps (rate limiting, exposure, injection, secrets)

**Source requirements:** `md files/documentation/11_Security/*` (API_Security, Rate_Limiting_Security, Data_Privacy, Input_Validation), `md files/upgraded_docs/12_Security_Fixes.md`, `md files/documentation/07_APIs/Rate_Limiting.md`, `Webhooks.md`
**Related:** [08-authentication-gaps](08-authentication-gaps.md) · [10-content-moderation-gaps](10-content-moderation-gaps.md) · [16-integrations-gaps](16-integrations-gaps.md) · [22-documentation-and-stub-endpoint-gaps](22-documentation-and-stub-endpoint-gaps.md)

## Verified as fully implemented
Security headers + CSP + HSTS (`main.py:241-258`); CORS explicit allowlist (`config.py:213-237`); input length caps and sanitisation; weak-secret startup guard; webhook HMAC signing with constant-time compare (`webhook_service.py:35-52`); admin routes behind `require_admin` (`admin.py:64,82,131,151`; `moderation.py:54,88,128`).

## Gaps (ordered by severity)
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| SEC-01 | Email cannot be abused as a relay | Incorrectly implemented | `api/v1/email.py:52-114`: 5 POST routes with no auth; `/email/test` accepts any `to_email`, `subject`, `html_content`, sent from `notifications@memegpt.com` | Remove public send routes; trigger emails only from internal events; admin-only test route | Critical |
| SEC-02 | Magic links server-generated | Incorrectly implemented | `email.py:81-84` mails whatever `magic_link` the client supplies, a ready-made phishing tool | Generate signed expiring tokens server-side | Critical |
| SEC-03 | Destructive privacy endpoints protected | Incorrectly implemented | `POST /privacy/purge-expired` (`privacy.py:105`) has no auth and accepts `days>=1`; `/privacy/export` and `/privacy/delete` accept any `session_id` | `require_admin` on purge; prove session ownership (signed session cookie) | Critical |
| SEC-04 | Rate limit cannot be bypassed | Incorrectly implemented | `main.py:174-176` trusts the first `X-Forwarded-For` value; `main.py:203` gives each random `X-API-Key` its own bucket | Trust XFF only from known proxies; rate-limit invalid keys by IP | Critical |
| SEC-05 | Correct sliding-window limiter (`Rate_Limiting_Security.md`: ZADD/ZCARD) | Incorrectly implemented | `core/cache.py:296-299` `INCR` + `EXPIRE` on every request resets the TTL, so steady clients stay blocked forever; fixed window; fails open | ZSET sliding window, or EXPIRE only when count==1 | Critical |
| SEC-06 | Distributed limiter in prod | Partially implemented | Redis optional; in-memory per-process fallback (`core/rate_limit.py`) | Require Redis when `APP_ENV=production` | High |
| SEC-07 | Webhooks: ownership + SSRF safety | Incorrectly implemented | `webhooks.py:46,67,82,98` use `optional_auth`, so all anonymous users share `owner_id="anonymous"`; `webhook_service.py:63` only checks the `http(s)` prefix | Require an API key; HTTPS only; block private/metadata IPs | High |
| SEC-08 | HTML email escaping | Not implemented | `email_service.py:57,74-78,111-113` put `username`, `sender_name` and `alert_message` into f-strings unescaped | `html.escape` / Jinja autoescape | High |
| SEC-09 | JSON-LD XSS-safe | Incorrectly implemented | `apps/web/app/meme/[slug]/page.tsx:92-104` raw `JSON.stringify` inside `dangerouslySetInnerHTML` | Escape `<` as `<` | High |
| SEC-10 | Minimal attack surface | Needs improvement | ~342 routes ×4 mounts, most of them doc "manifest" routes ([22](22-documentation-and-stub-endpoint-gaps.md)); public `/health/sentry-test` | Remove doc routes; one mount | High |
| SEC-11 | Unauthenticated push-token listing | Incorrectly implemented | `GET /mobile/push-tokens` has no auth | Admin only | High |
| SEC-12 | SSRF in NSFW URL fetch | Partially implemented | `nsfw_service.py:86` `requests.get(url)` (admin-only) | Host allowlist; restrict `image_path` to the media dir | Medium |
| SEC-13 | CI secrets not exposed to PR runs | Needs improvement | `.github/workflows/ci.yml` passes the real `DATABASE_URL`, `GROQ_API_KEY`, `QDRANT_URL` into PR tests | Mocks + SQLite in CI; secrets only on `main` | High |
| SEC-14 | Security scanning active | Not implemented | `security.yml` exists only in `.github/workflows-upgraded/` (never runs) | Move it to `workflows/` | Medium |
| SEC-15 | Literal fallback secrets | Needs improvement | See [02](02-backend-core-gaps.md) BE-06 | Remove | Medium |

## Verification
Pen-test checklist: anonymous `POST /email/test` → 401; `purge-expired` anonymous → 401; 200 requests with random `X-API-Key` → 429 after the limit; spoofed XFF ignored; webhook to `http://169.254.169.254` rejected.
