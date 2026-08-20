"""Tests for Favorites & Collections feature from 08_Features/Favorites_Collections.md."""

import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.services.favorites_service import (
    create_collection,
    list_collections,
    delete_collection,
    save_meme_to_collection,
    remove_meme_from_collection,
    list_saved_memes,
    add_recently_viewed,
    add_recently_copied,
    get_favorites_storage_limits,
)

client = TestClient(app)


def test_collections_crud_and_orphaned_migration():
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    # Default collections should include Favorites
    cols = list_collections(user_id=user_id)
    assert len(cols) == 1
    assert cols[0]["name"] == "Favorites"

    # Create custom collection "Work"
    work_col = create_collection(user_id=user_id, name="Work", icon="briefcase")
    assert work_col["name"] == "Work"

    # Save meme to "Work"
    save_res = save_meme_to_collection(
        user_id=user_id,
        meme_id="meme_work_01",
        name="Monday Work Meme",
        thumbnail_url="https://cdn.memegpt.com/thumbs/monday.webp",
        collection="Work",
    )
    assert save_res["status"] == "saved"
    assert save_res["meme"]["collection"] == "Work"

    # Verify counts
    cols_after_save = list_collections(user_id=user_id)
    work_entry = next(c for c in cols_after_save if c["name"] == "Work")
    assert work_entry["memeCount"] == 1

    # Delete "Work" collection -> should migrate meme to "Favorites"
    del_res = delete_collection(user_id=user_id, name="Work")
    assert del_res["deleted_collection"] == "Work"
    assert del_res["memes_migrated_to_favorites"] == 1

    # Verify meme is now in "Favorites"
    fav_memes = list_saved_memes(user_id=user_id, collection="Favorites")
    assert any(m["memeId"] == "meme_work_01" for m in fav_memes)


def test_duplicate_save_updates_timestamp():
    user_id = f"user_dup_{uuid.uuid4().hex[:8]}"

    # First save
    save1 = save_meme_to_collection(user_id=user_id, meme_id="meme_123", name="Original Name", collection="Favorites")
    assert save1["status"] == "saved"

    # Second save of same meme with updated collection
    save2 = save_meme_to_collection(user_id=user_id, meme_id="meme_123", name="Updated Name", collection="Gaming")
    assert save2["status"] == "updated"
    assert save2["meme"]["collection"] == "Gaming"

    # Total saved memes count should still be 1 (no duplicates)
    all_memes = list_saved_memes(user_id=user_id)
    assert len(all_memes) == 1


def test_recently_viewed_and_copied_limits():
    user_id = f"user_rec_{uuid.uuid4().hex[:8]}"

    # Add 25 recently viewed memes (should cap at 20)
    for i in range(25):
        add_recently_viewed(user_id=user_id, meme_id=f"view_{i}", name=f"Viewed {i}")

    # Add 15 recently copied memes (should cap at 10)
    for i in range(15):
        add_recently_copied(user_id=user_id, meme_id=f"copy_{i}", name=f"Copied {i}")

    # Verify endpoint results
    res_view = client.get(f"/api/v1/collections/recent-viewed?session_id={user_id}")
    assert res_view.status_code == 200
    assert len(res_view.json()["recent_viewed"]) == 20

    res_copy = client.get(f"/api/v1/collections/recent-copied?session_id={user_id}")
    assert res_copy.status_code == 200
    assert len(res_copy.json()["recent_copied"]) == 10


def test_collections_api_endpoints():
    session_id = f"sess_api_{uuid.uuid4().hex[:8]}"

    # Create collection via API
    res_create = client.post(f"/api/v1/collections?session_id={session_id}", json={"name": "Gaming", "icon": "gamepad"})
    assert res_create.status_code == 200

    # Save meme via API
    res_save = client.post(f"/api/v1/collections/memes?session_id={session_id}", json={
        "meme_id": "meme_game_01",
        "name": "Gaming Meme",
        "collection": "Gaming"
    })
    assert res_save.status_code == 200

    # Get limits
    res_limits = client.get("/api/v1/collections/storage-limits")
    assert res_limits.status_code == 200
    assert res_limits.json()["limits"]["anonymous_capacity"] == 200
