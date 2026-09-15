import React from 'react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useMemeSearchQuery,
  useTrendingQuery,
  useMemeQuery,
  useCategoriesQuery,
  useStatsQuery,
  useFeedbackMutation,
} from '../hooks/useQueryHooks';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('TanStack Query Hooks (Guide 10)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('useCategoriesQuery fetches category list successfully', async () => {
    const mockCategories = ['work', 'tech', 'gaming', 'relationships'];
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockCategories,
    } as Response);

    const { result } = renderHook(() => useCategoriesQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockCategories);
  });

  it('useTrendingQuery fetches trending memes', async () => {
    const mockTrending = [{ id: 't1', name: 'Distracted Boyfriend' }];
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockTrending,
    } as Response);

    const { result } = renderHook(() => useTrendingQuery('tech'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockTrending);
  });

  it('useMemeQuery fetches a meme by slug', async () => {
    const mockMeme = { id: 'm1', slug: 'drake-hotline', name: 'Drake Hotline Bling' };
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockMeme,
    } as Response);

    const { result } = renderHook(() => useMemeQuery('drake-hotline'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockMeme);
  });

  it('useStatsQuery fetches backend health and stats', async () => {
    const mockHealth = { status: 'healthy', version: '2.0.0' };
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockHealth,
    } as Response);

    const { result } = renderHook(() => useStatsQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockHealth);
  });

  it('useMemeSearchQuery fetches search results when enabled', async () => {
    const mockSearchResponse = {
      results: [{ id: 's1', name: 'Success Kid' }],
      latencyMs: 35,
    };
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => mockSearchResponse,
    } as Response);

    const { result } = renderHook(() => useMemeSearchQuery('winner', 'gif', true), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockSearchResponse);
  });

  it('useFeedbackMutation posts feedback and executes successfully', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'ok' }),
    } as Response);

    const { result } = renderHook(() => useFeedbackMutation(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ memeId: 'm123', type: 'upvote' });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/feedback'),
      expect.objectContaining({
        method: 'POST',
      })
    );
  });
});
