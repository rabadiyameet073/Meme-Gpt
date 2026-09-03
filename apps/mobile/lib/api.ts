/**
 * MemeGPT Mobile — API Client
 * Connects to the FastAPI backend.
 * Specification: 05_Mobile_App_Completion.md
 */

// Change this to your deployed Railway URL when in production
const API_BASE = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface MemeResult {
  id: number;
  slug: string;
  name: string;
  image_url: string;
  gif_url?: string;
  thumb_url?: string;
  format: "image" | "gif" | "video" | "webp";
  category?: string;
  emotion?: string;
  confidence?: number;
  explanation?: string;
}

export interface SearchResponse {
  matches: MemeResult[];
  query: string;
  total: number;
  latency_ms: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async search(
    query: string,
    formatPreference: string = "gif",
    limit: number = 10
  ): Promise<SearchResponse> {
    const response = await fetch(`${this.baseUrl}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, format_preference: formatPreference, limit }),
    });
    if (!response.ok) throw new Error(`Search failed: ${response.status}`);
    return response.json();
  }

  async getTrending(limit: number = 20): Promise<MemeResult[]> {
    const response = await fetch(`${this.baseUrl}/trending?limit=${limit}`);
    if (!response.ok) throw new Error(`Trending failed: ${response.status}`);
    const data = await response.json();
    return data.memes || data.trending || [];
  }

  async vote(memeId: number, vote: 1 | -1, sessionId: string): Promise<void> {
    await fetch(`${this.baseUrl}/vote`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ meme_id: memeId, vote, session_id: sessionId }),
    });
  }

  async sendFeedback(memeId: number, feedback: string): Promise<void> {
    await fetch(`${this.baseUrl}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ meme_id: memeId, feedback_type: feedback }),
    });
  }
}

export const api = new ApiClient(API_BASE);

export const submitFeedback = (memeId: number | string, feedback: string) =>
  api.sendFeedback(Number(memeId) || 0, feedback);

export const voteMeme = (memeId: number | string, vote: 1 | -1, sessionId: string = "mobile_session") =>
  api.vote(Number(memeId) || 0, vote, sessionId);

