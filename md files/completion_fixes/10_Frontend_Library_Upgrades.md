# 10 — Frontend Library Upgrades Guide
> Add Zustand, TanStack Query, and React Hook Form to the Vite frontend per spec.

---

## Problem Statement

The spec requires these libraries in the Vite SPA (`frontend/`):
- ❌ **Zustand** — lightweight state management
- ❌ **TanStack Query v5** — server-state caching & data fetching
- ❌ **React Hook Form** — form validation

Currently using React useState + custom hooks. The libraries will improve code organization, reduce boilerplate, and add automatic cache invalidation.

---

## Step 1: Install Dependencies

```powershell
cd "d:\Meme GPT\frontend"
npm install zustand @tanstack/react-query react-hook-form
npm install -D @tanstack/react-query-devtools
```

---

## Step 2: Create Zustand Store

**File (create new):** `frontend/src/lib/store.ts`

```typescript
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
```

---

## Step 3: Setup TanStack Query

**File (modify):** `frontend/src/main.tsx`

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import App from './App';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      gcTime: 30 * 60 * 1000,         // 30 minutes (was cacheTime)
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>,
);
```

---

## Step 4: Create Query Hooks

**File (create new):** `frontend/src/hooks/useQueryHooks.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ─── Search Query ─────────────────────────────────────────────
export function useMemeSearchQuery(query: string, format: string, enabled = false) {
  return useQuery({
    queryKey: ['search', query, format],
    queryFn: async () => {
      const resp = await fetch(`${API_BASE}/api/v1/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, format_preference: format, limit: 10 }),
      });
      if (!resp.ok) throw new Error('Search failed');
      return resp.json();
    },
    enabled: enabled && query.length > 0,
    staleTime: 10 * 60 * 1000, // Cache search results for 10 min
  });
}

// ─── Trending Query ───────────────────────────────────────────
export function useTrendingQuery(category?: string) {
  return useQuery({
    queryKey: ['trending', category],
    queryFn: async () => {
      const url = category
        ? `${API_BASE}/api/v1/trending?category=${category}`
        : `${API_BASE}/api/v1/trending`;
      const resp = await fetch(url);
      return resp.json();
    },
    staleTime: 5 * 60 * 1000,
  });
}

// ─── Meme Detail Query ───────────────────────────────────────
export function useMemeQuery(slug: string) {
  return useQuery({
    queryKey: ['meme', slug],
    queryFn: async () => {
      const resp = await fetch(`${API_BASE}/api/v1/memes/${slug}`);
      if (!resp.ok) throw new Error('Meme not found');
      return resp.json();
    },
    enabled: !!slug,
  });
}

// ─── Categories Query ────────────────────────────────────────
export function useCategoriesQuery() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const resp = await fetch(`${API_BASE}/api/v1/categories`);
      return resp.json();
    },
    staleTime: 30 * 60 * 1000, // 30 min
  });
}

// ─── Feedback Mutation ───────────────────────────────────────
export function useFeedbackMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ memeId, type }: { memeId: string; type: string }) => {
      await fetch(`${API_BASE}/api/v1/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meme_id: memeId, feedback_type: type }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trending'] });
    },
  });
}

// ─── Stats Query ─────────────────────────────────────────────
export function useStatsQuery() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const resp = await fetch(`${API_BASE}/api/v1/health`);
      return resp.json();
    },
    staleTime: 60 * 1000, // 1 min
  });
}
```

---

## Step 5: Create Form with React Hook Form

**File (create new):** `frontend/src/components/SearchFormRHF.tsx`

```tsx
import { useForm } from 'react-hook-form';
import { useSearchStore } from '../lib/store';

interface SearchFormValues {
  query: string;
  format: 'gif' | 'image' | 'video' | 'any';
}

export function SearchFormRHF({ onSubmit }: { onSubmit: (data: SearchFormValues) => void }) {
  const { register, handleSubmit, formState: { errors }, watch } = useForm<SearchFormValues>({
    defaultValues: {
      query: '',
      format: 'gif',
    },
  });

  const queryLength = watch('query')?.length || 0;

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <textarea
          {...register('query', {
            required: 'Tell us what you are looking for',
            minLength: { value: 2, message: 'At least 2 characters' },
            maxLength: { value: 2000, message: 'Max 2000 characters' },
          })}
          placeholder="Describe a situation, feeling, or conversation..."
          rows={3}
        />
        <span>{queryLength}/2000</span>
        {errors.query && <span className="error">{errors.query.message}</span>}
      </div>

      <select {...register('format')}>
        <option value="gif">GIF</option>
        <option value="image">Image</option>
        <option value="video">Video</option>
        <option value="any">Any</option>
      </select>

      <button type="submit">Search</button>
    </form>
  );
}
```

---

## Migration Strategy

These libraries can be adopted **incrementally** — you don't need to refactor everything at once:

1. **Week 1:** Install all three libraries, set up providers in `main.tsx`
2. **Week 2:** Move search state to Zustand store (replace `useState` in `App.tsx`)
3. **Week 3:** Replace `useMemeSearch` and `useTrending` hooks with TanStack Query versions
4. **Week 4:** Add React Hook Form to `SearchForm.tsx` and `AdminTab.tsx`

The old hooks can remain as wrappers around the new libraries for backward compatibility.

---

## Verification Checklist

- [ ] Zustand stores work and persist to localStorage
- [ ] TanStack Query fetches/caches search results
- [ ] React Hook Form validates search input
- [ ] DevTools appear in dev mode
- [ ] No regressions in existing functionality
