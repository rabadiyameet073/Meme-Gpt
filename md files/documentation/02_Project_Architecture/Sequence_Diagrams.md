# MemeGPT — Sequence Diagrams

> **Document Version:** 1.0  
> **Last Updated:** 2026-08-01

---

## Purpose

UML sequence diagrams for all major user flows and system interactions.

---

## 1. Meme Search Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as React Frontend
    participant API as FastAPI Backend
    participant Cache as Redis
    participant LLM as Groq (Llama)
    participant EMO as Emotion Model
    participant EMB as MiniLM
    participant VDB as Qdrant
    participant DB as Supabase

    User->>UI: Enter search query
    UI->>UI: Show loading skeleton
    UI->>API: POST /search {query}
    API->>Cache: GET hash(query)
    alt Cache Hit
        Cache-->>API: Cached results
        API-->>UI: Return results (cached: true)
    else Cache Miss
        par AI Processing
            API->>LLM: Parse intent
            LLM-->>API: Intent JSON
        and
            API->>EMO: Detect emotion
            EMO-->>API: Emotion labels
        end
        API->>API: Build enriched query
        API->>EMB: Encode query
        EMB-->>API: 384-dim vector
        API->>VDB: search(vector, filters)
        VDB-->>API: Top 10 candidates
        API->>API: Re-rank results
        API->>Cache: SET hash(query) TTL=3600
        API-->>UI: Return top 5 results
    end
    API-->>DB: Log search (async)
    UI->>UI: Render meme grid
    UI-->>User: Display results
```

---

## 2. Meme Download Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as React Frontend
    participant CDN as Cloudflare CDN
    participant API as FastAPI Backend
    participant DB as Supabase

    User->>UI: Click Download (GIF)
    UI->>UI: Show download spinner
    UI->>CDN: GET /gifs/meme-name.gif
    CDN-->>UI: File binary
    UI->>UI: Trigger browser download
    UI-->>User: "✓ Downloaded"
    UI->>API: POST /feedback {action: download}
    API->>DB: INSERT feedback record
    API->>DB: UPDATE meme download_count++
```

---

## 3. User Feedback Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as React Frontend
    participant API as FastAPI Backend
    participant DB as Supabase

    User->>UI: Click 👍 on meme result
    UI->>UI: Update UI (thumb filled)
    UI->>API: POST /feedback {meme_id, action: thumbs_up}
    API->>DB: INSERT feedback(meme_id, thumbs_up)
    API->>DB: UPDATE meme upvotes++
    API-->>UI: {recorded: true}
```

---

## 4. Offline Indexing Pipeline

```mermaid
sequenceDiagram
    participant Cron as GitHub Actions
    participant Script as Python Script
    participant Source as Data Sources
    participant R2 as Cloudflare R2
    participant AI as ML Models
    participant VDB as Qdrant
    participant DB as Supabase

    Cron->>Script: Trigger weekly pipeline
    Script->>Source: Fetch new memes (Reddit, Imgflip)
    Source-->>Script: Raw data + images
    Script->>R2: Upload images
    R2-->>Script: CDN URLs
    loop For each meme
        Script->>AI: OCR + BLIP + LLM tags
        AI-->>Script: Enriched metadata
        Script->>AI: MiniLM + CLIP embeddings
        AI-->>Script: Vectors (384 + 512 dim)
    end
    Script->>VDB: Batch upsert vectors
    Script->>DB: Batch insert metadata
    Script->>Script: Run verification tests
    Script-->>Cron: Pipeline complete ✅
```

---

## 5. App Startup Sequence

```mermaid
sequenceDiagram
    participant UV as Uvicorn
    participant APP as FastAPI App
    participant ML as ML Models
    participant DB as Database
    participant R as Redis

    UV->>APP: Create application
    APP->>APP: Load configuration
    APP->>ML: Load MiniLM model (~2s)
    ML-->>APP: Model ready
    APP->>ML: Load Emotion model (~3s)
    ML-->>APP: Model ready
    APP->>DB: Test connection
    DB-->>APP: Connection OK
    APP->>R: Test Redis connection
    alt Redis available
        R-->>APP: Connected
    else Redis unavailable
        APP->>APP: Cache disabled (graceful)
    end
    APP-->>UV: App ready
    UV->>UV: Listen on port 8000
    Note over UV: Ready to serve requests
```

---

> **Related Documents:**
> - [Request_Flow.md](./Request_Flow.md) — Detailed request lifecycle
> - [Data_Flow.md](./Data_Flow.md) — Data movement patterns
