# 06 — Mobile App Completion Guide
> Complete the React Native / Expo mobile app with push notifications, offline cache, animations, native share, and app store prep.

---

## Problem Statement

| Feature | Status | Gap |
|---------|--------|-----|
| Core tabs (Search, Trending, Library) | ✅ Built | — |
| Meme detail screen | 🟡 Route exists | Content may be skeleton |
| React Native Reanimated v3 | ❌ Not installed | No smooth animations |
| React Native Paper (Material UI) | ❌ Not installed | Using plain RN components |
| Push notifications | ❌ Missing | No expo-notifications |
| Offline meme cache (50 memes) | ❌ Missing | AsyncStorage exists but not wired |
| Native share sheet | 🟡 Dep installed | Not wired in components |
| Download to camera roll | 🟡 Dep installed | Not wired in components |
| App store submission | ❌ Not done | EAS config exists |

---

## Step 1: Install Missing Dependencies

```powershell
cd "d:\Meme GPT\apps\mobile"
npx expo install react-native-reanimated react-native-gesture-handler
npx expo install react-native-paper react-native-vector-icons
npx expo install expo-notifications expo-device
npx expo install @expo/vector-icons
```

Update `package.json` to include these.

---

## Step 2: Configure Reanimated

**File:** `apps/mobile/babel.config.js` (create if missing)

```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['react-native-reanimated/plugin'],
  };
};
```

---

## Step 3: Create API Client

**File (create new):** `apps/mobile/lib/api.ts`

```typescript
const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

interface SearchParams {
  query: string;
  format_preference?: 'gif' | 'image' | 'video';
  limit?: number;
}

export const api = {
  async search(params: SearchParams) {
    const resp = await fetch(`${API_BASE}/api/v1/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: params.query,
        format_preference: params.format_preference || 'gif',
        limit: params.limit || 10,
      }),
    });
    if (!resp.ok) throw new Error(`Search failed: ${resp.status}`);
    return resp.json();
  },

  async getTrending(limit = 20) {
    const resp = await fetch(`${API_BASE}/api/v1/trending?limit=${limit}`);
    return resp.json();
  },

  async getMeme(slug: string) {
    const resp = await fetch(`${API_BASE}/api/v1/memes/${slug}`);
    return resp.json();
  },

  async submitFeedback(memeId: string, type: 'thumbs_up' | 'thumbs_down') {
    await fetch(`${API_BASE}/api/v1/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ meme_id: memeId, feedback_type: type }),
    });
  },
};
```

---

## Step 4: Create Offline Cache Hook

**File (create new):** `apps/mobile/hooks/useOfflineCache.ts`

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useCallback, useEffect, useState } from 'react';

const CACHE_KEY = 'memegpt_offline_cache';
const MAX_CACHED_MEMES = 50;

export interface CachedMeme {
  id: string;
  name: string;
  slug: string;
  image_url: string;
  gif_url?: string;
  cachedAt: number;
}

export function useOfflineCache() {
  const [cachedMemes, setCachedMemes] = useState<CachedMeme[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load cache on mount
  useEffect(() => {
    loadCache();
  }, []);

  const loadCache = async () => {
    try {
      const raw = await AsyncStorage.getItem(CACHE_KEY);
      if (raw) {
        setCachedMemes(JSON.parse(raw));
      }
    } catch (e) {
      console.warn('Failed to load offline cache:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const addToCache = useCallback(async (meme: Omit<CachedMeme, 'cachedAt'>) => {
    setCachedMemes(prev => {
      const exists = prev.some(m => m.id === meme.id);
      if (exists) return prev;

      const updated = [
        { ...meme, cachedAt: Date.now() },
        ...prev,
      ].slice(0, MAX_CACHED_MEMES);

      AsyncStorage.setItem(CACHE_KEY, JSON.stringify(updated)).catch(() => {});
      return updated;
    });
  }, []);

  const removeFromCache = useCallback(async (memeId: string) => {
    setCachedMemes(prev => {
      const updated = prev.filter(m => m.id !== memeId);
      AsyncStorage.setItem(CACHE_KEY, JSON.stringify(updated)).catch(() => {});
      return updated;
    });
  }, []);

  const clearCache = useCallback(async () => {
    await AsyncStorage.removeItem(CACHE_KEY);
    setCachedMemes([]);
  }, []);

  return { cachedMemes, isLoading, addToCache, removeFromCache, clearCache };
}
```

---

## Step 5: Add Native Share & Download

**File (create new):** `apps/mobile/hooks/useShareAndDownload.ts`

```typescript
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';
import * as Haptics from 'expo-haptics';
import { Alert, Platform } from 'react-native';

export function useShareAndDownload() {
  const shareMeme = async (url: string, title: string) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

      const filename = `memegpt_${Date.now()}.jpg`;
      const fileUri = `${FileSystem.cacheDirectory}${filename}`;

      await FileSystem.downloadAsync(url, fileUri);
      await Sharing.shareAsync(fileUri, {
        mimeType: 'image/jpeg',
        dialogTitle: `Share: ${title}`,
      });
    } catch (e) {
      Alert.alert('Share failed', String(e));
    }
  };

  const downloadMeme = async (url: string) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

      // Request permissions
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Allow access to save memes to your library.');
        return false;
      }

      const filename = `memegpt_${Date.now()}.jpg`;
      const fileUri = `${FileSystem.documentDirectory}${filename}`;

      const download = await FileSystem.downloadAsync(url, fileUri);

      if (download.status === 200) {
        await MediaLibrary.saveToLibraryAsync(download.uri);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        return true;
      }
      return false;
    } catch (e) {
      Alert.alert('Download failed', String(e));
      return false;
    }
  };

  return { shareMeme, downloadMeme };
}
```

---

## Step 6: Update MemeCard with Share/Download Actions

**Update:** `apps/mobile/components/MemeCard.tsx`

Add these imports and action buttons:

```typescript
import { useShareAndDownload } from '../hooks/useShareAndDownload';

// Inside the component:
const { shareMeme, downloadMeme } = useShareAndDownload();

// Add action buttons below the image:
<View style={styles.actions}>
  <TouchableOpacity onPress={() => shareMeme(meme.image_url, meme.name)}>
    <Text style={styles.actionBtn}>📤 Share</Text>
  </TouchableOpacity>
  <TouchableOpacity onPress={async () => {
    const ok = await downloadMeme(meme.image_url);
    if (ok) Alert.alert('Saved!', 'Meme saved to your photo library.');
  }}>
    <Text style={styles.actionBtn}>💾 Save</Text>
  </TouchableOpacity>
</View>
```

---

## Step 7: Add Push Notifications

**File (create new):** `apps/mobile/hooks/usePushNotifications.ts`

```typescript
import { useEffect, useRef, useState } from 'react';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export function usePushNotifications() {
  const [expoPushToken, setExpoPushToken] = useState<string>('');
  const notificationListener = useRef<Notifications.EventSubscription>();

  useEffect(() => {
    registerForPushNotifications().then(token => {
      if (token) setExpoPushToken(token);
    });

    notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
      console.log('Notification received:', notification);
    });

    return () => {
      if (notificationListener.current) {
        Notifications.removeNotificationSubscription(notificationListener.current);
      }
    };
  }, []);

  return { expoPushToken };
}

async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.log('Push notifications only work on physical devices');
    return null;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') return null;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'MemeGPT',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
    });
  }

  const tokenData = await Notifications.getExpoPushTokenAsync();
  return tokenData.data;
}
```

---

## Step 8: Create Meme Detail Screen

**File (create/update):** `apps/mobile/app/meme/[id].tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator, Dimensions } from 'react-native';
import { useLocalSearchParams, Stack } from 'expo-router';
import { Image } from 'expo-image';
import { api } from '../../lib/api';
import { useShareAndDownload } from '../../hooks/useShareAndDownload';

const { width } = Dimensions.get('window');

export default function MemeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [meme, setMeme] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { shareMeme, downloadMeme } = useShareAndDownload();

  useEffect(() => {
    if (id) {
      api.getMeme(id).then(setMeme).finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) return <ActivityIndicator size="large" color="#7C3AED" style={{ flex: 1 }} />;
  if (!meme) return <Text style={styles.error}>Meme not found</Text>;

  return (
    <>
      <Stack.Screen options={{ title: meme.name }} />
      <ScrollView style={styles.container}>
        <Image
          source={{ uri: meme.gif_url || meme.image_url }}
          style={styles.image}
          contentFit="contain"
        />
        <View style={styles.info}>
          <Text style={styles.title}>{meme.name}</Text>
          <Text style={styles.subtitle}>{meme.explanation}</Text>
          {meme.emotions?.length > 0 && (
            <View style={styles.tags}>
              {meme.emotions.map((e: string) => (
                <View key={e} style={styles.tag}>
                  <Text style={styles.tagText}>{e}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0A0A0A' },
  image: { width, height: width * 0.8 },
  info: { padding: 16 },
  title: { fontSize: 22, fontWeight: '700', color: '#F5F5F5', marginBottom: 8 },
  subtitle: { fontSize: 14, color: '#A3A3A3', lineHeight: 20 },
  tags: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 12 },
  tag: { backgroundColor: '#7C3AED22', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, marginRight: 6, marginBottom: 6 },
  tagText: { color: '#7C3AED', fontSize: 12, fontWeight: '600' },
  error: { color: '#EF4444', textAlign: 'center', marginTop: 100, fontSize: 16 },
});
```

---

## Step 9: Add `.env` for Mobile

**File:** `apps/mobile/.env`

```env
EXPO_PUBLIC_API_URL=http://localhost:8000
```

For production:
```env
EXPO_PUBLIC_API_URL=https://api.memegpt.com
```

---

## Step 10: App Store Preparation

### 10.1 Update `app.json` with Store Metadata

**File:** `apps/mobile/app.json`

Ensure these fields are complete:
```json
{
  "expo": {
    "name": "MemeGPT",
    "slug": "memegpt",
    "version": "1.0.0",
    "description": "Find the perfect meme for any situation using AI",
    "primaryColor": "#7C3AED",
    "ios": {
      "bundleIdentifier": "com.memegpt.app",
      "buildNumber": "1",
      "supportsTablet": true,
      "infoPlist": {
        "NSPhotoLibraryUsageDescription": "Save memes to your photo library",
        "NSPhotoLibraryAddUsageDescription": "Save memes to your photo library"
      }
    },
    "android": {
      "package": "com.memegpt.app",
      "versionCode": 1,
      "permissions": ["WRITE_EXTERNAL_STORAGE"]
    }
  }
}
```

### 10.2 Build for Testing

```powershell
cd "d:\Meme GPT\apps\mobile"

# Development build (for testing on device)
npx eas build --platform android --profile development

# Preview build (for testers)
npx eas build --platform android --profile preview

# Production build (for store submission)
npx eas build --platform android --profile production
```

### 10.3 Submit to Stores

```powershell
# Submit to Google Play
npx eas submit --platform android

# Submit to Apple App Store (requires Apple Developer account)
npx eas submit --platform ios
```

---

## Verification Checklist

- [ ] Reanimated v3 installed and `babel.config.js` configured
- [ ] API client connects to backend from mobile
- [ ] Offline cache stores and retrieves up to 50 memes
- [ ] Share button opens native share sheet
- [ ] Download button saves meme to camera roll
- [ ] Push notification token registered
- [ ] Meme detail screen `/meme/[id]` loads and displays
- [ ] EAS build succeeds for Android/iOS
