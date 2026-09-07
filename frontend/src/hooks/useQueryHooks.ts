import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

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
    staleTime: 10 * 60 * 1000,
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
      if (!resp.ok) throw new Error('Trending fetch failed');
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
      if (!resp.ok) throw new Error('Categories fetch failed');
      return resp.json();
    },
    staleTime: 30 * 60 * 1000,
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
      if (!resp.ok) throw new Error('Health check failed');
      return resp.json();
    },
    staleTime: 60 * 1000,
  });
}
