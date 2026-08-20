"""Tests for Complete Database Schema Specification from 06_Database/Schema.md."""

from datetime import datetime, timedelta, timezone
from app.database import get_db, init_db, SearchLog
from app.services.database_service import (
    get_complete_postgresql_ddl,
    get_feedback_action_signals,
    validate_feedback_action,
    anonymize_query_to_hash,
    purge_old_search_logs,
    get_schema_validation_rules,
)

init_db()


def test_get_complete_postgresql_ddl():
    ddl = get_complete_postgresql_ddl()
    assert "CREATE TABLE IF NOT EXISTS users" in ddl
    assert "CREATE TABLE IF NOT EXISTS memes" in ddl
    assert "CREATE TABLE IF NOT EXISTS feedback" in ddl
    assert "CREATE TABLE IF NOT EXISTS saved_memes" in ddl
    assert "CREATE TABLE IF NOT EXISTS search_logs" in ddl

    # Indexes
    assert "idx_memes_slug" in ddl
    assert "idx_memes_categories ON memes USING GIN(categories)" in ddl
    assert "idx_memes_emotions ON memes USING GIN(emotions)" in ddl
    assert "idx_feedback_meme_id" in ddl
    assert "idx_saved_memes_user_id" in ddl
    assert "idx_search_logs_query_hash" in ddl


def test_feedback_action_signals_and_validation():
    signals = get_feedback_action_signals()
    assert len(signals) == 8
    assert signals["view"] == 0.1
    assert signals["click"] == 0.5
    assert signals["copy"] == 1.0
    assert signals["download"] == 2.0
    assert signals["share"] == 3.0
    assert signals["thumbs_up"] == 2.0
    assert signals["thumbs_down"] == -1.0
    assert signals["skip"] == -0.3

    assert validate_feedback_action("view") is True
    assert validate_feedback_action("thumbs_up") is True
    assert validate_feedback_action("invalid_action") is False


def test_anonymize_query_to_hash():
    query = "Drake pointing at something funny"
    h1 = anonymize_query_to_hash(query)
    h2 = anonymize_query_to_hash("drake pointing at something funny")
    assert h1 == h2
    assert len(h1) == 32  # MD5 hex length


def test_purge_old_search_logs():
    with next(get_db()) as db:
        old_log = SearchLog(
            query="old query",
            session_id="old_sess",
            created_at=datetime.now(timezone.utc) - timedelta(days=100),
        )
        new_log = SearchLog(
            query="new query",
            session_id="new_sess",
            created_at=datetime.now(timezone.utc),
        )
        db.add_all([old_log, new_log])
        db.commit()

        purged_count = purge_old_search_logs(db, retention_days=90)
        assert purged_count >= 1


def test_get_schema_validation_rules():
    rules = get_schema_validation_rules()
    assert "memes" in rules
    assert rules["memes"]["popularity_score"]["max"] == 1.0
    assert rules["search_logs"]["retention_days"] == 90
    assert "view" in rules["feedback"]["valid_actions"]
