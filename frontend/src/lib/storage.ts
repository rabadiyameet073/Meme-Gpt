/**
 * MemeGPT — LocalStorage Manager for Favorites & Collections
 * Specification: 08_Features/Favorites_Collections.md
 */

export interface SavedMeme {
  memeId: string;
  name: string;
  thumbnailUrl: string;
  savedAt: string; // ISO date
  collection: string; // "Favorites" by default
}

export interface Collection {
  name: string;
  createdAt: string;
  memeCount: number;
}

export interface RecentMeme {
  memeId: string;
  name: string;
  thumbnailUrl: string;
  viewedAt: string;
}

export interface LocalStorageSchema {
  favorites: SavedMeme[];
  collections: Collection[];
  recentlyViewed: RecentMeme[];
  recentlyCopied?: RecentMeme[];
}

const STORAGE_KEY = "memegpt_user_data";
const MAX_FAVORITES_CAPACITY = 200;
const MAX_RECENT_VIEWED = 20;
const MAX_RECENT_COPIED = 10;

function getInitialData(): LocalStorageSchema {
  return {
    favorites: [],
    collections: [
      {
        name: "Favorites",
        createdAt: new Date().toISOString(),
        memeCount: 0,
      },
    ],
    recentlyViewed: [],
    recentlyCopied: [],
  };
}

export function loadUserData(): LocalStorageSchema {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return getInitialData();
    const parsed = JSON.parse(raw);
    return {
      favorites: Array.isArray(parsed.favorites) ? parsed.favorites : [],
      collections: Array.isArray(parsed.collections) && parsed.collections.length > 0 ? parsed.collections : getInitialData().collections,
      recentlyViewed: Array.isArray(parsed.recentlyViewed) ? parsed.recentlyViewed : [],
      recentlyCopied: Array.isArray(parsed.recentlyCopied) ? parsed.recentlyCopied : [],
    };
  } catch {
    return getInitialData();
  }
}

export function saveUserData(data: LocalStorageSchema): boolean {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    return true;
  } catch (err) {
    console.warn("localStorage quota exceeded or unavailable:", err);
    return false;
  }
}

/**
 * Save meme to a collection. If already present, updates timestamp and collection without duplicating.
 */
export function saveMeme(
  meme: { id: string; name: string; formats?: { image?: string; thumb?: string }; preview_url?: string },
  collection: string = "Favorites"
): boolean {
  const data = loadUserData();
  const now = new Date().toISOString();
  const thumb = meme.formats?.thumb || meme.formats?.image || meme.preview_url || "";

  // Check if exists
  const existingIdx = data.favorites.findIndex((m) => m.memeId === meme.id);
  if (existingIdx >= 0) {
    data.favorites[existingIdx].savedAt = now;
    data.favorites[existingIdx].collection = collection;
    data.favorites[existingIdx].name = meme.name || data.favorites[existingIdx].name;
    data.favorites[existingIdx].thumbnailUrl = thumb || data.favorites[existingIdx].thumbnailUrl;
  } else {
    if (data.favorites.length >= MAX_FAVORITES_CAPACITY) {
      data.favorites.shift(); // Trim oldest
    }
    data.favorites.push({
      memeId: meme.id,
      name: meme.name,
      thumbnailUrl: thumb,
      savedAt: now,
      collection: collection || "Favorites",
    });
  }

  // Update collections count
  updateCollectionCounts(data);
  return saveUserData(data);
}

/**
 * Remove meme from favorites/collections.
 */
export function removeSavedMeme(memeId: string): boolean {
  const data = loadUserData();
  data.favorites = data.favorites.filter((m) => m.memeId !== memeId);
  updateCollectionCounts(data);
  return saveUserData(data);
}

/**
 * Create a new custom collection.
 */
export function createCustomCollection(name: string): boolean {
  const trimmed = name.trim();
  if (!trimmed) return false;
  const data = loadUserData();
  if (data.collections.some((c) => c.name.toLowerCase() === trimmed.toLowerCase())) {
    return false;
  }
  data.collections.push({
    name: trimmed,
    createdAt: new Date().toISOString(),
    memeCount: 0,
  });
  return saveUserData(data);
}

/**
 * Delete collection. Automatically moves contained memes to "Favorites".
 */
export function deleteCustomCollection(name: string): boolean {
  if (name.toLowerCase() === "favorites") return false;
  const data = loadUserData();
  data.collections = data.collections.filter((c) => c.name.toLowerCase() !== name.toLowerCase());
  for (const m of data.favorites) {
    if (m.collection.toLowerCase() === name.toLowerCase()) {
      m.collection = "Favorites";
    }
  }
  updateCollectionCounts(data);
  return saveUserData(data);
}

/**
 * Record recently viewed meme (capped at 20).
 */
export function recordRecentView(meme: { id: string; name: string; formats?: { thumb?: string; image?: string }; preview_url?: string }): void {
  const data = loadUserData();
  const now = new Date().toISOString();
  const thumb = meme.formats?.thumb || meme.formats?.image || meme.preview_url || "";

  data.recentlyViewed = data.recentlyViewed.filter((m) => m.memeId !== meme.id);
  data.recentlyViewed.unshift({
    memeId: meme.id,
    name: meme.name,
    thumbnailUrl: thumb,
    viewedAt: now,
  });
  if (data.recentlyViewed.length > MAX_RECENT_VIEWED) {
    data.recentlyViewed = data.recentlyViewed.slice(0, MAX_RECENT_VIEWED);
  }
  saveUserData(data);
}

/**
 * Record recently copied meme (capped at 10).
 */
export function recordRecentCopy(meme: { id: string; name: string; formats?: { thumb?: string; image?: string }; preview_url?: string }): void {
  const data = loadUserData();
  const now = new Date().toISOString();
  const thumb = meme.formats?.thumb || meme.formats?.image || meme.preview_url || "";

  data.recentlyCopied = (data.recentlyCopied || []).filter((m) => m.memeId !== meme.id);
  data.recentlyCopied.unshift({
    memeId: meme.id,
    name: meme.name,
    thumbnailUrl: thumb,
    viewedAt: now,
  });
  if (data.recentlyCopied.length > MAX_RECENT_COPIED) {
    data.recentlyCopied = data.recentlyCopied.slice(0, MAX_RECENT_COPIED);
  }
  saveUserData(data);
}

function updateCollectionCounts(data: LocalStorageSchema): void {
  for (const col of data.collections) {
    col.memeCount = data.favorites.filter((m) => m.collection === col.name).length;
  }
}
