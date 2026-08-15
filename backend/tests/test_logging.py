import json
import logging
from fastapi.testclient import TestClient
from app.main import app
from app.core.logging_config import StructuredFormatter, hash_pii

client = TestClient(app)


def test_structured_formatter_json_output():
    formatter = StructuredFormatter()
    record = logging.LogRecord(
        name="memegpt.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Search completed successfully",
        args=(),
        exc_info=None,
        func="test_func"
    )
    record.extra_data = {
        "query_hash": "a3f2b9c1e7d4",
        "latency_ms": 120,
        "cache_hit": True,
        "result_count": 5
    }

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["level"] == "INFO"
    assert data["logger"] == "memegpt.test"
    assert data["message"] == "Search completed successfully"
    assert data["query_hash"] == "a3f2b9c1e7d4"
    assert data["latency_ms"] == 120
    assert data["cache_hit"] is True
    assert data["result_count"] == 5
    assert "timestamp" in data
    assert data["timestamp"].endswith("Z")


def test_hash_pii_privacy():
    raw_query = "My secret sensitive search text"
    hashed1 = hash_pii(raw_query)
    hashed2 = hash_pii(raw_query)
    assert hashed1 == hashed2
    assert len(hashed1) == 12
    assert raw_query not in hashed1

    ip_hash = hash_pii("192.168.1.100", length=8)
    assert len(ip_hash) == 8


def test_request_timing_middleware_header():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert "x-response-time" in res.headers
    assert res.headers["x-response-time"].endswith("ms")
