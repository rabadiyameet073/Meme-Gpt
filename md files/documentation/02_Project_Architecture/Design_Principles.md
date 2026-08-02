# MemeGPT — Design Principles

> **Document Version:** 1.0  
> **Last Updated:** 2026-08-01

---

## Purpose

Core engineering and design principles that guide every architectural and implementation decision in MemeGPT.

---

## Engineering Principles

### 1. Free-Tier-First Architecture

> *"If it costs money at MVP scale, find an alternative."*

Every infrastructure choice must have a viable free tier. If a component exceeds its free limit, the system should degrade gracefully rather than fail.

**Implication:** Prefer Qdrant Cloud (1GB free) over Pinecone ($70/mo). Prefer Groq (6K req/day free) over OpenAI ($20/mo minimum).

### 2. Stateless API Design

> *"Any request can go to any server instance."*

The API server stores no session state. All state lives in external stores (Redis, Supabase, Qdrant). This enables horizontal scaling by simply adding server replicas.

**Implication:** No in-memory user sessions. No sticky sessions. Use Redis for anything that needs to persist between requests.

### 3. Graceful Degradation

> *"If a dependency is down, the app still works — just differently."*

| Dependency Down | Degraded Behavior |
|---|---|
| Groq API | Skip intent parsing, use raw query for embedding |
| Qdrant | Return cached results from Redis, or show trending |
| Redis | App works, just slower (no caching) |
| Supabase | Skip analytics logging, no impact on search |
| CDN | Serve from R2 origin directly |

### 4. Offline-First Processing

> *"Heavy computation happens offline. The API serves pre-computed data."*

All ML-intensive operations (OCR, BLIP captioning, CLIP embedding, LLM tagging) run in the offline indexing pipeline, not in the request path. The API server only runs lightweight models (MiniLM, emotion classifier).

### 5. Privacy by Default

> *"If we don't need the data, we don't collect it."*

- No user accounts required for core features
- Search queries anonymized (hashed) in analytics
- No PII in server logs
- GDPR-compliant by design

### 6. Convention Over Configuration

> *"Reduce decisions for contributors."*

- Standard directory structure across all components
- Consistent naming conventions (snake_case for Python, camelCase for TypeScript)
- Shared linting and formatting configurations
- Pre-configured VS Code workspace settings

---

## Design Principles (Product/UI)

### 1. Meme-First Design

The meme is always the hero element. UI chrome (headers, sidebars, controls) should be minimal and fade into the background.

### 2. Dark Mode Native

Memes are consumed on dark backgrounds (Discord, Reddit, Twitter). MemeGPT's UI matches this context.

### 3. Speed Perception

Show loading skeletons (not spinners). Pre-load thumbnails. Use optimistic UI. The user should feel like the app is faster than it actually is.

### 4. Mobile-Native Feel

Even the web app should feel like a native app — touch-friendly hit targets (44px minimum), gesture support, bottom-aligned actions for thumb reach.

---

> **Related Documents:**
> - [Design_Patterns.md](./Design_Patterns.md) — Patterns used in the codebase
> - [Architecture_Decisions.md](./Architecture_Decisions.md) — Why each decision was made
