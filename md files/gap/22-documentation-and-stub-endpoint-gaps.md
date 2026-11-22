# 22 — Documentation Truthfulness & "Manifest" Stub Endpoint Gaps

**Source requirements:** `md files/completion_fixes/00_MASTER_FIX_CHECKLIST.md`, `md files/implementation_guides/00_MASTER_CHECKLIST.md`, `md files/upgraded_docs/00_INDEX.md`, `md files/documentation/13_Project_Management/*` (MVP_Phases, Roadmap, Risk_Register), `md files/documentation/15_FAQs/*`, `md files/prompt.md`
**Related:** [00-gap-analysis-overview](00-gap-analysis-overview.md) · [19-testing-gaps](19-testing-gaps.md) · [09-security-gaps](09-security-gaps.md)

> Per the task rules, **no existing documentation was modified**. These gaps describe what should change later.

## Checkbox census (grep over `md files/`, excluding `gap/`)
| Folder | `[x]` | `[ ]` |
|---|---|---|
| documentation | 10 | 117 |
| completion_fixes | 15 (all in the master table) | 96 |
| implementation_guides | 0 | 40 |
| basic things of project upgraded version (v2) | 0 | 36 |
| basic things of project | 8 | 16 |
| upgraded_docs | 0 | 10 |
| **Total** | **33 (~9.5%)** | **315** |

## Gaps
| Gap ID | Issue | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| DOC-01 | Documentation served as API "features" | Incorrectly implemented | ~300 of 342 routes come from routers such as `marketing`, `project_management`, `appendix`, `references`, `faq`, `features`, `developer`, `deployment`, `testing`, `security`, `rate_limiting`, `mobile`, `troubleshooting`, which return hardcoded dicts copied from docs (e.g. `marketing_manifest_service.py:17-50`, `rate_limiting_security_service.py:19` describes a ZADD limiter that doesn't exist). 11 `*_manifest_service.py` files, 38 hardcoded `"status":"COMPLETED"`. Exceptions with real logic: `marketing/aso/evaluate-rating-prompt` and the docs-sync check | Remove these from `api/v1/__init__.py:12-74` (or move them under `/internal/docs` behind admin); delete the services + their tests | High |
| DOC-02 | Self-attested completion endpoints | Incorrectly implemented | `mvp_phases_service.py:194` returns `"overall_status":"MVP_COMPLETE"`; Sprint 4 is marked done there but ☐ in `MVP_Phases.md` | Delete, or compute from real checks | High |
| DOC-03 | Master checklist accuracy | Incorrectly implemented | `completion_fixes/00_MASTER_FIX_CHECKLIST.md:24-38` marks all 15 `[x]`; disproved by: 01 dual backend exists; 02 corpus 145; 08 not deployed; 13 placeholder Umami ID; 15 no i18n/retrain job | Reset to verified status (link to this gap folder) | Critical (decision-making risk) |
| DOC-04 | Conflicting corpus targets | Inconsistent | FAQ ~1,000 (`General_FAQ.md:25`); completion_fixes 5,000+; impl_guides 50K+; SEO 10,000+ | One target per phase (recommend: 1k MVP → 5k launch → 10k+ SEO scale) | Medium |
| DOC-05 | Deployment status claims | Incorrectly implemented | `MVP_Phases.md` Sprint 3 "memegpt.com live / api.memegpt.com live" | Mark "not deployed" | High |
| DOC-06 | Stale facts | Needs improvement | FAQ "mobile planned Phase 2", `/developer` route that doesn't exist; Risk R1 "Ollama fallback" (no Ollama code); R11 cites Render (target is Railway); Tech_Stack says React 18 (`frontend/package.json:20` uses ^19.1.0); `Scoring_Logic.md` weights ≠ code; Frontend_Overview describes one Next app | Refresh after consolidation | Medium |
| DOC-07 | Feature manifest accuracy | Incorrectly implemented | `feature_manifest_service.py:73-78` marks `visual_search` "active" (`POST /search` has no image input) | "planned" | Medium |
| DOC-08 | Doc volume vs signal | Needs improvement | 206 files / ~44k lines across 6 overlapping tracks (v1 basics, v2 basics, documentation, upgraded_docs, completion_fixes, implementation_guides); `prompt.md` is a doc-generation prompt, not requirements | Designate `documentation/` + this `gap/` folder as canonical; archive the superseded tracks | Low |
| DOC-09 | Prior gap reports out of date | Needs improvement | `GAP-ANALYSIS-2026-10-31.md` claims 195 memes (145 now in `memes.json`) and missing mobile assets (now present) | Mark them superseded by `md files/gap/` | Low |
