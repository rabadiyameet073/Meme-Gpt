import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// ─── Meme Search State ────────────────────────────────────────
interface SearchState {
  query: string;
  formatPreference: 'gif' | 'image' | 'video' | 'any';
  results: any[];
  isSearching: boolean;
  detectedEmotion: string;
  latencyMs: number;
  error: string | null;

  setQuery: (q: string) => void;
  setFormatPreference: (f: 'gif' | 'image' | 'video' | 'any') => void;
  setResults: (results: any[], emotion: string, latency: number) => void;
  setSearching: (v: boolean) => void;
  setError: (e: string | null) => void;
  clearResults: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: '',
  formatPreference: 'gif',
  results: [],
  isSearching: false,
  detectedEmotion: '',
  latencyMs: 0,
  error: null,

  setQuery: (query) => set({ query }),
  setFormatPreference: (formatPreference) => set({ formatPreference }),
  setResults: (results, detectedEmotion, latencyMs) =>
    set({ results, detectedEmotion, latencyMs, isSearching: false, error: null }),
  setSearching: (isSearching) => set({ isSearching }),
  setError: (error) => set({ error, isSearching: false }),
  clearResults: () => set({ results: [], detectedEmotion: '', latencyMs: 0 }),
}));

// ─── User Preferences (Persisted) ────────────────────────────
interface PreferencesState {
  theme: 'dark' | 'light';
  audioEnabled: boolean;
  nsfwFilter: boolean;
  searchHistory: string[];

  setTheme: (t: 'dark' | 'light') => void;
  setAudioEnabled: (v: boolean) => void;
  setNsfwFilter: (v: boolean) => void;
  addToHistory: (q: string) => void;
  clearHistory: () => void;
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      theme: 'dark',
      audioEnabled: false,
      nsfwFilter: true,
      searchHistory: [],

      setTheme: (theme) => set({ theme }),
      setAudioEnabled: (audioEnabled) => set({ audioEnabled }),
      setNsfwFilter: (nsfwFilter) => set({ nsfwFilter }),
      addToHistory: (q) =>
        set((state) => ({
          searchHistory: [q, ...state.searchHistory.filter((h) => h !== q)].slice(0, 20),
        })),
      clearHistory: () => set({ searchHistory: [] }),
    }),
    {
      name: 'memegpt-preferences',
      storage: createJSONStorage(() => localStorage),
    }
  )
);

// ─── Favorites State (Persisted) ─────────────────────────────
interface FavoritesState {
  favorites: string[]; // meme IDs
  addFavorite: (id: string) => void;
  removeFavorite: (id: string) => void;
  isFavorite: (id: string) => boolean;
  clearFavorites: () => void;
}

export const useFavoritesStore = create<FavoritesState>()(
  persist(
    (set, get) => ({
      favorites: [],
      addFavorite: (id) =>
        set((state) => ({
          favorites: [...new Set([id, ...state.favorites])],
        })),
      removeFavorite: (id) =>
        set((state) => ({
          favorites: state.favorites.filter((f) => f !== id),
        })),
      isFavorite: (id) => get().favorites.includes(id),
      clearFavorites: () => set({ favorites: [] }),
    }),
    {
      name: 'memegpt-favorites',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
