# MemeGPT — Database Tables

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Column-level documentation for every table in MemeGPT's PostgreSQL database — field types, constraints, indexes, and usage context.

---

## Table: `memes`

The core table — one row per indexed meme.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | VARCHAR(50) | ❌ | PK | Unique meme identifier (e.g., `meme_042`) |
| `name` | VARCHAR(200) | ❌ | — | Human-readable name ("This Is Fine") |
| `slug` | VARCHAR(200) | ❌ | UNIQUE | URL-safe slug (`this-is-fine`) |
| `description` | TEXT | ✅ | — | Visual description (BLIP caption) |
| `ocr_text` | TEXT | ✅ | — | Text extracted from image (Tesseract) |
| `emotions` | TEXT[] | ❌ | `{}` | Tagged emotions (Groq-generated) |
| `situations` | TEXT[] | ✅ | `{}` | Usage situations (Groq-generated) |
| `keywords` | TEXT[] | ✅ | `{}` | Search keywords (Groq-generated) |
| `categories` | TEXT[] | ✅ | `{}` | Content categories |
| `meme_type` | VARCHAR(50) | ✅ | `reaction` | `reaction\|comparison\|advice\|relatable\|wholesome` |
| `source` | VARCHAR(100) | ✅ | — | Data source (`imgflip`, `reddit`, `tenor`) |
| `image_url` | TEXT | ❌ | — | CDN URL for PNG/JPG |
| `gif_url` | TEXT | ✅ | — | CDN URL for GIF |
| `mp4_url` | TEXT | ✅ | — | CDN URL for MP4 |
| `webp_url` | TEXT | ✅ | — | CDN URL for WebP |
| `thumb_url` | TEXT | ✅ | — | CDN URL for thumbnail |
| `has_gif` | BOOLEAN | ❌ | `false` | GIF format available |
| `has_video` | BOOLEAN | ❌ | `false` | MP4 format available |
| `nsfw` | BOOLEAN | ❌ | `false` | NSFW content flag |
| `popularity_score` | FLOAT | ❌ | `0.0` | 0.0–1.0 (recalculated weekly) |
| `view_count` | INTEGER | ❌ | `0` | Total views |
| `download_count` | INTEGER | ❌ | `0` | Total downloads |
| `created_at` | TIMESTAMP | ❌ | `now()` | When first indexed |
| `updated_at` | TIMESTAMP | ❌ | `now()` | Last metadata update |

### Indexes

```sql
CREATE UNIQUE INDEX idx_memes_slug ON memes(slug);
CREATE INDEX idx_memes_categories ON memes USING GIN(categories);
CREATE INDEX idx_memes_emotions ON memes USING GIN(emotions);
CREATE INDEX idx_memes_popularity ON memes(popularity_score DESC);
CREATE INDEX idx_memes_nsfw ON memes(nsfw);
```

---

## Table: `search_logs`

Analytics table — one row per search request.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | SERIAL | ❌ | PK | Auto-increment ID |
| `query_id` | VARCHAR(50) | ❌ | UNIQUE | Unique query identifier |
| `query_hash` | VARCHAR(64) | ❌ | — | MD5 hash of raw query (no PII) |
| `query_length` | INTEGER | ❌ | — | Character count |
| `latency_ms` | INTEGER | ❌ | — | Server-side processing time |
| `result_count` | INTEGER | ❌ | — | Number of results returned |
| `cache_hit` | BOOLEAN | ❌ | `false` | Whether result was cached |
| `degraded` | BOOLEAN | ❌ | `false` | Whether graceful degradation was used |
| `emotion_detected` | VARCHAR(50) | ✅ | — | Primary emotion detected |
| `format_preference` | VARCHAR(20) | ✅ | `gif` | User's format preference |
| `created_at` | TIMESTAMP | ❌ | `now()` | When search occurred |

---

## Table: `feedback`

User interaction tracking — multiple rows per meme per session.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | SERIAL | ❌ | PK | Auto-increment ID |
| `query_id` | VARCHAR(50) | ✅ | — | Which search this feedback is for |
| `meme_id` | VARCHAR(50) | ❌ | FK → memes.id | Which meme was interacted with |
| `session_id` | VARCHAR(100) | ✅ | — | Anonymous session identifier |
| `action` | VARCHAR(20) | ❌ | — | `view\|click\|copy\|download\|share\|thumbs_up\|thumbs_down\|skip` |
| `created_at` | TIMESTAMP | ❌ | `now()` | When interaction occurred |

### Indexes

```sql
CREATE INDEX idx_feedback_meme_id ON feedback(meme_id);
CREATE INDEX idx_feedback_action ON feedback(action);
CREATE INDEX idx_feedback_created_at ON feedback(created_at DESC);
CREATE INDEX idx_feedback_query_id ON feedback(query_id);
```

---

## Table: `api_keys` (Phase 2)

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | PK |
| `key_hash` | VARCHAR(64) | SHA-256 hash of API key |
| `key_prefix` | VARCHAR(20) | Last 8 chars for display (`****n4o5p6`) |
| `tier` | VARCHAR(20) | `free\|pro\|internal` |
| `rate_limit` | INTEGER | Custom rate limit |
| `user_id` | VARCHAR(50) | Owner (Phase 3) |
| `revoked` | BOOLEAN | Key deactivated |
| `created_at` | TIMESTAMP | When key was generated |
| `last_used_at` | TIMESTAMP | Last API call |

---

## Row Estimates (MVP)

| Table | Rows (Launch) | Rows (1 Year) | Growth |
|---|---|---|---|
| memes | 10,000 | 50,000 | ~1K/month |
| search_logs | 0 | 500,000 | ~50K/month |
| feedback | 0 | 200,000 | ~20K/month |
| api_keys | 0 | 500 | Phase 2 |

---

> **Related Documents:**
> - [Schema.md](./Schema.md) — Full SQL DDL + Prisma schema
> - [Relationships.md](./Relationships.md) — Foreign key relationships
> - [Indexing.md](./Indexing.md) — Index strategy
