import { useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

const OFFLINE_MEMES_KEY = "memegpt_offline_memes";
const MAX_OFFLINE_MEMES = 50;

export interface MemeItem {
  id: string;
  name: string;
  slug: string;
  explanation?: string;
  image_url?: string;
  gif_url?: string;
  thumb_url?: string;
  imageRef?: string;
  gifRef?: string;
  category?: string;
  categories?: string[];
  emotions?: string[];
}

export function useOfflineCache() {
  const [offlineMemes, setOfflineMemes] = useState<MemeItem[]>([]);

  useEffect(() => {
    loadOfflineMemes();
  }, []);

  const loadOfflineMemes = async () => {
    try {
      const data = await AsyncStorage.getItem(OFFLINE_MEMES_KEY);
      if (data) {
        setOfflineMemes(JSON.parse(data));
      }
    } catch (e) {
      console.warn("Failed to load offline cache", e);
    }
  };

  const cacheMemes = async (newMemes: MemeItem[]) => {
    try {
      const existing = await AsyncStorage.getItem(OFFLINE_MEMES_KEY);
      const currentList: MemeItem[] = existing ? JSON.parse(existing) : [];

      const existingIds = new Set(currentList.map((m) => m.id));
      const filteredNew = newMemes.filter((m) => !existingIds.has(m.id));

      const updated = [...filteredNew, ...currentList].slice(0, MAX_OFFLINE_MEMES);
      await AsyncStorage.setItem(OFFLINE_MEMES_KEY, JSON.stringify(updated));
      setOfflineMemes(updated);
    } catch (e) {
      console.warn("Failed to cache memes offline", e);
    }
  };

  const clearOfflineCache = async () => {
    try {
      await AsyncStorage.removeItem(OFFLINE_MEMES_KEY);
      setOfflineMemes([]);
    } catch (e) {
      console.warn("Failed to clear cache", e);
    }
  };

  return { offlineMemes, cacheMemes, clearOfflineCache };
}
