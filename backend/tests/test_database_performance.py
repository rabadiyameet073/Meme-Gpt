"""Tests for Database Performance and Optimizations from 06_Database/Performance.md."""

from app.database import get_db, Meme
from app.services.database_service import (
    get_performance_query_targets,
    get_connection_pool_config,
    get_supabase_free_tier_limits,
    get_scaling_strategy_matrix,
    paginate_memes_offset,
    paginate_memes_cursor,
    get_memes_with_vote_aggregations,
    benchmark_query_latencies,
)


def test_get_performance_query_targets():
    targets = get_performance_query_targets()
    assert len(targets) == 8
    target_map = {t["query"]: t for t in targets}

    assert "Get meme by ID" in target_map
    assert target_map["Get meme by ID"]["target_ms"] == 2.0
    assert target_map["Get meme by ID"]["index_used"] == "PRIMARY KEY"

    assert "Get memes by category" in target_map
    assert target_map["Get memes by category"]["target_ms"] == 5.0

    assert "Get trending (ORDER BY usage)" in target_map
    assert target_map["Get trending (ORDER BY usage)"]["target_ms"] == 10.0

    assert "Search by name LIKE" in target_map
    assert target_map["Search by name LIKE"]["target_ms"] == 15.0


def test_get_connection_pool_and_supabase_limits():
    pool_cfg = get_connection_pool_config()
    assert "production_postgresql" in pool_cfg
    prod = pool_cfg["production_postgresql"]
    assert prod["pool_size"] == 5
    assert prod["max_overflow"] == 10
    assert prod["pool_timeout"] == 30
    assert prod["pool_recycle"] == 1800

    sb_limits = get_supabase_free_tier_limits()
    assert sb_limits["max_connections"] == 60
    assert sb_limits["database_size"] == "500MB"
    assert sb_limits["bandwidth"] == "2GB/month"


def test_get_scaling_strategy_matrix():
    matrix = get_scaling_strategy_matrix()
    assert len(matrix) == 4
    scales = {m["scale"]: m for m in matrix}

    assert "<10K memes" in scales
    assert scales["<10K memes"]["estimated_cost"] == "$0"

    assert "10K–100K memes" in scales
    assert "$25/month" in scales["10K–100K memes"]["estimated_cost"]

    assert "1M+ memes" in scales


def test_paginate_memes_offset_and_cursor():
    with next(get_db()) as db:
        # Offset pagination
        offset_res = paginate_memes_offset(db, page=1, page_size=10)
        assert offset_res["pagination_type"] == "offset"
        assert offset_res["page"] == 1
        assert offset_res["page_size"] == 10
        assert "items" in offset_res
        assert "total_items" in offset_res

        # Cursor pagination
        cursor_res = paginate_memes_cursor(db, limit=10)
        assert cursor_res["pagination_type"] == "cursor"
        assert cursor_res["limit"] == 10
        assert "items" in cursor_res


def test_get_memes_with_vote_aggregations():
    with next(get_db()) as db:
        res = get_memes_with_vote_aggregations(db, limit=10)
        assert isinstance(res, list)
        if res:
            assert "id" in res[0]
            assert "vote_count" in res[0]


def test_benchmark_query_latencies():
    with next(get_db()) as db:
        report = benchmark_query_latencies(db)
        assert report["status"] == "completed"
        assert report["total_benchmarks"] >= 4
        for b in report["benchmarks"]:
            assert "actual_ms" in b
            assert "target_ms" in b
            assert b["actual_ms"] >= 0.0
