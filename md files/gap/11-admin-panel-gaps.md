# 11 — Admin Panel Gaps

**Source requirements:** `md files/completion_fixes/05_Content_Moderation_NSFW.md`, `12_Missing_API_Endpoints.md` (admin CRUD), `md files/project-vision/01-vision-product.md` §1.9 (KPI dashboard), `md files/documentation/13_Project_Management/Roadmap.md` (P2c analytics dashboard)
**Related:** [08-authentication-gaps](08-authentication-gaps.md) · [10-content-moderation-gaps](10-content-moderation-gaps.md) · [17-reporting-analytics-monitoring-gaps](17-reporting-analytics-monitoring-gaps.md)

## Verified as implemented
- Backend admin CRUD `/admin/memes` behind `require_admin` (`backend/app/api/v1/admin.py:64,82,131,151`).
- The admin UI exists only in the Vite app: `frontend/src/components/AdminTab.tsx:43-140` (meme CRUD, moderation, classification).

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| ADM-01 | Admin UI can call admin APIs | Incorrectly implemented (broken end-to-end) | `frontend/src/lib/api.ts:53-55` sends `Authorization: Bearer <JWT>`; `require_admin` reads only `X-API-Key`, so every admin call → 403 | Accept JWT users with `role=admin` (needs [08](08-authentication-gaps.md) AUTH-05) | Critical |
| ADM-02 | Admin tab hidden from non-admins | Incorrectly implemented | `frontend/src/App.tsx:183` always adds the Admin tab; `:419` renders it with no role check | Render only for admins | High |
| ADM-03 | Audit trail for admin actions | Not implemented | `admin.py` writes only `logger.info` | `admin_audit_log` table (actor, action, target, diff, ts) | Medium |
| ADM-04 | Admin edits re-index and invalidate the cache | Not implemented | Create/patch don't embed or upsert; no cache flush | See [04](04-ai-pipeline-gaps.md) AI-08, [02](02-backend-core-gaps.md) BE-03 | High |
| ADM-05 | KPI / metrics dashboard | Not implemented | No metrics view in either frontend | See [17](17-reporting-analytics-monitoring-gaps.md) RPT-02 | Medium |
| ADM-06 | DMCA and flag queue management | Partially implemented | Flags exist; DMCA is CLI only | See [10](10-content-moderation-gaps.md) MOD-07 | Medium |
| ADM-07 | User management (role change, ban, key revoke) | Not implemented | Admin routes for keys exist (`auth.py:118,126,133`), none for users | `/admin/users` list/role/ban | Low |
