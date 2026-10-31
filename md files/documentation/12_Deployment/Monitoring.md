# MemeGPT — Monitoring

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete monitoring setup — uptime monitoring, error tracking, performance metrics, and alerting configuration.

---

## Monitoring Stack

| Tool | Purpose | Free Tier | What It Tracks |
|---|---|---|---|
| **UptimeRobot** | Uptime monitoring | 50 monitors | `/health` endpoint (5-min checks) |
| **Sentry** | Error tracking | 5K events/month | Unhandled exceptions, stack traces |
| **Umami** | Web analytics | Self-hosted (free) | Page views, search usage, referrers |
| **Railway Logs** | Application logs | Included | stdout/stderr from FastAPI |

---

## UptimeRobot Configuration

| Monitor | URL | Check Interval | Alert |
|---|---|---|---|
| API Health | `https://api.memegpt.com/health` | 5 min | Email + Slack |
| Web App | `https://memegpt.com` | 5 min | Email |
| Search Endpoint | `POST /api/v1/search` | 15 min | Email + Slack |

---

## Sentry Setup

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""),
    environment=os.environ.get("APP_ENV", "development"),
    traces_sample_rate=0.1,      # 10% of transactions
    profiles_sample_rate=0.1,     # 10% for profiling
    send_default_pii=False,       # NEVER send PII
)
```

### Alert Rules

| Condition | Threshold | Action |
|---|---|---|
| Error rate spike | >5% in 5 min | Email + Slack notification |
| New error type | First occurrence | Email notification |
| P95 latency | >3s for 10 min | Email notification |
| Unhandled exception | Any | Sentry auto-captures |

---

## Key Metrics Dashboard

| Metric | Source | Target | Alert If |
|---|---|---|---|
| Uptime | UptimeRobot | >99.5% | <99% |
| Error rate | Sentry | <2% | >5% |
| P50 latency | Application logs | <1.0s | >2.0s |
| P95 latency | Application logs | <3.0s | >5.0s |
| Cache hit rate | Redis metrics | >60% | <30% |
| Search volume | Application logs | — | Trending |
| Daily active users | Umami | — | Trending |

---

## Health Check Response

```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "models": {
    "text_model": "loaded",
    "emotion": "loaded"
  },
  "services": {
    "redis": "connected",
    "qdrant": "connected",
    "database": "connected"
  }
}
```

---

## Best Practices

1. **Monitor externally** — UptimeRobot checks from outside your infrastructure
2. **Set `send_default_pii=False`** — Sentry should never receive user data
3. **Sample traces at 10%** — full tracing is too expensive on free tier
4. **Alert on error rate, not individual errors** — reduces noise
5. **Check health endpoint every 5 min** — catches cold starts and outages

---

> **Related Documents:**
> - [Deployment_Overview.md](./Deployment_Overview.md) — Deployment guide
> - [Infrastructure.md](./Infrastructure.md) — Service inventory
> - [03_Backend/Logging.md](../03_Backend/Logging.md) — Logging strategy
