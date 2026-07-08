import type { MemeRecord, MemeSearchResult } from "@/types";

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error ?? "Request failed");
  }

  return res.json() as Promise<T>;
}

export function analyzeSituation(query: string): Promise<MemeSearchResult> {
  return request("/analyze", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export function searchMemes(q: string, category?: string): Promise<MemeRecord[]> {
  const params = new URLSearchParams({ q, limit: "50" });
  if (category) params.set("category", category);
  return request(`/memes?${params}`);
}

export function getTrending(): Promise<MemeRecord[]> {
  return request("/trending");
}

export function getCategories(): Promise<string[]> {
  return request("/categories");
}

export function createMeme(data: {
  name: string;
  category: string;
  dialogue: string;
  explanation: string;
  keywords: string[];
  videoRef?: string;
  gifRef?: string;
}): Promise<MemeRecord> {
  return request("/admin/memes", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deleteMeme(id: string): Promise<{ success: boolean }> {
  return request(`/admin/memes/${id}`, { method: "DELETE" });
}

export function voteMeme(memeId: string, vote: 1 | -1, sessionId: string) {
  return request("/vote", {
    method: "POST",
    body: JSON.stringify({ memeId, vote, sessionId }),
  });
}

export function exportResult(
  query: string,
  format: "txt" | "json" | "markdown",
  result: MemeSearchResult
): Promise<{ content: string; contentType: string; filename: string }> {
  return request("/export", {
    method: "POST",
    body: JSON.stringify({ query, format, result }),
  });
}

export function healthCheck(): Promise<{ status: string; memeCount: number }> {
  return request("/health");
}
