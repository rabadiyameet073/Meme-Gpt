# MemeGPT — Webhooks (Phase 2)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Webhook system specification for MemeGPT's developer API — event-driven notifications when memes are searched, trending changes, or new memes are indexed.

---

## Background

Webhooks allow developers to receive real-time notifications from MemeGPT without polling. Planned for Phase 2 when the developer API launches.

---

## Supported Events

| Event | Trigger | Payload |
|---|---|---|
| `meme.trending` | Meme enters top-20 trending | `{meme_id, name, trending_score}` |
| `meme.new` | New meme indexed | `{meme_id, name, categories}` |
| `search.popular` | Query searched >100 times/day | `{query_hash, count}` |
| `collection.updated` | Trending collection refreshed | `{category, meme_count}` |

---

## Webhook Registration

```bash
curl -X POST https://api.memegpt.com/api/v1/webhooks \
  -H "X-API-Key: mgpt_live_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/memegpt",
    "events": ["meme.trending", "meme.new"],
    "secret": "your_webhook_secret"
  }'
```

---

## Webhook Payload

```json
{
  "event": "meme.trending",
  "timestamp": "2026-08-02T04:30:00Z",
  "data": {
    "meme_id": "meme_042",
    "name": "This Is Fine",
    "trending_score": 0.94,
    "category": "work"
  },
  "signature": "sha256=abc123..."
}
```

---

## Security

- **HMAC-SHA256 signature** in `X-Webhook-Signature` header
- **Verify before processing** — compare signature against your secret
- **Retry on failure** — 3 retries with exponential backoff (5s, 30s, 5min)
- **Timeout** — 10 second response timeout per delivery

---

> **Related Documents:**
> - [API_Overview.md](./API_Overview.md) — All endpoints
> - [Authentication.md](./Authentication.md) — API key management
