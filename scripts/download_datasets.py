"""
MemeGPT — Dataset Ingestion Script
Matches specifications from 05_AI_System/AI_Pipeline.md
"""

import os
import json
import requests
from pathlib import Path

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_imgflip() -> list[dict]:
    """Free API — returns top 100 popular meme templates."""
    url = "https://api.imgflip.com/get_memes"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if not data.get("success"):
            print("⚠️ Imgflip API responded with non-success")
            return []
        memes = data["data"]["memes"]
        results = []
        for meme in memes:
            results.append({
                "id": f"imgflip_{meme['id']}",
                "name": meme["name"],
                "source": "imgflip",
                "image_url": meme["url"],
                "width": meme.get("width"),
                "height": meme.get("height"),
            })
        print(f"✓ Retrieved {len(results)} Imgflip templates")
        return results
    except Exception as e:
        print(f"⚠️ Error downloading Imgflip templates: {e}")
        return []


def download_reddit_dataset() -> list[dict]:
    """Loads Reddit meme dataset if datasets library is available."""
    try:
        from datasets import load_dataset
        dataset = load_dataset("headsmanjaeger/reddit-meme-dataset", split="train")
        results = []
        for item in dataset:
            results.append({
                "id": f"reddit_{item['id']}",
                "name": item.get("title", ""),
                "source": "reddit",
                "source_id": str(item.get("id")),
                "license": "fair_use",
                "image_url": item.get("url", ""),
                "score": item.get("score", 0),
            })
        print(f"✓ Loaded {len(results)} Reddit memes")
        return results
    except Exception as e:
        print(f"ℹ️ HuggingFace datasets library not configured or remote unavailable: {e}")
        return []


def download_giphy(limit: int = 50) -> list[dict]:
    """Retrieves trending memes/gifs from Giphy API."""
    api_key = os.getenv("GIPHY_API_KEY")
    if not api_key:
        print("ℹ️ GIPHY_API_KEY not configured — skipping Giphy download")
        return []
    url = "https://api.giphy.com/v1/gifs/trending"
    try:
        resp = requests.get(url, params={"api_key": api_key, "limit": limit, "rating": "pg-13"}, timeout=10)
        if resp.status_code != 200:
            print(f"⚠️ Giphy API responded with status {resp.status_code}")
            return []
        data = resp.json()
        results = []
        for g in data.get("data", []):
            results.append({
                "id": f"giphy_{g['id']}",
                "name": g.get("title") or "Giphy Meme",
                "source": "giphy",
                "source_id": g["id"],
                "license": "fair_use",
                "image_url": g.get("images", {}).get("original", {}).get("url"),
                "gif_url": g.get("images", {}).get("original", {}).get("url"),
                "mp4_url": g.get("images", {}).get("original_mp4", {}).get("mp4"),
            })
        print(f"✓ Retrieved {len(results)} Giphy memes")
        return results
    except Exception as e:
        print(f"⚠️ Error downloading Giphy memes: {e}")
        return []


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download meme datasets for MemeGPT")
    parser.add_argument("--source", choices=["imgflip", "reddit", "giphy", "all"], default="all")
    args = parser.parse_args()

    results = []
    if args.source in ["imgflip", "all"]:
        results.extend(download_imgflip())
    if args.source in ["reddit", "all"]:
        results.extend(download_reddit_dataset())
    if args.source in ["giphy", "all"]:
        results.extend(download_giphy())

    out_file = OUTPUT_DIR / "dataset_manifest.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"✓ Saved manifest with {len(results)} memes to {out_file}")


if __name__ == "__main__":
    main()
