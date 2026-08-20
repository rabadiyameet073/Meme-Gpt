"""Tests for Database Tables Specification from 06_Database/Tables.md."""

from app.services.database_service import (
    get_table_specifications_catalog,
    get_table_row_estimates,
    validate_meme_record,
    validate_search_log_record,
)


def test_get_table_specifications_catalog():
    catalog = get_table_specifications_catalog()
    assert "tables" in catalog
    tables = catalog["tables"]

    assert "memes" in tables
    assert "search_logs" in tables
    assert "feedback" in tables
    assert "api_keys" in tables

    meme_cols = {col["name"]: col for col in tables["memes"]["columns"]}
    assert "id" in meme_cols
    assert "name" in meme_cols
    assert "slug" in meme_cols
    assert "emotions" in meme_cols
    assert "popularity_score" in meme_cols

    assert "idx_memes_slug" in tables["memes"]["indexes"]
    assert "idx_memes_categories" in tables["memes"]["indexes"]


def test_get_table_row_estimates():
    estimates = get_table_row_estimates()
    assert len(estimates) == 4
    est_map = {e["table"]: e for e in estimates}

    assert est_map["memes"]["rows_launch"] == 10000
    assert est_map["memes"]["rows_1_year"] == 50000

    assert est_map["search_logs"]["rows_1_year"] == 500000
    assert est_map["feedback"]["rows_1_year"] == 200000
    assert est_map["api_keys"]["rows_1_year"] == 500


def test_validate_meme_record():
    valid_meme = {
        "id": "meme_042",
        "name": "This Is Fine",
        "slug": "this-is-fine",
        "meme_type": "reaction",
        "popularity_score": 0.85,
    }
    is_valid, errors = validate_meme_record(valid_meme)
    assert is_valid is True
    assert len(errors) == 0

    invalid_meme = {
        "id": "",
        "name": "A" * 201,
        "slug": "slug",
        "meme_type": "invalid_type",
        "popularity_score": 1.5,
    }
    is_valid, errors = validate_meme_record(invalid_meme)
    assert is_valid is False
    assert len(errors) >= 3


def test_validate_search_log_record():
    valid_log = {
        "query_id": "qid_12345",
        "query_hash": "e99a18c428cb38d5f260853678922e03",
        "latency_ms": 15,
    }
    is_valid, errors = validate_search_log_record(valid_log)
    assert is_valid is True
    assert len(errors) == 0

    invalid_log = {
        "query_id": "",
        "query_hash": "short",
        "latency_ms": -5,
    }
    is_valid, errors = validate_search_log_record(invalid_log)
    assert is_valid is False
    assert len(errors) == 3
