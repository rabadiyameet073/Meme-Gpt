"""Tests for Multi-Store Database Backup Strategy from 06_Database/Backup.md."""

from app.services.backup_service import (
    get_backup_status_summary,
    check_table_criticalities,
)


def test_get_backup_status_summary_matrix():
    summary = get_backup_status_summary()
    assert "backup_matrix" in summary
    matrix = summary["backup_matrix"]

    assert "supabase_postgresql" in matrix
    assert matrix["supabase_postgresql"]["frequency"] == "Daily"
    assert matrix["supabase_postgresql"]["retention"] == "7 days (free tier)"

    assert "qdrant_cloud" in matrix
    assert matrix["qdrant_cloud"]["method"] == "Re-index from source data"

    assert "cloudflare_r2" in matrix
    assert matrix["cloudflare_r2"]["retention"] == "Permanent"

    assert "redis_cache" in matrix
    assert matrix["redis_cache"]["method"] == "No backup needed"


def test_check_table_criticalities():
    tables = check_table_criticalities()
    assert "memes" in tables
    assert tables["memes"]["criticality"] == "Critical"

    assert "api_keys" in tables
    assert tables["api_keys"]["criticality"] == "Critical"

    assert "search_logs" in tables
    assert tables["search_logs"]["criticality"] == "Important"

    assert "feedback" in tables
    assert tables["feedback"]["criticality"] == "Important"
