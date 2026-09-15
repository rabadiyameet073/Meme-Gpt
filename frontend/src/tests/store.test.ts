import { describe, it, expect, beforeEach } from 'vitest';
import { useSearchStore, usePreferencesStore, useFavoritesStore } from '../lib/store';

describe('Zustand Stores (Guide 10)', () => {
  beforeEach(() => {
    localStorage.clear();
    useSearchStore.getState().clearResults();
    useSearchStore.getState().setQuery('');
    usePreferencesStore.getState().clearHistory();
    useFavoritesStore.getState().clearFavorites();
  });

  describe('useSearchStore', () => {
    it('initializes with default values', () => {
      const state = useSearchStore.getState();
      expect(state.query).toBe('');
      expect(state.formatPreference).toBe('gif');
      expect(state.results).toEqual([]);
      expect(state.isSearching).toBe(false);
      expect(state.detectedEmotion).toBe('');
      expect(state.latencyMs).toBe(0);
      expect(state.error).toBeNull();
    });

    it('updates query and format preference', () => {
      useSearchStore.getState().setQuery('friday deploy');
      useSearchStore.getState().setFormatPreference('image');

      expect(useSearchStore.getState().query).toBe('friday deploy');
      expect(useSearchStore.getState().formatPreference).toBe('image');
    });

    it('updates search results and clears loading/error', () => {
      useSearchStore.getState().setSearching(true);
      useSearchStore.getState().setError('Previous error');

      const mockResults = [{ id: 'm1', name: 'This is fine' }];
      useSearchStore.getState().setResults(mockResults, 'panic', 42);

      const state = useSearchStore.getState();
      expect(state.results).toEqual(mockResults);
      expect(state.detectedEmotion).toBe('panic');
      expect(state.latencyMs).toBe(42);
      expect(state.isSearching).toBe(false);
      expect(state.error).toBeNull();
    });

    it('clears results properly', () => {
      useSearchStore.getState().setResults([{ id: 'm1' }], 'joy', 10);
      useSearchStore.getState().clearResults();

      const state = useSearchStore.getState();
      expect(state.results).toEqual([]);
      expect(state.detectedEmotion).toBe('');
      expect(state.latencyMs).toBe(0);
    });
  });

  describe('usePreferencesStore (persisted)', () => {
    it('initializes with default preferences', () => {
      const state = usePreferencesStore.getState();
      expect(state.theme).toBe('dark');
      expect(state.audioEnabled).toBe(false);
      expect(state.nsfwFilter).toBe(true);
      expect(state.searchHistory).toEqual([]);
    });

    it('updates theme, audio, and nsfwFilter', () => {
      usePreferencesStore.getState().setTheme('light');
      usePreferencesStore.getState().setAudioEnabled(true);
      usePreferencesStore.getState().setNsfwFilter(false);

      const state = usePreferencesStore.getState();
      expect(state.theme).toBe('light');
      expect(state.audioEnabled).toBe(true);
      expect(state.nsfwFilter).toBe(false);
    });

    it('adds queries to search history, deduplicates, and caps at 20', () => {
      usePreferencesStore.getState().addToHistory('first query');
      usePreferencesStore.getState().addToHistory('second query');
      usePreferencesStore.getState().addToHistory('first query'); // duplicate should move to front

      let history = usePreferencesStore.getState().searchHistory;
      expect(history[0]).toBe('first query');
      expect(history[1]).toBe('second query');
      expect(history.length).toBe(2);

      // Add 25 more items
      for (let i = 1; i <= 25; i++) {
        usePreferencesStore.getState().addToHistory(`query ${i}`);
      }

      history = usePreferencesStore.getState().searchHistory;
      expect(history.length).toBe(20);
      expect(history[0]).toBe('query 25');
    });

    it('clears search history', () => {
      usePreferencesStore.getState().addToHistory('some query');
      usePreferencesStore.getState().clearHistory();
      expect(usePreferencesStore.getState().searchHistory).toEqual([]);
    });
  });

  describe('useFavoritesStore (persisted)', () => {
    it('initializes with empty favorites', () => {
      expect(useFavoritesStore.getState().favorites).toEqual([]);
    });

    it('adds and deduplicates favorites', () => {
      useFavoritesStore.getState().addFavorite('meme-1');
      useFavoritesStore.getState().addFavorite('meme-2');
      useFavoritesStore.getState().addFavorite('meme-1'); // duplicate

      expect(useFavoritesStore.getState().favorites).toEqual(['meme-1', 'meme-2']);
      expect(useFavoritesStore.getState().isFavorite('meme-1')).toBe(true);
      expect(useFavoritesStore.getState().isFavorite('meme-3')).toBe(false);
    });

    it('removes favorite correctly', () => {
      useFavoritesStore.getState().addFavorite('meme-1');
      useFavoritesStore.getState().addFavorite('meme-2');
      useFavoritesStore.getState().removeFavorite('meme-1');

      expect(useFavoritesStore.getState().favorites).toEqual(['meme-2']);
      expect(useFavoritesStore.getState().isFavorite('meme-1')).toBe(false);
      expect(useFavoritesStore.getState().isFavorite('meme-2')).toBe(true);
    });

    it('clears all favorites', () => {
      useFavoritesStore.getState().addFavorite('meme-1');
      useFavoritesStore.getState().addFavorite('meme-2');
      useFavoritesStore.getState().clearFavorites();

      expect(useFavoritesStore.getState().favorites).toEqual([]);
    });
  });
});
