from app.repositories import create_repository
from app.database import init_db

init_db()


def test_repository_lifecycle_and_methods():
    repo = create_repository()

    # 1. get_all_memes
    all_memes = repo.get_all_memes()
    assert isinstance(all_memes, list)
    assert len(all_memes) > 0

    first = all_memes[0]
    meme_id = first["id"]

    # 2. get_meme_by_id
    fetched = repo.get_meme_by_id(meme_id)
    assert fetched is not None
    assert fetched["id"] == meme_id

    # 3. get_meme_by_slug
    by_slug = repo.get_meme_by_slug(first.get("slug") or first["id"])
    assert by_slug is not None

    # 4. record_feedback
    ok = repo.record_feedback(meme_id, action="download", session_id="test_sess", format="gif")
    assert ok is True

    # 5. log_search
    log_ok = repo.log_search(query_hash="test_repo_hash", result_count=5, latency_ms=45, cached=False, emotion="joy")
    assert log_ok is True

    # 6. get_trending
    trending = repo.get_trending(limit=5)
    assert isinstance(trending, list)
    assert len(trending) > 0

    # 7. save_meme toggle
    fav_on = repo.save_meme(meme_id, session_id="test_sess")
    assert fav_on is True
    fav_off = repo.save_meme(meme_id, session_id="test_sess")
    assert fav_off is True
