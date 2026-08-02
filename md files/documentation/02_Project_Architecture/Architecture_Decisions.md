# MemeGPT — Architecture Decision Records (ADRs)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Captures key architectural decisions using the ADR format: **Context → Decision → Consequences**. Each ADR is immutable once accepted — superseded decisions get a new ADR referencing the old one.

---

## Background

Architecture decisions are documented here to:
- **Explain "why"** to future contributors and the developer's future self
- **Prevent repeated debates** about settled decisions
- **Track trade-offs** so they can be revisited when constraints change
- **Provide context** for code review discussions

---

## ADR-001: Use FastAPI over Flask/Django

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Need a Python API framework that supports async operations, auto-generates API docs, and integrates well with ML libraries (sentence-transformers, HuggingFace). Must serve <1.5s response times under concurrent load. |
| **Options Considered** | Flask (mature, large community), Django REST Framework (batteries-included), FastAPI (modern async), Starlette (minimal) |
| **Decision** | Use FastAPI with Uvicorn ASGI server. |
| **Consequences** | ✅ Native async support for concurrent Groq + Qdrant calls, ✅ Auto-generated Swagger UI at `/docs`, ✅ Pydantic validation with type hints, ✅ 3× faster than Flask under load (ASGI vs WSGI), ✅ Lifespan hooks for ML model loading. ❌ Smaller ecosystem than Flask/Django. ❌ Fewer tutorials for beginners. |
| **Validation** | Benchmark showed 2,100 req/s (FastAPI) vs 700 req/s (Flask) for the `/health` endpoint. |

---

## ADR-002: Use Qdrant over Pinecone/ChromaDB

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Need a vector database with: (a) free tier ≥1M vectors, (b) named vector support for separate text/image/combined spaces, (c) payload filtering for NSFW/format/category. |
| **Options Considered** | Pinecone (popular, expensive), ChromaDB (simple, no cloud), Weaviate (good but complex), Qdrant Cloud (free 1GB) |
| **Decision** | Use Qdrant Cloud (1GB free tier, 1M vectors). |
| **Consequences** | ✅ Free 1GB cluster (1M vectors), ✅ Named vectors (text/image/combined — 3 search spaces), ✅ Rich payload filtering with `must`/`should` conditions, ✅ HNSW tunable parameters (`m`, `ef_construct`). ❌ Smaller community than Pinecone. ❌ Migration is non-trivial (proprietary protocol). ❌ No free tier backup — data loss requires re-indexing. |
| **Validation** | 50ms average search latency across 10K vectors with `ef=128`. |

---

## ADR-003: Use MiniLM-L6-v2 for Text Embeddings

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Need a text embedding model that: (a) runs on CPU, (b) fits in 512MB free-tier hosting, (c) generates good semantic similarity, (d) is fast enough for real-time inference (<100ms). |
| **Options Considered** | |

| Model | Size | Dims | Speed (CPU) | MTEB Score |
|---|---|---|---|---|
| **MiniLM-L6-v2** ✅ | 80 MB | 384 | 14K sent/s | 0.630 |
| mpnet-base-v2 | 420 MB | 768 | 2.8K sent/s | 0.654 |
| BGE-small | 134 MB | 384 | 10K sent/s | 0.640 |
| GTE-small | 67 MB | 384 | 15K sent/s | 0.635 |

| | |
|---|---|
| **Decision** | Use `sentence-transformers/all-MiniLM-L6-v2` (80MB, 384-dim). |
| **Consequences** | ✅ Only 80MB — fits in free-tier RAM alongside other models, ✅ 14K sentences/sec on CPU (~50ms per query), ✅ Top-5 on MTEB benchmark for its size class, ✅ Apache 2.0 license. ❌ 2-4% lower accuracy than larger models (mpnet, BGE-large). ❌ 384-dim may under-represent very complex semantic relationships. |
| **Revisit When** | Dataset exceeds 100K memes — may upgrade to `gte-large` or fine-tune MiniLM on meme-specific pairs. |

---

## ADR-004: Use Groq for LLM Inference

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Need LLM inference for intent parsing with: (a) free tier ≥1K req/day, (b) sub-500ms latency, (c) structured JSON output, (d) no GPU required on server. |
| **Options Considered** | |

| Provider | Model | Free Limit | Speed | Quality |
|---|---|---|---|---|
| **Groq** ✅ | Llama 3.1 8B | 6K req/day | 500+ tok/s | Good |
| OpenAI | GPT-4o-mini | $5 free | 50 tok/s | Excellent |
| Google | Gemini Flash | 1M tok/day | 100 tok/s | Good |
| Together AI | Llama 3 8B | $25 credit | 200 tok/s | Good |
| Ollama (local) | Llama 3.2 3B | Unlimited | CPU speed | Fair |

| | |
|---|---|
| **Decision** | Primary: Groq API (Llama 3.1 8B Instant). Fallback: Ollama (local). |
| **Consequences** | ✅ 6K requests/day free (covers ~200 active users), ✅ 500+ tokens/sec (fastest cloud inference), ✅ Open model (Llama — no vendor lock-in), ✅ ~300ms per intent parse. ❌ Vendor dependency on Groq infrastructure. ❌ No fine-tuning available on Groq. ❌ Rate limit (30 req/min) requires caching strategy. |

---

## ADR-005: Monorepo over Multi-Repo

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Solo developer managing backend (Python), frontend (Next.js), mobile (React Native), data pipeline, and documentation. Need simplest possible dev workflow. |
| **Decision** | Single Git repository with directory-based separation (`apps/`, `services/`, `data/`, `docs/`). |
| **Consequences** | ✅ Single `git clone` to start, ✅ Single CI/CD pipeline, ✅ Shared TypeScript types between web and mobile, ✅ Atomic commits across frontend + backend. ❌ Larger repository size over time. ❌ All services share Git history (noisy log). ❌ CI runs all checks even for single-service changes (mitigated by path filters). |

---

## ADR-006: SQLite (Dev) + PostgreSQL (Prod) via Prisma

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Need zero-config database for rapid development with production-grade alternative for deployment. |
| **Decision** | SQLite via Prisma for development, Supabase PostgreSQL for production. Same Prisma schema, different providers. |
| **Consequences** | ✅ Zero setup for dev (no Docker, no installs), ✅ Same Prisma schema for both, ✅ Supabase free tier (500MB, built-in auth, realtime). ❌ Minor SQL dialect differences (no GIN indexes in SQLite, TEXT[] not supported). ❌ Must test on PostgreSQL before release. ❌ Migrations may diverge. |
| **Migration Path** | `prisma db push` for dev, `prisma migrate deploy` for prod. |

---

## ADR-007: Weighted Vector Combination (65% Text + 35% Image)

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Memes have both textual (OCR, captions, tags) and visual (image content) information. How to combine for search? |
| **Options Considered** | (a) Separate searches + merge, (b) Late fusion (rerank), (c) **Early fusion (weighted concatenation)** |
| **Decision** | Create a combined 896-dim vector (384-dim text × 0.65 + 512-dim image × 0.35), L2-normalized. Store separate vectors for specialized searches. |
| **Consequences** | ✅ Single vector search (fastest), ✅ Text-weighted (matches how users search — by meaning, not by image), ✅ Can fall back to text-only vector if image unavailable. ❌ Fixed weights — may need per-category tuning. ❌ 896-dim is larger than optimal for HNSW (slower indexing). |
| **Revisit When** | A/B testing reveals image-heavy searches underperform. |

---

## ADR-008: Cloudflare R2 over AWS S3

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Need object storage for meme files (GIF, PNG, MP4, WebP). Must be cheap, S3-compatible, with built-in CDN. |
| **Decision** | Cloudflare R2 with custom domain CDN (`cdn.memegpt.com`). |
| **Consequences** | ✅ 10GB free storage, ✅ **Zero egress costs** (S3 charges $0.09/GB), ✅ S3-compatible API (boto3 works), ✅ Built-in CDN with 300+ edge locations. ❌ Newer service, smaller community. ❌ Cloudflare ecosystem lock-in. ❌ No lifecycle policies (manual cleanup needed). |

---

## ADR-009: Upstash Redis over Self-Hosted Redis

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Need caching layer for search results and rate limiting. Must work with serverless/free-tier hosting. |
| **Decision** | Use Upstash Redis (serverless, 10K commands/day free). |
| **Consequences** | ✅ No infrastructure to manage, ✅ REST + Redis protocol support, ✅ Global replication available. ❌ 10K commands/day may be limiting at scale. ❌ ~5ms latency vs ~1ms for local Redis. |

---

## ADR-010: Dark-First Design over Light Default

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-01-01 |
| **Context** | Memes are consumed on dark platforms (Discord, Reddit, Twitter dark mode). Users share memes in dark-themed messaging apps. |
| **Decision** | Dark mode is the default. Light mode available but secondary. |
| **Consequences** | ✅ Matches user expectations — memes look best on dark backgrounds, ✅ Reduces eye strain for heavy users, ✅ Purple + amber brand colors pop on dark (#0A0A0A). ❌ Accessibility considerations for low-contrast text. ❌ Must ensure WCAG AA compliance on dark backgrounds. |

---

## Decision Summary

| ADR | Decision | Key Trade-off |
|---|---|---|
| 001 | FastAPI | Speed over community size |
| 002 | Qdrant Cloud | Named vectors over ecosystem maturity |
| 003 | MiniLM-L6-v2 | Speed + size over maximum accuracy |
| 004 | Groq API | Free tier + speed over fine-tuning |
| 005 | Monorepo | Simplicity over isolation |
| 006 | SQLite + PostgreSQL | Zero-config dev over consistency |
| 007 | 65/35 vector fusion | Single search over flexibility |
| 008 | Cloudflare R2 | Zero egress over maturity |
| 009 | Upstash Redis | Serverless over raw speed |
| 010 | Dark-first design | User context over convention |

---

> **Related Documents:**
> - [Design_Principles.md](./Design_Principles.md) — Principles behind these decisions
> - [High_Level_Architecture.md](./High_Level_Architecture.md) — How decisions map to architecture
> - [Tech_Stack.md](./Tech_Stack.md) — Detailed tech stack reference
