"""
MemeGPT — Test Configuration & Fixtures.
Sets up in-memory SQLite DB and test FastAPI client.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-32-chars-long-abc-123456"

from app.database import Base, get_db, Meme
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_test_db():
    """Create all tables in test database once per session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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
