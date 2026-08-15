/**
 * MemeGPT — Frontend API Client Module
 * Matches specifications from 04_Frontend/API_Integration.md
 */

import type { MemeRecord, MemeSearchResult } from "@/types";

export const API_BASE =
  (typeof process !== "undefined" && process.env?.NEXT_PUBLIC_API_URL) ||
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_URL) ||
  "/api";

export class ApiError extends Error {
  status: number;
  data: any;
  retry_after?: number;
  code?: string;

  constructor(status: number, data: any) {
    const message =
      data?.error?.message ||
      data?.message ||
      data?.detail ||
      `API Error ${status}`;
    super(message);
    this.status = status;
    this.data = data;
    this.retry_after = data?.retry_after;
    this.code = data?.error?.code || data?.code;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new ApiError(response.status, data);
  }

  return data as T;
}

export interface SearchResponse {
  primary: any;
  topFive: any[];
  alternatives: any[];
  detectedCategories: string[];
  detectedTags: string[];
  cached?: boolean;
  latencyMs: number;
}

export interface MemeDetail extends MemeRecord {}

export interface TrendingResponse {
  items?: MemeRecord[];
  trending?: MemeRecord[];
  category?: string;
  total?: number;
}

export interface FeedbackParams {
  queryId?: string;
  memeId: string;
  action: "copy" | "download" | "upvote" | "downvote" | "share";
  format?: string;
}

// Exported API client object
export const api = {
  // ── v1 API Specification Endpoints ──────────────────────────────────────────
  search: (query: string, format: string = "gif", limit: number = 5) =>
    apiRequest<SearchResponse>("/v1/search", {
      method: "POST",
      body: JSON.stringify({
        query,
        format_preference: format,
        limit,
        session_id: getSessionId(),
      }),
    }),

  getMeme: (slug: string) => apiRequest<MemeDetail>(`/v1/memes/${slug}`),

  getTrending: (category: string = "all", limit: number = 20) =>
    apiRequest<TrendingResponse | MemeRecord[]>(
      `/v1/trending?category=${category}&limit=${limit}`
    ),

  sendFeedback: (queryId: string, memeId: string, action: string, format = "image") =>
    apiRequest<{ recorded?: boolean; status?: string }>("/v1/feedback", {
      method: "POST",
      body: JSON.stringify({
        query_id: queryId,
        meme_id: memeId,
        signal: action,
        format,
        session_id: getSessionId(),
      }),
    }),

  // ── Compatibility and Utility Endpoints ─────────────────────────────────────
  analyze: (query: string) =>
    apiRequest<MemeSearchResult>("/analyze", {
      method: "POST",
      body: JSON.stringify({ query }),
    }),

  searchMemes: async (
    q = "",
    category = "",
    page = 1,
    limit = 50
  ): Promise<any> => {
    const p = new URLSearchParams({
      limit: limit.toString(),
      page: page.toString(),
    });
    if (q) p.set("q", q);
    if (category) p.set("category", category);
    return apiRequest(`/memes?${p}`);
  },

  categories: () => apiRequest<string[]>("/categories"),

  stats: () => apiRequest<any>("/stats"),

  favorites: (sessionId: string) =>
    apiRequest<MemeRecord[]>(
      `/favorites?sessionId=${encodeURIComponent(sessionId)}`
    ),

  toggleFavorite: (memeId: string, sessionId: string) =>
    apiRequest<{ isFavorite: boolean }>("/favorites/toggle", {
      method: "POST",
      body: JSON.stringify({ memeId, sessionId }),
    }),

  createMeme: (data: any) =>
    apiRequest<MemeRecord>("/admin/memes", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteMeme: (id: string) =>
    apiRequest<{ success: boolean }>(`/admin/memes/${id}`, {
      method: "DELETE",
    }),

  vote: (memeId: string, vote: 1 | -1, sessionId: string) =>
    apiRequest<{ success: boolean }>("/vote", {
      method: "POST",
      body: JSON.stringify({ memeId, vote, sessionId }),
    }),

  export: (query: string, format: string, result: MemeSearchResult) =>
    apiRequest<{ content: string; filename: string }>("/export", {
      method: "POST",
      body: JSON.stringify({ query, format, result }),
    }),

  health: () =>
    apiRequest<{
      status: string;
      service: string;
      version: string;
      uptime_seconds?: number;
      modelsLoaded?: boolean;
    }>("/health"),
};

export function getSessionId(): string {
  const key = "memegpt-session";
  if (typeof window === "undefined" || !window.localStorage) {
    return "anonymous-session";
  }
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID ? crypto.randomUUID() : `sess-${Date.now()}`;
    localStorage.setItem(key, id);
  }
  return id;
}

export function download(content: string, filename: string): void {
  if (typeof window === "undefined") return;
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
