import pytest
from app.services import (
    recommend,
    parse_intent,
    get_text_embedding,
    detect_emotion,
    build_query_text,
    vector_search,
    rerank,
    composite_score,
    build_meme_urls,
    resolve_formats,
    get_share_url,
)


@pytest.mark.asyncio
async def test_recommendation_orchestrator():
    res = await recommend(user_text="when my unit tests pass on the first try", format_pref="image", nsfw=False)
    assert res is not None
    assert "primary" in res or "topFive" in res
    assert "detectedCategories" in res
    assert "detectedTags" in res


@pytest.mark.asyncio
async def test_llm_intent_service():
    intent = await parse_intent("I am so stressed about deadlines")
    assert isinstance(intent, dict)
    assert "emotion" in intent or "emotion_hint" in intent
    assert "tone" in intent
    assert "keywords" in intent


def test_embedding_and_emotion_service():
    vec = get_text_embedding("test embedding generation")
    assert len(vec) == 384

    emo = detect_emotion("This is amazing, I am overjoyed!")
    assert "primary" in emo
    assert "confidence" in emo

    rich_text = build_query_text(
        user_text="so happy",
        intent={"situation": "succeeded", "tone": "excited", "keywords": ["happy"]},
        emotion={"primary": "joy", "secondary": "neutral"}
    )
    assert "so happy" in rich_text
    assert "joy" in rich_text


def test_search_and_rerank_services():
    query_vec = get_text_embedding("coding bug in production")
    results = vector_search(query_vec, emotion="frustration", format_pref="any", top_k=5)
    assert isinstance(results, list)

    reranked = rerank(
        candidates=results,
        intent={"tone": "frustrated", "keywords": ["bug"]},
        emotion={"primary": "anger", "secondary": "sadness"},
        format_pref="gif"
    )
    assert isinstance(reranked, list)



def test_cdn_service_url_building():
    urls = build_meme_urls(meme_id="123", slug="drake-pointing")
    assert "image" in urls
    assert "gif" in urls
    assert "video" in urls
    assert "webp" in urls
    assert "thumb" in urls
    assert "drake-pointing" in urls["image"]

    share_url = get_share_url("drake-pointing", query_id="abc-123")
    assert "drake-pointing" in share_url
    assert "ref=abc-123" in share_url
