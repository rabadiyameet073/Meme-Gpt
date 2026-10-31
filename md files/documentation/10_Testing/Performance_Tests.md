# MemeGPT — Performance Tests

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Performance benchmarking suite — latency tests per component, end-to-end timing, cache performance, and regression detection.

---

## Performance Test Suite

```python
# tests/test_performance.py
import time, asyncio, pytest

@pytest.mark.asyncio
async def test_search_latency_p50():
    """P50 latency must be under 1 second."""
    latencies = []
    for _ in range(20):
        start = time.time()
        await recommend_memes("test query performance")
        latencies.append(time.time() - start)
    p50 = sorted(latencies)[len(latencies) // 2]
    assert p50 < 1.0, f"P50 too slow: {p50:.2f}s"

@pytest.mark.asyncio
async def test_search_latency_p95():
    """P95 latency must be under 3 seconds."""
    latencies = []
    for _ in range(20):
        start = time.time()
        await recommend_memes("varied query " + str(time.time()))
        latencies.append(time.time() - start)
    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
    assert p95 < 3.0, f"P95 too slow: {p95:.2f}s"

@pytest.mark.asyncio
async def test_cache_hit_latency():
    """Cached search must return in under 100ms."""
    query = "cache performance test"
    await recommend_memes(query)  # Warm cache
    start = time.time()
    await recommend_memes(query)  # Cache hit
    elapsed = time.time() - start
    assert elapsed < 0.1, f"Cache too slow: {elapsed:.2f}s"

@pytest.mark.asyncio
async def test_embedding_generation_speed():
    """MiniLM embedding must generate in under 100ms."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    start = time.time()
    model.encode("test sentence for speed", normalize_embeddings=True)
    elapsed = time.time() - start
    assert elapsed < 0.1, f"Embedding too slow: {elapsed:.2f}s"

@pytest.mark.asyncio
async def test_concurrent_search_throughput():
    """10 concurrent searches must all complete within 5 seconds."""
    queries = [f"concurrent test {i}" for i in range(10)]
    start = time.time()
    results = await asyncio.gather(*[recommend_memes(q) for q in queries])
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Concurrent too slow: {elapsed:.2f}s"
    assert all(len(r) > 0 for r in results), "Some queries returned empty"
```

---

## Component Benchmarks

| Component | Target Latency | Test Method |
|---|---|---|
| MiniLM embedding | <100ms | Direct model.encode() |
| Emotion detection | <150ms | Direct pipeline() call |
| Groq API call | <500ms | httpx.post() timing |
| Qdrant search | <100ms | client.search() timing |
| Re-ranking | <20ms | Pure Python timing |
| Redis GET | <10ms | cache.get() timing |
| Full pipeline | <1.5s | End-to-end timing |

---

## Running Performance Tests

```bash
# Run performance suite only
pytest tests/test_performance.py -v --tb=short

# Run with detailed timing
pytest tests/test_performance.py -v --durations=10
```

---

> **Related Documents:**
> - [Testing_Strategy.md](./Testing_Strategy.md) — Overall testing strategy
> - [Load_Tests.md](./Load_Tests.md) — Locust load testing
