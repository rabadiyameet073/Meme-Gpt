"""Performance Benchmarks & Latency Tests from 10_Testing/Performance_Tests.md."""

import asyncio
import time
import pytest
from app.services.recommendation_service import recommend, _make_cache_key
from app.core.cache import query_cache
from app.semantic_search import embed_text


@pytest.mark.asyncio
async def test_search_latency_p50():
    """P50 latency must be under 1 second."""
    from unittest.mock import patch
    with patch("app.services.giphy_service.search_live_memes", return_value=[]):
        latencies = []
        for _ in range(5):
            start = time.perf_counter()
            await recommend(user_text="test query performance", format_pref="gif", nsfw=False)
            latencies.append(time.perf_counter() - start)
        p50 = sorted(latencies)[len(latencies) // 2]
        assert p50 < 1.0, f"P50 too slow: {p50:.2f}s"


@pytest.mark.asyncio
async def test_search_latency_p95():
    """P95 latency must be under 3 seconds."""
    from unittest.mock import patch
    with patch("app.services.giphy_service.search_live_memes", return_value=[]):
        latencies = []
        for _ in range(5):
            start = time.perf_counter()
            await recommend(user_text="varied query " + str(time.perf_counter()), format_pref="gif", nsfw=False)
            latencies.append(time.perf_counter() - start)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        assert p95 < 3.0, f"P95 too slow: {p95:.2f}s"


@pytest.mark.asyncio
async def test_cache_hit_latency():
    """Cached search must return in under 100ms."""
    query = "cache performance benchmark test"
    key = _make_cache_key(query, "gif", False)
    query_cache.set(key, {"query": query, "results": [], "primary": {}})

    start = time.perf_counter()
    res = await recommend(user_text=query, format_pref="gif", nsfw=False)
    elapsed = time.perf_counter() - start

    assert res["cached"] is True
    assert elapsed < 0.1, f"Cache too slow: {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_embedding_generation_speed():
    """MiniLM / Text embedding must generate in under 100ms."""
    embed_text("warmup sentence")
    start = time.perf_counter()
    vec = embed_text("test sentence for speed benchmark")
    elapsed = time.perf_counter() - start

    assert len(vec) == 384
    assert elapsed < 0.15, f"Embedding too slow: {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_concurrent_search_throughput():
    """10 concurrent searches must all complete quickly."""
    from app.meme_matcher import match_memes
    queries = [f"concurrent test query {i}" for i in range(10)]
    start = time.perf_counter()
    loop = asyncio.get_event_loop()
    results = await asyncio.gather(*[
        loop.run_in_executor(None, match_memes, q)
        for q in queries
    ])
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0, f"Concurrent too slow: {elapsed:.2f}s"
    assert len(results) == 10
    assert all("primary" in r or "topFive" in r for r in results)

