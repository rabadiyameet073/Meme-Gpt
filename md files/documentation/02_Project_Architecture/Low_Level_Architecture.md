# MemeGPT — Low-Level Architecture

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

This document provides the low-level implementation architecture of MemeGPT, covering internal module interactions, class-level design, function signatures, and data transformation details that complement the [High_Level_Architecture.md](./High_Level_Architecture.md).

---

## Module Dependency Graph

```mermaid
graph TD
    subgraph "Entry Points"
        MAIN["main.py<br/>HTTP routes"]
    end
    subgraph "Business Logic"
        MATCH["meme_matcher.py<br/>Pipeline orchestrator"]
        RULE["rule_engine.py<br/>Deterministic scoring"]
        SEARCH["semantic_search.py<br/>Vector similarity"]
    end
    subgraph "Data Access"
        DB["database.py<br/>CRUD operations"]
    end
    subgraph "Configuration"
        CONFIG["config.py<br/>Settings loader"]
    end
    subgraph "External SDKs"
        GROQ_SDK["groq<br/>LLM client"]
        QDRANT_SDK["qdrant-client<br/>Vector DB"]
        REDIS_SDK["redis<br/>Cache"]
    end

    MAIN --> MATCH
    MAIN --> DB
    MAIN --> CONFIG
    MATCH --> RULE
    MATCH --> SEARCH
    MATCH --> DB
    SEARCH --> QDRANT_SDK
    MATCH --> GROQ_SDK
    MATCH --> REDIS_SDK
```

---

## Internal Function Call Chain (Search Request)

```mermaid
sequenceDiagram
    participant H as Route Handler
    participant M as meme_matcher
    participant R as rule_engine
    participant S as semantic_search
    participant D as database

    H->>M: match_memes(query, limit=5)
    M->>M: clean_query(query)
    M->>M: extract_keywords(query)
    M->>R: apply_rules(keywords, all_memes)
    R-->>M: rule_scores: dict[str, float]
    M->>S: search_similar(query, top_k=10)
    S->>S: embed_text(query)
    S->>D: get_all_embeddings()
    D-->>S: embeddings: list[MemeEmbedding]
    S->>S: cosine_similarity(q_vec, meme_vecs)
    S-->>M: semantic_results: list[ScoredMeme]
    M->>M: merge_results(rule_scores, semantic_results)
    M->>M: deduplicate(merged)
    M->>M: sort_by_composite_score()
    M-->>H: top_n_results: list[MemeResult]
```

---

## Data Types (Internal)

```python
# Internal data types used across modules

class MemeRecord:
    """Raw meme data from database"""
    id: str
    name: str
    category: str
    dialogue: str
    explanation: str
    keywords: list[str]    # Parsed from JSON string
    viral_score: float
    usage_count: int
    upvotes: int
    downvotes: int

class ScoredMeme:
    """Meme with computed relevance score"""
    meme: MemeRecord
    keyword_score: float     # 0.0 – 1.0
    semantic_score: float    # 0.0 – 1.0
    emotion_score: float     # 0.0 – 1.0
    popularity_score: float  # 0.0 – 1.0
    composite_score: float   # Weighted combination

class MemeEmbedding:
    """Stored embedding for a meme"""
    meme_id: str
    text_vector: list[float]   # 384-dim
    image_vector: list[float]  # 512-dim (optional)
    combined_vector: list[float]  # 896-dim

class IntentResult:
    """LLM intent parsing output"""
    situation: str
    emotion_hint: str
    tone: str
    keywords: list[str]
    meme_format: str
    intensity: float

class EmotionResult:
    """Emotion classifier output"""
    primary: str      # joy, anger, surprise, etc.
    secondary: str
    confidence: float  # 0.0 – 1.0
```

---

## Composite Score Calculation (Detailed)

```python
def calculate_composite_score(
    keyword_score: float,
    semantic_score: float,
    emotion_match: bool,
    emotion_secondary: bool,
    popularity_score: float,
    format_match: bool,
    recency_days: int
) -> float:
    """
    Weighted scoring formula used by the re-ranking step.
    
    Weights:
        keyword_score:    0.30 (30%)
        semantic_score:   0.20 (20%)
        emotion match:    +0.15 primary, +0.08 secondary
        popularity:       0.20 (20%)
        format boost:     +0.05
        recency bonus:    0.10 (10%) decayed by age
    """
    score = (
        keyword_score * 0.30 +
        semantic_score * 0.20 +
        popularity_score * 0.20 +
        max(0, (30 - recency_days) / 30) * 0.10  # Newer = higher
    )
    
    if emotion_match:
        score += 0.15
    if emotion_secondary:
        score += 0.08
    if format_match:
        score += 0.05
    
    return min(score, 1.0)
```

---

## Memory Layout

```
Process Memory (~460MB)
├── Python Runtime (50MB)
├── FastAPI + Uvicorn (30MB)
├── MiniLM Model (80MB)
│   ├── Weights: 22MB
│   ├── Tokenizer: 3MB
│   └── Runtime buffers: 55MB
├── Emotion Model (250MB)
│   ├── Weights: 82MB
│   ├── Tokenizer: 5MB
│   └── Runtime buffers: 163MB
├── Application Data (50MB)
│   ├── Meme records cache: 10MB
│   ├── Embedding vectors: 30MB (for 5K memes)
│   └── Config + misc: 10MB
```

---

## Thread / Async Model

```mermaid
graph TD
    A["Uvicorn Event Loop<br/>(asyncio)"] --> B["Worker Thread Pool<br/>(default: 4 threads)"]
    A --> C["Async I/O<br/>(HTTP clients)"]
    
    B --> D["ML Model Inference<br/>(CPU-bound, GIL)"]
    C --> E["Groq API call<br/>(async HTTP)"]
    C --> F["Qdrant API call<br/>(async HTTP)"]
    C --> G["Redis call<br/>(async TCP)"]
```

- **Async routes:** All FastAPI route handlers are `async def`
- **ML inference:** Runs in thread pool (CPU-bound, blocked by GIL)
- **External I/O:** True async via `httpx.AsyncClient`
- **Concurrency:** ~50 concurrent requests on single-core free tier

---

## Error Propagation

```mermaid
flowchart TD
    A["Route Handler"] -->|try/except| B["meme_matcher.match_memes()"]
    B -->|try/except| C["groq_client.parse_intent()"]
    B -->|try/except| D["semantic_search.search_similar()"]
    B -->|try/except| E["redis.get_cached()"]
    
    C -->|GroqError| F["Log + skip LLM step"]
    D -->|QdrantError| G["Return cached / trending"]
    E -->|RedisError| H["Skip cache, continue"]
    
    F --> I["Degraded result<br/>(raw query embedding)"]
    G --> J["Fallback result<br/>(trending memes)"]
    H --> K["Normal result<br/>(no caching)"]
```

---

## Best Practices

1. **Never block the event loop** — use `run_in_executor()` for CPU-bound work
2. **Pre-load models** at startup, not per-request
3. **Use connection pools** for Redis and Qdrant
4. **Validate early** — Pydantic catches bad input before business logic
5. **Log at boundaries** — entry/exit of each service function

---

## Common Mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Loading model per request | 2–5s added per request | Load once at startup |
| Sync HTTP calls in async routes | Blocks event loop | Use `httpx.AsyncClient` |
| No timeout on Groq API | Request hangs forever | Set `timeout=5.0` |
| Storing embeddings as strings | Slow parsing | Store as binary numpy arrays |
| Not normalizing vectors | Wrong cosine similarity | Always L2-normalize |

---

## Edge Cases

| Input | Expected Behavior | Why |
|---|---|---|
| Empty string `""` | 422 Validation Error | Pydantic `min_length=1` |
| 2001+ characters | 422 Validation Error | Pydantic `max_length=2000` |
| Unicode emoji only `"😂😂😂"` | Valid search (low quality) | Embedding handles any text |
| SQL injection `"'; DROP TABLE"` | Safe (parameterized queries) | Prisma ORM prevents injection |
| Prompt injection | Safe (structured JSON output) | LLM output is JSON-parsed only |
| Very long conversation paste | Truncated at 2000 chars | Input validation |
| No memes match (score < 0.3) | Empty state + trending fallback | Score threshold filter |

---

## Future Improvements

1. **Replace in-memory search** with Qdrant for all environments
2. **Add request tracing** with OpenTelemetry spans
3. **Implement circuit breaker** for Groq API
4. **Add batch embedding** for query variants
5. **Profile GIL contention** and consider multiprocessing for ML

---

> **Related Documents:**
> - [High_Level_Architecture.md](./High_Level_Architecture.md) — Bird's-eye view
> - [System_Architecture.md](./System_Architecture.md) — Component specifications
> - [Component_Architecture.md](./Component_Architecture.md) — Module internals
> - [03_Backend/Services.md](../03_Backend/Services.md) — Service layer detail
