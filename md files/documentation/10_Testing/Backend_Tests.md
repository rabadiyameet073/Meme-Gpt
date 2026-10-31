# MemeGPT — Backend Tests

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Test Suite Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_main.py             # API endpoint integration tests
├── test_meme_matcher.py     # Pipeline orchestrator tests
├── test_rule_engine.py      # Scoring algorithm tests
├── test_semantic_search.py  # Embedding + search tests
├── test_database.py         # Database CRUD tests
└── test_config.py           # Configuration loading tests
```

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v                    # Run all tests
python -m pytest tests/ -v --cov=app          # With coverage
python -m pytest tests/test_main.py -v        # Single file
python -m pytest tests/ -k "test_search"      # By name pattern
python -m pytest tests/ --tb=short            # Short tracebacks
```

---

## Key Test Examples

### API Integration Tests

```python
# test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_search_valid():
    response = client.post("/search", json={"query": "Monday vibes"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) <= 5

def test_search_empty_query():
    response = client.post("/search", json={"query": ""})
    assert response.status_code == 422

def test_search_max_length():
    response = client.post("/search", json={"query": "a" * 2001})
    assert response.status_code == 422

def test_meme_not_found():
    response = client.get("/memes/nonexistent")
    assert response.status_code == 404
```

### Unit Tests

```python
# test_rule_engine.py
def test_keyword_score_full_match():
    score = calculate_keyword_score("monday morning work", ["monday", "morning", "work"])
    assert score > 0.8

def test_keyword_score_no_match():
    score = calculate_keyword_score("cats playing", ["monday", "work"])
    assert score < 0.1

# test_semantic_search.py
def test_embed_text_dimensions():
    vec = embed_text("hello world")
    assert len(vec) == 384

def test_embed_text_normalized():
    vec = embed_text("test query")
    norm = sum(v**2 for v in vec) ** 0.5
    assert abs(norm - 1.0) < 0.01  # L2 normalized
```

---

## Coverage Target: >80%

| Module | Current | Target |
|---|---|---|
| `main.py` | — | >90% |
| `meme_matcher.py` | — | >80% |
| `rule_engine.py` | — | >95% |
| `semantic_search.py` | — | >80% |
| `database.py` | — | >85% |

---

> **Related Documents:**
> - [Testing_Strategy.md](./Testing_Strategy.md) · [09_Development/Coding_Standards.md](../09_Development/Coding_Standards.md)
