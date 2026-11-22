# 08 — Authentication & Authorisation Gaps

**Source requirements:** `md files/completion_fixes/04_User_Authentication_OAuth.md`, `md files/upgraded_docs/08_Auth_Middleware_Fix.md`, `md files/documentation/07_APIs/Authentication.md`, `md files/documentation/11_Security/*`
**Related:** [09-security-gaps](09-security-gaps.md) · [11-admin-panel-gaps](11-admin-panel-gaps.md) · [12-frontend-web-gaps](12-frontend-web-gaps.md)

## Verified as fully implemented
- bcrypt password hashing (`services/jwt_service.py:22-41`).
- API keys stored as SHA-256 hashes, raw key shown once (`core/auth.py:95,148-177`).
- Bootstrap API keys from env only, disabled outside dev (`core/auth.py:53-81`).
- httpOnly + Secure + SameSite=lax cookies (`core/auth.py:331-338`).
- Google/GitHub OAuth flows exist in the backend (`services/oauth_service.py`, `api/v1/auth.py:171-191`), and the Vite frontend calls them (`frontend/src/lib/auth.ts`).

## Gaps
| Gap ID | Requirement | Status | Evidence | Expected | Required change | Priority |
|---|---|---|---|---|---|---|
| AUTH-01 | OAuth CSRF protection | Not implemented | `oauth_service.py:40-95` builds the auth URLs without `state`; the callbacks take only `code` | `state` (+PKCE) generated and verified | Sign `state` in a short-lived cookie; verify in the callback | Critical |
| AUTH-02 | Safe account linking | Incorrectly implemented | `auth.py:_oauth_login` links by email to an existing password account; `oauth_service.py:124` takes the GitHub primary email without checking `verified` | Only verified emails; no silent takeover | Require `verified`; require password confirmation before linking | Critical |
| AUTH-03 | API-key issuance scoped to the caller | Incorrectly implemented | `POST /auth/api-keys` (`auth.py:49-70`) works anonymously, takes `user_id=body.user_id`, allows a self-issued `pro` tier | Authenticated user, own keys only, free tier by default | `Depends(require_user)`; ignore `body.user_id` unless the caller is an admin; block `pro` | Critical |
| AUTH-04 | Key listing/revoke isolation | Incorrectly implemented | `auth.py:80`: anonymous → no filter, so all keys are listed (masked); `auth.py:97` revoke passes when both are `None` | Strict ownership | Require auth; compare non-null IDs | Critical |
| AUTH-05 | User roles / RBAC (`upgraded_docs/08`) | Not implemented | `User` has only `plan` (`database.py:516`); `require_admin` (`core/auth.py:234`) checks API-key tier only | `User.role` and JWT admins | Add a role column plus `require_role("admin")` that accepts a JWT or API key | High |
| AUTH-06 | Test-key shortcut removed | Incorrectly implemented | `core/auth.py:~207`: unknown keys with prefix `pk_test_`/`mgpt_test_` get the free tier at 120/min | Rejected outside tests | Guard with `APP_ENV == "test"` | Medium |
| AUTH-07 | Refresh-token revocation / rotation | Not implemented | `auth.py:359` logout only deletes cookies; refresh JWTs live 7 days, stateless | Revocable families | Store `jti` in Redis/DB; rotate on refresh; revoke on logout or reuse | Medium |
| AUTH-08 | One JWT implementation | Needs improvement | `core/auth.py:241-328` custom HMAC JWT fallback alongside python-jose | One library | Delete the custom codec and the literal fallback secrets | Medium |
| AUTH-09 | Password policy + brute-force protection | Partially implemented | `RegisterRequest.password min_length=6`; no login lockout | ≥8–12 characters; per-IP/account throttling | Add a policy and a `/auth/login` limiter | High |
| AUTH-10 | Web (Next.js) auth (`completion_fixes/04:24`) | Not implemented | `apps/web/app/api/auth/[...nextauth]/route.ts` returns `'Auth disabled in dev mode'`; `next-auth` is not a dependency | Real auth or no route | Depends on decision D-1 ([01](01-architecture-consolidation-gaps.md)) | High |
| AUTH-11 | Token storage on the client | Needs improvement | `frontend/src/lib/auth.ts:15-39` keeps access and refresh tokens in `localStorage` | httpOnly cookies (already supported by the backend) | Use the cookie mode; drop localStorage | High |

## Verification
- Security tests: CSRF state mismatch → 400; anonymous `POST /auth/api-keys` → 401; user A cannot list or revoke user B's keys; a JWT admin can reach `/admin/*`.
