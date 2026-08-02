# MemeGPT — Favorites & Collections Feature

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Feature specification for saving memes to personal favorites and organizing into custom collections.

---

## Feature Overview

Users can save memes they like and organize them into named collections for quick access later.

### Storage Strategy

| User Type | Storage | Sync | Capacity |
|---|---|---|---|
| Anonymous | localStorage | Device-only | 200 memes |
| Registered (Phase 3) | Supabase | Cross-device | Unlimited |

---

## User Stories

1. **As a user**, I want to save a meme so I can find it quickly next time
2. **As a user**, I want to organize memes into collections (e.g., "Work", "Friend Group")
3. **As a user**, I want to see my recently viewed memes
4. **As a user**, I want to quickly copy a previously saved meme

---

## localStorage Schema

```typescript
interface LocalStorage {
  favorites: SavedMeme[];
  collections: Collection[];
  recentlyViewed: RecentMeme[];
}

interface SavedMeme {
  memeId: string;
  name: string;
  thumbnailUrl: string;
  savedAt: string; // ISO date
  collection: string; // "Favorites" by default
}

interface Collection {
  name: string;
  createdAt: string;
  memeCount: number;
}

interface RecentMeme {
  memeId: string;
  name: string;
  thumbnailUrl: string;
  viewedAt: string;
}
```

---

## Default Collections

| Collection | Icon | Auto-populated |
|---|---|---|
| ⭐ Favorites | Star | User adds manually |
| 🕐 Recently Viewed | Clock | Last 20 memes viewed |
| 📋 Recently Copied | Clipboard | Last 10 memes copied |

---

## Edge Cases

| Scenario | Behavior |
|---|---|
| localStorage full | Show warning, offer to clear old entries |
| Same meme saved twice | Update timestamp, don't duplicate |
| Delete collection with memes | Move memes to "Favorites" |
| Browser cleared storage | Graceful empty state, no errors |

---

> **Related Documents:**
> - [Smart_Meme_Search.md](./Smart_Meme_Search.md) · [04_Frontend/State_Management.md](../04_Frontend/State_Management.md)
