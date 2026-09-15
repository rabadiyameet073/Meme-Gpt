/**
 * MemeGPT Mobile — API Client
 * Specification: 06_Mobile_App_Completion.md
 */

const RAW_API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
const BASE_URL = RAW_API_BASE.replace(/\/+$/, '').replace(/\/api\/v1$/, '');
const API_BASE = `${BASE_URL}/api/v1`;

export interface SearchParams {
  query: string;
  format_preference?: 'gif' | 'image' | 'video';
  limit?: number;
}

export interface MemeResult {
  id: string | number;
  slug: string;
  name: string;
  image_url: string;
  gif_url?: string;
  thumb_url?: string;
  format?: 'image' | 'gif' | 'video' | 'webp';
  formats?: { gif?: string; image?: string; video?: string; webp?: string; mp4?: string };
  preview_url?: string;
  category?: string;
  categories?: string[];
  emotion?: string;
  emotions?: string[];
  confidence?: number;
  explanation?: string;
  dialogue?: string;
}

export interface SearchResponse {
  matches: MemeResult[];
  results?: MemeResult[];
  query: string;
  query_id?: string;
  queryId?: string;
  total: number;
  latency_ms: number;
  response_time_ms?: number;
  cached?: boolean;
}

export const api = {
  async search(
    paramsOrQuery: SearchParams | string,
    formatPreference?: string,
    limit?: number
  ): Promise<SearchResponse> {
    let query = '';
    let format_pref = 'gif';
    let lim = 10;

    if (typeof paramsOrQuery === 'object' && paramsOrQuery !== null) {
      query = paramsOrQuery.query;
      format_pref = paramsOrQuery.format_preference || 'gif';
      lim = paramsOrQuery.limit || 10;
    } else {
      query = paramsOrQuery;
      format_pref = formatPreference || 'gif';
      lim = limit || 10;
    }

    const resp = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        format_preference: format_pref,
        limit: lim,
      }),
    });

    if (!resp.ok) throw new Error(`Search failed: ${resp.status}`);
    const data = await resp.json();

    const matches: MemeResult[] =
      data.results || data.matches || (data.primary ? [data.primary, ...(data.topFive || [])] : []);

    return {
      matches,
      results: matches,
      query,
      query_id: data.query_id || data.queryId || '',
      queryId: data.queryId || data.query_id || '',
      total: data.total || matches.length,
      latency_ms: data.latency_ms || data.latencyMs || 0,
      response_time_ms: data.latency_ms || data.latencyMs || 0,
      cached: Boolean(data.cached),
    };
  },

  async getTrending(limit = 20): Promise<MemeResult[]> {
    const resp = await fetch(`${API_BASE}/trending?limit=${limit}`);
    if (!resp.ok) throw new Error(`Trending failed: ${resp.status}`);
    const data = await resp.json();
    return (
      data.data?.results ||
      data.results ||
      data.memes ||
      data.trending ||
      []
    );
  },

  async getMeme(slug: string): Promise<MemeResult> {
    const resp = await fetch(`${API_BASE}/memes/${slug}`);
    if (!resp.ok) throw new Error(`Meme fetch failed: ${resp.status}`);
    return resp.json();
  },

  async submitFeedback(memeId: string | number, type: 'thumbs_up' | 'thumbs_down' | string, queryId?: string) {
    await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        meme_id: String(memeId),
        feedback_type: type,
        action: type,
        query_id: queryId,
      }),
    });
  },

  async vote(memeId: string | number, vote: 1 | -1, sessionId = 'mobile_session'): Promise<void> {
    await fetch(`${API_BASE}/vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ meme_id: String(memeId), vote, session_id: sessionId }),
    });
  },

  async sendFeedback(memeId: string | number, feedback: string, queryId?: string): Promise<void> {
    return this.submitFeedback(memeId, feedback, queryId);
  },

  getDownloadUrl(slug: string, format = 'gif'): string {
    return `${API_BASE}/memes/${slug}/download?format=${format}`;
  },
};

export const searchMemes = (paramsOrQuery: SearchParams | string, formatPref?: string, limit?: number) =>
  api.search(paramsOrQuery, formatPref, limit);

export const submitFeedback = (memeId: number | string, feedback: string, queryId?: string) =>
  api.submitFeedback(memeId, feedback, queryId);

export const voteMeme = (memeId: number | string, vote: 1 | -1, sessionId = 'mobile_session') =>
  api.vote(memeId, vote, sessionId);

export const getDownloadUrl = (slug: string, format = 'gif') =>
  api.getDownloadUrl(slug, format);

export const getMeme = (slug: string) =>
  api.getMeme(slug);
