import { useState, useEffect } from "react";
import { api } from "./api";
import { Icon } from "./components/Icon";
import { ChatTab } from "./components/ChatTab";
import { SearchTab } from "./components/SearchTab";
import { TrendingTab } from "./components/TrendingTab";
import { FavoritesTab } from "./components/FavoritesTab";
import { StatsTab } from "./components/StatsTab";
import { AdminTab } from "./components/AdminTab";

type Tab = "chat" | "search" | "trending" | "favorites" | "stats" | "admin";

interface ToastMsg {
  id: string;
  text: string;
}

export default function App() {
  const [tab, setTab] = useState<Tab>("chat");
  const [memeCount, setMemeCount] = useState<number | null>(null);
  const [toasts, setToasts] = useState<ToastMsg[]>([]);

  useEffect(() => {
    api
      .health()
      .then((h) => setMemeCount(h.memeCount))
      .catch(() => setMemeCount(null));

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName || "")) {
        e.preventDefault();
        const searchInput = document.querySelector<HTMLInputElement | HTMLTextAreaElement>("textarea, input[type='text']");
        searchInput?.focus();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const addToast = (text: string) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, text }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3200);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="logo-group">
          <span className="logo-icon">
            <Icon name="mask" size={20} />
          </span>
          <div>
            <div className="logo-title">
              MemeGPT <span className="version-badge">v2.5</span>
            </div>
            <div className="logo-tagline">AI-Powered Meme Recommendation & Semantic Matching Engine</div>
          </div>
        </div>

        <div className="status-pill">
          <div className="status-dot" />
          <span>FastAPI Engine</span>
          {memeCount !== null && (
            <span style={{ color: "var(--text-muted)", marginLeft: "2px" }}>
              ({memeCount} active)
            </span>
          )}
        </div>
      </header>

      {/* Tabs */}
      <nav className="tab-bar">
        <button
          className={`tab-btn ${tab === "chat" ? "active" : ""}`}
          onClick={() => setTab("chat")}
        >
          <Icon name="chat" size={16} /> AI Matcher
        </button>
        <button
          className={`tab-btn ${tab === "search" ? "active" : ""}`}
          onClick={() => setTab("search")}
        >
          <Icon name="search" size={16} /> Browse Memes
        </button>
        <button
          className={`tab-btn ${tab === "trending" ? "active" : ""}`}
          onClick={() => setTab("trending")}
        >
          <Icon name="trending" size={16} /> Trending
        </button>
        <button
          className={`tab-btn ${tab === "favorites" ? "active" : ""}`}
          onClick={() => setTab("favorites")}
        >
          <Icon name="heart" size={16} /> Saved
        </button>
        <button
          className={`tab-btn ${tab === "stats" ? "active" : ""}`}
          onClick={() => setTab("stats")}
        >
          <Icon name="stats" size={16} /> Analytics
        </button>
        <button
          className={`tab-btn ${tab === "admin" ? "active" : ""}`}
          onClick={() => setTab("admin")}
        >
          <Icon name="settings" size={16} /> Admin
        </button>
      </nav>

      {/* Main Content Area */}
      <main className="tab-content">
        {tab === "chat" && <ChatTab onToast={addToast} />}
        {tab === "search" && <SearchTab onToast={addToast} />}
        {tab === "trending" && <TrendingTab onToast={addToast} />}
        {tab === "favorites" && <FavoritesTab onToast={addToast} />}
        {tab === "stats" && <StatsTab />}
        {tab === "admin" && <AdminTab onToast={addToast} />}
      </main>

      {/* Toast Notifications */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className="toast">
            <Icon name="info" size={16} />
            <span>{t.text}</span>
          </div>
        ))}
      </div>

      {/* Footer */}
      <footer
        style={{
          marginTop: "60px",
          paddingTop: "20px",
          borderTop: "1px solid var(--border)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          fontSize: "0.78rem",
          color: "var(--text-muted)",
        }}
      >
        <span>MemeGPT v2.5 · FastAPI + SQLite + Semantic AI Search Engine</span>
        <span>Press <kbd style={{ padding: "2px 6px", background: "var(--bg-surface)", borderRadius: "4px", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>/</kbd> to search</span>
      </footer>
    </div>
  );
}
