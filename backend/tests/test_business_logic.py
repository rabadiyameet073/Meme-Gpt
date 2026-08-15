from app.services.rerank_service import rerank, _deduplicate
from app.services.recommendation_service import _make_cache_key


def test_cache_key_generation():
    key1 = _make_cache_key("When code works", "gif", False)
    key2 = _make_cache_key("when code works ", "gif", False)
    assert key1 == key2
    assert key1.startswith("search:")


def test_deduplication():
    candidates = [
        {"meme": {"name": "Drake Hotline Bling", "id": "1"}, "score": 0.95},
        {"meme": {"name": "drake hotline bling", "id": "2"}, "score": 0.85},
        {"meme": {"name": "Distracted Boyfriend", "id": "3"}, "score": 0.80},
    ]
    deduped = _deduplicate(candidates)
    assert len(deduped) == 2
    assert deduped[0]["meme"]["name"] == "Drake Hotline Bling"
    assert deduped[1]["meme"]["name"] == "Distracted Boyfriend"


def test_composite_scoring_and_reranking():
    candidates = [
        {
            "id": "1",
            "score": 0.70,
            "meme": {
                "id": "1",
                "name": "Success Kid",
                "category": "coding",
                "dialogue": "Code compiled with 0 errors",
                "keywords": ["success", "coding", "joy"],
                "viral_score": 50,
                "usage_count": 100,
                "upvotes": 50,
                "gif_ref": "https://cdn.memegpt.com/gifs/1.gif"
            }
        },
        {
            "id": "2",
            "score": 0.65,
            "meme": {
                "id": "2",
                "name": "Disaster Girl",
                "category": "chaos",
                "dialogue": "Deleted prod database",
                "keywords": ["fire", "chaos"],
                "viral_score": 10,
                "usage_count": 20,
                "upvotes": 5,
            }
        }
    ]

    intent = {"keywords": ["coding", "compiled"], "categories": ["coding"]}
    emotion = {"primary": "joy", "all": {"joy": 0.95, "neutral": 0.05}}

    results = rerank(candidates, intent, emotion, format_pref="gif")
    assert len(results) == 2
    top = results[0]
    assert top["meme"]["name"] == "Success Kid"
    assert top["score"] > results[1]["score"]
    assert top["emotion_match"] is True

