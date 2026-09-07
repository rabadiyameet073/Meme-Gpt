"""
Automated Latency Benchmark Check
Ensures P50 < 1.5s and P95 < 3.0s under simulated sequential requests.
Uses direct FastAPI TestClient or live HTTP endpoint.
"""
import time
import sys
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

QUERIES = [
    "when code compiles with no warnings",
    "monday morning meeting that could have been an email",
    "me pretending to listen to someone explain crypto",
    "when the food delivery finally arrives",
    "looking at my bank account after the weekend",
]


def benchmark():
    from starlette.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    latencies = []

    # Warmup query
    client.post("/api/v1/search", json={"query": "warmup"})

    for q in QUERIES:
        for _ in range(3):
            start = time.perf_counter()
            resp = client.post("/api/v1/search", json={"query": q, "limit": 5})
            elapsed = (time.perf_counter() - start) * 1000
            if resp.status_code == 200:
                latencies.append(elapsed)

    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)

    print("==================================================")
    print("MemeGPT Latency Benchmark SLA")
    print("==================================================")
    print(f"Latency P50: {p50:.1f}ms (Target: < 1500ms)")
    print(f"Latency P95: {p95:.1f}ms (Target: < 3000ms)")
    print("==================================================")

    assert p50 < 1500, f"P50 latency failed: {p50}ms >= 1500ms"
    assert p95 < 3000, f"P95 latency failed: {p95}ms >= 3000ms"
    print("[SUCCESS] Latency SLA passed successfully.")


if __name__ == "__main__":
    benchmark()
