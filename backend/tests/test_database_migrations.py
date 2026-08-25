"""Tests for Database Migrations Workflow and Safety from 06_Database/Migrations.md."""

from app.services.migration_service import (
    get_migration_workflow_guide,
    classify_schema_change,
    generate_safe_column_migration,
    get_rollback_decision_matrix,
    get_migration_checklist,
    get_common_migration_errors,
    verify_migration_health,
)


def test_get_migration_workflow_guide():
    guide = get_migration_workflow_guide()
    assert "environments" in guide
    envs = guide["environments"]
    assert "development_sqlite" in envs
    assert "staging_supabase" in envs
    assert "production_supabase" in envs

    # Verify commands
    dev_cmds = [s.get("command") for s in envs["development_sqlite"]["steps"] if "command" in s]
    assert any("prisma migrate dev" in c for c in dev_cmds)
    assert any("prisma generate" in c for c in dev_cmds)


def test_classify_schema_change_safety():
    # Safe changes
    assert classify_schema_change("add_nullable_column")["is_safe"] is True
    assert classify_schema_change("add_index")["is_safe"] is True
    assert classify_schema_change("add_table")["is_safe"] is True
    assert classify_schema_change("drop_index")["is_safe"] is True

    # Changes requiring backfill or deprecation
    not_null = classify_schema_change("add_not_null_column")
    assert not_null["is_safe"] is False
    assert not_null["safety"] == "requires_backfill"

    rename = classify_schema_change("rename_column")
    assert rename["is_safe"] is False
    assert rename["safety"] == "requires_deprecation"

    drop_col = classify_schema_change("drop_column")
    assert drop_col["is_safe"] is False

    cast_col = classify_schema_change("change_column_type")
    assert cast_col["safety"] == "needs_cast"


def test_generate_safe_column_migration():
    plan = generate_safe_column_migration(
        table="memes",
        column="emotion_score",
        col_type="REAL",
        default_val=0.5,
        batch_size=1000,
    )
    assert plan["table"] == "memes"
    assert plan["column"] == "emotion_score"
    assert len(plan["steps"]) == 3

    assert 'ALTER TABLE "memes" ADD COLUMN "emotion_score" REAL;' in plan["steps"][0]["sql"]
    assert 'SET "emotion_score" = 0.5' in plan["steps"][1]["sql"]
    assert 'ALTER TABLE "memes" ALTER COLUMN "emotion_score" SET NOT NULL;' in plan["steps"][2]["sql"]
    assert 'DROP COLUMN "emotion_score"' in plan["rollback_sql"]


def test_get_rollback_decision_matrix():
    matrix = get_rollback_decision_matrix()
    assert len(matrix) >= 4
    scenarios = {m["scenario"]: m for m in matrix}

    assert "Bug in new code that reads new schema" in scenarios
    assert scenarios["Bug in new code that reads new schema"]["downtime"] == "None"

    assert "Bug in migration that corrupts data" in scenarios
    assert "5–15 min" in scenarios["Bug in migration that corrupts data"]["downtime"]


def test_get_migration_checklist_and_errors():
    checklist = get_migration_checklist()
    assert len(checklist) == 7
    assert any("staging database" in item.lower() for item in checklist)
    assert any("rollback script" in item.lower() for item in checklist)

    errors = get_common_migration_errors()
    assert len(errors) == 4
    err_names = [e["error"] for e in errors]
    assert any("P2002" in e for e in err_names)
    assert any("Migration not found" in e for e in err_names)


def test_verify_migration_health():
    health = verify_migration_health()
    assert health["status"] == "healthy"
    assert health["prisma_schema_exists"] is True
    assert health["migrations_directory_exists"] is True
    assert health["total_migrations"] >= 3


def test_sqlite_migration_script_execution():
    """Verify migrate.py executes and applies / skips migrations safely."""
    from migrate import run_migration
    res = run_migration()
    assert isinstance(res, dict)
    assert "applied" in res
    assert "skipped" in res
    assert (res["applied"] + res["skipped"]) >= 20


def test_meme_model_upgraded_columns_step1():
    """Verify Meme model contains all 12+ upgraded columns from Step 1."""
    from app.database import Meme
    cols = Meme.__table__.columns.keys()

    # Required columns per Step 1
    expected_cols = [
        "id", "name", "slug", "categories", "emotions", "dialogue", "explanation", "keywords",
        "image_url", "gif_url", "mp4_url", "thumb_url", "webp_url",
        "image_ref", "gif_ref", "video_ref",
        "source", "nsfw",
        "view_count", "download_count", "usage_count", "upvotes", "downvotes",
        "viral_score", "popularity_score",
        "created_at", "updated_at", "indexed_at"
    ]
    for col in expected_cols:
        assert col in cols, f"Missing column on Meme model: {col}"

    # Verify serialization
    meme = Meme(
        id="test-migration-001",
        name="Migration Meme",
        slug="migration-meme",
        categories=["tech", "ai"],
        emotions=["joy", "excitement"],
        image_url="https://cdn.memegpt.com/m.png",
        thumb_url="https://cdn.memegpt.com/thumb.webp",
        popularity_score=0.88,
        source="imgflip",
        nsfw=False,
    )
    d = meme.to_dict()
    assert d["id"] == "test-migration-001"
    assert d["categories"] == ["tech", "ai"]
    assert d["emotions"] == ["joy", "excitement"]
    assert d["popularity_score"] == 0.88
    assert d["thumb_url"] == "https://cdn.memegpt.com/thumb.webp"
    assert d["source"] == "imgflip"
    assert d["nsfw"] is False


def test_user_model_upgraded_columns_step2():
    """Verify User model contains name, avatar_url, preferences from Step 2."""
    from app.database import User
    cols = User.__table__.columns.keys()

    assert "name" in cols
    assert "avatar_url" in cols
    assert "preferences" in cols
    assert "plan" in cols

    user = User(
        id="user-001",
        email="dev@memegpt.com",
        name="Developer",
        avatar_url="https://cdn.memegpt.com/avatar.png",
        preferences={"format_pref": "gif", "nsfw": False},
    )
    d = user.to_dict()
    assert d["name"] == "Developer"
    assert d["avatar_url"] == "https://cdn.memegpt.com/avatar.png"
    assert d["preferences"]["format_pref"] == "gif"


def test_search_log_gdpr_hash_step3():
    """Verify SearchLog stores MD5 query_hash and no raw PII query from Step 3."""
    from app.database import SearchLog
    cols = SearchLog.__table__.columns.keys()

    assert "query_hash" in cols
    assert "top_meme_id" in cols
    assert "cache_hit" in cols
    assert "model_used" in cols
    assert "emotion_detected" in cols
    assert "result_count" in cols

    log = SearchLog(
        query="Confidential user search text",
        result_count=5,
        latency_ms=120.5,
        cache_hit=True,
    )
    assert log.query_hash is not None
    assert len(log.query_hash) == 32
    assert "Confidential" not in log.query_hash
    d = log.to_dict()
    assert d["cache_hit"] is True
    assert d["result_count"] == 5
