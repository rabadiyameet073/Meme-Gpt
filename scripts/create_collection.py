#!/usr/bin/env python3
"""
MemeGPT — Recreate Qdrant Vector Collection Script
Specification: 06_Database/Recovery.md & 05_AI_System/Vector_Database.md
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.search_service import create_qdrant_collection


def main():
    print("\n=== Recreating Qdrant Collection 'memes' ===")
    res = create_qdrant_collection()
    print(f"Status: {res.get('status')}")
    print(f"Collection: {res.get('collection')}")
    print(f"Vector Spaces: {list(res.get('vector_spaces', {}).keys())}")
    print("✓ Collection successfully created / ready.")


if __name__ == "__main__":
    main()
