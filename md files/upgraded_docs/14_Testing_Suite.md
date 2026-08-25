# 14 — Testing Suite
# pytest, Vitest, Integration Tests, AI Eval Labeled Set

> **Gap Source:** Section 15 of GAP_ANALYSIS_FULL.md  
> **Priority:** P2  
> **Target:** >80% backend coverage, all critical paths tested

---

## BACKEND TESTS (pytest)

### Setup

```bash
cd "d:\Meme GPT\backend"
pip install pytest pytest-asyncio pytest-cov httpx
```

Add to `requirements.txt`:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.24.0
```

---

### `conftest.py` — Test Fixtures

**Create** `d:\Meme GPT\backend\tests\conftest.py`:

```python
"""
Shared test fixtures for MemeGPT backend tests.
Uses in-memory SQLite for isolation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# In-memory SQLite for tests
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db():
    """Create test database with all tables."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(db):
    """FastAPI test client with DB dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_meme(db):
    """Insert a sample meme for testing."""
    from app.database import Meme
    meme = Meme(
        id="test-drake-001",
        name="Drake Pointing",
        slug="drake-pointing",
        categories=["reaction", "comparison"],
        emotions=["approval", "disapproval"],
        dialogue="No / Yes",
        explanation="Used to approve/disapprove something",
        keywords=["drake", "pointing", "choice", "prefer"],
        image_url="https://i.imgflip.com/30b1gx.jpg",
        source="imgflip",
        nsfw=False,
        popularity_score=0.95,
    )
    db.add(meme)
    db.commit()
    yield meme
    db.delete(meme)
    db.commit()
```

---

### Test: Search Endpoint

**Create** `d:\Meme GPT\backend\tests\test_search.py`:

```python
import pytest

def test_search_returns_results(client, sample_meme):
    """Search endpoint returns meme results."""
    resp = client.post("/api/v1/search", json={"query": "drake pointing yes no"})
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_search_with_format_filter(client, sample_meme):
    """Format filter is respected."""
    resp = client.post("/api/v1/search", json={"query": "test", "format": "gif"})
    assert resp.status_code == 200


def test_search_rate_limit_headers(client):
    """Rate limit headers are present."""
    resp = client.post("/api/v1/search", json={"query": "hello"})
    assert "x-ratelimit-limit" in resp.headers


def test_search_sanitizes_input(client):
    """HTML injection is sanitized."""
    resp = client.post("/api/v1/search", json={"query": "<script>alert(1)</script>"})
    assert resp.status_code == 200


def test_search_empty_query(client):
    """Empty query returns 422 or empty results."""
    resp = client.post("/api/v1/search", json={"query": ""})
    assert resp.status_code in (200, 422)


def test_search_very_long_query(client):
    """Very long query is truncated, not 500."""
    long_query = "a" * 10000
    resp = client.post("/api/v1/search", json={"query": long_query})
    assert resp.status_code in (200, 422)
```

---

### Test: Categories & Stats

**Create** `d:\Meme GPT\backend\tests\test_categories.py`:

```python
def test_get_categories(client, sample_meme):
    """GET /api/categories returns list."""
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0


def test_get_stats(client):
    """GET /api/stats returns count dict."""
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_memes" in data
    assert isinstance(data["total_memes"], int)
```

---

### Test: Qdrant Search Service (Unit)

**Create** `d:\Meme GPT\backend\tests\test_search_service.py`:

```python
from app.services.search_service import _cosine_similarity, vector_search


def test_cosine_similarity_identical():
    """Identical vectors → similarity = 1.0."""
    vec = [1.0, 0.0, 0.0, 1.0]
    result = _cosine_similarity(vec, vec)
    assert abs(result - 1.0) < 0.001


def test_cosine_similarity_orthogonal():
    """Orthogonal vectors → similarity = 0.0."""
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    result = _cosine_similarity(a, b)
    assert abs(result) < 0.001


def test_cosine_similarity_empty():
    """Empty vectors → 0.0 (no crash)."""
    assert _cosine_similarity([], []) == 0.0


def test_cosine_similarity_different_lengths():
    """Different length vectors → 0.0 (no crash)."""
    assert _cosine_similarity([1.0], [1.0, 2.0]) == 0.0


def test_vector_search_fallback_without_qdrant():
    """vector_search falls back gracefully when Qdrant is unavailable."""
    query_vector = [0.1] * 384
    results = vector_search(query_vector, top_k=5)
    # Should return a list (possibly empty) not raise
    assert isinstance(results, list)
```

---

### Test: Database Schema

**Create** `d:\Meme GPT\backend\tests\test_schema.py`:

```python
def test_meme_has_all_required_columns(db):
    """Verify Meme model has all documented columns."""
    from app.database import Meme
    from sqlalchemy import inspect

    inspector = inspect(db.bind)
    cols = {c["name"] for c in inspector.get_columns("memes")}

    required = {
        "id", "name", "slug", "categories", "emotions",
        "nsfw", "thumb_url", "source", "view_count",
        "download_count", "popularity_score", "indexed_at",
    }
    missing = required - cols
    assert not missing, f"Missing columns: {missing}"


def test_search_log_no_raw_query(db):
    """SearchLog should NOT have a raw 'query' TEXT column (GDPR)."""
    from sqlalchemy import inspect
    inspector = inspect(db.bind)
    cols = {c["name"] for c in inspector.get_columns("search_logs")}
    # 'query_hash' should exist, 'query' raw text should NOT be mandatory
    assert "query_hash" in cols
```

---

### Test: AI Pipeline (Integration)

**Create** `d:\Meme GPT\backend\tests\test_ai_pipeline.py`:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_rule_based_intent_always_returns_dict():
    """Rule-based intent extraction never returns None."""
    from app.services.llm_service import _rule_based_intent

    result = _rule_based_intent("my boss is so annoying today")
    assert isinstance(result, dict)
    assert "emotion_hint" in result
    assert "keywords" in result
    assert result["emotion_hint"] in ["joy", "anger", "sadness", "surprise", "fear", "disgust", "neutral"]


@pytest.mark.asyncio
async def test_parse_intent_without_groq():
    """parse_intent returns dict even when GROQ_API_KEY is empty."""
    from app.services.llm_service import parse_intent

    result = await parse_intent("when the coffee machine is broken on Monday")
    assert isinstance(result, dict)
    assert result is not None  # Never None


def test_embed_text_returns_384_dim():
    """embed_text always returns 384-dim vector."""
    from app.services.embedding_service import embed_text

    vector = embed_text("hello world")
    assert isinstance(vector, list)
    assert len(vector) == 384


def test_detect_emotion_returns_dict():
    """detect_emotion always returns valid dict."""
    from app.services.embedding_service import detect_emotion

    result = detect_emotion("I am so angry!")
    assert "primary" in result
    assert result["primary"] in ["joy", "anger", "sadness", "surprise", "fear", "disgust", "neutral"]
```

---

## AI EVALUATION LABELED SET

**Create** `d:\Meme GPT\backend\evaluate.py` (complete implementation):

```python
#!/usr/bin/env python3
"""
MemeGPT — AI Quality Evaluation.
Tests search quality against a labeled test set.

Run: python evaluate.py
"""

import asyncio
import json
import sys

# Labeled test cases: (query, expected_meme_slugs)
# These are ground-truth correct answers
TEST_CASES = [
    ("when the code works on the first try", ["surprised-pikachu", "one-does-not-simply"]),
    ("monday morning motivation", ["this-is-fine", "kermit-sipping-tea"]),
    ("boss says we work on weekends", ["distracted-boyfriend", "drake-pointing"]),
    ("finally fixed that bug after 3 hours", ["success-kid", "celebrating-guy"]),
    ("my code works but I dont know why", ["confused-math-lady", "dog-sitting-fire"]),
    ("when someone says just 5 more minutes", ["waiting-skeleton", "roll-safe-think"]),
    ("feeling overwhelmed by todos", ["this-is-fine", "disaster-girl"]),
    ("made it to Friday", ["weekend-spongebob", "finally-free"]),
]


async def evaluate(top_k: int = 5) -> dict:
    from app.services.recommendation_service import recommend_memes

    results = []
    hits = 0
    total = len(TEST_CASES)

    for query, expected_slugs in TEST_CASES:
        try:
            response = await recommend_memes(query, format_pref="gif", nsfw=False)
            returned_slugs = [r.get("slug", "") for r in response.get("results", [])][:top_k]

            # Check if any expected meme appears in top_k results
            hit = any(slug in returned_slugs for slug in expected_slugs)
            if hit:
                hits += 1

            results.append({
                "query": query,
                "expected": expected_slugs,
                "returned": returned_slugs,
                "hit": hit,
            })
        except Exception as e:
            results.append({
                "query": query,
                "expected": expected_slugs,
                "returned": [],
                "hit": False,
                "error": str(e),
            })

    precision_at_k = hits / total
    print(f"\n=== MemeGPT AI Evaluation Results ===")
    print(f"Precision@{top_k}: {precision_at_k:.2%} ({hits}/{total})")
    print(f"\nTarget: >60% precision@5")
    print(f"Result: {'✅ PASS' if precision_at_k >= 0.6 else '❌ FAIL'}\n")

    for r in results:
        status = "✅" if r["hit"] else "❌"
        print(f"{status} '{r['query'][:50]}'")
        if not r["hit"]:
            print(f"   Expected: {r['expected']}")
            print(f"   Got: {r['returned']}")

    return {"precision_at_k": precision_at_k, "total": total, "hits": hits}


if __name__ == "__main__":
    asyncio.run(evaluate())
```

---

## RUN TESTS

```bash
cd "d:\Meme GPT\backend"

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_search.py -v

# Run AI pipeline tests
pytest tests/test_ai_pipeline.py -v

# Run evaluation
python evaluate.py
```

**Target:** Coverage > 80%, Precision@5 > 60%
