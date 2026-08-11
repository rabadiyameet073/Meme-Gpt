/**
 * useMemeSearch — React hook for AI meme search with loading/error state.
 * Implements: search, format preference, session tracking, result normalization,
 *             recent searches (localStorage), URL ?q= pre-fill.
 * Works with both v1 and v2 API response formats.
 */
'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { searchMemes, submitFeedback, SearchResponse, MemeResult } from '../api';

const SESSION_KEY = 'memegpt_session_id';
const RECENT_KEY  = 'memegpt_recent_searches';

function getSessionId(): string {
  if (typeof window === 'undefined') return 'ssr';
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id = `sess_${Math.random().toString(36).slice(2)}`;
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

function saveToRecent(query: string) {
  if (typeof window === 'undefined') return;
  try {
    const existing: string[] = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
    const updated = [query, ...existing.filter((q) => q !== query)].slice(0, 8);
    localStorage.setItem(RECENT_KEY, JSON.stringify(updated));
  } catch { /* ignore */ }
}

export { getSessionId };
export type FormatPref = 'gif' | 'image' | 'video' | 'any';

interface UseMemeSearchReturn {
  results: MemeResult[];
  primary: MemeResult | null;
  loading: boolean;
  error: string | null;
  queryId: string | null;
  responseTimeMs: number | null;
  cached: boolean;
  emotion: { primary: string; confidence: number } | null;
  detectedCategories: string[];
  search: (query: string) => Promise<void>;
  sendFeedback: (memeId: string, action: string) => Promise<void>;
  reset: () => void;
}

export function useMemeSearch(formatPref: FormatPref = 'gif'): UseMemeSearchReturn {
  const searchParams = useSearchParams();
  const [results, setResults] = useState<MemeResult[]>([]);
  const [primary, setPrimary] = useState<MemeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryId, setQueryId] = useState<string | null>(null);
  const [responseTimeMs, setResponseTimeMs] = useState<number | null>(null);
  const [cached, setCached] = useState(false);
  const [emotion, setEmotion] = useState<{ primary: string; confidence: number } | null>(null);
  const [detectedCategories, setDetectedCategories] = useState<string[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const search = useCallback(async (query: string) => {
    if (!query.trim()) return;

    // Cancel previous in-flight request
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      const res: SearchResponse = await searchMemes({
        query: query.trim(),
        format_preference: formatPref,
        nsfw: false,
        limit: 5,
        session_id: getSessionId(),
      });

      // Handle both v1 (topFive) and v2 (results) formats
      const resultList = res.topFive?.length > 0
        ? res.topFive
        : res.results ?? [];

      setResults(resultList);
      setPrimary(res.primary ?? resultList[0] ?? null);
      setQueryId(res.queryId ?? res.query_id ?? null);
      setResponseTimeMs(res.latencyMs ?? res.response_time_ms ?? null);
      setCached(res.cached ?? false);
      setEmotion(res.emotion ?? null);
      setDetectedCategories(res.detectedCategories ?? []);

      // Save to recent searches
      saveToRecent(query.trim());

      // Log view signal for all results (non-blocking)
      resultList.forEach((meme) => {
        submitFeedback({
          meme_id: meme.id,
          signal: 'view',
          action: 'view',
          session_id: getSessionId(),
        }).catch(() => {});
      });
    } catch (err: any) {
      if (err?.name !== 'AbortError') {
        setError(err?.message || 'Search failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [formatPref]);

  // Pre-fill from URL ?q= param (from landing page chips or sidebar links)
  useEffect(() => {
    const q = searchParams?.get('q');
    if (q) {
      search(q);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendFeedback = useCallback(async (memeId: string, action: string) => {
    await submitFeedback({
      meme_id: memeId,
      signal: action,
      action,
      session_id: getSessionId(),
    }).catch(() => {});
  }, []);

  const reset = useCallback(() => {
    setResults([]);
    setPrimary(null);
    setError(null);
    setQueryId(null);
    setResponseTimeMs(null);
    setCached(false);
    setEmotion(null);
    setDetectedCategories([]);
  }, []);

  return {
    results,
    primary,
    loading,
    error,
    queryId,
    responseTimeMs,
    cached,
    emotion,
    detectedCategories,
    search,
    sendFeedback,
    reset,
  };
}
