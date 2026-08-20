import { useState, useEffect, lazy, Suspense } from "react";
import { api } from "./api";
import { Icon } from "./components/Icon";
import { ChatTab } from "./components/ChatTab";

// Code splitting: Lazy load views to minimize initial JS bundle
const SearchTab = lazy(() => import("./components/SearchTab").then(m => ({ default: m.SearchTab })));
const TrendingTab = lazy(() => import("./components/TrendingTab").then(m => ({ default: m.TrendingTab })));
const FavoritesTab = lazy(() => import("./components/FavoritesTab").then(m => ({ default: m.FavoritesTab })));
const StatsTab = lazy(() => import("./components/StatsTab").then(m => ({ default: m.StatsTab })));
const AdminTab = lazy(() => import("./components/AdminTab").then(m => ({ default: m.AdminTab })));
const MemeDetail = lazy(() => import("./components/MemeDetail").then(m => ({ default: m.MemeDetail })));
const AboutView = lazy(() => import("./components/AboutView").then(m => ({ default: m.AboutView })));
const PrivacyView = lazy(() => import("./components/PrivacyView").then(m => ({ default: m.PrivacyView })));

type ViewState =
  | { type: "tab"; name: "chat" | "search" | "trending" | "favorites" | "stats" | "admin" }
  | { type: "meme"; slug: string }
  | { type: "about" }
  | { type: "privacy" };

interface ToastMsg {
  id: string;
  text: string;
}

function TabLoadingFallback() {
  return (
    <div style={{ padding: "40px 20px", textAlign: "center" }}>
      <div
        style={{
          width: "48px",
          height: "48px",
          margin: "0 auto 16px",
          border: "3px solid rgba(124, 58, 237, 0.2)",
          borderTopColor: "var(--brand-purple, #7C3AED)",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <p style={{ color: "var(--text-muted, #71717a)", fontSize: "0.9rem" }}>Loading view...</p>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState<ViewState>({ type: "tab", name: "chat" });
  const [memeCount, setMemeCount] = useState<number | null>(null);
  const [toasts, setToasts] = useState<ToastMsg[]>([]);

  // Hash route parsing
  useEffect(() => {
    const parseHash = () => {
      const hash = window.location.hash.replace(/^#\/?/, "");
      if (hash.startsWith("meme/")) {
        const slug = hash.replace("meme/", "");
        if (slug) {
          setView({ type: "meme", slug });
          return;
        }
      } else if (hash === "about") {
        setView({ type: "about" });
        return;
      } else if (hash === "privacy") {
        setView({ type: "privacy" });
        return;
      } else if (["chat", "search", "trending", "favorites", "stats", "admin"].includes(hash)) {
        setView({ type: "tab", name: hash as any });
        return;
      } else if (hash === "app") {
        setView({ type: "tab", name: "search" });
        return;
      }
      setView({ type: "tab", name: "chat" });
    };

    parseHash();
    window.addEventListener("hashchange", parseHash);
    return () => window.removeEventListener("hashchange", parseHash);
  }, []);

  const navigateTo = (newView: ViewState) => {
    setView(newView);
    if (newView.type === "tab") {
      window.location.hash = `#/${newView.name}`;
    } else if (newView.type === "meme") {
      window.location.hash = `#/meme/${newView.slug}`;
    } else if (newView.type === "about") {
      window.location.hash = `#/about`;
    } else if (newView.type === "privacy") {
      window.location.hash = `#/privacy`;
    }
  };

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

  const currentTab = view.type === "tab" ? view.name : null;

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div
          className="logo-group"
          style={{ cursor: "pointer" }}
          onClick={() => navigateTo({ type: "tab", name: "chat" })}
        >
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
          className={`tab-btn ${currentTab === "chat" ? "active" : ""}`}
          onClick={() => navigateTo({ type: "tab", name: "chat" })}
        >
          <Icon name="chat" size={16} /> AI Matcher
        </button>
        <button
          className={`tab-btn ${currentTab === "search" ? "active" : ""}`}
          onClick={() => navigateTo({ type: "tab", name: "search" })}
        >
          <Icon name="search" size={16} /> Browse Memes
        </button>
        <button
          className={`tab-btn ${currentTab === "trending" ? "active" : ""}`}
          onClick={() => navigateTo({ type: "tab", name: "trending" })}
        >
          <Icon name="trending" size={16} /> Trending
        </button>
        <button
          className={`tab-btn ${currentTab === "favorites" ? "active" : ""}`}
          onClick={() => navigateTo({ type: "tab", name: "favorites" })}
        >
          <Icon name="heart" size={16} /> Saved
        </button>
        <button
          className={`tab-btn ${currentTab === "stats" ? "active" : ""}`}
          onClick={() => navigateTo({ type: "tab", name: "stats" })}
        >
          <Icon name="stats" size={16} /> Analytics
        </button>
        <button
          className={`tab-btn ${currentTab === "admin" ? "active" : ""}`}
          onClick={() => navigateTo({ type: "tab", name: "admin" })}
        >
          <Icon name="settings" size={16} /> Admin
        </button>
      </nav>

      {/* Main Content Area */}
      <main className="tab-content">
        <Suspense fallback={<TabLoadingFallback />}>
          {view.type === "tab" && view.name === "chat" && <ChatTab onToast={addToast} />}
          {view.type === "tab" && view.name === "search" && <SearchTab onToast={addToast} />}
          {view.type === "tab" && view.name === "trending" && <TrendingTab onToast={addToast} />}
          {view.type === "tab" && view.name === "favorites" && <FavoritesTab onToast={addToast} />}
          {view.type === "tab" && view.name === "stats" && <StatsTab />}
          {view.type === "tab" && view.name === "admin" && <AdminTab onToast={addToast} />}
          {view.type === "meme" && (
            <MemeDetail
              slug={view.slug}
              onBack={() => navigateTo({ type: "tab", name: "search" })}
              onToast={addToast}
            />
          )}
          {view.type === "about" && <AboutView />}
          {view.type === "privacy" && <PrivacyView />}
        </Suspense>
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
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <a
            href="#/about"
            onClick={(e) => { e.preventDefault(); navigateTo({ type: "about" }); }}
            style={{ color: "var(--text-secondary)", textDecoration: "none" }}
          >
            About
          </a>
          <a
            href="#/privacy"
            onClick={(e) => { e.preventDefault(); navigateTo({ type: "privacy" }); }}
            style={{ color: "var(--text-secondary)", textDecoration: "none" }}
          >
            Privacy
          </a>
          <span>Press <kbd style={{ padding: "2px 6px", background: "var(--bg-surface)", borderRadius: "4px", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>/</kbd> to search</span>
        </div>
      </footer>
    </div>
  );
}

