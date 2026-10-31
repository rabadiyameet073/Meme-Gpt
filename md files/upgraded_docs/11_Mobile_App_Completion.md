# 11 — Mobile App Completion
# Share Sheet, Camera Roll, Haptics, MMKV Offline Cache

> **Gap Source:** Section 8 of GAP_ANALYSIS_FULL.md  
> **Priority:** P2  
> **Location:** `d:\Meme GPT\apps\mobile\`

---

## WHAT IS MISSING

The mobile app has basic Expo tab structure but none of the key features:
- No native share sheet (`expo-sharing`)
- No camera roll save (`expo-media-library`)
- No haptic feedback (`expo-haptics`)
- No offline cache (MMKV)
- No double-tap to favorite

---

## STEP 1 — Install All Required Expo Packages

```bash
cd "d:\Meme GPT\apps\mobile"
npx expo install expo-sharing expo-media-library expo-haptics
npx expo install react-native-mmkv
```

Add to `app.json` permissions:
```json
{
  "expo": {
    "plugins": [
      [
        "expo-media-library",
        {
          "photosPermission": "Allow MemeGPT to save memes to your camera roll.",
          "savePhotosPermission": "Allow MemeGPT to save memes to your photos."
        }
      ]
    ]
  }
}
```

---

## STEP 2 — MMKV Offline Cache Hook

**Create** `d:\Meme GPT\apps\mobile\hooks\useOfflineCache.ts`:

```ts
import { MMKV } from "react-native-mmkv";

const storage = new MMKV({ id: "memegpt-cache" });
const CACHE_KEY = "last_memes";
const MAX_CACHED = 50;

export interface CachedMeme {
  id: string;
  name: string;
  slug: string;
  gif_url?: string;
  image_url?: string;
  thumb_url?: string;
  cachedAt: number;
}

export function useOfflineCache() {
  const getCachedMemes = (): CachedMeme[] => {
    try {
      const raw = storage.getString(CACHE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  };

  const cacheMemes = (memes: CachedMeme[]) => {
    // Keep latest MAX_CACHED unique memes
    const existing = getCachedMemes();
    const merged = [
      ...memes.map((m) => ({ ...m, cachedAt: Date.now() })),
      ...existing.filter((e) => !memes.find((m) => m.id === e.id)),
    ].slice(0, MAX_CACHED);

    storage.set(CACHE_KEY, JSON.stringify(merged));
  };

  const clearCache = () => storage.delete(CACHE_KEY);

  return { getCachedMemes, cacheMemes, clearCache };
}
```

---

## STEP 3 — useMemeActions Hook (Share + Save + Haptics)

**Create** `d:\Meme GPT\apps\mobile\hooks\useMemeActions.ts`:

```ts
import * as Sharing from "expo-sharing";
import * as MediaLibrary from "expo-media-library";
import * as Haptics from "expo-haptics";
import * as FileSystem from "expo-file-system";
import { useState } from "react";

export function useMemeActions() {
  const [saving, setSaving] = useState(false);

  /**
   * Share meme URL using native share sheet.
   * iOS: AirDrop, Messages, Mail, etc.
   * Android: Share to WhatsApp, Twitter, etc.
   */
  const shareMeme = async (meme: { name: string; gif_url?: string; image_url?: string }) => {
    const url = meme.gif_url || meme.image_url;
    if (!url) return;

    await Haptics.selectionAsync();

    try {
      const isAvailable = await Sharing.isAvailableAsync();
      if (!isAvailable) {
        // Fallback: share text link
        await Sharing.shareAsync(`Check out this meme: ${url}`);
        return;
      }

      // Download to temp file then share
      const filename = `${meme.name.replace(/\s+/g, "-").toLowerCase()}.gif`;
      const localUri = FileSystem.cacheDirectory + filename;
      await FileSystem.downloadAsync(url, localUri);
      await Sharing.shareAsync(localUri, {
        mimeType: "image/gif",
        dialogTitle: `Share: ${meme.name}`,
      });
    } catch (e) {
      console.error("Share failed:", e);
    }
  };

  /**
   * Save meme to device camera roll.
   * Requests permission if not granted.
   */
  const saveToCameraRoll = async (meme: { name: string; gif_url?: string; image_url?: string }) => {
    const url = meme.gif_url || meme.image_url;
    if (!url || saving) return;

    setSaving(true);
    await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);

    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== "granted") {
        alert("Permission required to save to camera roll.");
        return;
      }

      const filename = `memegpt-${meme.name.replace(/\s+/g, "-")}.gif`;
      const localUri = FileSystem.cacheDirectory + filename;
      await FileSystem.downloadAsync(url, localUri);
      await MediaLibrary.saveToLibraryAsync(localUri);

      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (e) {
      console.error("Save failed:", e);
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setSaving(false);
    }
  };

  /**
   * Copy meme URL to clipboard with haptic.
   */
  const copyLink = async (url: string) => {
    const { setStringAsync } = await import("expo-clipboard");
    await setStringAsync(url);
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  return { shareMeme, saveToCameraRoll, copyLink, saving };
}
```

---

## STEP 4 — MemeCard Component with Double-Tap Favorite

**Create** `d:\Meme GPT\apps\mobile\components\MemeCard.tsx`:

```tsx
import React, { useRef, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Pressable,
} from "react-native";
import { Image } from "expo-image"; // Better GIF support than RN Image
import * as Haptics from "expo-haptics";
import { useMemeActions } from "../hooks/useMemeActions";

interface MemeCardProps {
  meme: {
    id: string;
    name: string;
    gif_url?: string;
    image_url?: string;
    thumb_url?: string;
    explanation?: string;
    categories?: string[];
  };
  onFavorite?: (id: string) => void;
  isFavorited?: boolean;
}

export function MemeCard({ meme, onFavorite, isFavorited = false }: MemeCardProps) {
  const { shareMeme, saveToCameraRoll, saving } = useMemeActions();
  const [favorited, setFavorited] = useState(isFavorited);
  const heartScale = useRef(new Animated.Value(1)).current;
  const lastTap = useRef<number>(0);

  // Double-tap to favorite
  const handleDoubleTap = () => {
    const now = Date.now();
    const DOUBLE_TAP_DELAY = 300;

    if (now - lastTap.current < DOUBLE_TAP_DELAY) {
      // Double tap!
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      setFavorited(true);
      onFavorite?.(meme.id);

      // Heart animation
      Animated.sequence([
        Animated.spring(heartScale, { toValue: 1.5, useNativeDriver: true }),
        Animated.spring(heartScale, { toValue: 1.0, useNativeDriver: true }),
      ]).start();
    }
    lastTap.current = now;
  };

  const imageUrl = meme.gif_url || meme.image_url || meme.thumb_url;

  return (
    <Pressable onPress={handleDoubleTap} style={styles.card}>
      {imageUrl && (
        <Image
          source={{ uri: imageUrl }}
          style={styles.image}
          contentFit="contain"
          autoplay={true}
        />
      )}

      <View style={styles.content}>
        <Text style={styles.name}>{meme.name}</Text>
        {meme.explanation ? (
          <Text style={styles.explanation} numberOfLines={2}>
            {meme.explanation}
          </Text>
        ) : null}

        <View style={styles.actions}>
          {/* Share */}
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => shareMeme(meme)}
            accessibilityLabel={`Share ${meme.name}`}
          >
            <Text style={styles.actionIcon}>📤</Text>
            <Text style={styles.actionText}>Share</Text>
          </TouchableOpacity>

          {/* Save to Camera Roll */}
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => saveToCameraRoll(meme)}
            disabled={saving}
            accessibilityLabel={`Save ${meme.name} to camera roll`}
          >
            <Text style={styles.actionIcon}>{saving ? "⏳" : "⬇️"}</Text>
            <Text style={styles.actionText}>Save</Text>
          </TouchableOpacity>

          {/* Favorite */}
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => {
              Haptics.selectionAsync();
              setFavorited((f) => !f);
              onFavorite?.(meme.id);
            }}
            accessibilityLabel={favorited ? "Unfavorite" : "Favorite"}
          >
            <Animated.Text
              style={[styles.actionIcon, { transform: [{ scale: heartScale }] }]}
            >
              {favorited ? "❤️" : "🤍"}
            </Animated.Text>
            <Text style={styles.actionText}>{favorited ? "Saved" : "Save"}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1A1A2E",
    borderRadius: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    overflow: "hidden",
    shadowColor: "#000",
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  image: {
    width: "100%",
    height: 240,
    backgroundColor: "#0D0D1A",
  },
  content: {
    padding: 14,
  },
  name: {
    color: "#E2E2FF",
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 4,
  },
  explanation: {
    color: "#9090B0",
    fontSize: 13,
    marginBottom: 10,
    lineHeight: 18,
  },
  actions: {
    flexDirection: "row",
    gap: 12,
  },
  actionBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(255,255,255,0.07)",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  actionIcon: {
    fontSize: 14,
  },
  actionText: {
    color: "#9090B0",
    fontSize: 12,
  },
});
```

---

## STEP 5 — Update Search Screen to Use Offline Cache

In `d:\Meme GPT\apps\mobile\app\(tabs)\index.tsx`:

```tsx
import { useOfflineCache } from "../../hooks/useOfflineCache";

// In component:
const { getCachedMemes, cacheMemes } = useOfflineCache();

// Show cached memes while loading
const [results, setResults] = useState(getCachedMemes());

// After successful search:
const handleSearch = async (query: string) => {
  setLoading(true);
  try {
    const data = await searchMemes(query);
    setResults(data.results);
    cacheMemes(data.results);  // ← Cache for offline use
  } finally {
    setLoading(false);
  }
};
```
