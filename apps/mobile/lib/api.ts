/**
 * MemeGPT Mobile API Client — mirrors web lib/api.ts for React Native.
 * Uses Axios for reliability (as per tech stack docs).
 */

const API_BASE = (process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1';

export interface MemeFormats {
  gif: string | null;
  image: string | null;
  video: string | null;
  webp: string | null;
}

export interface MemeResult {
  id: string;
  name: string;
  slug: string;
  relevance_score: number;
  emotion_match: string[];
  preview_url: string | null;
  formats: MemeFormats;
  share_url: string | null;
  meme_type: string;
  categories: string[];
  emotions: string[];
  nsfw: boolean;
  popularity_score: number;
}

export interface SearchRequest {
  query: string;
  format_preference?: 'gif' | 'image' | 'video' | 'any';
  nsfw?: boolean;
  limit?: number;
  session_id?: string;
}

export interface SearchResponse {
  success: boolean;
  query_id: string;
  results: MemeResult[];
  response_time_ms: number;
  cached: boolean;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.message || `API error: ${res.status}`);
  }
  return res.json();
}

export async function searchMemes(req: SearchRequest): Promise<SearchResponse> {
  return apiFetch('/search', {
    method: 'POST',
    body: JSON.stringify({
      query: req.query,
      format_preference: req.format_preference ?? 'gif',
      nsfw: req.nsfw ?? false,
      limit: req.limit ?? 5,
      session_id: req.session_id,
    }),
  });
}

export async function getTrending(category = 'all', limit = 20): Promise<MemeResult[]> {
  return apiFetch(`/trending?category=${category}&limit=${limit}`);
}

export async function getMeme(slug: string) {
  return apiFetch(`/memes/${slug}`);
}

export async function submitFeedback(memeId: string, action: string, queryId?: string) {
  return apiFetch('/feedback', {
    method: 'POST',
    body: JSON.stringify({ meme_id: memeId, action, query_id: queryId }),
  });
}

export function getDownloadUrl(slug: string, format = 'gif'): string {
  return `${API_BASE}/memes/${slug}/download?format=${format}`;
}
