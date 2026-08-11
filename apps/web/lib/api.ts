/**
 * MemeGPT API Client — typed fetch wrappers for all endpoints.
 * Base URL: NEXT_PUBLIC_API_URL (default: http://localhost:8000)
 *
 * Supports both the v2 (SearchResponse) and v1 (analyze) response formats.
 */

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

// ── Types ─────────────────────────────────────────────────────────────────

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
  category: string;
  dialogue: string;
  explanation: string;
  confidence: number;
  relevance_score: number;
  emotion_match: string[];
  preview_url: string | null;
  formats: MemeFormats;
  share_url: string | null;
  meme_type: string;
  categories: string[];
  emotions: string[];
  keywords: string[];
  nsfw: boolean;
  popularity_score: number;
  viralScore: number;
  usageCount: number;
  upvotes: number;
  downvotes: number;
}

export interface ParsedIntent {
  emotion: string;
  situation: string;
  tone: string;
  keywords: string[];
  meme_format: string;
}

export interface SearchResponse {
  success: boolean;
  queryId: string;
  query_id?: string;
  primary: MemeResult | null;
  topFive: MemeResult[];
  alternatives: MemeResult[];
  results?: MemeResult[];
  emotion: { primary: string; confidence: number; all: Record<string, number> };
  intent_parsed?: ParsedIntent | null;
  detectedCategories: string[];
  detectedTags: string[];
  gifs: string[];
  viralSuggestions: MemeResult[];
  latencyMs: number;
  response_time_ms?: number;
  cached: boolean;
}

export interface SearchRequest {
  query: string;
  format_preference?: 'gif' | 'image' | 'video' | 'any';
  nsfw?: boolean;
  limit?: number;
  session_id?: string;
}

export interface FeedbackRequest {
  query_id?: string;
  meme_id: string;
  signal: string;
  action?: string;
  session_id?: string;
  format?: string;
}

export interface MemeListItem {
  id: string;
  name: string;
  slug: string;
  category: string;
  dialogue: string;
  explanation: string;
  keywords: string[];
  imageRef: string | null;
  videoRef: string | null;
  gifRef: string | null;
  viralScore: number;
  usageCount: number;
  upvotes: number;
  downvotes: number;
  createdAt: string | null;
}

export interface MemeListResponse {
  items: MemeListItem[];
  total: number;
  page: number;
  pageSize: number;
}

// ── Normalize helper ──────────────────────────────────────────────────────

function normalizeResult(raw: any): MemeResult {
  return {
    id: raw.id ?? '',
    name: raw.name ?? 'Unknown',
    slug: raw.slug ?? raw.name?.toLowerCase().replace(/\s+/g, '-') ?? '',
    category: raw.category ?? 'general',
    dialogue: raw.dialogue ?? '',
    explanation: raw.explanation ?? '',
    confidence: raw.confidence ?? raw.relevance_score ?? 0,
    relevance_score: raw.relevance_score ?? raw.confidence ?? 0,
    emotion_match: raw.emotion_match ?? raw.emotions ?? [],
    preview_url: raw.preview_url ?? raw.thumbUrl ?? raw.imageRef ?? raw.formats?.image ?? null,
    formats: raw.formats ?? {
      gif: raw.gifRef ?? null,
      image: raw.imageRef ?? raw.preview_url ?? null,
      video: raw.videoRef ?? null,
      webp: raw.imageRef ?? null,
    },
    share_url: raw.share_url ?? raw.shareUrl ?? null,
    meme_type: raw.meme_type ?? 'reaction',
    categories: raw.categories ?? [raw.category ?? 'general'],
    emotions: raw.emotions ?? raw.emotion_match ?? [],
    keywords: raw.keywords ?? [],
    nsfw: raw.nsfw ?? false,
    popularity_score: raw.popularity_score ?? raw.viralScore ?? 0,
    viralScore: raw.viralScore ?? raw.popularity_score ?? 0,
    usageCount: raw.usageCount ?? 0,
    upvotes: raw.upvotes ?? 0,
    downvotes: raw.downvotes ?? 0,
  };
}

// ── Search ─────────────────────────────────────────────────────────────────

export async function searchMemes(req: SearchRequest): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/api/v1/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: req.query,
      format_preference: req.format_preference ?? 'gif',
      formatPreference: req.format_preference ?? 'gif',
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.message || `Search failed: ${res.status}`);
  }

  const data = await res.json();

  // Normalize: support both v1 (primary/topFive) and v2 (results) formats
  return {
    success: data.success ?? true,
    queryId: data.queryId ?? data.query_id ?? '',
    query_id: data.query_id ?? data.queryId ?? '',
    primary: data.primary ? normalizeResult(data.primary) : null,
    topFive: (data.topFive ?? data.results ?? []).map(normalizeResult),
    alternatives: (data.alternatives ?? []).map(normalizeResult),
    results: (data.results ?? data.topFive ?? []).map(normalizeResult),
    emotion: data.emotion ?? { primary: 'humor', confidence: 0.5, all: {} },
    intent_parsed: data.intent_parsed ?? null,
    detectedCategories: data.detectedCategories ?? [],
    detectedTags: data.detectedTags ?? [],
    gifs: data.gifs ?? [],
    viralSuggestions: (data.viralSuggestions ?? []).map(normalizeResult),
    latencyMs: data.latencyMs ?? data.response_time_ms ?? 0,
    response_time_ms: data.response_time_ms ?? data.latencyMs ?? 0,
    cached: data.cached ?? false,
  };
}

// ── Meme detail ────────────────────────────────────────────────────────────

export async function getMeme(slug: string): Promise<MemeListItem> {
  const res = await fetch(`${API_BASE}/api/v1/memes/${slug}`);
  if (!res.ok) throw new Error(`Meme not found: ${slug}`);
  return res.json();
}

export async function getAllMemeSlugs(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/memes?limit=100`);
  if (!res.ok) return [];
  const data: MemeListResponse = await res.json();
  return data.items.map((m) => m.slug);
}

export function getDownloadUrl(slug: string, format: 'gif' | 'image' | 'mp4' | 'webp' = 'gif'): string {
  return `${API_BASE}/api/v1/memes/${slug}/download?format=${format}`;
}

// ── Trending ───────────────────────────────────────────────────────────────

export async function getTrending(category = 'all', limit = 12): Promise<MemeListItem[]> {
  const params = new URLSearchParams({ category, limit: String(limit) });
  const res = await fetch(`${API_BASE}/api/v1/trending?${params}`);
  if (!res.ok) throw new Error('Failed to fetch trending');
  const data = await res.json();
  return Array.isArray(data) ? data : [];
}

// ── Meme list ──────────────────────────────────────────────────────────────

export async function listMemes(
  category = '',
  page = 1,
  limit = 50,
  q = ''
): Promise<MemeListResponse> {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  if (q) params.set('q', q);
  params.set('page', String(page));
  params.set('limit', String(limit));

  const res = await fetch(`${API_BASE}/api/memes?${params}`);
  if (!res.ok) throw new Error('Failed to fetch memes');
  return res.json();
}

// ── Categories ─────────────────────────────────────────────────────────────

export async function getCategories(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/categories`);
  if (!res.ok) return [];
  return res.json();
}

// ── Favorites ──────────────────────────────────────────────────────────────

export async function getFavorites(sessionId: string): Promise<MemeListItem[]> {
  const res = await fetch(`${API_BASE}/api/favorites?sessionId=${sessionId}`);
  if (!res.ok) return [];
  return res.json();
}

export async function toggleFavorite(memeId: string, sessionId: string): Promise<{ isFavorite: boolean }> {
  const res = await fetch(`${API_BASE}/api/favorites/toggle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ memeId, sessionId }),
  });
  if (!res.ok) throw new Error('Failed to toggle favorite');
  return res.json();
}

// ── Feedback ───────────────────────────────────────────────────────────────

export async function submitFeedback(req: FeedbackRequest): Promise<void> {
  await fetch(`${API_BASE}/api/v1/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      meme_id: req.meme_id,
      signal: req.signal ?? req.action ?? 'view',
      format: req.format ?? 'image',
      session_id: req.session_id ?? 'anonymous',
    }),
  }).catch(() => {});
}

// ── Vote ───────────────────────────────────────────────────────────────────

export async function submitVote(memeId: string, vote: 1 | -1, sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/api/vote`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ memeId, vote, sessionId }),
  });
}

// ── Health ─────────────────────────────────────────────────────────────────

export async function getHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  return res.json();
}

// ── Stats ──────────────────────────────────────────────────────────────────

export async function getStats() {
  const res = await fetch(`${API_BASE}/api/stats`);
  return res.json();
}
