# 21 — Performance Gaps

**Source requirements:** `md files/project-vision/01-vision-product.md` §1.3 (search <1.5s), `md files/documentation/10_Testing/Performance_Tests.md` (p50<1s, p95<3s; embedding <100ms; Redis GET <10ms), `Load_Tests.md`, `md files/completion_fixes/15_Non_Functional_Requirements.md`
**Related:** [04-ai-pipeline-gaps](04-ai-pipeline-gaps.md) · [02-backend-core-gaps](02-backend-core-gaps.md) · [16-integrations-gaps](16-integrations-gaps.md) · [19-testing-gaps](19-testing-gaps.md)

> No benchmarks were run in this audit. All latency statements are **ASSUMPTION – needs runtime validation**, but each risk below is grounded in code.

| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| PERF-01 | No blocking I/O in async search | Incorrectly implemented | 2 sequential sync `requests.get(timeout=5)` (`giphy_service.py:43,92`) in `recommend`, so worst case +10s | Async, parallel, ≤800ms, cached | Critical |
| PERF-02 | No full-table loads per request | Incorrectly implemented | `search.py:77` loads all memes each search; `trending_service` runs 2 queries per meme | Use Qdrant payloads; aggregate SQL | High |
| PERF-03 | No per-request DB tier lookup | Needs improvement | `main.py:184-192` | Cache | Medium |
| PERF-04 | Single model copy in memory | Needs improvement | Duplicate MiniLM in `semantic_search.py:26` | Share | Medium |
| PERF-05 | Horizontal scale | Not implemented | `--workers 1` (embedded Qdrant lock + in-memory chat) | Remote Qdrant + Redis sessions | Medium |
| PERF-06 | Latency SLO measured | Partially implemented | `test_performance.py` runs 5 iterations, Giphy patched, warm local index | Staging benchmark (`scripts/benchmark_latency.py`) with ≥200 samples; publish p50/p95 | High |
| PERF-07 | Per-component budgets | Not implemented | Only a cache-hit timing test exists | Timers for embedding, emotion, Groq, Qdrant | Low |
| PERF-08 | Load test thresholds | Partially implemented | See [19](19-testing-gaps.md) TEST-09 | — | Medium |
| PERF-09 | CDN + `next/image` for media | Not implemented | Hotlinked imgflip; raw `<img>` | See [07](07-data-corpus-pipeline-gaps.md) DATA-04, [15](15-seo-marketing-gaps.md) SEO-10 | High |
| PERF-10 | Caching headers | Fully implemented | `apps/web/vercel.json` `/meme/*` `s-maxage=86400`; `/assets` immutable | — | — |
