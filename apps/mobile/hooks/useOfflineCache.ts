import { useState, useEffect } from "react";

export interface CachedMeme {
  id: string;
  name: string;
  slug: string;
  gif_url?: string;
  image_url?: string;
  thumb_url?: string;
  explanation?: string;
  cachedAt?: number;
}

const CACHE_KEY = "memegpt_offline_memes";
const MAX_CACHED = 50;

let mmkvStorage: any = null;
try {
  const { MMKV } = require("react-native-mmkv");
  mmkvStorage = new MMKV({ id: "memegpt-cache" });
} catch {}

export function useOfflineCache() {
  const [offlineMemes, setOfflineMemes] = useState<CachedMeme[]>([]);

  const getCachedMemes = (): CachedMeme[] => {
    try {
      if (mmkvStorage) {
        const raw = mmkvStorage.getString(CACHE_KEY);
        return raw ? JSON.parse(raw) : [];
      }
      return offlineMemes;
    } catch {
      return [];
    }
  };

  const cacheMemes = (memes: CachedMeme[]) => {
    try {
      const existing = getCachedMemes();
      const existingIds = new Set(existing.map((m) => m.id));
      const filtered = memes.filter((m) => !existingIds.has(m.id));
      const merged = [
        ...filtered.map((m) => ({ ...m, cachedAt: Date.now() })),
        ...existing,
      ].slice(0, MAX_CACHED);

      if (mmkvStorage) {
        mmkvStorage.set(CACHE_KEY, JSON.stringify(merged));
      }
      setOfflineMemes(merged);
    } catch (e) {
      console.warn("Failed to cache memes", e);
    }
  };

  const clearCache = () => {
    try {
      if (mmkvStorage) {
        mmkvStorage.delete(CACHE_KEY);
      }
      setOfflineMemes([]);
    } catch (e) {
      console.warn("Failed to clear cache", e);
    }
  };

  return { getCachedMemes, cacheMemes, clearCache, offlineMemes };
}
