# 19 — Testing Gaps

**Source requirements:** `md files/documentation/10_Testing/*` (Testing_Strategy, Backend_Tests, Frontend_Tests, AI_Evaluation, Performance_Tests, Load_Tests), `md files/upgraded_docs/14_Testing_Suite.md`, `md files/completion_fixes/14_Testing_CI_Gaps.md`
**Related:** [20-ci-cd-deployment-gaps](20-ci-cd-deployment-gaps.md) · [22-documentation-and-stub-endpoint-gaps](22-documentation-and-stub-endpoint-gaps.md) · [21-performance-gaps](21-performance-gaps.md)

## Verified facts (read, not executed)
- `backend/tests/` has **142** files.
  - **~22 (≈15%) are pure documentation assertions**, e.g. `test_glossary.py` asserts `total_terms == 41`; `test_deployment_manifest.py` `total_documents == 7`; `test_infrastructure.py` `len(layers) == 4`; `test_ci_cd_pipeline.py` `len(stages) == 4`; `test_backup.py` asserts the string `"7 days (free tier)"`. Others include the `*_manifest`, `*_faq`, `*_readme`, `changelog` and `appendix` tests.
  - **~88 import `app.services.*`**, but many of those services are themselves hardcoded doc dicts ([22](22-documentation-and-stub-endpoint-gaps.md)), so the tests verify copied text, not behaviour.
- **Real behavioural tests (good):** `test_api_memes`, `test_api_search_v2`, `test_cache`, `test_auth`, `test_embeddings_service` (384/896 dims, norm), `test_api_rate_limiting` (headers), `test_background_jobs`, `test_config`.
- The prior report claims "713 passed". **Not re-run in this audit** (the user asked for no local execution), so ASSUMPTION.
- Frontend: 7 test files (Vitest) across `frontend/src` and `apps/web`.
- `services/api/tests/*`: 9-line stubs.

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| TEST-01 | Tests validate behaviour (`Testing_Strategy.md`) | Partially implemented | ~15% doc-assertion tests plus tests of doc-dict services | Mark them `@pytest.mark.doc`, exclude from the quality metrics; delete them with their services | High |
| TEST-02 | Coverage ≥80% (`Backend_Tests.md:97`) | Not enforced | Only `deploy.yml:50` `--cov-fail-under=60`; the PR jobs have no `--cov` | `--cov=app --cov-fail-under=80` on PRs; `omit` the manifest services | High |
| TEST-03 | Security regression tests | Not implemented | No tests for the gaps in [08](08-authentication-gaps.md) and [09](09-security-gaps.md) (anon key issuance, XFF spoof, email relay, purge) | Add a negative test per finding | Critical |
| TEST-04 | API contract tests (`nsfw`, categories, limit) | Not implemented | Would have caught [03](03-search-api-gaps.md) API-01..03 | Add | High |
| TEST-05 | AI evaluation P@5 gate (`AI_Evaluation.md`) | Partially implemented | 3 golden queries; 4 copies of `evaluate.py` | ≥100 labelled queries; CI threshold | Medium |
| TEST-06 | Frontend tests in CI (`Frontend_Tests.md`) | Partially implemented | Only the never-run `workflows-upgraded/ci.yml:95` runs `npm test` | Activate | Medium |
| TEST-07 | E2E tests (search → copy → favorite) | Not implemented | No Playwright/Cypress | Playwright smoke suite on the canonical app | Medium |
| TEST-08 | Mobile tests | Not implemented | See [18](18-mobile-gaps.md) MOB-09 | — | Medium |
| TEST-09 | Load tests with pass criteria (`Load_Tests.md`) | Partially implemented | `locustfile.py` task mix ok, but no thresholds; fake IDs (`meme_042`, `q_loadtest`) → 4xx | Seeded IDs; p95 exit criteria; manual workflow | Medium |
| TEST-10 | Tests isolated from live services | Incorrectly implemented | PR CI passes the real `GROQ_API_KEY`, `QDRANT_URL`, `DATABASE_URL` | Mocks/fixtures | High |
