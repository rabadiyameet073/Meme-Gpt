# 20 — CI/CD & Deployment Gaps

**Source requirements:** `md files/documentation/12_Deployment/*` (Deployment_Overview, CI_CD_Pipeline, Rollback_Strategy, Monitoring, Infrastructure), `md files/upgraded_docs/16_CI_CD_Deployment.md`, `01_Environment_Setup.md`, `md files/completion_fixes/08_Production_Deployment.md`, `md files/implementation_guides/06_Deployment_Railway_Vercel.md`, `07_CI_CD_GitHub_Actions.md`, `09_Environment_Variables_Final.md`
**Related:** [01-architecture-consolidation-gaps](01-architecture-consolidation-gaps.md) · [19-testing-gaps](19-testing-gaps.md) · [06-database-gaps](06-database-gaps.md) · [17-reporting-analytics-monitoring-gaps](17-reporting-analytics-monitoring-gaps.md)

## Verified facts
- **Not deployed**, as far as the repo shows: no live-URL evidence; `implementation-report/00-status-overview.md` lists "live URLs + domains" as remaining. `MVP_Phases.md` claims `memegpt.com live`, which is false ([22](22-documentation-and-stub-endpoint-gaps.md) DOC-05).
- Implemented correctly: `--workers 1` with the reason documented and `healthcheckPath=/api/v1/health` (both `railway.toml`); prod secret guard; `dependabot.yml` active; caching headers in `apps/web/vercel.json` and `frontend/vercel.json`.

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| CI-01 | One active workflow set | Incorrectly implemented | GitHub runs only `.github/workflows/`; the fixes live in `.github/workflows-upgraded/` (`ci.yml`, `cron.yml`, `index.yml`, `test.yml`, `weekly_reindex.yml` differ; `security.yml` exists only there) | Move upgraded → `workflows/`; delete the folder | Critical |
| CI-02 | PR pipeline passes | Incorrectly implemented (likely red) | `workflows/ci.yml:45-47` runs `npm run lint`/`build` at the root, but the root `package.json` has neither | Use the upgraded `ci.yml` (`working-directory`) | Critical |
| CI-03 | Single deploy path | Incorrectly implemented | `ci_cd.yml` (service `memegpt-backend`), `deploy.yml` (`memegpt-api`) and `test.yml` all deploy on push to main, in parallel | One `deploy.yml`, one service name | Critical |
| CI-04 | Post-deploy smoke test (`CI_CD_Pipeline.md:106-112`) | Not implemented | No smoke job | `curl -f /api/v1/health` + frontend | High |
| CI-05 | Deploy fails loudly without secrets | Needs improvement | `deploy.yml:102` `if: env.RAILWAY_TOKEN != ''`, so a missing secret gives a silent green | Fail on main | Medium |
| CI-06 | Blocking lint | Needs improvement | flake8 `continue-on-error: true` (`ci_cd.yml`); full ruff likely red | One linter, blocking rule set | Medium |
| CI-07 | Migrations in every deploy | Partially implemented | `deploy.yml` runs `migrate.py`; `ci_cd.yml` doesn't | Covered by CI-03 + Alembic ([06](06-database-gaps.md) DB-03) | Medium |
| DEP-01 | Railway build works from the repo root | Incorrectly implemented (likely) | Root `railway.toml` → `backend/Dockerfile`, which `COPY requirements.txt .` (no root file). ASSUMPTION: works if the Railway root dir = `backend` | Set the root dir or use the root `Dockerfile` | Critical |
| DEP-02 | `services/api/Dockerfile` | Incorrectly implemented | `COPY ../../backend/...` (outside the context) | Delete ([01](01-architecture-consolidation-gaps.md) ARC-01) | High |
| DEP-03 | One Dockerfile per service | Needs improvement | Root `Dockerfile` ≈ `backend/Dockerfile`; two `railway.toml` | Consolidate | Medium |
| DEP-04 | Models baked into the image | Partially implemented | Download step ends with `\|\| true` | Remove `\|\| true`; fail the build | Medium |
| DEP-05 | Container hardening | Needs improvement | Runs as root; no `HEALTHCHECK` | Non-root `USER`; `HEALTHCHECK` | Low |
| DEP-06 | docker-compose parity | Incorrectly implemented | Sets `ENVIRONMENT` (app reads `APP_ENV`) and `QDRANT_HOST` (app reads `QDRANT_URL`), so the qdrant container is probably unused (ASSUMPTION) | Fix the env names; pin the Redis version | High |
| DEP-07 | One frontend deploy + one API URL | Incorrectly implemented | 3 `vercel.json`; `ci_cd.yml` uses `VITE_API_URL=https://memegpt.railway.app/api/v1`, `deploy.yml` uses `https://api.memegpt.com` | After D-1 | High |
| DEP-08 | Production Postgres + Redis + Qdrant Cloud + R2 provisioned | Not implemented | No evidence; `.env` not present; only `frontend/.env.*` with `VITE_API_URL` | User provisions; set the env in Railway/Vercel | Critical |
| DEP-09 | Rollback procedure (`Rollback_Strategy.md`) | Partially implemented (documentation only) | No workflow/script; manual UI rollback | `workflow_dispatch` rollback, or document as manual | Low |
| ENV-01 | `.env.example` complete | Partially implemented | ~60 keys; missing `QDRANT_HOST`, `QDRANT_PORT`, `QDRANT_LOCAL_PATH`, `EXPO_PUBLIC_API_URL`, `EXPO_PUBLIC_EAS_PROJECT_ID` | Add them | Medium |
