# MemeGPT — Database Backup & Recovery

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Documentation of backup strategies, disaster recovery procedures, and data protection for all MemeGPT data stores.

---

## Backup Strategy

### Supabase PostgreSQL (Production)

| Feature | Details |
|---|---|
| Automatic backups | Daily snapshots (Supabase managed) |
| Retention | 7 days (Free), 30 days (Pro) |
| Point-in-time recovery | Pro plan only |
| Manual export | `pg_dump` via Supabase CLI |

```bash
# Manual backup
supabase db dump --data-only > backup_$(date +%Y%m%d).sql

# Restore from backup
psql $DATABASE_URL < backup_20260115.sql
```

### SQLite (Development)

```bash
# Simple file copy
cp prisma/dev.db prisma/dev.db.backup

# Or use sqlite3 backup command
sqlite3 prisma/dev.db ".backup 'backup.db'"
```

### Qdrant (Vector Database)

```bash
# Qdrant Cloud: managed snapshots (automatic)
# Self-hosted: create snapshot via API
curl -X POST "http://localhost:6333/collections/memes/snapshots"
```

### Cloudflare R2 (Media Files)

R2 doesn't support versioning on the free tier. Backup strategy:
1. Media files are immutable (never modified, only added)
2. Meme images can be re-downloaded from source APIs
3. Weekly sync to a secondary R2 bucket (Phase 2)

---

## Recovery Procedures

### Scenario 1: Supabase Database Corruption

```
1. Stop all backend services
2. Identify last good backup in Supabase dashboard
3. Restore from snapshot
4. Verify data integrity: SELECT COUNT(*) FROM memes;
5. Re-deploy backend services
6. Verify search functionality
```

### Scenario 2: Qdrant Index Loss

```
1. Search will degrade to keyword-only mode (rule engine)
2. Trigger re-indexing pipeline: python scripts/index_qdrant.py
3. Re-indexing takes ~30 minutes for 5K memes
4. Verify: python scripts/verify_index.py
```

### Scenario 3: Complete Data Loss

```
1. Restore PostgreSQL from Supabase backup
2. Re-run indexing pipeline (regenerates all embeddings)
3. Media files re-download from source APIs
4. Total recovery time: ~2 hours
```

---

## Recovery Time Objectives

| Scenario | RTO (Target) | RPO (Data Loss) |
|---|---|---|
| Database restore | <1 hour | <24 hours |
| Vector index rebuild | <30 min | 0 (regenerated) |
| Media re-download | <2 hours | 0 (re-downloadable) |
| Full system recovery | <4 hours | <24 hours |

---

## Best Practices

1. **Test restores monthly** — a backup you can't restore is useless
2. **Automate backups** — never rely on manual processes
3. **Monitor backup success** — alert on failed backups
4. **Store backups off-site** — not in the same cloud account
5. **Document recovery procedures** — runbooks for every scenario

---

> **Related Documents:**
> - [Database_Overview.md](./Database_Overview.md) · [12_Deployment/Deployment_Overview.md](../12_Deployment/Deployment_Overview.md)
