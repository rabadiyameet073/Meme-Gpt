# MemeGPT — Environment Variables Reference

> **Document Version:** 1.0  
> **Last Updated:** 2026-08-01  
> **Related Documents:** [Installation.md](./Installation.md) · [Prerequisites.md](./Prerequisites.md)

---

## Purpose

Complete reference for all environment variables used across the MemeGPT system. Every variable includes its purpose, required status, format, and example value.

---

## Backend Environment Variables (`.env`)

### Database

| Variable | Required | Description | Example |
|---|---|---|---|
| `DATABASE_URL` | ✅ Yes | SQLite/PostgreSQL connection string | `file:./memegpt.db` |

### AI / ML Services

| Variable | Required | Description | Example |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Groq API key for Llama 3.1 LLM inference | `gsk_abcdef123456...` |

### Vector Database (Qdrant)

| Variable | Required | Description | Example |
|---|---|---|---|
| `QDRANT_URL` | ⚠️ Production | Qdrant Cloud cluster URL | `https://abc-123.us-east.aws.cloud.qdrant.io` |
| `QDRANT_API_KEY` | ⚠️ Production | Qdrant Cloud API key | `qdrant_api_key_here` |

### Relational Database (Supabase)

| Variable | Required | Description | Example |
|---|---|---|---|
| `SUPABASE_URL` | ⚠️ Production | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | ⚠️ Production | Supabase anon/service key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### Cache (Redis)

| Variable | Required | Description | Example |
|---|---|---|---|
| `REDIS_URL` | ⚠️ Production | Upstash Redis connection URL | `rediss://default:abc@us1-xxx.upstash.io:6379` |

### External APIs

| Variable | Required | Description | Example |
|---|---|---|---|
| `GIPHY_API_KEY` | ❌ Optional | Giphy API key for GIF sourcing | `abc123giphy` |
| `TENOR_API_KEY` | ❌ Optional | Google Tenor API key | `AIza...` |
| `REDDIT_CLIENT_ID` | ❌ Optional | Reddit app client ID | `abc123reddit` |
| `REDDIT_CLIENT_SECRET` | ❌ Optional | Reddit app client secret | `secret_here` |

### Media Storage (Cloudflare R2)

| Variable | Required | Description | Example |
|---|---|---|---|
| `CLOUDFLARE_R2_ACCESS_KEY` | ⚠️ Production | R2 API access key | `abc123` |
| `CLOUDFLARE_R2_SECRET_KEY` | ⚠️ Production | R2 API secret key | `secret123` |
| `CLOUDFLARE_R2_BUCKET` | ⚠️ Production | R2 bucket name | `memegpt-media` |
| `CLOUDFLARE_ACCOUNT_ID` | ⚠️ Production | Cloudflare account ID | `abc123def456` |

### Application Configuration

| Variable | Required | Description | Default | Example |
|---|---|---|---|---|
| `ALLOWED_ORIGINS` | ❌ Optional | CORS allowed origins (comma-separated) | `*` | `https://memegpt.com,https://app.memegpt.com` |
| `ENVIRONMENT` | ❌ Optional | Runtime environment | `development` | `production` |
| `LOG_LEVEL` | ❌ Optional | Logging verbosity | `INFO` | `DEBUG` |

---

## Frontend Environment Variables (`.env.local`)

| Variable | Required | Description | Example |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | Backend API base URL | `http://localhost:8000` (dev) / `https://api.memegpt.com` (prod) |
| `NEXT_PUBLIC_CDN_URL` | ❌ Optional | CDN base URL for meme media | `https://cdn.memegpt.com` |
| `NEXT_PUBLIC_POSTHOG_KEY` | ❌ Optional | PostHog analytics key | `phc_abc123` |
| `NEXT_PUBLIC_SENTRY_DSN` | ❌ Optional | Sentry error tracking DSN | `https://abc@sentry.io/123` |
| `NEXTAUTH_URL` | ⚠️ If using auth | NextAuth.js base URL | `https://memegpt.com` |
| `NEXTAUTH_SECRET` | ⚠️ If using auth | NextAuth.js secret (32+ chars) | `random_32_char_string` |
| `GOOGLE_CLIENT_ID` | ❌ Optional | Google OAuth client ID | `123.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | ❌ Optional | Google OAuth secret | `GOCSPX-abc123` |

---

## Mobile App Configuration (`app.json` extras)

```json
{
  "expo": {
    "extra": {
      "apiUrl": "https://api.memegpt.com",
      "cdnUrl": "https://cdn.memegpt.com",
      "eas": {
        "projectId": "YOUR_EAS_PROJECT_ID"
      }
    }
  }
}
```

---

## Environment File Templates

### Development (`.env`)

```env
# Database
DATABASE_URL="file:./memegpt.db"

# AI Services
GROQ_API_KEY=gsk_your_key_here

# Optional for development
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Production (`.env.production`)

```env
# Database
DATABASE_URL="file:./memegpt.db"

# AI Services
GROQ_API_KEY=gsk_production_key

# Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key

# PostgreSQL
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_supabase_key

# Cache
REDIS_URL=rediss://default:key@us1-xxx.upstash.io:6379

# Media Storage
CLOUDFLARE_R2_ACCESS_KEY=your_r2_key
CLOUDFLARE_R2_SECRET_KEY=your_r2_secret
CLOUDFLARE_R2_BUCKET=memegpt-media

# External APIs
GIPHY_API_KEY=your_giphy_key
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://memegpt.com,https://app.memegpt.com
```

---

## Security Best Practices

> [!CAUTION]
> Never commit `.env` files to Git. They are included in `.gitignore` by default.

1. **Never hardcode API keys** in source code
2. **Use different keys** for development and production
3. **Rotate keys** immediately if exposed
4. **Use secret management** in CI/CD (GitHub Secrets, Vercel env vars, Render env vars)
5. **Minimum permissions** — use `anon` keys for Supabase, not `service_role` in frontend

---

> **Related Documents:**
> - [Installation.md](./Installation.md) — Setup steps
> - [12_Deployment/Infrastructure.md](../12_Deployment/Infrastructure.md) — Production env configuration
> - [11_Security/Data_Privacy.md](../11_Security/Data_Privacy.md) — Security policies
