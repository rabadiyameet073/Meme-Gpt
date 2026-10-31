# MemeGPT — Technology Stack Reference

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete catalog of every technology used in MemeGPT, with rationale for selection, alternatives considered, and configuration details. This document fulfills the prompt.md Phase 6 requirement to document every technology with: what it is, why it is used, why it was selected, benefits, limitations, alternatives, configuration, and best practices.

---

## Backend Technologies

### Python 3.11

| Aspect | Details |
|---|---|
| **What it is** | General-purpose programming language |
| **Why it is used** | Backend API development and ML model inference |
| **Why selected** | Best ML/AI ecosystem (PyTorch, HuggingFace, sentence-transformers) |
| **Benefits** | Huge library ecosystem, async support, type hints |
| **Limitations** | GIL limits true parallelism, slower than Go/Rust |
| **Alternatives considered** | Node.js (poor ML support), Go (no HuggingFace), Rust (complex) |
| **Configuration** | `python 3.11+`, virtual environment via `venv` |
| **Best practices** | Use type hints, async for I/O, thread pool for CPU work |

### FastAPI

| Aspect | Details |
|---|---|
| **What it is** | Modern Python web framework for building APIs |
| **Why it is used** | HTTP API serving for MemeGPT backend |
| **Why selected** | Auto-docs (Swagger), Pydantic validation, async support, high performance |
| **Benefits** | Type-safe, auto-generated docs, dependency injection, WebSocket support |
| **Limitations** | Smaller community than Flask/Django, fewer battle-tested plugins |
| **Alternatives considered** | Flask (no async), Django (too heavy), Express.js (wrong language) |
| **Configuration** | `pip install fastapi uvicorn`, run with `uvicorn app.main:app` |
| **Best practices** | Thin route handlers, service layer pattern, Pydantic models for I/O |

### Uvicorn

| Aspect | Details |
|---|---|
| **What it is** | ASGI web server for running FastAPI |
| **Why it is used** | Serves the FastAPI application |
| **Why selected** | Fastest Python ASGI server, async-native |
| **Configuration** | `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1` |

---

## Frontend Technologies

### React 18

| Aspect | Details |
|---|---|
| **What it is** | JavaScript UI library for building user interfaces |
| **Why it is used** | Web app UI for MemeGPT |
| **Why selected** | Largest ecosystem, component reuse with React Native, hooks-based state |
| **Benefits** | Component model, virtual DOM, massive ecosystem, React Native sharing |
| **Limitations** | Not a full framework (need routing, state management), JSX learning curve |
| **Alternatives considered** | Vue.js (smaller ecosystem), Svelte (less mature), Angular (too heavy) |
| **Best practices** | Functional components, hooks, memoization for performance |

### Vite 5

| Aspect | Details |
|---|---|
| **What it is** | Fast build tool and dev server for modern web apps |
| **Why it is used** | Development server and production bundler |
| **Why selected** | Sub-second HMR, ESBuild for transforms, Rollup for production |
| **Benefits** | 10–100x faster than Webpack, native ESM, simple config |
| **Alternatives considered** | Webpack (slow), Parcel (less control), Turbopack (not stable) |
| **Configuration** | `vite.config.ts` with React plugin |

### Next.js 14

| Aspect | Details |
|---|---|
| **What it is** | React framework with SSR, SSG, and API routes |
| **Why it is used** | SEO pages for individual memes, server-side rendering |
| **Why selected** | Best React framework for SEO, Vercel integration, App Router |
| **Benefits** | SSG for meme pages, ISR for freshness, image optimization, API routes |
| **Limitations** | Heavier than Vite for pure SPA, Vercel-centric |

### TailwindCSS 3

| Aspect | Details |
|---|---|
| **What it is** | Utility-first CSS framework |
| **Why it is used** | Rapid UI styling with consistent design tokens |
| **Why selected** | Fast prototyping, small production bundle (purged), responsive utilities |
| **Alternatives considered** | Vanilla CSS (slower dev), CSS Modules (verbose), Styled Components (runtime) |

---

## AI/ML Technologies

### sentence-transformers (MiniLM-L6-v2)

| Aspect | Details |
|---|---|
| **What it is** | Python library for computing dense text embeddings |
| **Why it is used** | Convert text to 384-dim vectors for semantic search |
| **Why selected** | Best quality/size ratio, runs on CPU, free, 50ms inference |
| **Benefits** | 22MB download, L2-normalized output, 256-token input |
| **Limitations** | English-only (multi-lingual variant exists), max 256 tokens |
| **Alternatives** | OpenAI ada-002 (paid), BGE-large (1.3GB), E5-large (slow) |

### Groq Cloud (Llama 3.1 8B)

| Aspect | Details |
|---|---|
| **What it is** | AI inference cloud with ultra-fast LPU chips |
| **Why it is used** | Intent parsing — extracting emotion, situation, tone from queries |
| **Why selected** | 6,000 free requests/day, ~200ms inference, adequate quality |
| **Benefits** | Free tier, fastest inference, Llama 3.1 quality, JSON mode |
| **Limitations** | 30 req/min rate limit, no fine-tuning, may change pricing |
| **Alternatives** | OpenAI (expensive), Ollama (requires GPU), Together.ai (slower free) |

### Qdrant

| Aspect | Details |
|---|---|
| **What it is** | Open-source vector database for similarity search |
| **Why it is used** | Store and search meme embeddings (text + image) |
| **Why selected** | 1GB free cloud tier, named vectors, payload filtering, HNSW index |
| **Benefits** | Named vector support (text/image/combined), efficient filtering, gRPC API |
| **Limitations** | Smaller community than Pinecone, fewer managed features |
| **Alternatives** | Pinecone (limited free), Weaviate (heavier), ChromaDB (no cloud) |

### HuggingFace Transformers

| Aspect | Details |
|---|---|
| **What it is** | Library for pre-trained ML models |
| **Why it is used** | Emotion detection (DistilRoBERTa), BLIP captioning, CLIP embeddings |
| **Why selected** | Industry standard, thousands of pre-trained models, easy pipeline API |

---

## Infrastructure Technologies

### Vercel

| Aspect | Details |
|---|---|
| **What it is** | Frontend hosting platform with global CDN |
| **Why it is used** | Host the Next.js frontend at `memegpt.com` |
| **Why selected** | Free tier (100GB/month), Git-push deploy, Edge Network, Next.js optimized |
| **Limitations** | Serverless function limits (10s execution), 100GB bandwidth limit |

### Render.com / Railway

| Aspect | Details |
|---|---|
| **What it is** | Backend hosting platforms |
| **Why it is used** | Host the FastAPI backend at `api.memegpt.com` |
| **Why selected** | Free tier, Docker support, auto-deploy from Git |
| **Limitations** | Render free tier sleeps after 15 min inactivity (cold start) |
| **Mitigation** | UptimeRobot pings `/health` every 5 minutes to prevent sleep |

### Supabase

| Aspect | Details |
|---|---|
| **What it is** | Open-source Firebase alternative (PostgreSQL + Auth + Storage) |
| **Why it is used** | Production database (PostgreSQL) and future auth |
| **Why selected** | 500MB free, managed PostgreSQL, built-in auth, real-time subscriptions |
| **Limitations** | 500MB storage limit, rate limits on free tier |

### Cloudflare R2

| Aspect | Details |
|---|---|
| **What it is** | S3-compatible object storage with no egress fees |
| **Why it is used** | Store meme media files (GIF, PNG, MP4) |
| **Why selected** | 10GB free, zero egress costs (huge for media-heavy apps), global CDN |
| **Alternatives** | AWS S3 (egress costs), Google Cloud Storage (egress costs) |

### Upstash Redis

| Aspect | Details |
|---|---|
| **What it is** | Serverless Redis database |
| **Why it is used** | Cache search results, rate limiting |
| **Why selected** | 10,000 commands/day free, serverless (no idle cost), REST API |

---

## Development Tools

| Tool | Purpose | Why Selected |
|---|---|---|
| **Prisma** | ORM for database access | Type-safe, migration system, works with SQLite + PostgreSQL |
| **Ruff** | Python linter + formatter | 10–100x faster than flake8, single tool for lint + format |
| **ESLint** | TypeScript linter | Industry standard, extensible rules |
| **Prettier** | Code formatter | Consistent formatting, opinionated |
| **GitHub Actions** | CI/CD | Free for public repos, integrated with GitHub |
| **Docker** | Containerization | Consistent environments, Render/Railway support |
| **UptimeRobot** | Uptime monitoring | Free tier, 5-minute intervals |
| **Sentry** | Error tracking | Free tier, auto-capture exceptions, source maps |

---

> **Related Documents:**
> - [02_Project_Architecture/Architecture_Decisions.md](../02_Project_Architecture/Architecture_Decisions.md) — ADRs for key choices
> - [17_Appendix/Glossary.md](../17_Appendix/Glossary.md) — Term definitions
