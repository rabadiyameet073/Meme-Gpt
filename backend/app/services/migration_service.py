"""
MemeGPT — Database Migration Management Service
Specification: 06_Database/Migrations.md
"""

from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
PRISMA_DIR = PROJECT_ROOT / "prisma" if (PROJECT_ROOT / "prisma").exists() else BACKEND_DIR / "prisma"
MIGRATIONS_DIR = PRISMA_DIR / "migrations"


def get_migration_workflow_guide() -> dict[str, Any]:
    """Return the migration workflow instructions across environments from 06_Database/Migrations.md."""
    return {
        "environments": {
            "development_sqlite": {
                "environment": "Development (Local SQLite)",
                "steps": [
                    {"step": 1, "action": "Edit schema.prisma with changes"},
                    {"step": 2, "command": "npx prisma migrate dev --name <migration_name>", "desc": "Create and apply migration"},
                    {"step": 3, "command": "npx prisma migrate dev --create-only --name <migration_name>", "desc": "Generate migration without applying"},
                    {"step": 4, "command": "npx prisma generate", "desc": "Regenerate Prisma client"},
                    {"step": 5, "command": "npx prisma migrate reset", "desc": "Reset local DB (destructive)"},
                ],
            },
            "staging_supabase": {
                "environment": "Staging (Supabase)",
                "steps": [
                    {"step": 1, "command": "npx prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script > migrations/001_initial.sql", "desc": "Generate SQL from schema diff"},
                    {"step": 2, "command": "supabase db push", "desc": "Apply via Supabase CLI"},
                    {"step": 3, "action": "Or apply via Supabase Dashboard SQL Editor"},
                ],
            },
            "production_supabase": {
                "environment": "Production (Supabase)",
                "steps": [
                    {"step": 1, "command": "npx prisma migrate dev --create-only --name <migration_name>", "desc": "Create migration file for review"},
                    {"step": 2, "action": "Review generated SQL in prisma/migrations/"},
                    {"step": 3, "command": "npx prisma migrate deploy", "desc": "Apply via CI/CD pipeline"},
                    {"step": 4, "command": "npx prisma migrate status", "desc": "Verify migration status"},
                ],
            },
        },
    }


def classify_schema_change(change_type: str) -> dict[str, Any]:
    """Classify schema change risk, safety level, and required procedure from 06_Database/Migrations.md."""
    rules = {
        "add_nullable_column": {
            "change_type": "Add nullable column",
            "safety": "safe",
            "is_safe": True,
            "procedure": "Create migration, deploy, zero downtime",
        },
        "add_not_null_column": {
            "change_type": "Add NOT NULL column",
            "safety": "requires_backfill",
            "is_safe": False,
            "procedure": "Add as nullable -> backfill data in batches (1000 rows) -> ALTER to NOT NULL",
        },
        "rename_column": {
            "change_type": "Rename column",
            "safety": "requires_deprecation",
            "is_safe": False,
            "procedure": "Add new column -> dual-write -> migrate data -> drop old column",
        },
        "drop_column": {
            "change_type": "Drop column",
            "safety": "requires_deprecation",
            "is_safe": False,
            "procedure": "Mark deprecated -> wait 1 week -> drop",
        },
        "add_index": {
            "change_type": "Add index",
            "safety": "safe",
            "is_safe": True,
            "procedure": "Can run concurrently with CREATE INDEX CONCURRENTLY",
        },
        "drop_index": {
            "change_type": "Drop index",
            "safety": "safe",
            "is_safe": True,
            "procedure": "No data loss risk",
        },
        "add_table": {
            "change_type": "Add table",
            "safety": "safe",
            "is_safe": True,
            "procedure": "No impact on existing queries",
        },
        "change_column_type": {
            "change_type": "Change column type",
            "safety": "needs_cast",
            "is_safe": False,
            "procedure": "Add temp column -> migrate data with CAST -> swap -> drop old column",
        },
    }
    normalized = change_type.lower().strip().replace(" ", "_")
    return rules.get(normalized, {
        "change_type": change_type,
        "safety": "unknown",
        "is_safe": False,
        "procedure": "Manual review required",
    })


def generate_safe_column_migration(
    table: str,
    column: str,
    col_type: str,
    default_val: Any = None,
    batch_size: int = 1000,
) -> dict[str, Any]:
    """Generate 3-step safe column addition SQL with batch backfill from 06_Database/Migrations.md."""
    val_repr = f"'{default_val}'" if isinstance(default_val, str) else (default_val if default_val is not None else "0.0")

    step1_sql = f'ALTER TABLE "{table}" ADD COLUMN "{column}" {col_type};'
    step2_sql = f'UPDATE "{table}" SET "{column}" = {val_repr} WHERE "{column}" IS NULL; -- Batch size: {batch_size} rows'
    step3_sql = f'ALTER TABLE "{table}" ALTER COLUMN "{column}" SET NOT NULL;'

    rollback_sql = f'ALTER TABLE "{table}" DROP COLUMN "{column}";'

    return {
        "table": table,
        "column": column,
        "col_type": col_type,
        "steps": [
            {
                "step": 1,
                "description": "Add as nullable (safe, no downtime)",
                "sql": step1_sql,
            },
            {
                "step": 2,
                "description": f"Backfill data in batches of {batch_size} rows (background job)",
                "sql": step2_sql,
            },
            {
                "step": 3,
                "description": "Make NOT NULL (brief exclusive lock)",
                "sql": step3_sql,
            },
        ],
        "full_sql": f"{step1_sql}\n\n{step2_sql}\n\n{step3_sql}",
        "rollback_sql": rollback_sql,
    }


def get_rollback_decision_matrix() -> list[dict[str, str]]:
    """Return rollback scenario decision matrix from 06_Database/Migrations.md."""
    return [
        {
            "scenario": "Bug in new code that reads new schema",
            "action": "Rollback code only",
            "downtime": "None",
        },
        {
            "scenario": "Bug in migration that corrupts data",
            "action": "Rollback migration + restore from backup",
            "downtime": "5–15 min",
        },
        {
            "scenario": "Migration too slow (table lock)",
            "action": "Kill migration process, fix, retry",
            "downtime": "None (lock released)",
        },
        {
            "scenario": "NOT NULL failure on backfill",
            "action": "Rollback, fix backfill, retry",
            "downtime": "None",
        },
    ]


def get_migration_checklist() -> list[str]:
    """Return standard migration pre-flight checklist from 06_Database/Migrations.md."""
    return [
        "Migration tested on a staging database first",
        "Backfill plan exists for NOT NULL columns",
        "Rollback script prepared before applying",
        "Migration reviewed by a second engineer",
        "No long-running locks expected during peak hours",
        "Prisma client regenerated after migration (npx prisma generate)",
        "Application tested against migrated schema",
    ]


def get_common_migration_errors() -> list[dict[str, str]]:
    """Return common migration errors, causes, and fixes from 06_Database/Migrations.md."""
    return [
        {
            "error": "P2002: Unique constraint failed",
            "cause": "Duplicate data violates unique constraint",
            "fix": "Deduplicate before adding constraint",
        },
        {
            "error": "Migration not found",
            "cause": "Migration file deleted or renamed",
            "fix": "Restore from git history",
        },
        {
            "error": "Can't reach database",
            "cause": "Supabase connection string wrong",
            "fix": "Check DATABASE_URL env var",
        },
        {
            "error": "The migration was not applied correctly",
            "cause": "Partial application",
            "fix": "prisma migrate reset (dev only)",
        },
    ]


def verify_migration_health() -> dict[str, Any]:
    """Verify local Prisma migration files and directory structure."""
    schema_exists = (PRISMA_DIR / "schema.prisma").exists()
    migrations_exist = MIGRATIONS_DIR.exists()

    found_migrations = []
    if migrations_exist:
        for child in sorted(MIGRATIONS_DIR.iterdir()):
            if child.is_dir():
                sql_file = child / "migration.sql"
                found_migrations.append({
                    "name": child.name,
                    "has_sql": sql_file.exists(),
                    "size_bytes": sql_file.stat().st_size if sql_file.exists() else 0,
                })

    return {
        "status": "healthy" if schema_exists and len(found_migrations) >= 3 else "degraded",
        "prisma_schema_exists": schema_exists,
        "migrations_directory_exists": migrations_exist,
        "total_migrations": len(found_migrations),
        "migrations": found_migrations,
    }
