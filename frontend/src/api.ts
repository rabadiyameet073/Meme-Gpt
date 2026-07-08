/* ── Types ─────────────────────────────────────────────────── */

export interface MemeMatch {
  id: string;
  name: string;
  category: string;
  dialogue: string;
  explanation: string;
  confidence: number;
  videoRef?: string | null;
  gifRef?: string | null;
  viralScore: number;
  usageCount: number;
}

export interface MemeSearchResult {
  primary: MemeMatch;
  topFive: MemeMatch[];
  alternatives: MemeMatch[];
  detectedCategories: string[];
  detectedTags: string[];
  gifs: string[];
  viralSuggestions: MemeMatch[];
  latencyMs: number;
}

export interface MemeRecord extends MemeMatch {
  keywords: string[];
  upvotes: number;
  downvotes: number;
}

/* ── HTTP client ────────────────────────────────────────────── */

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || err.error || "Request failed");
  }
  return res.json();
}

/* ── API surface ────────────────────────────────────────────── */

export const api = {
  analyze: (query: string) =>
    request<MemeSearchResult>("/analyze", { method: "POST", body: JSON.stringify({ query }) }),

  searchMemes: (q = "", category = "") => {
    const p = new URLSearchParams({ limit: "100" });
    if (q) p.set("q", q);
    if (category) p.set("category", category);
    return request<MemeRecord[]>(`/memes?${p}`);
  },

  trending: () => request<MemeRecord[]>("/trending"),

  categories: () => request<string[]>("/categories"),

  createMeme: (data: {
    name: string;
    category: string;
    dialogue: string;
    explanation: string;
    keywords: string[];
    videoRef?: string;
    gifRef?: string;
  }) => request<MemeRecord>("/admin/memes", { method: "POST", body: JSON.stringify(data) }),

  deleteMeme: (id: string) =>
    request<{ success: boolean }>(`/admin/memes/${id}`, { method: "DELETE" }),

  vote: (memeId: string, vote: 1 | -1, sessionId: string) =>
    request<{ success: boolean }>("/vote", {
      method: "POST",
      body: JSON.stringify({ memeId, vote, sessionId }),
    }),

  export: (query: string, format: string, result: MemeSearchResult) =>
    request<{ content: string; filename: string }>("/export", {
      method: "POST",
      body: JSON.stringify({ query, format, result }),
    }),

  health: () => request<{ status: string; memeCount: number }>("/health"),
};

/* ── Utilities ──────────────────────────────────────────────── */

export function getSessionId(): string {
  const key = "memegpt-session";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

export function download(content: string, filename: string): void {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
