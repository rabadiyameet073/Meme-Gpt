"""
Step 1 of ML Pipeline — Download meme datasets from free sources.
Sources: Imgflip API (top 100 templates), HuggingFace Reddit dataset, Tenor GIF API.
Run once to build initial dataset.

Usage:
  python scripts/download_datasets.py
  python scripts/download_datasets.py --source imgflip   # fast start (30 memes)
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Source 1: Imgflip Top 100 Templates ──────────────────────────────────────

def download_imgflip() -> list:
    """Free API — no key needed. Returns top 100 popular meme templates."""
    print("Downloading Imgflip top templates...")
    url = "https://api.imgflip.com/get_memes"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        memes_data = response.json()["data"]["memes"]
    except Exception as e:
        print(f"  ✗ Imgflip API error: {e}")
        return []

    results = []
    img_dir = OUTPUT_DIR / "images"
    img_dir.mkdir(exist_ok=True)

    for meme in memes_data:
        img_path = img_dir / f"{meme['id']}.jpg"
        if not img_path.exists():
            try:
                r = requests.get(meme["url"], timeout=10)
                img_path.write_bytes(r.content)
            except Exception:
                pass

        slug = meme["name"].lower().replace(" ", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

        results.append({
            "id": f"imgflip_{meme['id']}",
            "name": meme["name"],
            "slug": slug,
            "source": "imgflip",
            "image_path": str(img_path),
            "image_url": meme["url"],
            "box_count": meme.get("box_count", 0),
        })

    print(f"  ✓ Downloaded {len(results)} Imgflip templates")
    return results


# ── Source 2: HuggingFace Reddit Dataset ─────────────────────────────────────

def download_reddit_dataset() -> list:
    """6500+ memes with Reddit metadata — requires `pip install datasets`."""
    print("Downloading Reddit meme dataset from HuggingFace...")
    try:
        from datasets import load_dataset
        dataset = load_dataset("headsmanjaeger/reddit-meme-dataset", split="train")
        results = []
        for item in dataset:
            results.append({
                "id": f"reddit_{item['id']}",
                "name": item.get("title", "Reddit Meme")[:100],
                "slug": str(item['id']).lower().replace(" ", "-"),
                "source": "reddit",
                "image_url": item.get("url", ""),
                "subreddit": item.get("subreddit", ""),
                "score": item.get("score", 0),
            })
        print(f"  ✓ Loaded {len(results)} Reddit memes")
        return results
    except Exception as e:
        print(f"  ✗ Reddit dataset error: {e} — skipping (run: pip install datasets)")
        return []


# ── Source 3: Tenor GIF API ───────────────────────────────────────────────────

def download_tenor_gifs(api_key: str, categories: list | None = None) -> list:
    """Animated GIFs for popular meme categories."""
    if not api_key:
        print("  ✗ TENOR_API_KEY not set — skipping Tenor")
        return []

    cats = categories or [
        "funny", "reaction", "coding meme", "monday meme",
        "programming humor", "work meme", "success", "fail"
    ]
    results = []
    print(f"Downloading Tenor GIFs for {len(cats)} categories...")

    for category in cats:
        try:
            url = "https://tenor.googleapis.com/v2/search"
            params = {"q": f"{category}", "key": api_key, "limit": 20, "media_filter": "gif"}
            resp = requests.get(url, params=params, timeout=10)
            for item in resp.json().get("results", []):
                gif_url = item["media_formats"].get("gif", {}).get("url", "")
                if gif_url:
                    slug = item.get("title", category).lower().replace(" ", "-")[:50]
                    results.append({
                        "id": f"tenor_{item['id']}",
                        "name": item.get("title") or category,
                        "slug": slug,
                        "source": "tenor",
                        "gif_url": gif_url,
                        "category": category,
                    })
        except Exception as e:
            print(f"  ✗ Tenor error for '{category}': {e}")

    print(f"  ✓ Downloaded {len(results)} Tenor GIFs")
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Download MemeGPT datasets")
    parser.add_argument("--source", choices=["all", "imgflip", "reddit", "tenor"], default="all")
    args = parser.parse_args()

    all_memes = []

    if args.source in ("all", "imgflip"):
        all_memes.extend(download_imgflip())

    if args.source in ("all", "reddit"):
        all_memes.extend(download_reddit_dataset())

    if args.source in ("all", "tenor"):
        tenor_key = os.getenv("TENOR_API_KEY", "")
        all_memes.extend(download_tenor_gifs(tenor_key))

    # Save master list
    out_path = OUTPUT_DIR / "memes_master.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_memes, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Total memes collected: {len(all_memes)}")
    print(f"   Saved to: {out_path}")


if __name__ == "__main__":
    main()
