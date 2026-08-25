#!/usr/bin/env python3
"""
MemeGPT — Qdrant Indexer Script.

CLI script for indexing database memes into Qdrant cloud vector database.
Can be scheduled via Windows Task Scheduler or cron.

Usage:
    python scripts/index_to_qdrant.py [--limit 500] [--recreate] [--skip-images]
"""

import argparse
import logging
import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from generate_embeddings import index_memes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("index_to_qdrant")


def main():
    parser = argparse.ArgumentParser(description="Index memes from SQLite database into Qdrant Vector DB")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of newest memes to index")
    parser.add_argument("--recreate", action="store_true", help="Recreate Qdrant collection from scratch")
    parser.add_argument("--skip-images", action="store_true", help="Skip image download, CLIP, and BLIP processing")
    args = parser.parse_args()

    logger.info("Starting Qdrant indexing task...")
    index_memes(
        limit=args.limit,
        recreate=args.recreate,
        skip_images=args.skip_images,
    )
    logger.info("Qdrant indexing task finished.")


if __name__ == "__main__":
    main()
