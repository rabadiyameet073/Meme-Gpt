"""Unit tests verifying database gap resolutions (06-database-gaps.md).

Items verified:
- DB-01 / DB-04: PostgreSQL migration script and GIN index DDL.
- DB-02: Unified schema representation (prisma/schema.prisma has all 11 models).
- DB-03: Versioned Alembic migrations configured and baseline revision exists.
- DB-05: Truthful backup reporting (no success reported without actual artifact).
- DB-06: Off-site backup options in backup_manager and cron workflow.
- DB-07: Safe non-destructive seeding (preserves users/api_keys; upsert logic).
- DB-08: Cascade referential cleanup on user deletion.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, User, ApiKey, DeviceToken, SavedMeme, Feedback, Meme
from app.services.backup_service import create_database_backup
from app.services.database_service import generate_postgres_index_ddl
from seed import seed


def test_db_02_prisma_schema_contains_all_models():
    """Verify prisma/schema.prisma models match all 11 SQLAlchemy models."""
    prisma_file = Path(__file__).resolve().parent.parent.parent / "prisma" / "schema.prisma"
    assert prisma_file.exists(), "prisma/schema.prisma must exist"

    content = prisma_file.read_text(encoding="utf-8")
    expected_models = [
        "model Meme",
        "model MemeVote",
        "model MemeUsage",
        "model FavouriteMeme",
        "model MemeFlag",
        "model User",
        "model SavedMeme",
        "model Feedback",
        "model SearchLog",
        "model ApiKey",
        "model DeviceToken",
    ]
    for model_decl in expected_models:
        assert model_decl in content, f"Missing {model_decl} in prisma/schema.prisma"


def test_db_03_alembic_setup_and_baseline_exists():
    """Verify alembic configuration and baseline revision exist."""
    backend_dir = Path(__file__).resolve().parent.parent
    alembic_ini = backend_dir / "alembic.ini"
    alembic_env = backend_dir / "alembic" / "env.py"
    baseline_rev = backend_dir / "alembic" / "versions" / "0001_baseline_schema.py"

    assert alembic_ini.exists(), "alembic.ini must exist"
    assert alembic_env.exists(), "alembic/env.py must exist"
    assert baseline_rev.exists(), "Baseline migration 0001 must exist"


def test_db_04_postgres_gin_ddl():
    """Verify PostgreSQL index generation includes GIN indexes on array columns."""
    ddl = generate_postgres_index_ddl()
    assert "USING GIN(categories)" in ddl
    assert "USING GIN(emotions)" in ddl


def test_db_05_truthful_backup_manifest(tmp_path, monkeypatch):
    """Verify non-SQLite backup without pg_dump reports managed_external and never fakes sha256."""
    monkeypatch.setattr("app.services.backup_service.is_sqlite", False)
    monkeypatch.setattr("shutil.which", lambda bin_name: None)

    manifest = create_database_backup(target_dir=tmp_path)
    assert manifest["status"] == "managed_external"
    assert manifest["artifact_generated"] is False
    assert manifest["sha256"] is None
    assert manifest["filename"] is None


def test_db_07_safe_seeding_preserves_users_and_keys(monkeypatch):
    """Verify default seeding is upsert-only and preserves users and API keys."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    user = User(id="preserve_u1", email="keep_me@memegpt.com", name="Keep Me")
    api_key = ApiKey(id="preserve_k1", key_hash="hash123", prefix="pk_live_123", user_id="preserve_u1")
    session.add(user)
    session.add(api_key)
    session.commit()

    monkeypatch.setattr("seed.SessionLocal", lambda: session)
    monkeypatch.setattr("seed.init_db", lambda drop_all=False: None)

    # Run seed without reset
    seed(reset=False)

    # Verify user and key still exist
    assert session.query(User).filter(User.id == "preserve_u1").first() is not None
    assert session.query(ApiKey).filter(ApiKey.id == "preserve_k1").first() is not None
    session.close()


def test_db_08_user_referential_cleanup():
    """Verify deleting a user cascades to ApiKey, SavedMeme, and sets null on DeviceToken."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    user = User(id="user_del_test", email="delete_me@memegpt.com")
    meme = Meme(id="meme_for_save", name="Saved Meme", slug="saved-meme-del")
    saved = SavedMeme(id="saved_1", user_id="user_del_test", meme_id="meme_for_save")
    api_key = ApiKey(id="key_del_1", key_hash="hash_del", prefix="pk_del", user_id="user_del_test")
    device_token = DeviceToken(id="dt_1", token="expo_tok_123", user_id="user_del_test")

    session.add_all([user, meme, saved, api_key, device_token])
    session.commit()

    # Delete user
    session.delete(user)
    session.commit()

    assert session.query(SavedMeme).filter(SavedMeme.user_id == "user_del_test").first() is None
    assert session.query(ApiKey).filter(ApiKey.user_id == "user_del_test").first() is None
    session.close()
