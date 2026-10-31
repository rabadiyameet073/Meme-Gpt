# MemeGPT — Database Overview

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete overview of MemeGPT's polyglot persistence strategy — why four different data stores, what data lives where, and how they interact.

---

## Background

MemeGPT uses **four specialized data stores** instead of one monolithic database. Each store is optimized for its specific access pattern — vectors for similarity search, relational for structured queries, key-value for caching, and object storage for binary files.

---

## Data Store Architecture

```mermaid
graph TD
    subgraph "Application"
        API["FastAPI Backend"]
    end

    subgraph "Vector Storage"
        QD["Qdrant Cloud<br/>Vector embeddings<br/>384/512/896-dim<br/>Cosine similarity search"]
    end

    subgraph "Relational Storage"
        PG["Supabase PostgreSQL<br/>Meme metadata<br/>Search logs<br/>Feedback<br/>API keys"]
    end

    subgraph "Cache Storage"
        RD["Upstash Redis<br/>Search result cache<br/>Rate limit counters<br/>Trending cache"]
    end

    subgraph "Object Storage"
        R2["Cloudflare R2<br/>GIF/PNG/MP4/WebP<br/>Thumbnails"]
    end

    API -->|"Vector search<br/>(gRPC)"| QD
    API -->|"CRUD operations<br/>(Prisma)"| PG
    API -->|"GET/SET<br/>(Redis protocol)"| RD
    API -->|"Pre-signed URLs<br/>(S3 API)"| R2
```

---

## Why Four Data Stores?

| Data Store | What It Stores | Why Not PostgreSQL? |
|---|---|---|
| **Qdrant** | Vector embeddings | PostgreSQL pgvector is 10× slower for ANN search |
| **Supabase PG** | Structured metadata | Perfect fit — relational data with indexes |
| **Redis** | Ephemeral cache | PostgreSQL adds 10ms+ latency for cache reads |
| **R2** | Binary files (GIF/MP4) | Binary objects don't belong in relational DB |

---

## Data Ownership

| Entity | Primary Store | Secondary Store | What's Stored |
|---|---|---|---|
| Meme metadata | Supabase | — | name, slug, categories, emotions, source |
| Meme embeddings | Qdrant | — | text (384-dim), image (512-dim), combined (896-dim) |
| Meme media | R2 | — | GIF, PNG, MP4, WebP, thumbnails |
| Search logs | Supabase | — | query_hash, latency, result_count |
| User feedback | Supabase | — | meme_id, action, session_id |
| Trending scores | Supabase + Redis | — | Calculated in PG, cached in Redis |
| Search results | Redis | — | Full JSON response, 1h TTL |
| Rate limit state | Redis | — | Request counts per IP, 1min TTL |

---

## Access Patterns

| Pattern | Store | Query | Frequency |
|---|---|---|---|
| Vector similarity | Qdrant | ANN search (HNSW) | Every search |
| Meme by slug | Supabase | `WHERE slug = ?` | Meme detail pages |
| Trending by category | Redis → Supabase | Cached list, hourly refresh | High (trending page) |
| Search result cache | Redis | `GET search:{hash}` | Every search (cache check) |
| Log search | Supabase | `INSERT INTO search_logs` | Every search (async) |
| Record feedback | Supabase | `INSERT INTO feedback` | User interactions |
| Rate limit check | Redis | `ZADD + ZCARD` | Every request |

---

## Connection Configuration

```python
# Supabase (PostgreSQL via Prisma)
DATABASE_URL="postgresql://user:pass@db.xxx.supabase.co:5432/postgres"

# Qdrant Cloud
QDRANT_URL="https://xxx.qdrant.io"
QDRANT_API_KEY="xxx"

# Upstash Redis
UPSTASH_REDIS_URL="rediss://default:xxx@xxx.upstash.io:6379"

# Cloudflare R2
R2_ENDPOINT="https://xxx.r2.cloudflarestorage.com"
R2_ACCESS_KEY="xxx"
R2_SECRET_KEY="xxx"
R2_BUCKET="memegpt-memes"
```

---

## Free Tier Limits

| Service | Free Tier | MemeGPT Usage | Headroom |
|---|---|---|---|
| Supabase | 500 MB, 50K rows | ~100 MB, ~15K rows | 5× |
| Qdrant Cloud | 1 GB | ~70 MB (10K memes) | 14× |
| Upstash Redis | 10K cmd/day | ~5K cmd/day | 2× |
| Cloudflare R2 | 10 GB storage, 10M reads | ~5 GB | 2× |

---

## Best Practices

1. **Right tool for right data** — don't force vectors into PostgreSQL
2. **Co-locate in same region** — all services in US-East for minimal latency
3. **Cache aggressively** — Redis reduces load on all other stores
4. **Async writes** — search logs and feedback should never block responses
5. **Monitor free tier usage** — set alerts at 80% of limits

---

> **Related Documents:**
> - [Schema.md](./Schema.md) — PostgreSQL schema
> - [Tables.md](./Tables.md) — Table descriptions
> - [05_AI_System/Vector_Database.md](../05_AI_System/Vector_Database.md) — Qdrant config
> - [Backup.md](./Backup.md) — Backup strategy
