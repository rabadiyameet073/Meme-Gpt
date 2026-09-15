/**
 * MemeGPT — Frontend Auth Module
 * Custom JWT Flow for Vite SPA supporting localStorage + cookies,
 * Google & GitHub OAuth initiation, and profile synchronization.
 */
import { apiRequest, API_BASE } from "./api";
import type { User, AuthResponse } from "@/types";

const ACCESS_TOKEN_KEY = "memegpt_access_token";
const REFRESH_TOKEN_KEY = "memegpt_refresh_token";
const USER_CACHE_KEY = "memegpt_user";

export function getStoredToken(): string | null {
  try {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getStoredRefreshToken(): string | null {
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setStoredTokens(accessToken: string, refreshToken?: string, user?: User) {
  try {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
    if (user) {
      localStorage.setItem(USER_CACHE_KEY, JSON.stringify(user));
    }
  } catch (e) {
    console.warn("Could not save auth tokens to localStorage", e);
  }
}

export function clearStoredTokens() {
  try {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_CACHE_KEY);
  } catch (e) {
    console.warn("Could not clear auth tokens", e);
  }
}

export function getCachedUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export async function fetchCurrentUser(): Promise<User | null> {
  const token = getStoredToken();
  if (!token) {
    return null;
  }

  try {
    const res = await apiRequest<{ user: User }>("/api/v1/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (res?.user) {
      try {
        localStorage.setItem(USER_CACHE_KEY, JSON.stringify(res.user));
      } catch {}
      return res.user;
    }
    return null;
  } catch (err: any) {
    if (err?.status === 401) {
      // Try refresh
      const refreshed = await refreshSession();
      if (refreshed?.user) {
        return refreshed.user;
      }
      clearStoredTokens();
    }
    return null;
  }
}

export async function loginWithEmail(email: string, password: string): Promise<AuthResponse> {
  const res = await apiRequest<AuthResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (res.access_token) {
    setStoredTokens(res.access_token, res.refresh_token, res.user);
  }
  return res;
}

export async function registerWithEmail(
  email: string,
  password: string,
  name?: string
): Promise<AuthResponse> {
  const res = await apiRequest<AuthResponse>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, name }),
  });
  if (res.access_token) {
    setStoredTokens(res.access_token, res.refresh_token, res.user);
  }
  return res;
}

export async function refreshSession(): Promise<AuthResponse | null> {
  const refreshToken = getStoredRefreshToken();
  try {
    const res = await apiRequest<AuthResponse>("/api/v1/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken || undefined }),
    });
    if (res.access_token) {
      setStoredTokens(res.access_token, res.refresh_token, res.user);
      return res;
    }
    return null;
  } catch {
    clearStoredTokens();
    return null;
  }
}

export async function logout(): Promise<void> {
  try {
    await apiRequest("/api/v1/auth/logout", { method: "POST" });
  } catch {}
  clearStoredTokens();
}

export async function updateProfile(data: Partial<User>): Promise<User> {
  const token = getStoredToken();
  const res = await apiRequest<{ user: User }>("/api/v1/auth/me", {
    method: "PUT",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: JSON.stringify(data),
  });
  if (res?.user) {
    try {
      localStorage.setItem(USER_CACHE_KEY, JSON.stringify(res.user));
    } catch {}
    return res.user;
  }
  throw new Error("Could not update profile");
}

export async function getGoogleOAuthUrl(): Promise<string> {
  const res = await apiRequest<{ url: string }>("/api/v1/auth/google/login");
  return res.url;
}

export async function getGithubOAuthUrl(): Promise<string> {
  const res = await apiRequest<{ url: string }>("/api/v1/auth/github/login");
  return res.url;
}
