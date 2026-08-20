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
                "image_url": item.get("url", ""),
                "score": item.get("score", 0),
            })
        print(f"✓ Loaded {len(results)} Reddit memes")
        return results
    except Exception as e:
        print(f"ℹ️ HuggingFace datasets library not configured or remote unavailable: {e}")
        return []


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download meme datasets for MemeGPT")
    parser.add_argument("--source", choices=["imgflip", "reddit", "all"], default="imgflip")
    args = parser.parse_args()

    results = []
    if args.source in ["imgflip", "all"]:
        results.extend(download_imgflip())
    if args.source in ["reddit", "all"]:
        results.extend(download_reddit_dataset())

    out_file = OUTPUT_DIR / "dataset_manifest.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"✓ Saved manifest with {len(results)} memes to {out_file}")


if __name__ == "__main__":
    main()
