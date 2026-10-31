# MemeGPT — Database Migrations

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete migration workflow guide — managing schema changes safely across development, staging, and production environments using Prisma.

---

## Migration Workflow

### Development (Local SQLite)

```bash
# 1. Edit schema.prisma with your changes
# 2. Create a migration
npx prisma migrate dev --name add_emotion_score_to_memes

# 3. Apply the migration (auto-applied with --create-only)
#    Use --create-only to generate without applying:
npx prisma migrate dev --create-only --name add_emotion_score_to_memes

# 4. Generate updated Prisma client
npx prisma generate

# 5. Reset local DB (destructive — drops all data)
npx prisma migrate reset
```

### Staging (Supabase)

```bash
# 1. Generate SQL from Prisma schema diff
npx prisma migrate diff \
  --from-empty \
  --to-schema-datamodel prisma/schema.prisma \
  --script > migrations/001_initial.sql

# 2. Apply via Supabase CLI
supabase db push

# 3. Or apply via Supabase Dashboard SQL editor
#    Copy the generated SQL and run in the dashboard
```

### Production (Supabase)

```bash
# 1. Create a migration file
npx prisma migrate dev --create-only --name add_emotion_score_to_memes

# 2. Review the generated SQL in prisma/migrations/
# 3. Apply via CI/CD pipeline
npx prisma migrate deploy

# 4. Verify migration status
npx prisma migrate status
```

---

## Migration Best Practices

### Schema Change Rules

| Change Type | Safe? | Procedure |
|---|---|---|
| Add nullable column | ✅ Safe | Create migration, deploy, no downtime |
| Add NOT NULL column | ⚠️ Requires backfill | Add as nullable → backfill data → ALTER to NOT NULL |
| Rename column | ⚠️ Requires deprecation | Add new column → dual-write → migrate data → drop old |
| Drop column | ⚠️ Requires deprecation | Mark deprecated → wait 1 week → drop |
| Add index | ✅ Safe | Can run concurrently with CREATE INDEX CONCURRENTLY |
| Drop index | ✅ Safe | No data loss risk |
| Add table | ✅ Safe | No impact on existing queries |
| Change column type | ⚠️ Needs CAST | Add temp column → migrate data → swap → drop old |

### Safe Column Addition (with Backfill)

```sql
-- Step 1: Add as nullable (safe, no downtime)
ALTER TABLE memes ADD COLUMN emotion_score REAL;

-- Step 2: Backfill data in batches (background job)
UPDATE memes SET emotion_score = 0.5 WHERE emotion_score IS NULL;
-- Repeat for batches of 1000 rows to avoid long-running locks

-- Step 3: Make NOT NULL (requires exclusive lock, brief downtime)
ALTER TABLE memes ALTER COLUMN emotion_score SET NOT NULL;
```

### Migration Checklist

- [ ] Migration tested on a staging database first
- [ ] Backfill plan exists for NOT NULL columns
- [ ] Rollback script prepared before applying
- [ ] Migration reviewed by a second engineer
- [ ] No long-running locks expected during peak hours
- [ ] Prisma client regenerated after migration
- [ ] Application tested against migrated schema

---

## Rollback Procedures

### Quick Rollback (Last Migration)

```bash
# Prisma: roll back the last migration
npx prisma migrate down 1

# Regenerate client after rollback
npx prisma generate
```

### Manual Rollback (Complex Changes)

```sql
-- Example: rollback adding emotion_score column
ALTER TABLE memes DROP COLUMN emotion_score;

-- Example: rollback a new table
DROP TABLE IF EXISTS meme_collections;

-- Example: restore a dropped column
ALTER TABLE memes ADD COLUMN old_column TEXT;
UPDATE memes SET old_column = new_column;
-- Then deploy code that references old_column
```

### Rollback Decision Matrix

| Scenario | Action | Downtime |
|---|---|---|
| Bug in new code that reads new schema | Rollback code only | None |
| Bug in migration that corrupts data | Rollback migration + restore from backup | 5–15 min |
| Migration too slow (table lock) | Kill migration process, fix, retry | None (lock released) |
| NOT NULL failure on backfill | Rollback, fix backfill, retry | None |

---

## Migration File Structure

```
prisma/
├── schema.prisma           # Source of truth schema
├── migrations/
│   ├── 20260101_initial/
│   │   └── migration.sql   # Initial schema
│   ├── 20260215_add_emotion/
│   │   └── migration.sql   # Added emotion_score
│   └── 20260301_add_indexes/
│       └── migration.sql   # Performance indexes
└── seed.ts                 # Seed data script
```

---

## Common Migration Errors

| Error | Cause | Fix |
|---|---|---|
| `P2002: Unique constraint failed` | Duplicate data violates unique constraint | Deduplicate before adding constraint |
| `Migration not found` | Migration file deleted or renamed | Restore from git history |
| `Can't reach database` | Supabase connection string wrong | Check `DATABASE_URL` env var |
| `The migration was not applied correctly` | Partial application | `prisma migrate reset` (dev only) |

---

> **Related Documents:**
> - [Schema.md](./Schema.md) — Prisma schema reference
> - [Backup_Recovery.md](./Backup_Recovery.md) — Backup and restore procedures
> - [Database_Overview.md](./Database_Overview.md) — Database architecture
> - [01_Getting_Started/Installation.md](../01_Getting_Started/Installation.md) — Local setup guide