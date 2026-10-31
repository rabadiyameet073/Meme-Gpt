# MemeGPT — Request Flow (Complete Lifecycle)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Traces the complete lifecycle of a user search request — from keystroke in the browser to meme displayed on screen — with exact timing, HTTP headers, and every service call documented.

---

## Background

A single MemeGPT search request touches **8 distinct services** across 6 phases. Understanding this flow is critical for debugging latency issues and optimizing the pipeline.

---

## Search Request Lifecycle

```mermaid
sequenceDiagram
    actor U as User
    participant C as React Client
    participant A as FastAPI Server
    participant R as Redis Cache
    participant G as Groq API
    participant E as Emotion Model
    participant M as MiniLM Model
    participant Q as Qdrant
    participant S as Supabase
    participant CDN as Cloudflare CDN

    Note over U,CDN: Phase 1 — Request Initiation (~50ms)
    U->>C: Types query + Ctrl+Enter
    C->>C: Validate input (1-2000 chars)
    C->>C: Show loading skeleton
    C->>A: POST /api/v1/search<br/>{query, format, limit}

    Note over A,R: Phase 2 — Cache Check (~15ms)
    A->>A: MD5 hash(query:format:nsfw) → cache key
    A->>R: GET cache:md5(query)
    alt Cache Hit (>60% of requests)
        R-->>A: Cached JSON response
        A-->>C: 200 OK (cached: true, ~15ms)
        C->>CDN: Load thumbnail images
        CDN-->>C: WebP thumbnails
        C-->>U: Display results
    end

    Note over A,M: Phase 3 — AI Processing (~350ms)
    par Parallel execution
        A->>G: Parse intent (async, ~300ms)
        G-->>A: {emotion, situation, tone, keywords}
    and
        A->>E: Detect emotion (local, ~100ms)
        E-->>A: {primary: joy, secondary: surprise, confidence: 0.87}
    end
    A->>A: Build enriched query text<br/>(user_text + intent + emotion)
    A->>M: Generate 384-dim embedding (~50ms)
    M-->>A: Normalized vector

    Note over A,Q: Phase 4 — Search & Rank (~60ms)
    A->>Q: Vector search(vector, filters, limit=10)
    Q-->>A: Top 10 candidates + cosine scores
    A->>A: Re-rank: +15% emotion match<br/>+10% popularity<br/>+5% format match
    A->>A: Select top 5 results

    Note over A,CDN: Phase 5 — Response (~10ms)
    A->>R: SETEX cache:key 3600 (async)
    A->>S: INSERT INTO search_logs (BackgroundTask)
    A-->>C: 200 OK {results: [...5 memes]}
    C->>C: Render MemeCard grid
    C->>CDN: Load 5 × thumbnail images (parallel)
    CDN-->>C: WebP thumbnails (50-100KB each)
    C-->>U: Display results (total: ~1.2s)

    Note over U,S: Phase 6 — User Action
    U->>C: Clicks Download on meme
    C->>CDN: GET /gifs/meme-name.gif (301 redirect)
    CDN-->>C: File download (100KB-2MB)
    C->>A: POST /api/v1/feedback {action: "download"}
    A->>S: INSERT INTO feedback (BackgroundTask)
```

---

## Latency Budget (Detailed)

```mermaid
gantt
    title Search Request Latency Budget
    dateFormat X
    axisFormat %L ms

    section Client
    Validate + show skeleton        :c1, 0, 50

    section Server
    CORS + Rate Limit + Validation  :s1, 50, 55
    Cache check (Redis GET)         :s2, 55, 70

    section AI Processing
    Intent Parsing (Groq)           :a1, 70, 370
    Emotion Detection (local)       :a2, 70, 170
    Build enriched query            :a3, 370, 375
    Generate embedding (MiniLM)     :a4, 375, 425

    section Search
    Qdrant vector search            :q1, 425, 475
    Re-ranking (Python)             :q2, 475, 485

    section Response
    Cache write + serialize         :r1, 485, 495
    HTTP response                   :r2, 495, 500

    section Client Render
    Parse JSON + render cards       :c2, 500, 530
    Load 5 thumbnails (parallel)    :c3, 530, 700
```

| Phase | Duration | % of Total |
|---|---|---|
| Client-side initiation | ~50ms | 7% |
| Middleware pipeline | ~5ms | <1% |
| Cache check (Redis) | ~15ms | 2% |
| Intent parsing (Groq) | ~300ms | **43%** |
| Emotion detection | ~100ms | 14% |
| Embedding generation | ~50ms | 7% |
| Vector search (Qdrant) | ~50ms | 7% |
| Re-ranking | ~10ms | 1% |
| Response serialization | ~10ms | 1% |
| Thumbnail loading (CDN) | ~170ms | 24% |
| **Total (wall clock)** | **~700ms** | |

> **Note:** Groq + Emotion run in **parallel** via `asyncio.gather()`, so the real wall-clock for AI processing is ~300ms (not 400ms).

---

## HTTP Request/Response (Complete)

### Request

```http
POST /api/v1/search HTTP/1.1
Host: api.memegpt.com
Content-Type: application/json
Origin: https://memegpt.com
User-Agent: MemeGPT-Web/1.0

{
  "query": "when your code works but you don't know why",
  "format_preference": "gif",
  "nsfw": false,
  "limit": 5,
  "session_id": "sess_abc123"
}
```

### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Response-Time: 487ms
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 27
X-RateLimit-Reset: 1706745600
X-Cache: MISS
Access-Control-Allow-Origin: https://memegpt.com

{
  "success": true,
  "query_id": "q_xyz789",
  "results": [
    {
      "id": "meme_042",
      "name": "This Is Fine",
      "slug": "this-is-fine",
      "relevance_score": 0.94,
      "emotion_match": ["surprise", "confusion"],
      "preview_url": "https://cdn.memegpt.com/thumbs/this-is-fine.webp",
      "formats": {
        "gif": "https://cdn.memegpt.com/gifs/this-is-fine.gif",
        "image": "https://cdn.memegpt.com/images/this-is-fine.jpg",
        "video": null,
        "webp": "https://cdn.memegpt.com/webp/this-is-fine.webp"
      },
      "share_url": "https://memegpt.com/meme/this-is-fine?ref=q_xyz789",
      "meme_type": "reaction",
      "categories": ["programming", "stress"]
    }
  ],
  "intent_parsed": {
    "emotion": "surprise",
    "situation": "code working unexpectedly",
    "tone": "confused"
  },
  "response_time_ms": 487,
  "cached": false
}
```

---

## Cache Flow

```mermaid
flowchart LR
    Q["Query: 'Monday vibes'<br/>Format: gif<br/>NSFW: false"] --> H["MD5 Hash"]
    H --> K["cache:a3f2b9c1e7d4..."]
    K --> R{"Redis GET"}
    R -->|HIT| RES["Return cached JSON<br/>~15ms"]
    R -->|MISS| P["Full Pipeline<br/>~500ms"]
    P --> S["SETEX key 3600<br/>(cache for 1 hour)"]
    S --> RES2["Return fresh JSON"]
```

**Cache key format:** `search:{md5(query:format:nsfw)}`  
**TTL:** 3600 seconds (1 hour)  
**Expected hit rate:** >60% (popular queries repeat frequently)

---

## Feedback Flow (Post-Search)

```mermaid
sequenceDiagram
    actor U as User
    participant C as Client
    participant A as API
    participant S as Supabase

    U->>C: Clicks "Download" on meme
    C->>C: Trigger file download (CDN)
    C->>A: POST /api/v1/feedback
    Note right of C: {query_id, meme_id,<br/>action: "download",<br/>session_id}
    A->>A: Validate payload
    A-->>C: 200 {recorded: true}
    A->>S: INSERT INTO feedback<br/>(BackgroundTask — non-blocking)
    Note right of S: Used weekly for<br/>popularity recalculation
```

---

## Error Scenarios in Flow

| Scenario | Detection Point | User Experience | Recovery |
|---|---|---|---|
| Network timeout | Client (5s timeout) | "Connection error. Retry?" | Auto-retry once |
| Rate limited (429) | Middleware | "Too many requests. Wait 23s" | Show countdown timer |
| Groq API down | Service layer | Degraded results (no LLM) | Skip intent parsing |
| Qdrant down | Service layer | Return cached/trending | Fallback to trending |
| Invalid query (422) | Pydantic validation | "Please enter a valid query" | Show error inline |

---

## Best Practices

1. **Parallel I/O** — intent parsing + emotion detection run concurrently via `asyncio.gather()`
2. **Background logging** — search_logs and feedback use `BackgroundTasks` to avoid blocking responses
3. **Cache first** — always check cache before starting the AI pipeline
4. **Lazy image loading** — thumbnails load after JSON response renders
5. **Optimistic UI** — show skeleton immediately, don't wait for API response to render layout

---

> **Related Documents:**
> - [07_APIs/Search_API.md](../07_APIs/Search_API.md) — Full API specification
> - [Data_Flow.md](./Data_Flow.md) — Data movement details
> - [03_Backend/API_Architecture.md](../03_Backend/API_Architecture.md) — Backend architecture
> - [03_Backend/Services.md](../03_Backend/Services.md) — Service layer
