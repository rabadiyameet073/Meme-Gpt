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

export class ValidationError extends Error {
  errors: Array<{ field: string; message: string }>;
  status: number;

  constructor(errors: Array<{ field: string; message: string }>) {
    const summary = errors.map((e) => `${e.field}: ${e.message}`).join(", ") || "Validation Error";
    super(summary);
    this.name = "ValidationError";
    this.status = 422;
    this.errors = errors;
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

  if (response.status === 422) {
    const details = Array.isArray(data?.detail)
      ? data.detail.map((d: any) => ({
          field: Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : d.field || "query",
          message: d.msg || d.message || "Invalid value",
        }))
      : Array.isArray(data?.details)
      ? data.details
      : [{ field: "query", message: data?.message || "Validation failed" }];
    throw new ValidationError(details);
  }

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
  data?: {
    category?: string;
    period?: string;
    results?: MemeRecord[];
    meta?: any;
  };
  results?: MemeRecord[];
}

export interface FeedbackParams {
  queryId?: string;
  memeId: string;
  action: "copy" | "download" | "upvote" | "downvote" | "share" | string;
  format?: string;
}

// Exported API client object
export const api = {
  // ── v1 API Specification Endpoints ──────────────────────────────────────────
  search: (
    query: string,
    formatOrOptions: string | { format?: string; limit?: number } = "gif",
    limitParam: number = 5
  ) => {
    let format = "gif";
    let limit = limitParam;

    if (typeof formatOrOptions === "object" && formatOrOptions !== null) {
      format = formatOrOptions.format || "gif";
      limit = formatOrOptions.limit ?? limitParam;
    } else if (typeof formatOrOptions === "string") {
      format = formatOrOptions || "gif";
    }

    return apiRequest<SearchResponse>("/v1/search", {
      method: "POST",
      body: JSON.stringify({
        query,
        format_preference: format,
        limit,
        session_id: getSessionId(),
      }),
    });
  },

  getMeme: (slug: string) => apiRequest<MemeDetail>(`/v1/memes/${slug}`),

  getTrending: async (
    categoryOrOptions?: string | { category?: string; limit?: number; period?: string; offset?: number },
    limitParam: number = 20,
    periodParam: string = "24h"
  ) => {
    let category = "all";
    let limit = 20;
    let period = "24h";
    let offset = 0;

    if (typeof categoryOrOptions === "object" && categoryOrOptions !== null) {
      category = categoryOrOptions.category || "all";
      limit = categoryOrOptions.limit ?? 20;
      period = categoryOrOptions.period || "24h";
      offset = categoryOrOptions.offset ?? 0;
    } else if (typeof categoryOrOptions === "string") {
      category = categoryOrOptions || "all";
      limit = limitParam;
      period = periodParam;
    }

    const query = new URLSearchParams({
      category,
      limit: limit.toString(),
      period,
      offset: offset.toString(),
    });

    return apiRequest<TrendingResponse | MemeRecord[]>(`/v1/trending?${query.toString()}`);
  },

  trending: async (
    categoryOrOptions?: string | { category?: string; limit?: number; period?: string; offset?: number },
    limitParam: number = 20,
    periodParam: string = "24h"
  ) => {
    return api.getTrending(categoryOrOptions, limitParam, periodParam);
  },

  sendFeedback: (
    arg1: string | FeedbackParams,
    arg2?: string,
    arg3?: string,
    arg4?: string
  ) => {
    let query_id: string | undefined;
    let meme_id: string;
    let action: string;
    let format = "image";

    if (typeof arg1 === "object" && arg1 !== null) {
      query_id = arg1.queryId;
      meme_id = arg1.memeId;
      action = arg1.action;
      format = arg1.format || "image";
    } else if (arg4 !== undefined) {
      query_id = arg1;
      meme_id = arg2!;
      action = arg3!;
      format = arg4;
    } else if (arg3 !== undefined) {
      meme_id = arg1;
      action = arg2!;
      format = arg3;
    } else if (arg2 !== undefined) {
      meme_id = arg1;
      action = arg2;
    } else {
      meme_id = arg1;
      action = "click";
    }

    return apiRequest<{ recorded?: boolean; status?: string; message?: string }>("/v1/feedback", {
      method: "POST",
      body: JSON.stringify({
        query_id,
        meme_id,
        action,
        signal: action,
        format,
        session_id: getSessionId(),
      }),
    });
  },

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
