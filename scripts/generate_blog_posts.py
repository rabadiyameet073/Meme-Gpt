"""
Generate SEO Blog Posts for MemeGPT Web App.
Uses database memes, trending metrics, and semantic tags to produce automated blog articles.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Setup UTF-8 output for Windows console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "memegpt.db"
if not DB_PATH.exists():
    alt_db = ROOT_DIR / "backend" / "memegpt.db"
    if alt_db.exists():
        DB_PATH = alt_db
OUTPUT_DIR = ROOT_DIR / "apps" / "web" / "content" / "blog"


def get_top_memes(limit: int = 10):
    if not DB_PATH.exists():
        print(f"Warning: Database {DB_PATH} not found.")
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT name, slug, categories, dialogue, explanation, viral_score, upvotes
            FROM memes
            WHERE moderation_status = 'approved' OR moderation_status IS NULL
            ORDER BY viral_score DESC, upvotes DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        return rows
    except Exception as e:
        print(f"Error querying top memes: {e}")
        return []
    finally:
        conn.close()


def generate_article(memes):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.utcnow().strftime("%B %d, %Y")
    slug_date = datetime.utcnow().strftime("%Y-%m-%d")

    post_slug = f"top-trending-memes-{slug_date}"
    post_file = OUTPUT_DIR / f"{post_slug}.md"

    content = [
        "---",
        f'title: "Top 10 Trending Memes in {datetime.utcnow().strftime("%B %Y")}: Why They\'re Viral"',
        f'slug: "{post_slug}"',
        f'date: "{today}"',
        'readTime: "6 min read"',
        'category: "Meme Culture"',
        'emoji: "🔥"',
        f'excerpt: "From relatable workplace struggles to classic reaction formats, explore the top viral memes discovered by MemeGPT\'s AI vector search."',
        "---",
        "",
        f"# Top Trending Memes in {datetime.utcnow().strftime('%B %Y')}",
        "",
        "Every month, internet culture shifts with lightning speed. Using **MemeGPT's** multi-modal neural search "
        "and emotion detection pipeline, we analyzed thousands of user queries and meme interactions to surface "
        "the most culturally resonant memes right now.",
        "",
        "---",
        "",
    ]

    for i, meme in enumerate(memes, 1):
        name = meme.get("name", "Unknown Meme")
        slug = meme.get("slug", "")
        raw_cats = meme.get("categories") or "general"
        if isinstance(raw_cats, str) and raw_cats.startswith("["):
            try:
                raw_cats = ", ".join(json.loads(raw_cats))
            except Exception:
                pass
        elif isinstance(raw_cats, list):
            raw_cats = ", ".join(raw_cats)
        category = str(raw_cats).replace("_", " ").title()
        dialogue = meme.get("dialogue") or ""
        explanation = meme.get("explanation") or ""
        viral = meme.get("viral_score", 0)

        content.append(f"### {i}. [{name}](https://memegpt.com/meme/{slug})")
        content.append(f"- **Category:** `{category}`")
        content.append(f"- **Viral Score:** `{viral}`")
        if dialogue:
            content.append(f"- **Classic Line:** *\"{dialogue}\"*")
        content.append("")
        content.append(f"{explanation}")
        content.append("")
        content.append(f"[👉 Search or download {name} on MemeGPT](https://memegpt.com/meme/{slug})")
        content.append("")
        content.append("---")
        content.append("")

    content.append("## How MemeGPT Matches These Memes")
    content.append(
        "MemeGPT uses a 5-stage AI pipeline: Groq LLM parses context and subtext, DistilRoBERTa extracts emotional tone, "
        "and MiniLM generates dense 384-dimensional embeddings queried against our Qdrant vector database."
    )
    content.append("")
    content.append("[Try MemeGPT AI Matcher Now →](https://app.memegpt.com)")

    post_file.write_text("\n".join(content), encoding="utf-8")
    print(f"[OK] Generated blog post: {post_file}")


def main():
    print("[*] Generating SEO blog posts from database...")
    top_memes = get_top_memes(10)
    if not top_memes:
        print("[!] No memes found in DB, using fallback template data.")
        top_memes = [
            {
                "name": "Distracted Boyfriend",
                "slug": "distracted-boyfriend",
                "category": "reaction",
                "dialogue": "Looking away at something new",
                "explanation": "The ultimate betrayal meme template representing wandering attention and shiny new options.",
                "viral_score": 98,
            }
        ]
    generate_article(top_memes)


if __name__ == "__main__":
    main()
