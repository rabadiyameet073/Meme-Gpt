# MemeGPT — API Overview

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete API summary — all endpoints, authentication, versioning, and common patterns.

---

## Base URL

| Environment | Base URL |
|---|---|
| Production | `https://api.memegpt.com` |
| Staging | `https://api-staging.memegpt.com` |
| Development | `http://localhost:8000` |

---

## API Version

All endpoints are prefixed with `/api/v1/`. Future breaking changes will increment to `/api/v2/`.

---

## Complete Endpoint Catalog

| Method | Path | Description | Rate Limit | Docs |
|---|---|---|---|---|
| `POST` | `/api/v1/search` | AI-powered meme search | 30/min | [Search_API.md](./Search_API.md) |
| `GET` | `/api/v1/memes/{slug}` | Meme detail by slug | 60/min | [Meme_API.md](./Meme_API.md) |
| `GET` | `/api/v1/memes/{slug}/download` | Download meme file | 60/min | [Meme_API.md](./Meme_API.md) |
| `GET` | `/api/v1/trending` | Trending memes | 60/min | [Meme_API.md](./Meme_API.md) |
| `POST` | `/api/v1/feedback` | Record user interaction | 120/min | [Meme_API.md](./Meme_API.md) |
| `GET` | `/health` | Service health check | None | — |

---

## Common Response Format

### Success

```json
{
  "success": true,
  "data": { ... }
}
```

### Error

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable message"
}
```

---

## Response Headers (Every Request)

```http
X-Response-Time: 487ms
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 27
X-RateLimit-Reset: 1706745600
```

---

## Content Types

| Request | Response |
|---|---|
| `application/json` | `application/json` |

---

## HTTP Status Codes Used

| Status | When |
|---|---|
| 200 | Success |
| 301 | Download redirect to CDN |
| 400 | Invalid request |
| 404 | Meme not found |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service unavailable |

---

> **Related Documents:**
> - [Search_API.md](./Search_API.md) — Core search endpoint
> - [Meme_API.md](./Meme_API.md) — Meme, trending, feedback
> - [Authentication.md](./Authentication.md) — API authentication
> - [Rate_Limiting.md](./Rate_Limiting.md) — Rate limiting details
