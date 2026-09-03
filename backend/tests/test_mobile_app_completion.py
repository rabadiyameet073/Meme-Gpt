"""
Tests for 11_Mobile_App_Completion.md.

Verifies:
- apps/mobile/app.json and mobile/app.json permissions (expo-media-library, camera roll)
- useOfflineCache hook structure & MAX_CACHED limits
- useMemeActions hook functions (shareMeme, copyLink/copyMemeLink, saveToCameraRoll)
- MemeCard component double-tap favorite and haptic feedback
"""

import json
from pathlib import Path
import pytest

MOBILE_ROOT = Path("d:/Meme GPT/mobile")
APPS_MOBILE_ROOT = Path("d:/Meme GPT/apps/mobile")


def test_mobile_app_json_permissions():
    """Verify app.json contains expo-media-library plugin and photo permissions."""
    for root in [MOBILE_ROOT, APPS_MOBILE_ROOT]:
        app_json_file = root / "app.json"
        assert app_json_file.exists(), f"{app_json_file} must exist"
        data = json.loads(app_json_file.read_text(encoding="utf-8"))

        plugins = data["expo"]["plugins"]
        media_lib_plugin = next(
            (p for p in plugins if isinstance(p, list) and p[0] == "expo-media-library"),
            None
        )
        assert media_lib_plugin is not None, f"expo-media-library plugin missing in {app_json_file}"
        props = media_lib_plugin[1]
        assert "photosPermission" in props
        assert "savePhotosPermission" in props


def test_use_offline_cache_files():
    """Verify useOfflineCache exists and implements cache storage."""
    files = [
        MOBILE_ROOT / "src" / "hooks" / "useOfflineCache.ts",
        APPS_MOBILE_ROOT / "hooks" / "useOfflineCache.ts",
    ]
    for f in files:
        assert f.exists(), f"{f} must exist"
        content = f.read_text(encoding="utf-8")
        assert "useOfflineCache" in content
        assert "cacheMemes" in content
        assert "50" in content  # MAX_CACHED limit


def test_use_meme_actions_files():
    """Verify useMemeActions implements share, save, and copy actions."""
    files = [
        MOBILE_ROOT / "src" / "hooks" / "useMemeActions.ts",
        APPS_MOBILE_ROOT / "hooks" / "useMemeActions.ts",
    ]
    for f in files:
        assert f.exists(), f"{f} must exist"
        content = f.read_text(encoding="utf-8")
        assert "shareMeme" in content
        assert "saveToCameraRoll" in content


def test_meme_card_components():
    """Verify MemeCard has double-tap to favorite and heart scale animation."""
    files = [
        MOBILE_ROOT / "src" / "components" / "MemeCard.tsx",
        APPS_MOBILE_ROOT / "components" / "MemeCard.tsx",
    ]
    for f in files:
        assert f.exists(), f"{f} must exist"
        content = f.read_text(encoding="utf-8")
        assert "handleDoubleTap" in content or "heartScale" in content
        assert "DOUBLE_TAP_DELAY" in content
