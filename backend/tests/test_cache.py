"""
Tests for Redis Cache Module from 04_Redis_Cache.md and GAP_ANALYSIS_FULL.md.
"""

import time
from unittest.mock import MagicMock, patch
from app.core.cache import (
    make_cache_key,
    cache_get,
    cache_set,
    cache_delete,
    cache_flush_pattern,
    rate_limit_check,
    get_cache_stats,
    query_cache,
    _fallback_cache,
    _rate_counts,
)


def setup_function():
    """Clear caches before each test."""
    _fallback_cache.clear()
    _rate_counts.clear()


def test_make_cache_key():
    key1 = make_cache_key("When code compiles", "gif", False)
    key2 = make_cache_key("  when code compiles  ", "gif", False)
    key3 = make_cache_key("when code compiles", "image", False)
    key4 = make_cache_key("when code compiles", "gif", True)

    assert key1 == key2
    assert key1.startswith("search:")
    assert len(key1) == len("search:") + 32  # MD5 length is 32 hex chars
    assert key1 != key3
    assert key1 != key4


def test_cache_set_and_get_in_memory():
    test_key = make_cache_key("unit_test_query", "gif", False)
    test_data = {"id": "meme_123", "name": "Success Kid", "score": 0.99}

    assert cache_get(test_key) is None

    success = cache_set(test_key, test_data, ttl=60)
    assert success is True

    cached = cache_get(test_key)
    assert cached is not None
    assert cached["id"] == "meme_123"
    assert cached["name"] == "Success Kid"
    assert cached["score"] == 0.99


def test_cache_delete():
    test_key = make_cache_key("delete_me", "gif", False)
    cache_set(test_key, {"status": "active"}, ttl=60)
    assert cache_get(test_key) is not None

    deleted = cache_delete(test_key)
    assert deleted is True
    assert cache_get(test_key) is None


def test_cache_flush_pattern():
    k1 = "search:abc1"
    k2 = "search:abc2"
    k3 = "other:xyz1"

    cache_set(k1, {"val": 1}, ttl=60)
    cache_set(k2, {"val": 2}, ttl=60)
    cache_set(k3, {"val": 3}, ttl=60)

    flushed = cache_flush_pattern("search:*")
    assert flushed >= 2
    assert cache_get(k1) is None
    assert cache_get(k2) is None
    assert cache_get(k3) is not None


def test_cache_ttl_expiration():
    test_key = "search:expires_soon"
    cache_set(test_key, {"data": "temp"}, ttl=1)

    # Manually expire the item
    _fallback_cache[test_key] = ({"data": "temp"}, time.time() - 10)

    assert cache_get(test_key) is None
    assert test_key not in _fallback_cache


def test_rate_limit_check_allow_and_block():
    user_id = "test_user_ip_127_0_0_1"
    limit = 3
    window = 10

    # First request
    allowed, remaining = rate_limit_check(user_id, limit=limit, window_seconds=window)
    assert allowed is True
    assert remaining == 2

    # Second request
    allowed, remaining = rate_limit_check(user_id, limit=limit, window_seconds=window)
    assert allowed is True
    assert remaining == 1

    # Third request
    allowed, remaining = rate_limit_check(user_id, limit=limit, window_seconds=window)
    assert allowed is True
    assert remaining == 0

    # Fourth request (should exceed limit)
    allowed, remaining = rate_limit_check(user_id, limit=limit, window_seconds=window)
    assert allowed is False
    assert remaining == 0


def test_get_cache_stats():
    stats = get_cache_stats()
    assert isinstance(stats, dict)
    assert "backend" in stats
    assert "connected" in stats
    assert "keys" in stats


def test_query_cache_legacy_wrapper():
    key = "search:legacy_key"
    val = {"status": "ok"}

    query_cache.set(key, val, ttl=60)
    assert query_cache.get(key) == val

    stats = query_cache.stats()
    assert isinstance(stats, dict)

    query_cache.delete(key)
    assert query_cache.get(key) is None


def test_redis_mock_pipeline_operations():
    mock_redis = MagicMock()
    mock_redis.get.return_value = '{"id": "cached_redis_meme"}'
    mock_redis.info.return_value = {"keyspace_hits": 42, "keyspace_misses": 8}
    mock_redis.dbsize.return_value = 100

    # Pipeline mock for rate limiter
    mock_pipe = MagicMock()
    mock_pipe.execute.return_value = [2]
    mock_redis.pipeline.return_value = mock_pipe

    with patch("app.core.cache.get_redis_client", return_value=mock_redis):
        # 1. Test get
        val = cache_get("search:mock_redis")
        assert val == {"id": "cached_redis_meme"}

        # 2. Test set
        cache_set("search:mock_redis", {"id": "new"}, ttl=120)
        mock_redis.setex.assert_called_with("search:mock_redis", 120, '{"id": "new"}')

        # 3. Test stats
        stats = get_cache_stats()
        assert stats["backend"] == "redis"
        assert stats["connected"] is True
        assert stats["hits"] == 42
        assert stats["keys"] == 100

        # 4. Test rate limiting
        allowed, remaining = rate_limit_check("user_redis", limit=5, window_seconds=60)
        assert allowed is True
        assert remaining == 3
