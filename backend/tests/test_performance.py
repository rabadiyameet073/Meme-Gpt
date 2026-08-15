import asyncio
import pytest
from app.services.recommendation_service import recommend, _make_cache_key
from app.core.cache import query_cache


@pytest.mark.asyncio
async def test_input_truncation_safeguards():
    # Massive query string > 5000 chars
    huge_query = "when code fails in production " * 200
    assert len(huge_query) > 5000

    # Pipeline should truncate cleanly and execute without memory crash
    result = await recommend(user_text=huge_query, format_pref="gif", nsfw=False)
    assert result is not None
    assert "primary" in result or "topFive" in result
    assert result["cached"] is False



@pytest.mark.asyncio
async def test_cache_hit_performance():
    query = "performance latency test query"
    key = _make_cache_key(query, "gif", False)
    query_cache.set(key, {"query": query, "results": [], "primary": {}})

    res = await recommend(user_text=query, format_pref="gif", nsfw=False)
    assert res["cached"] is True
    assert res["latencyMs"] < 50
