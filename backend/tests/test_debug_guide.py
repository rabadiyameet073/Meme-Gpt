"""Tests for Comprehensive Debug Guide from 14_Troubleshooting/Debug_Guide.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.debug_guide_service import (
    get_backend_debug_procedures,
    get_frontend_debug_guide,
    get_database_debug_commands,
    get_ml_debug_recipes,
    get_network_debug_tools,
    get_search_quality_decision_tree,
    simulate_search_quality_diagnosis,
)

client = TestClient(app)


def test_backend_debug_procedures():
    res = get_backend_debug_procedures()
    assert "run_with_debug_logging" in res
    assert "LOG_LEVEL=DEBUG" in res["run_with_debug_logging"]["command"]
    assert len(res["curl_endpoint_tests"]) == 3
    assert "search_quality_debug_script" in res
    assert "embedding_generation_debug_script" in res


def test_frontend_debug_guide():
    res = get_frontend_debug_guide()
    assert len(res["chrome_devtools_tabs"]) == 5
    tab_names = [t["tab"] for t in res["chrome_devtools_tabs"]]
    assert "Console" in tab_names
    assert "Network" in tab_names
    assert "Performance" in tab_names
    assert "React DevTools" in tab_names
    assert "Application" in tab_names


def test_database_debug_commands():
    res = get_database_debug_commands()
    assert res["visual_browser"]["tool"] == "Prisma Studio"
    assert len(res["sql_inspection_queries"]) == 3


def test_ml_debug_recipes():
    res = get_ml_debug_recipes()
    assert "emotion_detection_test" in res
    assert "distilroberta" in res["emotion_detection_test"]
    assert "groq_intent_parsing_test" in res
    assert "llama-3.1" in res["groq_intent_parsing_test"]


def test_network_debug_tools():
    res = get_network_debug_tools()
    assert res["total_tools"] == 4
    tools = [t["tool"] for t in res["tools"]]
    assert "nslookup" in tools
    assert "netstat" in tools
    assert "openssl" in tools
    assert "curl" in tools


def test_search_quality_decision_tree():
    tree = get_search_quality_decision_tree()
    assert "root_step" in tree
    assert "Database seeded?" in tree["root_step"]["question"]


def test_simulate_search_quality_diagnosis():
    # DB unseeded
    s1 = simulate_search_quality_diagnosis(db_seeded=False)
    assert s1["step"] == 1
    assert "seed" in s1["action"]

    # Embeddings unindexed
    s2 = simulate_search_quality_diagnosis(db_seeded=True, embeddings_generated=False)
    assert s2["step"] == 2
    assert "index_qdrant.py" in s2["action"]

    # Groq down
    s3 = simulate_search_quality_diagnosis(db_seeded=True, embeddings_generated=True, groq_working=False)
    assert s3["step"] == 3
    assert "GROQ_API_KEY" in s3["action"]

    # Qdrant down
    s4 = simulate_search_quality_diagnosis(db_seeded=True, embeddings_generated=True, groq_working=True, qdrant_connected=False)
    assert s4["step"] == 4
    assert "QDRANT_URL" in s4["action"]

    # All healthy
    s5 = simulate_search_quality_diagnosis(db_seeded=True, embeddings_generated=True, groq_working=True, qdrant_connected=True)
    assert s5["step"] == 5
    assert s5["status"] == "ALL_SUBSYSTEMS_HEALTHY"


def test_debug_guide_api_endpoints():
    res_be = client.get("/api/v1/troubleshooting/debug/backend")
    assert res_be.status_code == 200
    assert "run_with_debug_logging" in res_be.json()

    res_fe = client.get("/api/v1/troubleshooting/debug/frontend")
    assert res_fe.status_code == 200
    assert len(res_fe.json()["chrome_devtools_tabs"]) == 5

    res_db = client.get("/api/v1/troubleshooting/debug/database")
    assert res_db.status_code == 200
    assert "visual_browser" in res_db.json()

    res_ml = client.get("/api/v1/troubleshooting/debug/ml")
    assert res_ml.status_code == 200
    assert "emotion_detection_test" in res_ml.json()

    res_net = client.get("/api/v1/troubleshooting/debug/network")
    assert res_net.status_code == 200
    assert res_net.json()["total_tools"] == 4

    res_tree = client.get("/api/v1/troubleshooting/debug/decision-tree")
    assert res_tree.status_code == 200
    assert "root_step" in res_tree.json()

    res_diag = client.post(
        "/api/v1/troubleshooting/debug/diagnose-quality",
        json={
            "db_seeded": True,
            "embeddings_generated": True,
            "groq_working": True,
            "qdrant_connected": True,
        },
    )
    assert res_diag.status_code == 200
    assert res_diag.json()["status"] == "ALL_SUBSYSTEMS_HEALTHY"
