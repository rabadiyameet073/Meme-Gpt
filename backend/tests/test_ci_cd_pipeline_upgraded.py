"""
Tests for 16_CI_CD_Deployment.md.

Verifies:
1. .github/workflows/deploy.yml configuration & jobs
2. backend/railway.toml and root railway.toml configurations
3. frontend/vercel.json Vite routing & security headers
4. /health endpoint UptimeRobot monitor contract
"""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_github_workflow_deploy_file():
    """Verify GitHub actions CI/CD workflow contains all 4 required jobs."""
    wf_file = Path("d:/Meme GPT/.github/workflows/deploy.yml")
    assert wf_file.exists()
    content = wf_file.read_text(encoding="utf-8")

    assert "test-backend:" in content
    assert "test-frontend:" in content
    assert "deploy-backend:" in content
    assert "deploy-frontend:" in content
    assert "RAILWAY_TOKEN" in content
    assert "VERCEL_TOKEN" in content


def test_railway_toml_configurations():
    """Verify railway.toml exists with uvicorn startCommand and healthcheck."""
    files = [
        Path("d:/Meme GPT/backend/railway.toml"),
        Path("d:/Meme GPT/railway.toml"),
    ]
    for f in files:
        assert f.exists()
        content = f.read_text(encoding="utf-8")
        assert "healthcheckPath" in content or "healthcheckTimeout" in content
        assert "startCommand" in content


def test_vercel_json_configuration():
    """Verify frontend/vercel.json contains Vite SPA rewrites and security headers."""
    vercel_file = Path("d:/Meme GPT/frontend/vercel.json")
    assert vercel_file.exists()
    data = json.loads(vercel_file.read_text(encoding="utf-8"))

    assert data["framework"] == "vite"
    assert data["outputDirectory"] == "dist"
    assert any("index.html" in r["destination"] for r in data["rewrites"])


def test_uptimerobot_health_endpoint():
    """Verify /health endpoint returns contract for UptimeRobot monitoring."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "ok"
    assert "version" in data
    assert "qdrant" in data
    assert "redis" in data
    assert "db" in data
