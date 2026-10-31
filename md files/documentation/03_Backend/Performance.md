# MemeGPT — Backend Performance

> **Document Version:** 1.0  
> **Last Updated:** 2026-08-01

---

## Purpose

Performance optimization strategies, benchmarks, and tuning guidelines for the MemeGPT backend.

---

## Performance Targets

| Metric | Target | Current |
|---|---|---|
| P50 Latency | <1.0s | ~560ms ✅ |
| P95 Latency | <3.0s | ~1.2s ✅ |
| Cache Hit Rate | >50% | Target 60%+ |
| Throughput | 100 req/s | ~50 req/s on free tier |
| Memory Usage | <1GB | ~512MB |
| Cold Start | <10s | ~5s |

---

## Optimization Strategies

### 1. Model Loading (Startup)

**Problem:** Loading ML models per request would add 2–5 seconds per request.

**Solution:** Load models once at application startup, keep in memory.

```python
# Models loaded once at module import time
text_model = SentenceTransformer('all-MiniLM-L6-v2')  # 22MB
emotion_model = pipeline("text-classification", ...)    # 250MB
```

### 2. Redis Caching

**Strategy:** Cache search results by query hash with 1-hour TTL.

```python
import hashlib

def cache_key(query, format_pref, nsfw):
    raw = f"{query}:{format_pref}:{nsfw}"
    return f"search:{hashlib.md5(raw.encode()).hexdigest()}"
```

**Expected Hit Rate:** 60%+ (many users search similar phrases)

### 3. Parallel Processing

Intent parsing (Groq) and emotion detection (local) can run in parallel:

```python
import asyncio

# Run LLM and emotion detection concurrently
intent_task = asyncio.create_task(parse_intent(query))
emotion = detect_emotion(query)  # Sync local model
intent = await intent_task
```

### 4. Input Truncation

Limit input processing to prevent resource exhaustion:

| Input | Max Length | Reason |
|---|---|---|
| Search query | 2,000 chars | LLM context window limit |
| Emotion input | 512 chars | Model max input |
| Embedding input | 256 tokens | MiniLM max sequence |

### 5. Connection Pooling

```python
# Qdrant — persistent connection
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)

# Redis — connection pool
redis_pool = redis.ConnectionPool.from_url(REDIS_URL, max_connections=10)
redis_client = redis.Redis(connection_pool=redis_pool)
```

---

## Memory Budget

| Component | Memory | Notes |
|---|---|---|
| Python runtime | ~50MB | Base Python process |
| FastAPI + deps | ~30MB | Framework overhead |
| MiniLM model | ~80MB | Text embedding model |
| Emotion model | ~250MB | DistilRoBERTa |
| Application data | ~50MB | In-memory structures |
| **Total** | **~460MB** | Fits in 512MB free tier |

---

## Monitoring

| Metric | Tool | Alert Threshold |
|---|---|---|
| Response time | Server-side timing | P95 > 3s |
| Error rate | Sentry | >5% of requests |
| Cache hit ratio | Redis info | <40% |
| Memory usage | Container metrics | >90% of limit |
| CPU usage | Container metrics | >80% sustained |

---

> **Related Documents:**
> - [Backend_Overview.md](./Backend_Overview.md) — Backend architecture
> - [12_Deployment/Monitoring.md](../12_Deployment/Monitoring.md) — Production monitoring
