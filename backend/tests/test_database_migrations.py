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
