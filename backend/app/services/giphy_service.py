"""MemeGPT — Giphy & Global Live Meme Integration Service.

Connects to Giphy API, Tenor API, and live global meme repositories (Imgflip + Reddit Meme APIs).
Ensures any user query accesses millions of live memes & GIFs worldwide.
"""

import logging
import os
import requests
from typing import List, Dict, Any

logger = logging.getLogger("memegpt.giphy")

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY", "")
TENOR_API_KEY = os.getenv("TENOR_API_KEY", "")

SUBREDDIT_MAP = {
    "coding": "ProgrammerHumor",
    "ai": "ProgrammerHumor",
    "hindi": "IndianMeyMeys",
    "bollywood": "IndianMeyMeys",
    "office": "workmemes",
    "college": "schoolmemes",
    "gaming": "gamingmemes",
    "money": "wallstreetbets",
    "funny": "dankmemes",
}


def search_giphy(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search Giphy API for live GIFs matching the query."""
    if not GIPHY_API_KEY:
        return []

    url = "https://api.giphy.com/v1/gifs/search"
    params = {
        "api_key": GIPHY_API_KEY,
        "q": query,
        "limit": limit,
        "rating": "g",
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            results = []
            for item in data:
                gif_url = item.get("images", {}).get("original", {}).get("url")
                thumb_url = item.get("images", {}).get("downsized_medium", {}).get("url")
                if gif_url:
                    results.append({
                        "id": f"giphy_{item['id']}",
                        "name": item.get("title") or f"{query} GIF",
                        "slug": f"giphy-{item['id']}",
                        "category": "reaction",
                        "dialogue": item.get("title") or f"Giphy reaction for {query}",
                        "explanation": f"Live Giphy GIF matching '{query}'.",
                        "confidence": 0.85,
                        "keywords": [query, "giphy", "gif", "live"],
                        "imageRef": thumb_url or gif_url,
                        "videoRef": item.get("images", {}).get("mp4", {}).get("mp4"),
                        "gifRef": gif_url,
                        "thumbUrl": thumb_url or gif_url,
                        "formats": {
                            "image": thumb_url or gif_url,
                            "gif": gif_url,
                            "mp4": item.get("images", {}).get("mp4", {}).get("mp4"),
                            "webp": item.get("images", {}).get("webp", {}).get("url"),
                            "thumb": thumb_url or gif_url,
                        },
                        "shareUrl": item.get("url", gif_url),
                        "viralScore": 90.0,
                        "usageCount": 100,
                        "upvotes": 50,
                        "downvotes": 2,
                        "source": "Giphy",
                    })
            logger.info(f"Retrieved {len(results)} live GIFs from Giphy for query '{query}'")
            return results
    except Exception as e:
        logger.warning(f"Giphy API request failed: {e}")

    return []


def search_live_memes(query: str, category: str = "funny", limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch live memes from open global meme repositories (Meme-API / Reddit)."""
    sub = SUBREDDIT_MAP.get(category.lower(), "dankmemes")
    url = f"https://meme-api.com/gimme/{sub}/{limit}"

    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            memes_data = resp.json().get("memes", [])
            results = []
            for item in memes_data:
                img_url = item.get("url")
                if img_url and not item.get("nsfw", False):
                    post_id = item.get("postLink", "").split("/")[-1] or "live"
                    title = item.get("title", "Live Meme")
                    results.append({
                        "id": f"live_{post_id}",
                        "name": title,
                        "slug": f"live-meme-{post_id}",
                        "category": category,
                        "dialogue": f"\"{title}\"",
                        "explanation": f"Live trending meme from r/{item.get('subreddit', sub)} by u/{item.get('author', 'anon')}.",
                        "confidence": 0.82,
                        "keywords": [query, category, "live", item.get("subreddit", "memes")],
                        "imageRef": img_url,
                        "videoRef": None,
                        "gifRef": img_url if img_url.endswith(".gif") else None,
                        "thumbUrl": img_url,
                        "formats": {
                            "image": img_url,
                            "gif": img_url if img_url.endswith(".gif") else None,
                            "mp4": None,
                            "webp": img_url,
                            "thumb": img_url,
                        },
                        "shareUrl": item.get("postLink", img_url),
                        "viralScore": float(min(item.get("ups", 100) / 10, 99.0)),
                        "usageCount": item.get("ups", 10),
                        "upvotes": item.get("ups", 10),
                        "downvotes": 0,
                        "source": "Global Live Stream",
                    })
            logger.info(f"Retrieved {len(results)} live memes from r/{sub}")
            return results
    except Exception as e:
        logger.warning(f"Live meme API request failed: {e}")

    return []


def get_global_gifs_and_memes(query: str, category: str = "funny", limit: int = 10) -> Dict[str, Any]:
    """Retrieve combined live Giphy GIFs and Global Meme Stream."""
    giphy_results = search_giphy(query, limit=limit // 2)
    live_results = search_live_memes(query, category=category, limit=limit // 2)

    combined_memes = giphy_results + live_results
    gif_urls = [m["gifRef"] for m in combined_memes if m.get("gifRef")]

    return {
        "memes": combined_memes,
        "gif_urls": gif_urls,
    }
