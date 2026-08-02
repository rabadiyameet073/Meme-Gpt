# MemeGPT — Database Recovery

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Step-by-step recovery procedures for every data loss scenario — database corruption, vector index loss, media file loss, and full disaster recovery.

---

## Recovery Scenarios

### Scenario 1: Supabase Database Corrupted

```bash
# Step 1: Identify the issue
supabase db status

# Step 2: Restore from latest backup (Supabase dashboard)
# Dashboard → Project → Backups → Select date → Restore

# Step 3: Verify data integrity
supabase db diff

# Step 4: Re-sync with Qdrant if needed
python scripts/sync_popularity_scores.py
```

**Recovery Time:** ~5 minutes  
**Data Loss:** Up to 24 hours (daily backup)

---

### Scenario 2: Qdrant Index Lost

```bash
# Step 1: Verify the issue
python scripts/verify_index.py
# Output: "Collection 'memes' not found" or "0 vectors"

# Step 2: Recreate collection
python scripts/create_collection.py

# Step 3: Re-generate embeddings (if processed data exists)
python scripts/generate_embeddings.py

# Step 4: Re-index all vectors
python scripts/index_qdrant.py

# Step 5: Verify
python scripts/verify_index.py
# Output: "10,247 vectors indexed. Test search: ✓"
```

**Recovery Time:** ~30 minutes  
**Data Loss:** None (regenerated from source)

---

### Scenario 3: R2 Media Files Lost

```bash
# Step 1: Re-upload from local source
python scripts/upload_to_r2.py --source data/raw/ --bucket memegpt-memes

# Step 2: Verify URLs
python scripts/verify_cdn_urls.py
```

**Recovery Time:** ~1 hour (depends on file count)  
**Data Loss:** None (source files are canonical)

---

### Scenario 4: Full Disaster Recovery

```bash
# Complete rebuild from scratch

# 1. Deploy fresh backend
railway init && railway up

# 2. Deploy fresh frontend  
cd apps/web && vercel --prod

# 3. Restore database
supabase db restore backup_latest.sql

# 4. Rebuild vector index
python scripts/generate_embeddings.py
python scripts/index_qdrant.py

# 5. Re-upload media
python scripts/upload_to_r2.py

# 6. Verify everything
python scripts/verify_index.py
curl https://api.memegpt.com/health
```

**Recovery Time:** ~2 hours  
**Data Loss:** Up to 24 hours of search logs/feedback

---

## Recovery Checklist

- [ ] Database restored and accessible
- [ ] Qdrant collection exists with correct vector count
- [ ] Health endpoint returns `status: ok`
- [ ] Search returns results for test query
- [ ] CDN images load correctly
- [ ] Rate limiting functional
- [ ] Monitoring alerts cleared

---

> **Related Documents:**
> - [Backup.md](./Backup.md) — Backup strategy
> - [12_Deployment/Deployment_Overview.md](../12_Deployment/Deployment_Overview.md) — Deployment procedures
