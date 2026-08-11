/**
 * useMemeSearch — React Native hook for AI meme search.
 * Same logic as web version, adapted for React Native.
 */
import { useState, useCallback } from 'react';
import { searchMemes, submitFeedback, MemeResult, SearchResponse } from '../lib/api';

export type FormatPref = 'gif' | 'image' | 'video' | 'any';

interface UseMemeSearchReturn {
  results: MemeResult[];
  loading: boolean;
  error: string | null;
  queryId: string | null;
  responseTimeMs: number | null;
  cached: boolean;
  search: (query: string) => Promise<void>;
  sendFeedback: (memeId: string, action: string) => Promise<void>;
  reset: () => void;
}

export function useMemeSearch(formatPref: FormatPref = 'gif'): UseMemeSearchReturn {
  const [results, setResults] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryId, setQueryId] = useState<string | null>(null);
  const [responseTimeMs, setResponseTimeMs] = useState<number | null>(null);
  const [cached, setCached] = useState(false);

  const search = useCallback(async (query: string) => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res: SearchResponse = await searchMemes({
        query: query.trim(),
        format_preference: formatPref,
        nsfw: false,
        limit: 5,
      });
      setResults(res.results);
      setQueryId(res.query_id);
      setResponseTimeMs(res.response_time_ms);
      setCached(res.cached);
      // Log view signals
      res.results.forEach((m) => {
        submitFeedback(m.id, 'view', res.query_id).catch(() => {});
      });
    } catch (e: any) {
      setError(e?.message || 'Search failed. Check your connection.');
    } finally {
      setLoading(false);
    }
  }, [formatPref]);

  const sendFeedback = useCallback(async (memeId: string, action: string) => {
    if (queryId) await submitFeedback(memeId, action, queryId);
  }, [queryId]);

  const reset = useCallback(() => {
    setResults([]);
    setError(null);
    setQueryId(null);
  }, []);

  return { results, loading, error, queryId, responseTimeMs, cached, search, sendFeedback, reset };
}
