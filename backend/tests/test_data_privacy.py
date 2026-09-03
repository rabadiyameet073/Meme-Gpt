"""Tests for Data Privacy & GDPR from 11_Security/Data_Privacy.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Feedback, MemeVote, FavouriteMeme
from app.services.data_privacy_service import (
    get_privacy_by_design_principles,
    get_data_classification_matrix,
    get_gdpr_rights_catalog,
    get_cookie_policy_spec,
    get_dpa_status_matrix,
    export_session_data,
    delete_session_data,
    purge_expired_privacy_data,
    evaluate_privacy_compliance,
)

client = TestClient(app)


def test_privacy_by_design_principles():
    res = get_privacy_by_design_principles()
    assert res["total_principles"] == 7
    names = [p["name"] for p in res["principles"]]
    assert "Proactive, not reactive" in names
    assert "Default privacy" in names
    assert "Embedded in design" in names
    assert "Full functionality" in names
    assert "End-to-end security" in names
    assert "Transparency" in names
    assert "User-centric" in names


def test_data_classification_matrix():
    matrix = get_data_classification_matrix()
    assert matrix["total_categories"] == 6
    cats = [c["category"] for c in matrix["classifications"]]
    assert "Meme catalog" in cats
    assert "Search queries" in cats
    assert "Feedback signals" in cats
    assert "Session IDs" in cats
    assert "IP addresses" in cats
    assert "User email" in cats


def test_gdpr_rights_catalog():
    catalog = get_gdpr_rights_catalog()
    assert catalog["total_rights"] == 5
    rights = [r["right"] for r in catalog["rights"]]
    assert "Right to access" in rights
    assert "Right to deletion" in rights
    assert "Right to portability" in rights
    assert "Right to object" in rights
    assert "Right to rectification" in rights


def test_cookie_policy_spec():
    policy = get_cookie_policy_spec()
    assert policy["total_cookies"] == 3
    names = [c["cookie"] for c in policy["cookies"]]
    assert "session_id" in names
    assert "format_pref" in names
    assert "theme" in names

    guarantees = policy["guarantees"]
    assert guarantees["third_party_cookies"] is False
    assert guarantees["advertising_cookies"] is False
    assert guarantees["analytics_cookies"] is False


def test_dpa_status_matrix():
    dpa = get_dpa_status_matrix()
    assert dpa["total_services"] == 5
    services = [s["service"] for s in dpa["dpas"]]
    assert "Supabase" in services
    assert "Groq" in services
    assert "Qdrant" in services
    assert "Cloudflare" in services
    assert "Vercel" in services


def test_gdpr_export_and_delete_workflow():
    import uuid
    db = SessionLocal()
    test_sid = f"test_privacy_session_{uuid.uuid4().hex[:8]}"

    # Seed test feedback, vote, and favorite
    fb = Feedback(session_id=test_sid, meme_id="meme_priv_1", action="click")
    vote = MemeVote(session_id=test_sid, meme_id="meme_priv_1", vote=1)
    fav = FavouriteMeme(session_id=test_sid, meme_id="meme_priv_1")
    db.add_all([fb, vote, fav])
    db.commit()


    # 1. Test Export via API
    export_res = client.get(f"/api/v1/privacy/export?session_id={test_sid}")
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert export_data["session_id"] == test_sid
    assert export_data["total_records"] >= 3
    assert len(export_data["feedback_records"]) >= 1
    assert len(export_data["votes"]) >= 1
    assert len(export_data["favorites"]) >= 1

    # 2. Test Deletion via API (Right to Erasure)
    delete_res = client.delete(f"/api/v1/privacy/delete?session_id={test_sid}")
    assert delete_res.status_code == 200
    del_data = delete_res.json()
    assert del_data["success"] is True
    assert del_data["deleted_records"]["total"] >= 3

    # 3. Verify data is gone
    post_export = client.get(f"/api/v1/privacy/export?session_id={test_sid}")
    assert post_export.status_code == 200
    assert post_export.json()["total_records"] == 0
    db.close()


def test_privacy_api_endpoints_and_compliance():
    res_prin = client.get("/api/v1/privacy/principles")
    assert res_prin.status_code == 200
    assert res_prin.json()["total_principles"] == 7

    res_class = client.get("/api/v1/privacy/classification")
    assert res_class.status_code == 200
    assert res_class.json()["total_categories"] == 6

    res_rights = client.get("/api/v1/privacy/gdpr-rights")
    assert res_rights.status_code == 200
    assert res_rights.json()["total_rights"] == 5

    res_cookies = client.get("/api/v1/privacy/cookies")
    assert res_cookies.status_code == 200
    assert res_cookies.json()["total_cookies"] == 3

    res_dpa = client.get("/api/v1/privacy/dpa")
    assert res_dpa.status_code == 200
    assert res_dpa.json()["total_services"] == 5

    res_purge = client.post("/api/v1/privacy/purge-expired", json={"retention_days": 90})
    assert res_purge.status_code == 200
    assert res_purge.json()["success"] is True

    res_comp = client.get("/api/v1/privacy/compliance")
    assert res_comp.status_code == 200
    assert res_comp.json()["compliance_score"] == 100.0
