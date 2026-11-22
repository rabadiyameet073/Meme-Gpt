# 02 — Upstash Redis Setup (Cache + Rate Limiting)
> **Priority:** 🔴 Critical — Without Redis, cache resets on every server restart
> **Time Needed:** ~30 minutes
> **Result:** Sub-5ms cache hits, persistent rate limiting, 1-hour search result cache

---

## 🔴 Why Redis Matters for MemeGPT

**Without Redis:**
- Every search hits Qdrant + runs ML models → ~300-800ms latency
- "Monday morning feeling" searched 100 times = 100 Qdrant queries
- Rate limit counters reset when server restarts (useless)
- Groq API gets hammered for every query

**With Redis:**
- Same query the 2nd time: Redis returns cached result in <5ms
- Rate limit counters survive server restarts
- Groq API called only for unique queries never seen before
- Response time drops to <50ms for cached queries

**Where Redis is Used in the Code:**
- `backend/app/core/cache.py` — search result cache (1hr TTL)
- `backend/app/core/rate_limit.py` — per-IP and per-API-key counters (1min TTL)
- `backend/app/services/search_service.py` — trending cache (15min TTL)

---

## 📋 Step 1 — Create Upstash Account + Redis Database

```
1. Go to: https://upstash.com
2. Sign up (free, no credit card)
3. Click "Create Database"
4. Settings:
   - Type: Redis
   - Name: memegpt-cache
   - Region: US-East-1 (or match your Railway/Render region)
   - Plan: Free (10,000 commands/day, 256MB)
5. Click "Create"
6. Copy from the dashboard:
   - REDIS_URL (looks like: redis://default:password@alive-xxx.upstash.io:6379)
   - OR the REST API URL + Token (for HTTP-based access)
```

---

## 📋 Step 2 — Add to Your .env File

Open `d:\Meme GPT\.env` and fill in:

```env
# ── REDIS CACHE (Upstash) ─────────────────────────
# Use the Redis URL (connection string format):
REDIS_URL=redis://default:YOUR_PASSWORD@alive-xxx.upstash.io:6379

# OR use the REST API (better for serverless):
UPSTASH_REDIS_REST_URL=https://alive-xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=YOUR_TOKEN_HERE

# Cache TTL settings
REDIS_CACHE_TTL=3600
```

> **Note:** You only need ONE of these methods. If both are set, `REDIS_URL` takes priority in `core/cache.py`.

---

## 📋 Step 3 — Test Redis Connection

```powershell
cd "d:\Meme GPT\backend"
python -c "
from dotenv import load_dotenv
load_dotenv('../.env')
from app.core.cache import get_redis_client

client = get_redis_client()
if client:
    client.set('test_key', 'hello_memegpt', ex=60)
    value = client.get('test_key')
    print(f'✅ Redis connected! Test read: {value}')
else:
    print('❌ Redis not connected — using in-memory fallback')
    print('Check REDIS_URL in .env')
"
```

---

## 📋 Step 4 — Verify Cache Works in Search

Start the backend and run two identical searches:

```powershell
# First search (should be slow ~300-800ms)
$start = Get-Date
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query": "monday morning feeling", "limit": 5}'
$end = Get-Date
Write-Host "First search: $(($end - $start).TotalMilliseconds)ms"

# Second search (should be fast <50ms — cache hit)
$start = Get-Date
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query": "monday morning feeling", "limit": 5}'
$end = Get-Date
Write-Host "Second search (cached): $(($end - $start).TotalMilliseconds)ms"
```

**Expected:**
```
First search: 450ms
Second search (cached): 18ms
```

---

## 📋 Step 5 — Verify Rate Limiting Works

The `backend/app/core/rate_limit.py` stores counters in Redis. Without Redis, counters reset on server restart.

```powershell
# Hit the search endpoint 70 times rapidly (limit is 60/min for anonymous)
for ($i = 1; $i -le 70; $i++) {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search" `
      -Method POST `
      -ContentType "application/json" `
      -Body '{"query": "test rate limit"}' `
      -StatusCodeVariable statusCode 2>&1
    if ($i -eq 61) { Write-Host "Request $i status: $statusCode" }
}
```

**Expected:** Request 61 returns `429 Too Many Requests`.

---

## 📋 Step 6 — Monitor Cache Usage in Upstash Dashboard

Go to `https://upstash.com → Your Database → Data Browser`

You should see keys like:
```
search:abc123def456  ← MD5 hash of a query
rate:192.168.1.1     ← IP-based rate limit counter
trending:v1          ← Trending memes cache
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused on port 6379` | Use TLS URL: `rediss://` (double s) instead of `redis://` |
| `WRONGPASS` authentication error | Check password in REDIS_URL — copy from Upstash dashboard exactly |
| `SSL wrong version` | Add `ssl_cert_reqs=None` or use REST API instead |
| Rate limits not persisting across restarts | REDIS_URL is empty — in-memory fallback is active |
| `redis` package not installed | Run: `pip install redis>=5.0.0` |

**If you prefer HTTP REST API over TCP connection** (more reliable through firewalls):

The code in `core/cache.py` already supports `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`. Set those instead of `REDIS_URL`.

```python
# This is already handled in core/cache.py
redis_url = (
    getattr(settings, "REDIS_URL", "")
    or getattr(settings, "UPSTASH_REDIS_URL", "")
    or getattr(settings, "UPSTASH_REDIS_REST_URL", "")
)
```

---

## ✅ Done When

- [ ] `get_redis_client()` returns non-None
- [ ] Second identical search is <50ms (cache hit)
- [ ] Upstash dashboard shows keys after searches
- [ ] Server restart doesn't reset rate limit counters

**Next step → `03_Cloudflare_R2_CDN_Setup.md`**
