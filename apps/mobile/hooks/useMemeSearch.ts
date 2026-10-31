/**
 * useMemeSearch — React Native hook for AI meme search.
 * Same logic as web version, adapted for React Native.
 *
 * Results are written to the offline cache on every successful search, and the
 * cache is used as a fallback when the request fails, so the app keeps showing
 * something useful on a train with no signal instead of a bare error.
 */
import { useState, useCallback } from 'react';
import { searchMemes, submitFeedback, MemeResult, SearchResponse } from '../lib/api';
import { useOfflineCache, CachedMeme } from './useOfflineCache';

export type FormatPref = 'gif' | 'image' | 'video' | 'any';

interface UseMemeSearchReturn {
  results: MemeResult[];
  loading: boolean;
  error: string | null;
  /** True when the results shown come from the offline cache. */
  offline: boolean;
  queryId: string | null;
  responseTimeMs: number | null;
  cached: boolean;
  search: (query: string) => Promise<void>;
  sendFeedback: (memeId: string, action: string) => Promise<void>;
  reset: () => void;
}

function toMemeResult(meme: CachedMeme): MemeResult {
  return {
    id: meme.id,
    slug: meme.slug,
    name: meme.name,
    image_url: meme.image_url,
    gif_url: meme.gif_url,
    thumb_url: meme.thumb_url,
    explanation: meme.explanation,
  };
}

function toCachedMeme(meme: MemeResult): CachedMeme {
  return {
    id: String(meme.id),
    slug: meme.slug,
    name: meme.name,
    image_url: meme.image_url,
    gif_url: meme.gif_url,
    thumb_url: meme.thumb_url,
    explanation: meme.explanation,
  };
}

export function useMemeSearch(formatPref: FormatPref = 'gif'): UseMemeSearchReturn {
  const [results, setResults] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offline, setOffline] = useState(false);
  const [queryId, setQueryId] = useState<string | null>(null);
  const [responseTimeMs, setResponseTimeMs] = useState<number | null>(null);
  const [cached, setCached] = useState(false);
  const { cacheMemes, getCachedMemes } = useOfflineCache();

  const search = useCallback(async (query: string) => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res: SearchResponse = await searchMemes({
        query: query.trim(),
        format_preference: formatPref === 'any' ? 'gif' : formatPref,
        limit: 5,
      });
      const matches = res.results || res.matches || [];
      setResults(matches);
      setOffline(false);
      setQueryId(res.query_id || res.queryId || null);
      setResponseTimeMs(res.response_time_ms || res.latency_ms || null);
      setCached(Boolean(res.cached));
      // Keep the last 50 seen memes available without a connection.
      cacheMemes(matches.map(toCachedMeme)).catch(() => {});
      // Log view signals
      matches.forEach((m) => {
        submitFeedback(m.id, 'view', res.query_id || res.queryId).catch(() => {});
      });
    } catch (e: any) {
      const offlineMemes = getCachedMemes();
      if (offlineMemes.length > 0) {
        setResults(offlineMemes.map(toMemeResult));
        setOffline(true);
        setError(null);
      } else {
        setError(e?.message || 'Search failed. Check your connection.');
      }
    } finally {
      setLoading(false);
    }
  }, [formatPref, cacheMemes, getCachedMemes]);

  const sendFeedback = useCallback(async (memeId: string, action: string) => {
    if (queryId) await submitFeedback(memeId, action, queryId);
  }, [queryId]);

  const reset = useCallback(() => {
    setResults([]);
    setError(null);
    setOffline(false);
    setQueryId(null);
  }, []);

  return {
    results, loading, error, offline, queryId, responseTimeMs, cached,
    search, sendFeedback, reset,
  };
}
