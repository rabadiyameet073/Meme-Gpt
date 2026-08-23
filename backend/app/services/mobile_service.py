"""Mobile Application Specifications and Offline Sync Service for MemeGPT.
Specification: 15_Mobile/Mobile_Overview.md

Covers:
- Mobile Tech Stack (React Native 0.74, Expo SDK 51, Expo Router 3.x, EAS Build, Hermes)
- 4 Core Screen Architecture & Native API Modules (Sharing, Media Library, Haptics, Clipboard)
- Platform Differences Matrix (iOS vs Android OS, permissions, push notifications, binaries)
- Build & Release Pipelines (Expo CLI, EAS Build & Submit)
- App Size Budget Breakdown (~29MB total target)
- Mobile-Specific Features Catalog with Priority (P0, P1, P2)
- Offline Cache Sync Simulator (last 50 memes via AsyncStorage/MMKV)
- Mobile App Readiness Evaluator
"""

from typing import Any, Dict, List, Optional


# ── 1. Tech Stack ─────────────────────────────────────────────────────────────

MOBILE_TECH_STACK = [
    {"technology": "React Native", "version": "0.74", "purpose": "Cross-platform UI framework"},
    {"technology": "Expo", "version": "SDK 51", "purpose": "Build toolchain + native APIs"},
    {"technology": "Expo Router", "version": "3.x", "purpose": "File-based routing & tab navigation"},
    {"technology": "EAS Build", "version": "Latest", "purpose": "Cloud builds for iOS (IPA) and Android (AAB/APK)"},
    {"technology": "Hermes", "version": "Engine", "purpose": "Optimized JavaScript engine for fast cold-start"},
]


# ── 2. Screen Architecture & Native APIs ──────────────────────────────────────

MOBILE_SCREENS = [
    {"screen": "SearchScreen", "route": "/(tabs)/index", "purpose": "Main AI search UI with natural language prompt bar"},
    {"screen": "TrendingScreen", "route": "/(tabs)/trending", "purpose": "Trending & viral meme feed with pull-to-refresh"},
    {"screen": "LibraryScreen", "route": "/(tabs)/library", "purpose": "Saved memes and offline cache collection"},
    {"screen": "SettingsScreen", "route": "/(tabs)/settings", "purpose": "User preferences, theme, safe search, and cache cleaner"},
]

NATIVE_APIS = [
    {"feature": "Share Sheet", "module": "expo-sharing", "purpose": "Native iOS UIActivityViewController and Android Intent.ACTION_SEND"},
    {"feature": "Camera Roll", "module": "expo-media-library", "purpose": "Save downloaded memes directly to user photo gallery"},
    {"feature": "Haptics", "module": "expo-haptics", "purpose": "Tactile feedback on meme copy, favorite, and action triggers"},
    {"feature": "Clipboard", "module": "expo-clipboard", "purpose": "Instant copy of meme image binary and direct share link"},
]


# ── 3. Platform Differences Matrix ────────────────────────────────────────────

PLATFORM_DIFFERENCES = [
    {
        "feature": "Share sheet",
        "ios": "Native UIActivityViewController",
        "android": "Native Intent.ACTION_SEND",
    },
    {
        "feature": "Save to camera roll",
        "ios": "Photos permission (NSPhotoLibraryAddUsageDescription)",
        "android": "Storage permission (WRITE_EXTERNAL_STORAGE on <=API 28)",
    },
    {
        "feature": "Haptic feedback",
        "ios": "Taptic Engine (UIImpactFeedbackGenerator)",
        "android": "Vibration API (Vibrator / VibrationEffect)",
    },
    {
        "feature": "Push notifications",
        "ios": "Apple Push Notification service (APNs)",
        "android": "Firebase Cloud Messaging (FCM)",
    },
    {
        "feature": "App binary size",
        "ios": "~35MB (Hermes optimized)",
        "android": "~29MB (Hermes optimized)",
    },
    {
        "feature": "Minimum supported OS",
        "ios": "iOS 15+",
        "android": "Android 10+ (API level 29)",
    },
]


# ── 4. Build & Release Pipelines ──────────────────────────────────────────────

BUILD_AND_RELEASE_WORKFLOWS = {
    "development": {
        "start_server": "npx expo start",
        "run_ios_simulator": "npx expo run:ios",
        "run_android_emulator": "npx expo run:android",
    },
    "production_eas_build": {
        "build_ios": "eas build --platform ios --profile production",
        "build_android": "eas build --platform android --profile production",
    },
    "store_submission": {
        "submit_ios": "eas submit --platform ios",
        "submit_android": "eas submit --platform android",
    },
}


# ── 5. App Size Budget Matrix ─────────────────────────────────────────────────

APP_SIZE_BUDGET = {
    "target_maximum_mb": 35.0,
    "breakdown": [
        {"component": "Hermes runtime", "size_mb": 15.0},
        {"component": "JS bundle (minified)", "size_mb": 4.0},
        {"component": "Expo modules", "size_mb": 8.0},
        {"component": "App assets", "size_mb": 2.0},
    ],
    "total_size_mb": 29.0,
    "budget_status": "WITHIN_BUDGET",
}


# ── 6. Mobile Features Catalog & Priorities ────────────────────────────────────

MOBILE_FEATURES = [
    {"feature": "Native share sheet", "implementation": "expo-sharing", "priority": "P0", "description": "Share memes to WhatsApp, iMessage, Twitter, Instagram"},
    {"feature": "Save to camera roll", "implementation": "expo-media-library", "priority": "P0", "description": "One-tap download to device photo gallery"},
    {"feature": "Haptic feedback on copy", "implementation": "expo-haptics", "priority": "P1", "description": "Light haptic tap when copying meme or link"},
    {"feature": "Offline cache (last 50 memes)", "implementation": "AsyncStorage + MMKV", "priority": "P1", "description": "Local offline storage of last 50 viewed memes and metadata"},
    {"feature": "Double-tap to favorite", "implementation": "GestureHandler", "priority": "P1", "description": "Instagram-style double-tap gesture to save meme"},
    {"feature": "Pull-to-refresh", "implementation": "FlatList onRefresh", "priority": "P1", "description": "Swipe down to refresh search results and trending feed"},
    {"feature": "Voice input", "implementation": "expo-speech", "priority": "P2", "description": "Speech-to-text dictation for meme search queries"},
]


# ── 7. Service Functions ──────────────────────────────────────────────────────

def get_mobile_tech_stack() -> Dict[str, Any]:
    """Retrieve mobile application tech stack."""
    return {
        "total_technologies": len(MOBILE_TECH_STACK),
        "stack": MOBILE_TECH_STACK,
    }


def get_mobile_architecture() -> Dict[str, Any]:
    """Retrieve 4-screen navigation architecture and native API integrations."""
    return {
        "total_screens": len(MOBILE_SCREENS),
        "screens": MOBILE_SCREENS,
        "total_native_apis": len(NATIVE_APIS),
        "native_apis": NATIVE_APIS,
    }


def get_platform_differences() -> Dict[str, Any]:
    """Retrieve comparison matrix of iOS vs Android differences."""
    return {
        "total_differences": len(PLATFORM_DIFFERENCES),
        "differences": PLATFORM_DIFFERENCES,
    }


def get_build_and_release_workflows() -> Dict[str, Any]:
    """Retrieve Expo and EAS build, simulator, and release commands."""
    return BUILD_AND_RELEASE_WORKFLOWS


def get_app_size_budget() -> Dict[str, Any]:
    """Retrieve app binary size budget breakdown and Hermes optimization metrics."""
    return APP_SIZE_BUDGET


def get_mobile_features_catalog() -> Dict[str, Any]:
    """Retrieve mobile-specific features list sorted by priority."""
    p0_count = sum(1 for f in MOBILE_FEATURES if f["priority"] == "P0")
    p1_count = sum(1 for f in MOBILE_FEATURES if f["priority"] == "P1")
    p2_count = sum(1 for f in MOBILE_FEATURES if f["priority"] == "P2")

    return {
        "total_features": len(MOBILE_FEATURES),
        "priority_breakdown": {
            "P0_critical": p0_count,
            "P1_high": p1_count,
            "P2_medium": p2_count,
        },
        "features": MOBILE_FEATURES,
    }


def simulate_mobile_offline_sync(
    cached_memes: List[Dict[str, Any]],
    max_cache_size: int = 50,
) -> Dict[str, Any]:
    """Simulate MMKV / AsyncStorage local cache maintenance enforcing 50-meme LRU eviction."""
    total_received = len(cached_memes)
    # Maintain strictly the most recent max_cache_size items
    active_cache = cached_memes[-max_cache_size:] if total_received > max_cache_size else cached_memes
    evicted_count = max(0, total_received - max_cache_size)

    return {
        "max_cache_limit": max_cache_size,
        "input_memes_count": total_received,
        "retained_memes_count": len(active_cache),
        "evicted_memes_count": evicted_count,
        "cache_status": "CACHE_OPTIMAL" if evicted_count == 0 else "CACHE_TRIMMED_LRU",
        "retained_memes": active_cache,
    }


def evaluate_mobile_app_readiness() -> Dict[str, Any]:
    """Evaluate readiness of mobile client specification across features, stack, and size budget."""
    stack_valid = len(MOBILE_TECH_STACK) == 5
    screens_valid = len(MOBILE_SCREENS) == 4
    size_valid = APP_SIZE_BUDGET["total_size_mb"] <= APP_SIZE_BUDGET["target_maximum_mb"]
    features_valid = len(MOBILE_FEATURES) == 7

    ready = stack_valid and screens_valid and size_valid and features_valid

    return {
        "status": "READY" if ready else "INCOMPLETE",
        "ready_for_phase_2": ready,
        "checks": {
            "tech_stack_configured": stack_valid,
            "core_screens_defined": screens_valid,
            "size_budget_compliant": size_valid,
            "features_prioritized": features_valid,
        },
        "target_binary_size": f"{APP_SIZE_BUDGET['total_size_mb']}MB / {APP_SIZE_BUDGET['target_maximum_mb']}MB",
    }
