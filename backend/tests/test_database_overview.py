"""Tests for Polyglot Database Architecture from 06_Database/Database_Overview.md."""

from app.services.database_service import (
    get_polyglot_database_overview,
    get_data_ownership_matrix,
    get_access_patterns,
    verify_polyglot_health,
)


def test_get_polyglot_database_overview_stores_and_headroom():
    overview = get_polyglot_database_overview()
    assert "stores" in overview
    stores = overview["stores"]

    # 1. Supabase PostgreSQL
    assert "relational" in stores
    assert stores["relational"]["name"] == "Supabase PostgreSQL"
    assert stores["relational"]["free_tier_limits"]["headroom"] == "5x"

    # 2. Qdrant Cloud
    assert "vector" in stores
    assert stores["vector"]["name"] == "Qdrant Cloud"
    assert stores["vector"]["free_tier_limits"]["headroom"] == "14x"

    # 3. Upstash Redis
    assert "cache" in stores
    assert stores["cache"]["name"] == "Upstash Redis"
    assert stores["cache"]["free_tier_limits"]["headroom"] == "2x"

    # 4. Cloudflare R2
    assert "object_storage" in stores
    assert stores["object_storage"]["name"] == "Cloudflare R2"
    assert stores["object_storage"]["free_tier_limits"]["headroom"] == "2x"


def test_get_data_ownership_matrix():
    matrix = get_data_ownership_matrix()
    entities = {item["entity"]: item for item in matrix}

    assert "Meme metadata" in entities
    assert entities["Meme metadata"]["primary_store"] == "Supabase"

    assert "Meme embeddings" in entities
    assert entities["Meme embeddings"]["primary_store"] == "Qdrant"

    assert "Meme media" in entities
    assert entities["Meme media"]["primary_store"] == "Cloudflare R2"

    assert "Search results" in entities
    assert entities["Search results"]["primary_store"] == "Redis"


def test_get_access_patterns():
    patterns = get_access_patterns()
    pattern_map = {p["pattern"]: p for p in patterns}

    assert "Vector similarity" in pattern_map
    assert pattern_map["Vector similarity"]["store"] == "Qdrant"
    assert pattern_map["Vector similarity"]["frequency"] == "Every search"

    assert "Meme by slug" in pattern_map
    assert pattern_map["Meme by slug"]["store"] == "Supabase"

    assert "Search result cache" in pattern_map
    assert pattern_map["Search result cache"]["store"] == "Redis"


def test_verify_polyglot_health():
    health = verify_polyglot_health()
    assert health["status"] == "healthy"
    assert health["total_stores_active"] == 4


def test_free_tier_limits_and_alert_thresholds():
    from app.services.database_service import get_free_tier_limits, check_free_tier_alerts

    limits = get_free_tier_limits()
    assert "supabase" in limits
    assert "qdrant" in limits
    assert "redis" in limits
    assert "r2" in limits

    assert limits["supabase"]["headroom"] == "5x"
    assert limits["qdrant"]["headroom"] == "14x"

    # Default alert threshold at 80% -> no alerts since max utilization is 50%
    alerts = check_free_tier_alerts(threshold_pct=80.0)
    assert len(alerts) == 0

    # Custom alert threshold at 40% -> triggers alerts for Redis & R2 (50% utilization)
    low_threshold_alerts = check_free_tier_alerts(threshold_pct=40.0)
    assert len(low_threshold_alerts) >= 2
    alert_services = [a["service"] for a in low_threshold_alerts]
    assert "Upstash Redis" in alert_services
    assert "Cloudflare R2" in alert_services
