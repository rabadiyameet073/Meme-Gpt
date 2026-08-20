"""Favorites & Collections Service for MemeGPT.
Specification: 08_Features/Favorites_Collections.md
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memegpt.services.favorites")

ANONYMOUS_STORAGE_CAPACITY = 200
MAX_RECENT_VIEWED = 20
MAX_RECENT_COPIED = 10

# In-memory store per user/session
# Structure: {
#   user_id: {
#       "collections": [{"name": "Favorites", "createdAt": "...", "icon": "star", "is_default": True}],
#       "saved_memes": [{"memeId": "...", "name": "...", "thumbnailUrl": "...", "savedAt": "...", "collection": "Favorites"}],
#       "recent_viewed": [{"memeId": "...", "name": "...", "thumbnailUrl": "...", "viewedAt": "..."}],
#       "recent_copied": [{"memeId": "...", "name": "...", "thumbnailUrl": "...", "copiedAt": "..."}],
#   }
# }
_USER_STORAGE: Dict[str, Dict[str, Any]] = {}


def _get_or_create_user_store(user_id: str) -> Dict[str, Any]:
    if user_id not in _USER_STORAGE:
        _USER_STORAGE[user_id] = {
            "collections": [
                {
                    "name": "Favorites",
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "icon": "star",
                    "is_default": True,
                }
            ],
            "saved_memes": [],
            "recent_viewed": [],
            "recent_copied": [],
        }
    return _USER_STORAGE[user_id]


def get_favorites_storage_limits() -> Dict[str, Any]:
    """Return storage quota and capacity limits."""
    return {
        "anonymous_capacity": ANONYMOUS_STORAGE_CAPACITY,
        "max_recent_viewed": MAX_RECENT_VIEWED,
        "max_recent_copied": MAX_RECENT_COPIED,
        "storage_backends": {
            "anonymous": {"type": "localStorage", "sync": "Device-only", "capacity": ANONYMOUS_STORAGE_CAPACITY},
            "registered": {"type": "Supabase / Database", "sync": "Cross-device", "capacity": "unlimited"},
        }
    }


def list_collections(user_id: str = "anonymous") -> List[Dict[str, Any]]:
    """List collections with live meme counts."""
    store = _get_or_create_user_store(user_id)
    collections = store["collections"]
    memes = store["saved_memes"]

    result = []
    for col in collections:
        count = sum(1 for m in memes if m.get("collection", "Favorites") == col["name"])
        result.append({
            "name": col["name"],
            "createdAt": col["createdAt"],
            "icon": col.get("icon", "folder"),
            "memeCount": count,
            "isDefault": col.get("is_default", False),
        })
    return result


def create_collection(user_id: str = "anonymous", name: str = "My Collection", icon: str = "folder") -> Dict[str, Any]:
    """Create a new custom collection."""
    name = name.strip()
    if not name:
        raise ValueError("Collection name cannot be empty")
    store = _get_or_create_user_store(user_id)
    for col in store["collections"]:
        if col["name"].lower() == name.lower():
            raise ValueError(f"Collection '{name}' already exists")

    new_col = {
        "name": name,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "icon": icon,
        "is_default": False,
    }
    store["collections"].append(new_col)
    return {**new_col, "memeCount": 0}


def delete_collection(user_id: str = "anonymous", name: str = "") -> Dict[str, Any]:
    """Delete a custom collection. Orphaned memes are moved to 'Favorites'."""
    name = name.strip()
    if name.lower() == "favorites":
        raise ValueError("Cannot delete default 'Favorites' collection")

    store = _get_or_create_user_store(user_id)
    initial_count = len(store["collections"])
    store["collections"] = [c for c in store["collections"] if c["name"].lower() != name.lower()]

    if len(store["collections"]) == initial_count:
        raise ValueError(f"Collection '{name}' not found")

    # Move memes to default "Favorites" collection
    moved_count = 0
    for m in store["saved_memes"]:
        if m.get("collection", "").lower() == name.lower():
            m["collection"] = "Favorites"
            moved_count += 1

    return {
        "deleted_collection": name,
        "memes_migrated_to_favorites": moved_count,
    }


def save_meme_to_collection(
    user_id: str = "anonymous",
    meme_id: str = "",
    name: str = "",
    thumbnail_url: str = "",
    collection: str = "Favorites",
) -> Dict[str, Any]:
    """Save a meme to a collection. If already present, updates timestamp and collection without duplicating."""
    store = _get_or_create_user_store(user_id)
    saved_list = store["saved_memes"]
    now_iso = datetime.now(timezone.utc).isoformat()

    # Check for existing meme
    for item in saved_list:
        if item["memeId"] == meme_id:
            item["savedAt"] = now_iso
            item["collection"] = collection or "Favorites"
            item["name"] = name or item["name"]
            item["thumbnailUrl"] = thumbnail_url or item["thumbnailUrl"]
            return {"status": "updated", "meme": item}

    # If storage capacity exceeded, trim oldest
    if len(saved_list) >= ANONYMOUS_STORAGE_CAPACITY:
        saved_list.pop(0)

    new_saved = {
        "memeId": meme_id,
        "name": name,
        "thumbnailUrl": thumbnail_url,
        "savedAt": now_iso,
        "collection": collection or "Favorites",
    }
    saved_list.append(new_saved)
    return {"status": "saved", "meme": new_saved}


def remove_meme_from_collection(
    user_id: str = "anonymous",
    meme_id: str = "",
    collection: Optional[str] = None,
) -> bool:
    """Remove a meme from saved favorites or a specific collection."""
    store = _get_or_create_user_store(user_id)
    initial_len = len(store["saved_memes"])
    if collection:
        store["saved_memes"] = [
            m for m in store["saved_memes"]
            if not (m["memeId"] == meme_id and m.get("collection", "Favorites").lower() == collection.lower())
        ]
    else:
        store["saved_memes"] = [m for m in store["saved_memes"] if m["memeId"] != meme_id]

    return len(store["saved_memes"]) < initial_len


def list_saved_memes(
    user_id: str = "anonymous",
    collection: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List saved memes, optionally filtered by collection name."""
    store = _get_or_create_user_store(user_id)
    memes = store["saved_memes"]
    if collection:
        return [m for m in memes if m.get("collection", "Favorites").lower() == collection.lower()]
    return memes


def add_recently_viewed(
    user_id: str = "anonymous",
    meme_id: str = "",
    name: str = "",
    thumbnail_url: str = "",
) -> List[Dict[str, Any]]:
    """Record a viewed meme (capped at 20)."""
    store = _get_or_create_user_store(user_id)
    recents = store["recent_viewed"]
    now_iso = datetime.now(timezone.utc).isoformat()

    # Remove existing instance to move to front
    store["recent_viewed"] = [r for r in recents if r["memeId"] != meme_id]
    store["recent_viewed"].insert(0, {
        "memeId": meme_id,
        "name": name,
        "thumbnailUrl": thumbnail_url,
        "viewedAt": now_iso,
    })
    # Trim to 20
    if len(store["recent_viewed"]) > MAX_RECENT_VIEWED:
        store["recent_viewed"] = store["recent_viewed"][:MAX_RECENT_VIEWED]

    return store["recent_viewed"]


def add_recently_copied(
    user_id: str = "anonymous",
    meme_id: str = "",
    name: str = "",
    thumbnail_url: str = "",
) -> List[Dict[str, Any]]:
    """Record a copied meme (capped at 10)."""
    store = _get_or_create_user_store(user_id)
    recents = store["recent_copied"]
    now_iso = datetime.now(timezone.utc).isoformat()

    store["recent_copied"] = [r for r in recents if r["memeId"] != meme_id]
    store["recent_copied"].insert(0, {
        "memeId": meme_id,
        "name": name,
        "thumbnailUrl": thumbnail_url,
        "copiedAt": now_iso,
    })
    # Trim to 10
    if len(store["recent_copied"]) > MAX_RECENT_COPIED:
        store["recent_copied"] = store["recent_copied"][:MAX_RECENT_COPIED]

    return store["recent_copied"]


def get_recently_viewed(user_id: str = "anonymous") -> List[Dict[str, Any]]:
    """Get list of recently viewed memes."""
    store = _get_or_create_user_store(user_id)
    return store.get("recent_viewed", [])


def get_recently_copied(user_id: str = "anonymous") -> List[Dict[str, Any]]:
    """Get list of recently copied memes."""
    store = _get_or_create_user_store(user_id)
    return store.get("recent_copied", [])
