# MemeGPT — Load Tests

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Load testing configuration and results — Locust setup, test scenarios, performance targets, and how to run load tests against staging.

---

## Locust Configuration

```python
# locustfile.py
from locust import HttpUser, task, between

class MemeGPTUser(HttpUser):
    """Simulates a typical MemeGPT user session."""
    wait_time = between(1, 3)  # 1-3 seconds between actions
    
    @task(10)  # 10x weight — most common action
    def search_meme(self):
        self.client.post("/api/v1/search", json={
            "query": "Monday morning feeling",
            "format_preference": "gif",
            "limit": 5
        })
    
    @task(5)
    def view_trending(self):
        self.client.get("/api/v1/trending?category=all&limit=20")
    
    @task(3)
    def view_meme_detail(self):
        self.client.get("/api/v1/memes/this-is-fine")
    
    @task(2)
    def submit_feedback(self):
        self.client.post("/api/v1/feedback", json={
            "query_id": "q_loadtest",
            "meme_id": "meme_042",
            "action": "download"
        })
    
    @task(1)
    def health_check(self):
        self.client.get("/health")
```

---

## Running Load Tests

```bash
# Install Locust
pip install locust

# Run against staging (10 users, 2/sec spawn rate)
locust -f locustfile.py \
  --host https://api-staging.memegpt.com \
  --users 10 \
  --spawn-rate 2 \
  --run-time 5m \
  --headless \
  --csv results/load_test

# Run with web UI (for interactive monitoring)
locust -f locustfile.py --host https://api-staging.memegpt.com
# Open http://localhost:8089
```

---

## Performance Targets

| Metric | Target | Failure Threshold |
|---|---|---|
| P50 response time | <1.0s | >2.0s |
| P95 response time | <3.0s | >5.0s |
| Error rate | <1% | >5% |
| Throughput | >10 req/s | <5 req/s |
| Concurrent users | 50 | N/A |

---

## Load Test Scenarios

| Scenario | Users | Duration | Purpose |
|---|---|---|---|
| Smoke test | 5 | 1 min | Verify basic functionality |
| Normal load | 25 | 5 min | Simulate typical traffic |
| Peak load | 50 | 10 min | Simulate viral moment |
| Stress test | 100 | 15 min | Find breaking point |
| Endurance | 25 | 30 min | Check for memory leaks |

---

## Best Practices

1. **Never load test production** — always use staging
2. **Start small, scale up** — 5 users → 25 → 50 → 100
3. **Monitor server resources** — CPU, RAM, network during test
4. **Cache warmup first** — run a small test to populate Redis cache
5. **Save results** — `--csv` flag generates CSV files for trend analysis

---

> **Related Documents:**
> - [Testing_Strategy.md](./Testing_Strategy.md) — Overall testing strategy
> - [Performance_Tests.md](./Performance_Tests.md) — Performance benchmarks
