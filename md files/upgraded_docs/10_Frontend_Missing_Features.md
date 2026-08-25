# 10 — Frontend Missing Features
# ThemeToggle, Sidebar, Skeleton Loaders, PWA, Search History

> **Gap Source:** Section 7 of GAP_ANALYSIS_FULL.md  
> **Priority:** P1  
> **Files to create/edit:**  
> - `d:\Meme GPT\frontend\src\components\ThemeToggle.tsx` (NEW)  
> - `d:\Meme GPT\frontend\src\components\Sidebar.tsx` (NEW)  
> - `d:\Meme GPT\frontend\src\components\SkeletonCard.tsx` (NEW)  
> - `d:\Meme GPT\frontend\src\hooks\useSearchHistory.ts` (NEW)  
> - `d:\Meme GPT\frontend\public\manifest.json` (NEW — PWA)  
> - `d:\Meme GPT\frontend\public\sw.js` (NEW — Service Worker)  
> - `d:\Meme GPT\frontend\src\App.tsx` (update to use sidebar + theme)

---

## 1. ThemeToggle Component

**Create** `d:\Meme GPT\frontend\src\components\ThemeToggle.tsx`:

```tsx
import { useEffect, useState } from "react";
import { Icon } from "./Icon";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("theme") as "dark" | "light") || "dark";
    }
    return "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggle = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  return (
    <button
      className="theme-toggle"
      onClick={toggle}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
    >
      <Icon name={theme === "dark" ? "sun" : "moon"} size={18} />
    </button>
  );
}
```

Add these CSS rules to `d:\Meme GPT\frontend\src\index.css`:

```css
/* Theme toggle button */
.theme-toggle {
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  transition: all 0.2s ease;
}
.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--brand-purple);
}

/* Light theme overrides */
[data-theme="light"] {
  --bg-base: #F8F8F8;
  --bg-surface: #FFFFFF;
  --bg-elevated: #F0F0F0;
  --bg-hover: #E8E8E8;
  --text-primary: #1A1A1A;
  --text-secondary: #555555;
  --text-muted: #999999;
  --border-subtle: #E0E0E0;
  --border-default: #CCCCCC;
}
```

---

## 2. Search History Hook

**Create** `d:\Meme GPT\frontend\src\hooks\useSearchHistory.ts`:

```ts
import { useState, useEffect } from "react";

const HISTORY_KEY = "memegpt-history";
const MAX_HISTORY = 10;

export interface SearchHistoryItem {
  query: string;
  timestamp: number;
}

export function useSearchHistory() {
  const [history, setHistory] = useState<SearchHistoryItem[]>(() => {
    try {
      const stored = localStorage.getItem(HISTORY_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const addToHistory = (query: string) => {
    const trimmed = query.trim();
    if (!trimmed) return;

    setHistory((prev) => {
      // Remove duplicate if exists
      const filtered = prev.filter((h) => h.query !== trimmed);
      // Add to front, limit to MAX_HISTORY
      const updated = [
        { query: trimmed, timestamp: Date.now() },
        ...filtered,
      ].slice(0, MAX_HISTORY);

      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem(HISTORY_KEY);
  };

  const removeFromHistory = (query: string) => {
    setHistory((prev) => {
      const updated = prev.filter((h) => h.query !== query);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  return { history, addToHistory, clearHistory, removeFromHistory };
}
```

---

## 3. Sidebar Component

**Create** `d:\Meme GPT\frontend\src\components\Sidebar.tsx`:

```tsx
import { Icon } from "./Icon";
import { SearchHistoryItem } from "../hooks/useSearchHistory";

interface SidebarProps {
  history: SearchHistoryItem[];
  onSelectQuery: (query: string) => void;
  onClearHistory: () => void;
  onRemoveItem: (query: string) => void;
}

export function Sidebar({
  history,
  onSelectQuery,
  onClearHistory,
  onRemoveItem,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-header">
          <span className="sidebar-label">
            <Icon name="clock" size={13} /> Recent
          </span>
          {history.length > 0 && (
            <button className="sidebar-clear" onClick={onClearHistory} title="Clear history">
              Clear
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <div className="sidebar-empty">No recent searches</div>
        ) : (
          <ul className="sidebar-list">
            {history.map((item) => (
              <li key={item.timestamp} className="sidebar-item">
                <button
                  className="sidebar-query"
                  onClick={() => onSelectQuery(item.query)}
                  title={item.query}
                >
                  <Icon name="search" size={12} />
                  <span>{item.query.length > 38 ? item.query.slice(0, 36) + "…" : item.query}</span>
                </button>
                <button
                  className="sidebar-remove"
                  onClick={() => onRemoveItem(item.query)}
                  aria-label="Remove from history"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
```

Add CSS to `index.css`:

```css
/* Sidebar */
.app-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 0;
  min-height: 100vh;
}

.sidebar {
  background: var(--bg-surface);
  border-right: 1px solid var(--border-subtle);
  padding: 16px 12px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.sidebar-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  display: flex;
  gap: 4px;
  align-items: center;
}

.sidebar-clear {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 11px;
  padding: 2px 4px;
  border-radius: 4px;
}
.sidebar-clear:hover { color: var(--error); }

.sidebar-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sidebar-query {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12.5px;
  padding: 5px 6px;
  border-radius: 6px;
  text-align: left;
  display: flex;
  gap: 6px;
  align-items: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all 0.15s;
}
.sidebar-query:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-remove {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 2px 4px;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.15s;
}
.sidebar-item:hover .sidebar-remove { opacity: 1; }

.sidebar-empty {
  color: var(--text-muted);
  font-size: 12px;
  padding: 8px 6px;
}

/* Responsive — hide sidebar on mobile */
@media (max-width: 768px) {
  .app-layout {
    grid-template-columns: 1fr;
  }
  .sidebar {
    display: none;
  }
}
```

---

## 4. Skeleton Loader Component

**Create** `d:\Meme GPT\frontend\src\components\SkeletonCard.tsx`:

```tsx
export function SkeletonCard() {
  return (
    <div className="skeleton-card" aria-label="Loading meme..." role="status">
      <div className="skeleton-image" />
      <div className="skeleton-body">
        <div className="skeleton-line skeleton-line--wide" />
        <div className="skeleton-line skeleton-line--medium" />
        <div className="skeleton-line skeleton-line--short" />
        <div className="skeleton-actions">
          <div className="skeleton-btn" />
          <div className="skeleton-btn" />
        </div>
      </div>
    </div>
  );
}

export function SkeletonGrid({ count = 3 }: { count?: number }) {
  return (
    <div className="skeleton-grid" aria-busy="true">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
```

Add CSS to `index.css`:

```css
/* Skeleton Loaders */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.skeleton-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  overflow: hidden;
}

.skeleton-image {
  width: 100%;
  height: 220px;
  background: var(--bg-elevated);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  height: 12px;
  border-radius: 6px;
  background: var(--bg-elevated);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
.skeleton-line--wide { width: 80%; }
.skeleton-line--medium { width: 60%; }
.skeleton-line--short { width: 40%; }

.skeleton-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.skeleton-btn {
  height: 28px;
  width: 70px;
  border-radius: 6px;
  background: var(--bg-elevated);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
```

---

## 5. PWA Setup

**Create** `d:\Meme GPT\frontend\public\manifest.json`:

```json
{
  "name": "MemeGPT — AI Meme Search",
  "short_name": "MemeGPT",
  "description": "Find the perfect meme for any situation using AI",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0A0A0A",
  "theme_color": "#7C3AED",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "categories": ["entertainment", "utilities"],
  "screenshots": []
}
```

**Create** `d:\Meme GPT\frontend\public\sw.js` (basic service worker):

```js
const CACHE_NAME = "memegpt-v1";
const STATIC_ASSETS = ["/", "/index.html"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener("fetch", (event) => {
  // Network-first for API calls
  if (event.request.url.includes("/api/")) {
    return;
  }
  event.respondWith(
    fetch(event.request).catch(() =>
      caches.match(event.request)
    )
  );
});
```

**Add to** `d:\Meme GPT\frontend\index.html` `<head>`:
```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#7C3AED" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
```

**Register SW** in `d:\Meme GPT\frontend\src\main.tsx`:
```tsx
// Add at the bottom of main.tsx
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}
```

---

## 6. Update App.tsx to Use All New Components

In `d:\Meme GPT\frontend\src\App.tsx`, add:

```tsx
import { Sidebar } from "./components/Sidebar";
import { ThemeToggle } from "./components/ThemeToggle";
import { SkeletonGrid } from "./components/SkeletonCard";
import { useSearchHistory } from "./hooks/useSearchHistory";

// Inside the component:
const { history, addToHistory, clearHistory, removeFromHistory } = useSearchHistory();

// When search completes, add to history:
addToHistory(query);

// In the JSX, wrap main content with sidebar layout:
return (
  <div className="app-layout">
    <Sidebar
      history={history}
      onSelectQuery={(q) => { setQuery(q); submit(q); }}
      onClearHistory={clearHistory}
      onRemoveItem={removeFromHistory}
    />
    <main className="main-content">
      {/* existing header with ThemeToggle added */}
      <ThemeToggle />
      {/* Replace loading spinner with SkeletonGrid */}
      {loading && <SkeletonGrid count={3} />}
      {/* existing results */}
    </main>
  </div>
);
```
