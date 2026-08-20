"""Tests for Database Indexing Strategy from 06_Database/Indexing.md."""

from app.services.database_service import (
    generate_postgres_index_ddl,
    get_query_performance_targets,
    get_bloat_maintenance_policy,
    get_hnsw_vector_index_config,
    verify_database_indexes,
)


def test_generate_postgres_index_ddl():
    ddl = generate_postgres_index_ddl()
    assert "CREATE INDEX IF NOT EXISTS idx_memes_categories ON memes USING GIN(categories);" in ddl
    assert "CREATE INDEX IF NOT EXISTS idx_memes_emotions ON memes USING GIN(emotions);" in ddl
    assert "CREATE INDEX IF NOT EXISTS idx_memes_usage_count ON memes(usage_count DESC);" in ddl
    assert "CREATE INDEX IF NOT EXISTS idx_memes_viral_active ON memes(viral_score) WHERE viral_score > 0;" in ddl
    assert "CREATE INDEX IF NOT EXISTS idx_feedback_meme_action ON feedback(meme_id, action, created_at DESC);" in ddl


def test_get_query_performance_targets():
    targets = get_query_performance_targets()
    target_map = {t["pattern"]: t for t in targets}

    assert "Get meme by slug" in target_map
    assert target_map["Get meme by slug"]["target_ms"] == 2.0
    assert target_map["Get meme by slug"]["worst_case_ms"] == 5.0

    assert "Search memes by category" in target_map
    assert target_map["Search memes by category"]["target_ms"] == 5.0

    assert "Top trending (ORDER BY usage)" in target_map
    assert target_map["Top trending (ORDER BY usage)"]["target_ms"] == 10.0


def test_get_bloat_maintenance_policy():
    policies = get_bloat_maintenance_policy()
    assert len(policies) == 4

    types = [p["index_type"] for p in policies]
    assert any("B-tree on high-write" in t for t in types)
    assert any("GIN on array" in t for t in types)
    assert any("Partial index" in t for t in types)


def test_get_hnsw_vector_index_config():
    hnsw = get_hnsw_vector_index_config()
    assert hnsw["vector_size"] == 384
    assert hnsw["distance"] == "Cosine"
    assert hnsw["hnsw_config"]["m"] == 16
    assert hnsw["hnsw_config"]["ef_construct"] == 128
    assert hnsw["hnsw_config"]["full_scan_threshold"] == 10000


def test_verify_database_indexes():
    verification = verify_database_indexes()
    assert verification["status"] == "verified"
    assert verification["is_indexed"] is True
    assert "memes" in verification["model_indexes"]
