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
  thumb_url?: string;
  explanation?: string;
  cachedAt?: number;
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
    setCachedMemes((prev) => {
      const exists = prev.some((m) => String(m.id) === String(meme.id));
      if (exists) return prev;

      const updated = [
        { ...meme, id: String(meme.id), cachedAt: Date.now() },
        ...prev,
      ].slice(0, MAX_CACHED_MEMES);

      AsyncStorage.setItem(CACHE_KEY, JSON.stringify(updated)).catch(() => {});
      return updated;
    });
  }, []);

  const removeFromCache = useCallback(async (memeId: string) => {
    setCachedMemes((prev) => {
      const updated = prev.filter((m) => String(m.id) !== String(memeId));
      AsyncStorage.setItem(CACHE_KEY, JSON.stringify(updated)).catch(() => {});
      return updated;
    });
  }, []);

  const clearCache = useCallback(async () => {
    await AsyncStorage.removeItem(CACHE_KEY);
    setCachedMemes([]);
  }, []);

  // Backwards compatibility helpers
  const cacheMemes = useCallback(async (memes: CachedMeme[]) => {
    for (const m of memes) {
      await addToCache(m);
    }
  }, [addToCache]);

  const getCachedMemes = useCallback((): CachedMeme[] => {
    return cachedMemes;
  }, [cachedMemes]);

  return {
    cachedMemes,
    isLoading,
    addToCache,
    removeFromCache,
    clearCache,
    cacheMemes,
    getCachedMemes,
    offlineMemes: cachedMemes,
  };
}
