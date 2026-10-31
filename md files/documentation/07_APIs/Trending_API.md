# MemeGPT — Trending API

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete specification for the trending memes endpoint — returns memes ranked by real-time popularity, updated hourly, categorized by topic.

---

## `GET /api/v1/trending`

Returns trending memes, sorted by trending score descending.

### Query Parameters

| Param | Type | Required | Default | Validation | Description |
|---|---|---|---|---|---|
| `category` | string | No | `"all"` | Enum: `all`, `work`, `gaming`, `relationships`, `tech`, `sports`, `tv`, `wholesome` | Filter by meme category |
| `limit` | integer | No | `20` | Min: 1, Max: 50 | Number of results to return |
| `period` | string | No | `"24h"` | Enum: `24h`, `7d`, `30d` | Lookback window for trend calculation |
| `offset` | integer | No | `0` | Min: 0 | Pagination offset |

### Example Request

```http
GET /api/v1/trending?category=tech&limit=5&period=24h HTTP/1.1
Host: api.memegpt.com
Accept: application/json
```

### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "category": "tech",
    "period": "24h",
    "results": [
      {
        "id": "meme_042",
        "name": "This Is Fine",
        "slug": "this-is-fine",
        "trending_score": 0.94,
        "trending_rank": 1,
        "category_rank": 1,
        "downloads_24h": 1523,
        "copies_24h": 842,
        "shares_24h": 356,
        "searches_24h": 2103,
        "preview_url": "https://cdn.memegpt.com/thumbs/this-is-fine.webp",
        "formats": {
          "gif": "https://cdn.memegpt.com/memes/this-is-fine.gif",
          "image": "https://cdn.memegpt.com/images/this-is-fine.png",
          "video": null
        }
      }
    ],
    "meta": {
      "total_results": 150,
      "total_trending": 1200,
      "updated_at": "2026-01-15T14:00:00Z",
      "next_update": "2026-01-15T15:00:00Z",
      "cached": true
    }
  }
}
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `results[].trending_score` | float (0–1) | Normalized trending score |
| `results[].trending_rank` | integer | Overall position across all categories |
| `results[].category_rank` | integer | Position within the requested category |
| `results[].downloads_24h` | integer | Raw download count in period |
| `results[].copies_24h` | integer | Raw copy-to-clipboard count |
| `results[].shares_24h` | integer | Raw share count |
| `results[].searches_24h` | integer | Times this meme appeared in search results |
| `meta.cached` | boolean | Whether response was served from cache |

### Error Responses

| Status | Error Code | Condition |
|---|---|---|
| 400 | `INVALID_CATEGORY` | Category not in allowed list |
| 400 | `INVALID_PERIOD` | Period not one of `24h`, `7d`, `30d` |
| 422 | `VALIDATION_ERROR` | Limit out of range |
| 429 | `RATE_LIMITED` | Too many requests |

---

## Trending Score Algorithm

### Raw Score Calculation

```python
import math
from datetime import datetime, timezone

def calculate_trending_score(
    meme_id: str,
    period_hours: int = 24,
) -> float:
    # Raw engagement counts (from search_logs + feedback tables)
    downloads = get_download_count(meme_id, period_hours)
    copies = get_copy_count(meme_id, period_hours)
    shares = get_share_count(meme_id, period_hours)
    searches = get_search_appearance_count(meme_id, period_hours)

    # Weighted engagement score
    raw_score = (
        downloads * 3.0 +
        copies * 2.0 +
        shares * 4.0 +
        searches * 1.0
    )

    # Time decay: newer activity matters more
    hours_since_peak = get_hours_since_peak_activity(meme_id)
    time_decay = math.exp(-hours_since_peak / (period_hours * 0.5))

    # Recency bonus: memes with recent activity get a boost
    last_activity_hours = get_hours_since_last_activity(meme_id)
    recency_bonus = max(0, 10 - last_activity_hours) * 0.5

    # Novelty factor: boost memes that are new to trending
    days_on_trending = get_days_on_trending(meme_id)
    novelty_boost = max(0, 1.0 - days_on_trending * 0.05)  # Decays 5% per day

    return (raw_score * time_decay + recency_bonus) * novelty_boost
```

### Normalization

Raw scores are min-max normalized across all memes to produce a 0–1 trending_score:

```python
def normalize_scores(memes: list[dict]) -> list[dict]:
    scores = [m["raw_score"] for m in memes]
    min_s, max_s = min(scores), max(scores)
    for m in memes:
        m["trending_score"] = (m["raw_score"] - min_s) / (max_s - min_s + 1e-10)
    return sorted(memes, key=lambda m: m["trending_score"], reverse=True)
```

### Category Score

When a category filter is applied, scores are computed independently within that category, so #1 in "wholesome" may have a different raw score than #1 in "tech". Each category's scores are normalized independently.

---

## Caching Strategy

| Aspect | Detail |
|---|---|
| **Cache backend** | Redis |
| **TTL** | 1 hour (3600 seconds) |
| **Cache key pattern** | `trending:{category}:{period}:{offset},{limit}` |
| **Background job** | Cron runs every hour, pre-computes top 8 categories |
| **Cache warming** | On deploy, warm top-3 categories immediately |
| **Stale-while-revalidate** | Serve stale cache + refresh in background if recompute fails |

### Cache Invalidation

```python
# On feedback event that affects trending (download, copy, share):
async def invalidate_trending_cache(meme_id: str, event_type: str):
    # Don't invalidate immediately — batch updates
    # The hourly cron picks up all recent events
    pass  # No-op: hourly cron handles freshness
```

---

## Rate Limiting

| Tier | Limit | Window |
|---|---|---|
| Free | 30 requests/min | 1 minute sliding |
| Pro (API key) | 300 requests/min | 1 minute sliding |
| Trending endpoint | Shared with search limit | Same bucket per tier |

---

## Related Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/trending?category=tech` | Filtered by category |
| `GET /api/v1/memes/{slug}` | Full meme detail |
| `POST /api/v1/feedback` | Record interaction (feeds trending) |

---

## Database Queries

### Trending Recalculation (Cron Job)

```sql
-- Simplified trending query (runs hourly)
SELECT
  m.id,
  m.name,
  m.slug,
  COUNT(DISTINCT sl.id) AS searches,
  COUNT(DISTINCT f.id) FILTER (WHERE f.action = 'download') AS downloads,
  COUNT(DISTINCT f.id) FILTER (WHERE f.action = 'copy') AS copies,
  COUNT(DISTINCT f.id) FILTER (WHERE f.action = 'share') AS shares
FROM memes m
LEFT JOIN search_logs sl ON sl.meme_id = m.id
  AND sl.created_at > NOW() - INTERVAL '24 hours'
LEFT JOIN feedback f ON f.meme_id = m.id
  AND f.created_at > NOW() - INTERVAL '24 hours'
GROUP BY m.id
ORDER BY (downloads * 3.0 + copies * 2.0 + shares * 4.0 + searches * 1.0) DESC
LIMIT 200;
```

---

> **Related Documents:**
> - [Search_API.md](./Search_API.md) — Core search endpoint
> - [API_Overview.md](./API_Overview.md) — API summary
> - [Feedback_API.md](./Feedback_API.md) — Feedback signal processing
> - [Rate_Limiting.md](./Rate_Limiting.md) — Rate limiting details
> - [06_Database/Indexing.md](../06_Database/Indexing.md) — Database index strategy