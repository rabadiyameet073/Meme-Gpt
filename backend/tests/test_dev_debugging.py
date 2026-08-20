"""Tests for Debugging Guide from 09_Development/Debugging_Guide.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.debugging_service import (
    get_debugging_matrix,
    get_quick_debug_commands,
    get_debugging_best_practices,
    diagnose_issue,
)

client = TestClient(app)


def test_debugging_matrix_structure():
    matrix_data = get_debugging_matrix()
    categories = matrix_data["categories"]
    assert "backend" in categories
    assert "frontend" in categories
    assert "ai_pipeline" in categories
    assert "database" in categories

    backend_items = get_debugging_matrix("backend")["items"]
    assert any(i["problem"] == "ModuleNotFoundError" for i in backend_items)
    assert any(i["problem"] == "Groq API 429" for i in backend_items)

    ai_items = get_debugging_matrix("ai_pipeline")["items"]
    assert any(i["problem"] == "Low search quality" for i in ai_items)
    assert any(i["problem"] == "Qdrant returns 0 results" for i in ai_items)


def test_quick_debug_commands_and_practices():
    cmds = get_quick_debug_commands()
    assert len(cmds) == 5
    assert any("curl http://localhost:8000/health" in c["command"] for c in cmds)
    assert any("redis-cli ping" in c["command"] for c in cmds)

    practices = get_debugging_best_practices()
    assert len(practices) == 5
    assert any("Check health endpoint first" in p for p in practices)


def test_diagnose_issue_engine():
    # Test Redis Connection error
    diag_redis = diagnose_issue("redis.exceptions.ConnectionRefusedError: Error 111 connecting to localhost:6379")
    assert diag_redis["has_match"] is True
    assert diag_redis["top_match"]["problem"] == "ConnectionRefusedError on Redis"
    assert "docker-compose up redis" in diag_redis["top_match"]["fix"]

    # Test Qdrant 0 results
    diag_qdrant = diagnose_issue("qdrant returns 0 results on queries")
    assert diag_qdrant["has_match"] is True
    assert "0.35" in diag_qdrant["top_match"]["fix"]

    # Test SQLite locked
    diag_sqlite = diagnose_issue("sqlite3.OperationalError: database is locked")
    assert diag_sqlite["has_match"] is True
    assert diag_sqlite["top_match"]["problem"] == "SQLite locked"

    # Test Unmatched error
    diag_unknown = diagnose_issue("some obscure mystery error")
    assert diag_unknown["has_match"] is False
    assert "fallback_advice" in diag_unknown


def test_dev_debugging_api_endpoints():
    res_matrix = client.get("/api/v1/dev/debugging/matrix?category=backend")
    assert res_matrix.status_code == 200
    assert len(res_matrix.json()["items"]) >= 5

    res_cmds = client.get("/api/v1/dev/debugging/commands")
    assert res_cmds.status_code == 200
    assert len(res_cmds.json()["commands"]) == 5

    res_diag = client.post("/api/v1/dev/debugging/diagnose", json={
        "symptom_text": "Error: Groq rate limit exceeded 429"
    })
    assert res_diag.status_code == 200
    assert res_diag.json()["has_match"] is True
    assert res_diag.json()["top_match"]["problem"] == "Groq API 429"
