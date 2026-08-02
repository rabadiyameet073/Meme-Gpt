# MemeGPT — Database Performance

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Database performance optimization strategies, query analysis, and scaling considerations.

---

## Query Performance Targets

| Query | Target Latency | Index Used |
|---|---|---|
| Get meme by ID | <2ms | PRIMARY KEY |
| Get memes by category | <5ms | `idx_memes_category` |
| Get trending (ORDER BY usage) | <10ms | `idx_memes_usage` |
| Search by name LIKE | <15ms | `idx_memes_name` |
| Get votes for meme | <5ms | `idx_votes_meme_id` |
| Get user's saved memes | <5ms | `idx_saved_user_id` |
| Insert vote | <5ms | — |
| Insert usage log | <3ms | — |

---

## Connection Pooling

### Development (SQLite)
SQLite is file-based — no connection pooling needed. Single-writer, multiple-reader via WAL mode.

### Production (PostgreSQL / Supabase)

```python
# Connection pool configuration
POOL_SIZE = 5           # Minimum connections
MAX_OVERFLOW = 10       # Max additional connections
POOL_TIMEOUT = 30       # Seconds to wait for connection
POOL_RECYCLE = 1800     # Recycle connections every 30 min
```

### Supabase Free Tier Limits

| Limit | Value |
|---|---|
| Max connections | 60 |
| Database size | 500MB |
| Bandwidth | 2GB/month |
| Rows read | Unlimited |

---

## Query Optimization

### N+1 Problem Prevention

```python
# ❌ BAD: N+1 queries
for meme in get_all_memes():
    votes = get_votes_for_meme(meme.id)  # N extra queries!

# ✅ GOOD: Single query with JOIN
memes_with_votes = db.query("""
    SELECT m.*, COUNT(v.id) as vote_count
    FROM memes m
    LEFT JOIN meme_votes v ON m.id = v.memeId
    GROUP BY m.id
""")
```

### Pagination

```python
# Offset pagination (simple, OK for <100K rows)
SELECT * FROM memes ORDER BY createdAt DESC LIMIT 20 OFFSET 40;

# Cursor pagination (efficient for large datasets)
SELECT * FROM memes WHERE createdAt < ? ORDER BY createdAt DESC LIMIT 20;
```

---

## Scaling Strategy

| Scale | Database | Estimated Cost |
|---|---|---|
| <10K memes | SQLite (dev) / Supabase Free | $0 |
| 10K–100K memes | Supabase Pro | $25/month |
| 100K–1M memes | Supabase Pro + read replicas | $50/month |
| 1M+ memes | Self-managed PostgreSQL | $100+/month |

---

> **Related Documents:**
> - [Tables.md](./Tables.md) · [Indexing.md](./Indexing.md) · [03_Backend/Performance.md](../03_Backend/Performance.md)
