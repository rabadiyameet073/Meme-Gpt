#!/usr/bin/env python3
"""
MemeGPT — Environment Setup Verification Script.
Specification: 01_Environment_Setup.md (Step 4)

Checks all required environment variables and service credentials.
Run: python scripts/verify_env.py
"""

import io
import os
import sys
from pathlib import Path

# Ensure UTF-8 output across all platforms/consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings


def verify_environment() -> bool:
    print("=" * 64)
    print("MemeGPT - Environment Configuration Status")
    print("Specification: 01_Environment_Setup.md")
    print("=" * 64)

    # 1. Step 4 Essential Checklist
    print("\n--- Step 4 Verification Checklist ---")
    essential_checks = [
        ("GROQ", bool(settings.GROQ_API_KEY)),
        ("QDRANT URL", bool(settings.QDRANT_URL)),
        ("QDRANT KEY", bool(settings.QDRANT_API_KEY)),
        ("REDIS", bool(settings.REDIS_URL or settings.UPSTASH_REDIS_REST_URL)),
        ("SECRET", bool(settings.SECRET_KEY and settings.SECRET_KEY != "changeme")),
        ("R2", bool(settings.R2_ACCESS_KEY)),
        ("GIPHY", bool(settings.GIPHY_API_KEY)),
    ]

    for label, is_set in essential_checks:
        status = "SET" if is_set else "MISSING (using local fallback)"
        print(f"  {label:<12}: {status}")

    # 2. Detailed Service Overview
    print("\n--- Detailed Service Status ---")
    detailed_checks = [
        ("GROQ API KEY", bool(settings.GROQ_API_KEY), f"Model: {settings.GROQ_MODEL} (timeout {settings.GROQ_TIMEOUT}s)"),
        ("QDRANT URL", bool(settings.QDRANT_URL), f"Collection: {settings.QDRANT_COLLECTION}"),
        ("QDRANT API KEY", bool(settings.QDRANT_API_KEY), "Vector Search Auth Token"),
        ("REDIS URL", bool(settings.REDIS_URL or settings.UPSTASH_REDIS_REST_URL), f"TTL: {settings.REDIS_CACHE_TTL}s"),
        ("SECRET KEY", bool(settings.SECRET_KEY and len(settings.SECRET_KEY) >= 32), f"Algorithm: {settings.JWT_ALGORITHM}"),
        ("R2 MEDIA CDN", bool(settings.R2_ACCESS_KEY and settings.R2_SECRET_KEY), f"Bucket: {settings.R2_BUCKET}, CDN: {settings.CDN_BASE_URL}"),
        ("GIPHY API KEY", bool(settings.GIPHY_API_KEY), "Live GIF Integrations"),
        ("SENTRY DSN", bool(settings.SENTRY_DSN), "Error Tracking & APM"),
    ]

    for name, is_set, description in detailed_checks:
        status = "[SET]" if is_set else "[OPTIONAL / FALLBACK]"
        print(f"  {name:<16}: {status:<24} ({description})")

    # 3. Application Metadata
    print("\n" + "-" * 64)
    print(f"  App Name:          {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"  Environment:       {settings.APP_ENV} (debug={settings.DEBUG})")
    print(f"  Database URL:      {settings.DATABASE_URL}")
    print(f"  Embedding Model:   {settings.EMBEDDING_MODEL} ({settings.EMBEDDING_DIM}d)")
    print(f"  Emotion Model:     {settings.EMOTION_MODEL}")
    print(f"  Rate Limit Pro:    {settings.RATE_LIMIT_PRO} req/min")
    print("=" * 64)

    is_valid = True
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32 or settings.SECRET_KEY == "changeme":
        print("[FAIL] SECRET_KEY must be a cryptographically secure hex key of >= 32 chars.")
        is_valid = False
    else:
        print("[OK] Core security secret key is configured and valid.")

    return is_valid


if __name__ == "__main__":
    success = verify_environment()
    sys.exit(0 if success else 1)
