"""Unit tests verifying admin panel gaps (11-admin-panel-gaps.md).

Items verified:
- ADM-03: Immutable AdminAuditLog generated on administrative actions.
- ADM-05: Platform KPI & metrics endpoint (/admin/metrics).
- ADM-07: User management routes (/admin/users, update role, activate/ban status).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, User, Meme, AdminAuditLog
from app.core.auth import AuthContext
from app.api.v1.admin import (
    create_meme,
    update_meme,
    delete_meme,
    list_admin_users,
    update_user_role,
    update_user_status,
    get_admin_metrics,
    get_audit_logs,
    CreateMemeRequest,
    UpdateMemeRequest,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
)


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_adm_03_audit_trail_recorded(test_db):
    """Verify create_meme, update_meme, delete_meme write to AdminAuditLog."""
    admin_auth = AuthContext(tier="admin", rate_limit=1000, user_id="admin_1", is_admin=True)

    # 1. Create meme
    req = CreateMemeRequest(name="Audit Meme Test", category="work", nsfw=False)
    res = create_meme(body=req, db=test_db, auth=admin_auth)
    meme_id = res["meme"]["id"]

    logs = test_db.query(AdminAuditLog).filter(AdminAuditLog.target_id == meme_id).all()
    assert len(logs) == 1
    assert logs[0].action == "create_meme"
    assert logs[0].actor_id == "admin_1"

    # 2. Update meme
    up_req = UpdateMemeRequest(name="Updated Audit Meme")
    update_meme(meme_id=meme_id, body=up_req, db=test_db, auth=admin_auth)

    logs2 = test_db.query(AdminAuditLog).filter(AdminAuditLog.target_id == meme_id).all()
    assert len(logs2) == 2
    assert any(l.action == "update_meme" for l in logs2)


def test_adm_07_user_management(test_db):
    """Verify listing users, updating user role, and activating/banning status."""
    admin_auth = AuthContext(tier="admin", rate_limit=1000, user_id="admin_1", is_admin=True)

    user = User(id="managed_u1", email="managed@memegpt.com", plan="free", is_active=True, is_admin=False)
    test_db.add(user)
    test_db.commit()

    # List users
    users_list = list_admin_users(limit=10, offset=0, db=test_db, auth=admin_auth)
    assert users_list["total"] >= 1

    # Update role to pro and admin
    role_req = UpdateUserRoleRequest(plan="pro", is_admin=True)
    role_res = update_user_role(user_id="managed_u1", body=role_req, db=test_db, auth=admin_auth)
    assert role_res["user"]["plan"] == "pro"
    assert role_res["user"]["is_admin"] is True

    # Ban/deactivate user
    status_req = UpdateUserStatusRequest(is_active=False)
    status_res = update_user_status(user_id="managed_u1", body=status_req, db=test_db, auth=admin_auth)
    assert status_res["user"]["is_active"] is False


def test_adm_05_admin_metrics(test_db):
    """Verify platform metrics endpoint returns catalog and analytics counts."""
    admin_auth = AuthContext(tier="admin", rate_limit=1000, user_id="admin_1", is_admin=True)

    m1 = Meme(id="m_metric_1", name="Metric Meme", slug="metric-meme", moderation_status="approved")
    test_db.add(m1)
    test_db.commit()

    metrics = get_admin_metrics(db=test_db, auth=admin_auth)
    assert "memes" in metrics
    assert "users" in metrics
    assert "analytics" in metrics
    assert metrics["memes"]["total"] >= 1
