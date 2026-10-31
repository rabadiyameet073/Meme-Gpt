# 05 — Mobile App Completion (React Native + Expo)
> **Priority:** 🟠 High — Mobile app is ~25% done (navigation shell only, no search)
> **Time Needed:** ~5-7 days
> **Result:** Fully functional iOS + Android app submitted to App Stores

---

## 📱 Current State of Mobile App

**What already exists:**
- `apps/mobile/app/_layout.tsx` — Tab bar navigation ✅
- `apps/mobile/app/(tabs)/index.tsx` — Search tab (SHELL ONLY) ❌
- `apps/mobile/app/(tabs)/library.tsx` — Library tab (SHELL ONLY) ❌
- `apps/mobile/app/(tabs)/trending.tsx` — Trending tab (SHELL ONLY) ❌
- `apps/mobile/app/meme/[id].tsx` — Detail screen (SHELL ONLY) ❌
- `mobile/src/components/MemeCard.tsx` — Full card with haptics ✅
- `mobile/src/hooks/useMemeActions.ts` — Share/copy/camera roll ✅
- `mobile/src/hooks/useOfflineCache.ts` — MMKV cache interface ✅
- `apps/mobile/app.json` — Bundle IDs, permissions ✅

**What's missing:**
- SearchForm component (text input + format selector)
- API client (calls to backend)
- MemeGrid component (results list)
- PreviewModal (full-screen view)
- Favorites storage
- All tab screens connected to real data

---

## 📋 Step 1 — Install Missing Dependencies

```powershell
cd "d:\Meme GPT\apps\mobile"
npm install

# Install missing packages
npx expo install expo-haptics expo-media-library expo-clipboard expo-sharing
npx expo install @react-native-async-storage/async-storage
```

---

## 📋 Step 2 — Create API Client

Create `d:\Meme GPT\apps\mobile\lib\api.ts`:

```typescript
/**
 * MemeGPT Mobile — API Client
 * Connects to the FastAPI backend.
 */

// Change this to your deployed Railway URL when in production
const API_BASE = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface MemeResult {
  id: number;
  slug: string;
  name: string;
  image_url: string;
  gif_url?: string;
  thumb_url?: string;
  format: "image" | "gif" | "video" | "webp";
  category?: string;
  emotion?: string;
  confidence?: number;
  explanation?: string;
}

export interface SearchResponse {
  matches: MemeResult[];
  query: string;
  total: number;
  latency_ms: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async search(
    query: string,
    formatPreference: string = "gif",
    limit: number = 10
  ): Promise<SearchResponse> {
    const response = await fetch(`${this.baseUrl}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, format_preference: formatPreference, limit }),
    });
    if (!response.ok) throw new Error(`Search failed: ${response.status}`);
    return response.json();
  }

  async getTrending(limit: number = 20): Promise<MemeResult[]> {
    const response = await fetch(`${this.baseUrl}/trending?limit=${limit}`);
    if (!response.ok) throw new Error(`Trending failed: ${response.status}`);
    const data = await response.json();
    return data.memes || data.trending || [];
  }

  async vote(memeId: number, vote: 1 | -1, sessionId: string): Promise<void> {
    await fetch(`${this.baseUrl}/vote`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ meme_id: memeId, vote, session_id: sessionId }),
    });
  }

  async sendFeedback(memeId: number, feedback: string): Promise<void> {
    await fetch(`${this.baseUrl}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ meme_id: memeId, feedback_type: feedback }),
    });
  }
}

export const api = new ApiClient(API_BASE);
```

---

## 📋 Step 3 — Create SearchScreen (Main Tab)

Replace the shell `d:\Meme GPT\apps\mobile\app\(tabs)\index.tsx` with:

```typescript
import React, { useState, useRef, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet,
  ActivityIndicator, KeyboardAvoidingView, Platform, SafeAreaView,
  RefreshControl, ScrollView,
} from "react-native";
import { Image } from "expo-image";
import { api, MemeResult } from "../../lib/api";
import { useMemeActions } from "../../hooks/useMemeActions";

const FORMATS = [
  { label: "All", value: "any" },
  { label: "GIF", value: "gif" },
  { label: "Image", value: "image" },
  { label: "Video", value: "video" },
];

const SUGGESTIONS = [
  "when monday hits", "code works first try", "friday feeling",
  "boss vs employee", "me procrastinating", "when budget cuts",
  "meeting that couldve been email", "waiting for deploy",
];

function SuggestionChips({ onPress }: { onPress: (s: string) => void }) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipsScroll}>
      {SUGGESTIONS.map((s) => (
        <TouchableOpacity key={s} style={styles.chip} onPress={() => onPress(s)}>
          <Text style={styles.chipText}>{s}</Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

function MemeCard({ item, onAction }: { item: MemeResult; onAction: (msg: string) => void }) {
  const { shareMeme, saveToCameraRoll } = useMemeActions();
  const imageUrl = item.gif_url || item.image_url || item.thumb_url || "";

  return (
    <View style={styles.card}>
      <Image
        source={{ uri: imageUrl }}
        style={styles.cardImage}
        contentFit="cover"
        transition={300}
      />
      <View style={styles.cardFooter}>
        <Text style={styles.cardName} numberOfLines={2}>{item.name}</Text>
        <View style={styles.cardActions}>
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => shareMeme({ url: imageUrl, title: item.name }).then(() => onAction("Shared!"))}
          >
            <Text style={styles.actionIcon}>↗</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={() => saveToCameraRoll(imageUrl).then(() => onAction("Saved!"))}
          >
            <Text style={styles.actionIcon}>⬇</Text>
          </TouchableOpacity>
        </View>
      </View>
      {item.confidence != null && (
        <View style={styles.confidenceBadge}>
          <Text style={styles.confidenceText}>{Math.round(item.confidence * 100)}% match</Text>
        </View>
      )}
    </View>
  );
}

export default function SearchScreen() {
  const [query, setQuery] = useState("");
  const [format, setFormat] = useState("gif");
  const [results, setResults] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const inputRef = useRef<TextInput>(null);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2500);
  }, []);

  const handleSearch = useCallback(async (q?: string) => {
    const searchQuery = q ?? query;
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError("");
    try {
      const data = await api.search(searchQuery, format, 10);
      setResults(data.matches || []);
      if ((data.matches || []).length === 0) {
        setError("No memes found. Try a different query!");
      }
    } catch (err) {
      setError("Search failed. Check your connection.");
    } finally {
      setLoading(false);
    }
  }, [query, format]);

  const handleSuggestion = useCallback((s: string) => {
    setQuery(s);
    handleSearch(s);
  }, [handleSearch]);

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={{ flex: 1 }}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🎭 MemeGPT</Text>
          <Text style={styles.headerSub}>Say anything. Get the perfect meme.</Text>
        </View>

        {/* Search Bar */}
        <View style={styles.searchBar}>
          <TextInput
            ref={inputRef}
            style={styles.searchInput}
            placeholder="Describe your situation..."
            placeholderTextColor="#71717a"
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={() => handleSearch()}
            returnKeyType="search"
            multiline={false}
          />
          <TouchableOpacity
            style={[styles.searchBtn, loading && styles.searchBtnDisabled]}
            onPress={() => handleSearch()}
            disabled={loading}
          >
            <Text style={styles.searchBtnText}>{loading ? "..." : "🔍"}</Text>
          </TouchableOpacity>
        </View>

        {/* Format Filter */}
        <View style={styles.formatRow}>
          {FORMATS.map((f) => (
            <TouchableOpacity
              key={f.value}
              style={[styles.formatChip, format === f.value && styles.formatChipActive]}
              onPress={() => setFormat(f.value)}
            >
              <Text style={[styles.formatText, format === f.value && styles.formatTextActive]}>
                {f.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Suggestions (when no results) */}
        {results.length === 0 && !loading && (
          <SuggestionChips onPress={handleSuggestion} />
        )}

        {/* Results */}
        {loading ? (
          <View style={styles.loadingView}>
            <ActivityIndicator size="large" color="#7C3AED" />
            <Text style={styles.loadingText}>Finding the perfect meme...</Text>
          </View>
        ) : error ? (
          <View style={styles.errorView}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : (
          <FlatList
            data={results}
            keyExtractor={(item) => String(item.id)}
            numColumns={2}
            columnWrapperStyle={styles.columnWrapper}
            renderItem={({ item }) => (
              <MemeCard item={item} onAction={showToast} />
            )}
            contentContainerStyle={styles.list}
            showsVerticalScrollIndicator={false}
          />
        )}

        {/* Toast */}
        {toast ? (
          <View style={styles.toast}>
            <Text style={styles.toastText}>{toast}</Text>
          </View>
        ) : null}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090B" },
  header: { padding: 20, paddingBottom: 12 },
  headerTitle: { color: "#fff", fontSize: 26, fontWeight: "800" },
  headerSub: { color: "#71717a", fontSize: 13, marginTop: 2 },
  searchBar: { flexDirection: "row", marginHorizontal: 16, marginBottom: 10, gap: 8 },
  searchInput: {
    flex: 1, backgroundColor: "#18181B", color: "#fff", borderRadius: 12,
    paddingHorizontal: 16, paddingVertical: 12, fontSize: 15,
    borderWidth: 1, borderColor: "#3F3F46",
  },
  searchBtn: {
    backgroundColor: "#7C3AED", borderRadius: 12, paddingHorizontal: 16,
    justifyContent: "center", alignItems: "center",
  },
  searchBtnDisabled: { backgroundColor: "#4C1D95" },
  searchBtnText: { fontSize: 20 },
  formatRow: { flexDirection: "row", paddingHorizontal: 16, gap: 8, marginBottom: 12 },
  formatChip: {
    paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20,
    backgroundColor: "#18181B", borderWidth: 1, borderColor: "#3F3F46",
  },
  formatChipActive: { backgroundColor: "#7C3AED", borderColor: "#7C3AED" },
  formatText: { color: "#71717a", fontSize: 13, fontWeight: "600" },
  formatTextActive: { color: "#fff" },
  chipsScroll: { paddingHorizontal: 16, marginBottom: 12 },
  chip: {
    backgroundColor: "#18181B", borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6,
    marginRight: 8, borderWidth: 1, borderColor: "#3F3F46",
  },
  chipText: { color: "#a1a1aa", fontSize: 12 },
  loadingView: { flex: 1, justifyContent: "center", alignItems: "center", gap: 16 },
  loadingText: { color: "#71717a", fontSize: 15 },
  errorView: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24 },
  errorText: { color: "#ef4444", textAlign: "center", fontSize: 15 },
  list: { paddingHorizontal: 12, paddingBottom: 24 },
  columnWrapper: { gap: 8, marginBottom: 8 },
  card: {
    flex: 1, backgroundColor: "#18181B", borderRadius: 16,
    overflow: "hidden", borderWidth: 1, borderColor: "#27272A",
  },
  cardImage: { width: "100%", aspectRatio: 1 },
  cardFooter: { padding: 8, flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" },
  cardName: { flex: 1, color: "#e4e4e7", fontSize: 11, fontWeight: "600", marginRight: 4 },
  cardActions: { flexDirection: "row", gap: 4 },
  actionBtn: { width: 28, height: 28, borderRadius: 8, backgroundColor: "#27272A", justifyContent: "center", alignItems: "center" },
  actionIcon: { fontSize: 12, color: "#a1a1aa" },
  confidenceBadge: {
    position: "absolute", top: 8, right: 8,
    backgroundColor: "rgba(124,58,237,0.85)", borderRadius: 6, paddingHorizontal: 6, paddingVertical: 2,
  },
  confidenceText: { color: "#fff", fontSize: 10, fontWeight: "700" },
  toast: {
    position: "absolute", bottom: 20, left: 32, right: 32,
    backgroundColor: "#7C3AED", borderRadius: 12, padding: 14, alignItems: "center",
  },
  toastText: { color: "#fff", fontWeight: "600", fontSize: 14 },
});
```

---

## 📋 Step 4 — Create TrendingScreen

Replace `d:\Meme GPT\apps\mobile\app\(tabs)\trending.tsx`:

```typescript
import React, { useEffect, useState } from "react";
import {
  View, Text, FlatList, StyleSheet, ActivityIndicator, SafeAreaView, RefreshControl,
} from "react-native";
import { Image } from "expo-image";
import { api, MemeResult } from "../../lib/api";

export default function TrendingScreen() {
  const [memes, setMemes] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const data = await api.getTrending(20);
      setMemes(data);
    } catch {
      /* silently fail */
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#7C3AED" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>🔥 Trending Memes</Text>
      <FlatList
        data={memes}
        keyExtractor={(item) => String(item.id)}
        numColumns={2}
        columnWrapperStyle={{ gap: 8, marginBottom: 8 }}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Image
              source={{ uri: item.thumb_url || item.image_url }}
              style={styles.image}
              contentFit="cover"
              transition={200}
            />
            <Text style={styles.name} numberOfLines={2}>{item.name}</Text>
          </View>
        )}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090B" },
  loading: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#09090B" },
  title: { color: "#fff", fontSize: 22, fontWeight: "800", padding: 20, paddingBottom: 12 },
  card: { flex: 1, backgroundColor: "#18181B", borderRadius: 12, overflow: "hidden" },
  image: { width: "100%", aspectRatio: 1 },
  name: { color: "#e4e4e7", fontSize: 11, padding: 8, fontWeight: "600" },
});
```

---

## 📋 Step 5 — Create LibraryScreen (Favorites)

Replace `d:\Meme GPT\apps\mobile\app\(tabs)\library.tsx`:

```typescript
import React, { useState, useCallback } from "react";
import {
  View, Text, FlatList, StyleSheet, SafeAreaView, TouchableOpacity,
} from "react-native";
import { Image } from "expo-image";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect } from "expo-router";
import { MemeResult } from "../../lib/api";

const FAV_KEY = "memegpt_favorites_v1";

export default function LibraryScreen() {
  const [favorites, setFavorites] = useState<MemeResult[]>([]);

  const loadFavorites = useCallback(async () => {
    const raw = await AsyncStorage.getItem(FAV_KEY);
    if (raw) setFavorites(JSON.parse(raw));
  }, []);

  useFocusEffect(() => { loadFavorites(); });

  const removeFavorite = async (id: number) => {
    const updated = favorites.filter((f) => f.id !== id);
    setFavorites(updated);
    await AsyncStorage.setItem(FAV_KEY, JSON.stringify(updated));
  };

  if (favorites.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.title}>❤️ Saved Memes</Text>
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>📂</Text>
          <Text style={styles.emptyText}>No saved memes yet!</Text>
          <Text style={styles.emptySubtext}>Search and save memes to see them here</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>❤️ Saved Memes ({favorites.length})</Text>
      <FlatList
        data={favorites}
        keyExtractor={(item) => String(item.id)}
        numColumns={2}
        columnWrapperStyle={{ gap: 8, marginBottom: 8 }}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Image
              source={{ uri: item.thumb_url || item.image_url }}
              style={styles.image}
              contentFit="cover"
              transition={200}
            />
            <View style={styles.cardBottom}>
              <Text style={styles.name} numberOfLines={1}>{item.name}</Text>
              <TouchableOpacity onPress={() => removeFavorite(item.id)}>
                <Text style={styles.remove}>✕</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090B" },
  title: { color: "#fff", fontSize: 22, fontWeight: "800", padding: 20, paddingBottom: 12 },
  empty: { flex: 1, justifyContent: "center", alignItems: "center", gap: 12 },
  emptyIcon: { fontSize: 64 },
  emptyText: { color: "#fff", fontSize: 18, fontWeight: "700" },
  emptySubtext: { color: "#71717a", fontSize: 14, textAlign: "center" },
  card: { flex: 1, backgroundColor: "#18181B", borderRadius: 12, overflow: "hidden" },
  image: { width: "100%", aspectRatio: 1 },
  cardBottom: { flexDirection: "row", justifyContent: "space-between", padding: 8, alignItems: "center" },
  name: { flex: 1, color: "#e4e4e7", fontSize: 11, fontWeight: "600" },
  remove: { color: "#71717a", fontSize: 16, paddingLeft: 4 },
});
```

---

## 📋 Step 6 — Add useMemeActions Hook

Create `d:\Meme GPT\apps\mobile\hooks\useMemeActions.ts`:

```typescript
import { Alert } from "react-native";
import * as MediaLibrary from "expo-media-library";
import * as Sharing from "expo-sharing";
import * as Clipboard from "expo-clipboard";
import * as FileSystem from "expo-file-system";

export function useMemeActions() {
  const saveToCameraRoll = async (imageUrl: string): Promise<boolean> => {
    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission needed", "Please allow photo library access to save memes.");
        return false;
      }
      const filename = FileSystem.cacheDirectory + "meme_" + Date.now() + ".jpg";
      await FileSystem.downloadAsync(imageUrl, filename);
      await MediaLibrary.saveToLibraryAsync(filename);
      return true;
    } catch {
      return false;
    }
  };

  const shareMeme = async ({ url, title }: { url: string; title?: string }): Promise<void> => {
    try {
      const filename = FileSystem.cacheDirectory + "meme_share_" + Date.now() + ".jpg";
      await FileSystem.downloadAsync(url, filename);
      await Sharing.shareAsync(filename, { dialogTitle: title || "Share Meme" });
    } catch {
      /* silently fail */
    }
  };

  const copyMemeLink = async (url: string): Promise<void> => {
    await Clipboard.setStringAsync(url);
  };

  return { saveToCameraRoll, shareMeme, copyMemeLink };
}
```

---

## 📋 Step 7 — Add Environment Config

Create `d:\Meme GPT\apps\mobile\.env`:
```env
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
```

For production (after deploying to Railway):
```env
EXPO_PUBLIC_API_URL=https://your-app.railway.app/api/v1
```

---

## 📋 Step 8 — Run on Simulator/Device

```powershell
cd "d:\Meme GPT\apps\mobile"

# iOS Simulator (Mac required)
npx expo start --ios

# Android Emulator
npx expo start --android

# Physical device via Expo Go app
npx expo start
# Then scan QR code with Expo Go
```

---

## 📋 Step 9 — EAS Build for App Stores

```powershell
npm install -g eas-cli
eas login

cd "d:\Meme GPT\apps\mobile"

# Create eas.json
```

Create `d:\Meme GPT\apps\mobile\eas.json`:
```json
{
  "cli": { "version": ">= 5.9.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": false },
      "android": { "buildType": "apk" }
    },
    "production": {
      "ios": { "buildConfiguration": "Release" },
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "production": {
      "ios": { "appleId": "your@email.com", "ascAppId": "YOUR_APP_ID" },
      "android": { "serviceAccountKeyPath": "./google-service-account.json" }
    }
  }
}
```

```powershell
# Build for Android (Preview APK — for testing)
eas build --platform android --profile preview

# Build for iOS (requires Apple Developer account $99/yr)
eas build --platform ios --profile production

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

---

## ✅ Done When

- [ ] `npx expo start` runs without errors
- [ ] Search tab: typing a query → results appear
- [ ] Results show meme images with names
- [ ] Share button opens iOS/Android share sheet
- [ ] Camera roll save works (asks permission then saves)
- [ ] Trending tab shows memes
- [ ] Library tab shows saved memes
- [ ] App runs on physical device via Expo Go
- [ ] EAS build completes without error

**Next step → `06_Deployment_Railway_Vercel.md`**
