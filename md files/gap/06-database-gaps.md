# 06 — Database Gaps

**Source requirements:** `md files/documentation/06_Database/*` (Database_Overview, Schema, Migrations, Indexing, Backup, Relationships), `md files/upgraded_docs/02_Database_Schema_Migration.md`, `md files/completion_fixes/08_Production_Deployment.md`
**Related:** [01-architecture-consolidation-gaps](01-architecture-consolidation-gaps.md) · [23-data-privacy-retention-gaps](23-data-privacy-retention-gaps.md) · [20-ci-cd-deployment-gaps](20-ci-cd-deployment-gaps.md)

## Verified facts
- **Engine actually used:** SQLAlchemy on **SQLite** (`backend/app/config.py:76-80` defaults `sqlite:///{DB_PATH}`; `database.py` sets WAL pragmas). No `*.db` file is committed.
- **Tables:** 11 SQLAlchemy models (`database.py:184-688`), including users, api_keys, meme_flags, favourite_memes, device_tokens, feedback, search_logs, saved_memes.
- **Done well:** unique constraints on votes and favourites (`database.py:454,468`); search queries stored only as `query_hash` (`:596,611-616`); SQLite online backup with checksum plus a restore script (`backup_service.py:41-108,126`).

## Gaps
| Gap ID | Requirement | Status | Evidence | Expected | Required change | Priority |
|---|---|---|---|---|---|---|
| DB-01 | Production DB = Supabase PostgreSQL (`Database_Overview.md:32`) | Not implemented | SQLite default; no Postgres `DATABASE_URL` configured in the repo (ASSUMPTION – production env not visible) | Postgres in prod | Provision Supabase; run `backend/scripts/migrate_sqlite_to_postgres.py`; fix SQLite-only SQL | Critical |
| DB-02 | One schema source (`upgraded_docs/02`) | Incorrectly implemented | `prisma/schema.prisma` (6 models, `provider="sqlite"`) is unused and missing 5 tables; `prisma/seed.ts:1-2` imports a missing `../server/` | One ORM | Delete `prisma/` (recommended) or regenerate it | High |
| DB-03 | Versioned migrations (`Migrations.md`) | Partially implemented | `backend/migrate.py:17` uses `create_all` + raw SQLite `ALTER TABLE` inside try/except `sqlite3.OperationalError`; 3 Prisma SQL migrations are never applied; no Alembic | Alembic revisions, forward and backward | Add Alembic with a baseline from the current models; run in the deploy step | High |
| DB-04 | Postgres-grade indexes (`upgraded_docs/02:68`: GIN on arrays) | Partially implemented | B-tree only (`database.py:253` etc.); keywords/emotions stored as JSON text | `TEXT[]`/JSONB + GIN | After DB-01 | Medium |
| DB-05 | Truthful backup status (`Backup.md`) | Incorrectly implemented | `backup_service.py:110-123`: the non-SQLite branch writes nothing but returns `"sha256":"supabase-managed","status":"success"` | Never report success without an artifact | Real `pg_dump`, or verify that Supabase PITR is enabled and report `managed` honestly | High |
| DB-06 | Scheduled off-site backups | Not implemented | Local folder only; no workflow references backups | Daily encrypted upload to R2/S3 with retention | Add a GitHub Actions cron + `scripts/backup_manager.py` | High |
| DB-07 | Safe seeding (`upgraded_docs/15`) | Incorrectly implemented | `backend/seed.py:14` `init_db(drop_all=True)` drops users and api_keys | Upsert-only, with `--reset` opt-in | Change the default | High |
| DB-08 | Referential cleanup on user deletion | Partially implemented | See [23](23-data-privacy-retention-gaps.md) PRIV-03 | Cascade | FK `ondelete` or explicit cleanup | Medium |
| DB-09 | DB health checked | Not implemented | `/health` has no `SELECT 1` | Included | See [02](02-backend-core-gaps.md) BE-01 | Medium |

## Dependencies
DB-01 → DB-03 → DB-04/DB-05. Supabase credentials are a user-side action.
