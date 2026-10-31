"""
MemeGPT — Test Configuration & Fixtures.

Every test runs against a throwaway SQLite file. Several modules call
``next(get_db())`` or ``SessionLocal()`` directly instead of using a fixture,
which bypasses the FastAPI dependency override; while the engine still pointed
at ``backend/memegpt.db`` those calls wrote fixture memes straight into the real
corpus. The throwaway file isolates all of them, not just the ones that resolve
through dependency injection.
"""

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Set test environment
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-32-chars-long-abc-123456"

# Bootstrap API keys are env-sourced and non-production only (AUDIT S-1).
# The suite opts in explicitly so these literals keep working under test.
os.environ.setdefault("BOOTSTRAP_DEMO_API_KEY", "memegpt_dev_demo_key")
os.environ.setdefault("BOOTSTRAP_PRO_API_KEY", "memegpt_pro_demo_key")
os.environ.setdefault("BOOTSTRAP_ADMIN_API_KEY", "memegpt_admin_secret_key")

# Point the application engine at a disposable database *before* importing it.
TEST_DB_DIR = Path(tempfile.mkdtemp(prefix="memegpt-tests-"))
TEST_DB_FILE = TEST_DB_DIR / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE.as_posix()}"

from app.database import Base, SessionLocal, engine, get_db, Meme
from app.main import app

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
TestingSessionLocal = SessionLocal  # same factory, so stray callers are isolated too


def _cleanup_test_db() -> None:
    shutil.rmtree(TEST_DB_DIR, ignore_errors=True)


atexit.register(_cleanup_test_db)

# Create the schema immediately: tests that talk to ``SessionLocal()`` directly
# without requesting the ``db`` fixture never trigger ``setup_test_db``, and used
# to get away with it only because the real database already had tables.
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def setup_test_db():
    """Create all tables in the disposable test database once per session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


#: Deterministic corpus for the endpoint tests.
#:
#: Endpoint tests assert that search/analyze/recommend return results, which the
#: service refuses to do against an empty database. They previously borrowed the
#: developer's populated database for this; the dependency is now explicit.
SHARED_CORPUS = [
    ("seed_0001", "First Try Success", ["tech", "success"], ["joy", "pride"],
     "It compiled on the first attempt",
     "Use when code, a deploy or a test passes without a single retry.",
     ["first try", "code", "works", "compile", "deploy", "production", "bug", "success"],
     "https://i.imgflip.com/1ur9b0.jpg"),
    ("seed_0002", "Promotion Celebration", ["success", "work"], ["joy", "pride"],
     "You are promoted",
     "Use when someone earns a promotion, a raise or a big achievement.",
     ["promoted", "promotion", "achievement", "raise", "success", "win", "job", "boss"],
     "https://i.imgflip.com/65xvg9.jpg"),
    ("seed_0003", "Friday Clock Out", ["work", "funny"], ["joy", "relieved"],
     "Laptop closed until Monday",
     "Use when the work week ends and the weekend finally begins.",
     ["friday", "weekend", "relief", "clock out", "work", "happy", "freedom"],
     "https://i.imgflip.com/261o3j.jpg"),
    ("seed_0004", "Monday Blues", ["work", "failure"], ["frustration", "tired"],
     "Monday again",
     "Use when a new work week starts and everything already feels heavy.",
     ["monday", "tired", "work", "coffee", "week", "office", "frustration"],
     "https://i.imgflip.com/1otk96.jpg"),
    ("seed_0005", "Cancelled Flight Rage", ["failure", "relationships"], ["anger", "frustration"],
     "Your flight is cancelled",
     "Use when travel plans collapse and the airline offers nothing useful.",
     ["flight", "cancelled", "travel", "airport", "delay", "disappointment", "rage"],
     "https://i.imgflip.com/1ur9b0.jpg"),
    ("seed_0006", "This Is Fine Fire", ["work", "failure"], ["denial", "calm"],
     "This is fine",
     "Use when everything is on fire and you pretend nothing is wrong.",
     ["this is fine", "fire", "chaos", "stress", "denial", "office", "disaster"],
     "https://i.imgflip.com/wxica.jpg"),
    ("seed_0007", "Surprised Pikachu", ["gaming", "funny"], ["surprise", "shock"],
     "Surprised Pikachu face",
     "Use when an obvious consequence of your own actions surprises you.",
     ["pikachu", "surprised", "shocked", "pokemon", "obvious", "gaming"],
     "https://i.imgflip.com/3ocgt8.jpg"),
    ("seed_0008", "Drake Approve", ["funny"], ["approval", "disapproval"],
     "No / Yes",
     "Use to reject one option and endorse another.",
     ["drake", "approve", "disapprove", "choice", "prefer", "comparison"],
     "https://i.imgflip.com/30b1gx.jpg"),
]


@pytest.fixture(scope="session", autouse=True)
def seed_shared_corpus(setup_test_db):
    """Seed the deterministic corpus every endpoint test searches over."""
    session = SessionLocal()
    try:
        if session.query(Meme).count() == 0:
            for (
                meme_id, name, categories, emotions, dialogue, explanation, keywords, image_url
            ) in SHARED_CORPUS:
                session.add(Meme(
                    id=meme_id,
                    name=name,
                    slug=meme_id.replace("_", "-"),
                    categories=categories,
                    emotions=emotions,
                    dialogue=dialogue,
                    explanation=explanation,
                    keywords=keywords,
                    image_url=image_url,
                    gif_url=None,
                    source="test",
                    nsfw=False,
                    moderation_status="approved",
                    alt_text=f"{name} meme",
                    viral_score=80.0,
                    popularity_score=0.8,
                    usage_count=10,
                    upvotes=5,
                    downvotes=0,
                ))
            session.commit()
    finally:
        session.close()
    yield


@pytest.fixture(autouse=True)
def isolate_committed_rows(seed_shared_corpus):
    """Drop memes a test commits through a session outside the ``db`` fixture.

    Modules that use ``next(get_db())`` or ``SessionLocal()`` commit directly, so
    the rollback in ``db_session`` cannot reach them. Without this every later
    test inherits those fixtures and assertions depend on execution order.
    """
    session = SessionLocal()
    try:
        before = {meme_id for (meme_id,) in session.query(Meme.id).all()}
    finally:
        session.close()

    yield

    session = SessionLocal()
    try:
        residue = [
            meme for meme in session.query(Meme).all() if meme.id not in before
        ]
        if residue:
            for meme in residue:
                session.delete(meme)  # ORM delete so relationship cascades fire
            session.commit()
    finally:
        session.close()


@pytest.fixture(autouse=True)
def reset_rate_limits_auto():
    """Auto-reset rate limiters between all test executions."""
    from app.core.rate_limit import rate_limiter
    from app.core.cache import _rate_counts, _fallback_cache
    rate_limiter.reset()
    _rate_counts.clear()
    yield
    rate_limiter.reset()
    _rate_counts.clear()


@pytest.fixture
def db_session(setup_test_db):
    """Yields an isolated DB session with rollback after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Seed sample memes for search tests
    sample_memes = [
        Meme(
            id="test-drake-001",
            name="Drake Pointing",
            slug="drake-pointing",
            categories=["comparison", "reaction"],
            emotions=["approval", "disapproval"],
            dialogue="No / Yes",
            explanation="Used to approve/disapprove something",
            keywords=["drake", "pointing", "prefer", "choice"],
            image_url="https://i.imgflip.com/30b1gx.jpg",
            source="imgflip",
            nsfw=False,
            popularity_score=0.95,
        ),
        Meme(
            id="test-fine-002",
            name="This Is Fine Dog",
            slug="this-is-fine",
            categories=["stress", "work", "chaos"],
            emotions=["denial", "calm"],
            dialogue="This is fine",
            explanation="Use when everything is going wrong but you pretend it is ok.",
            keywords=["fine", "burning", "dog", "fire", "chaos"],
            image_url="https://i.imgflip.com/26am.jpg",
            source="manual",
            nsfw=False,
            popularity_score=0.92,
        ),
        Meme(
            id="test-pikachu-003",
            name="Surprised Pikachu",
            slug="surprised-pikachu",
            categories=["gaming", "reaction"],
            emotions=["surprise", "shock"],
            dialogue="Surprised Pikachu face",
            explanation="Use when surprised by an obvious outcome of your own actions.",
            keywords=["pikachu", "surprised", "shocked", "pokemon"],
            image_url="https://i.imgflip.com/3ocgt8.jpg",
            source="manual",
            nsfw=False,
            popularity_score=0.90,
        ),
    ]
    for m in sample_memes:
        session.add(m)
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def db(db_session):
    """Alias for db_session fixture."""
    return db_session


@pytest.fixture
def sample_meme(db_session):
    """Fixture returning sample meme."""
    meme = db_session.query(Meme).filter(Meme.id == "test-drake-001").first()
    return meme


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden DB dependency."""
    from app.core.rate_limit import rate_limiter
    rate_limiter.reset()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    rate_limiter.reset()


# ── Interpreter Teardown Guard ────────────────────────────────────────────────
# A native extension pulled in by the ML stack (hf_xet's Rust runtime) can crash
# inside Py_Finalize on Python 3.12 *after* the suite has completed, which turns a
# fully green run into exit code 1 and fails the build for no reason. Record the
# genuine pytest status, then hard-exit once plugin teardown is finished.
_SESSION_EXIT_STATUS = {"code": 0}


def pytest_sessionfinish(session, exitstatus):
    _SESSION_EXIT_STATUS["code"] = int(exitstatus)


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):
    """Skip interpreter finalization for hermetic runs, preserving the real status."""
    if os.getenv("APP_ENV", "").lower() not in {"test", "testing", "ci"}:
        return
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(_SESSION_EXIT_STATUS["code"])
