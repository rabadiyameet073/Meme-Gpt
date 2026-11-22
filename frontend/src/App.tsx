import { useState, useEffect, lazy, Suspense } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "./api";
import { Icon, type IconName } from "./components/Icon";
import { ChatTab } from "./components/ChatTab";
import { Sidebar } from "./components/Sidebar";
import { ThemeToggle } from "./components/ThemeToggle";
import { Canvas3DBackground } from "./components/Canvas3DBackground";
import { useSearchHistory } from "./hooks/useSearchHistory";
import { soundFx } from "./lib/audio";
import { AuthModal } from "./components/AuthModal";
import { fetchCurrentUser, getCachedUser, setStoredTokens } from "./lib/auth";
import type { User } from "@/types";

// Code splitting: Lazy load views
const SearchTab = lazy(() => import("./components/SearchTab").then((m) => ({ default: m.SearchTab })));
const TrendingTab = lazy(() => import("./components/TrendingTab").then((m) => ({ default: m.TrendingTab })));
const FavoritesTab = lazy(() => import("./components/FavoritesTab").then((m) => ({ default: m.FavoritesTab })));
const StatsTab = lazy(() => import("./components/StatsTab").then((m) => ({ default: m.StatsTab })));
const AdminTab = lazy(() => import("./components/AdminTab").then((m) => ({ default: m.AdminTab })));
const MemeDetail = lazy(() => import("./components/MemeDetail").then((m) => ({ default: m.MemeDetail })));
const AboutView = lazy(() => import("./components/AboutView").then((m) => ({ default: m.AboutView })));
const PrivacyView = lazy(() => import("./components/PrivacyView").then((m) => ({ default: m.PrivacyView })));

type ViewState =
  | { type: "tab"; name: "chat" | "search" | "trending" | "favorites" | "stats" | "admin"; category?: string }
  | { type: "meme"; slug: string }
  | { type: "about" }
  | { type: "privacy" };

interface ToastMsg {
  id: string;
  text: string;
}

function TabLoadingFallback() {
  return (
    <div style={{ padding: "80px 20px", textAlign: "center" }}>
      <div
        style={{
          width: "40px",
          height: "40px",
          margin: "0 auto 16px",
          border: "3px solid var(--border)",
          borderTopColor: "var(--brand-primary)",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>Loading view...</p>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState<ViewState>({ type: "tab", name: "chat" });
  const [memeCount, setMemeCount] = useState<number | null>(null);
  const [audioEnabled, setAudioEnabled] = useState<boolean>(soundFx.isEnabled());
  const [toasts, setToasts] = useState<ToastMsg[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(getCachedUser());
  const [isAuthModalOpen, setIsAuthModalOpen] = useState<boolean>(false);
  const { history, addToHistory, clearHistory, removeFromHistory } = useSearchHistory();

  // Clean URL & Hash route parsing
  useEffect(() => {
    const parseRoute = () => {
      const hash = window.location.hash.replace(/^#\/?/, "");
      const path = window.location.pathname.replace(/^\//, "");
      const route = hash || path;

      if (route.startsWith("meme/")) {
        const slug = route.replace("meme/", "");
        if (slug) {
          setView({ type: "meme", slug });
          return;
        }
      } else if (route === "about") {
        setView({ type: "about" });
        return;
      } else if (route === "privacy") {
        setView({ type: "privacy" });
        return;
      } else if (["chat", "search", "trending", "favorites", "stats", "admin"].includes(route)) {
        setView({ type: "tab", name: route as any });
        return;
      }
      setView({ type: "tab", name: "chat" });
    };

    parseRoute();
    window.addEventListener("hashchange", parseRoute);
    window.addEventListener("popstate", parseRoute);
    return () => {
      window.removeEventListener("hashchange", parseRoute);
      window.removeEventListener("popstate", parseRoute);
    };
  }, []);

  const navigateTo = (newView: ViewState) => {
    soundFx.playTap();
    setView(newView);
    let targetPath = "/";
    if (newView.type === "tab") {
      targetPath = `/${newView.name}`;
      window.location.hash = `#/${newView.name}`;
    } else if (newView.type === "meme") {
      targetPath = `/meme/${newView.slug}`;
      window.location.hash = `#/meme/${newView.slug}`;
    } else if (newView.type === "about") {
      targetPath = "/about";
      window.location.hash = `#/about`;
    } else if (newView.type === "privacy") {
      targetPath = "/privacy";
      window.location.hash = `#/privacy`;
    }
    try {
      if (window.location.pathname !== targetPath) {
        window.history.pushState(null, "", targetPath);
      }
    } catch {}
  };

  const toggleSound = () => {
    const next = soundFx.toggle();
    setAudioEnabled(next);
  };

  useEffect(() => {
    // Check if OAuth callback passed token in URL params
    const params = new URLSearchParams(window.location.search);
    const tokenParam = params.get("token") || params.get("access_token");
    if (tokenParam) {
      setStoredTokens(tokenParam);
      window.history.replaceState({}, document.title, window.location.pathname + window.location.hash);
    }

    fetchCurrentUser().then((u) => {
      if (u) setCurrentUser(u);
    });

    api
      .health()
      .then((h: any) => setMemeCount(h.memeCount || h.totalMemes || null))
      .catch(() => setMemeCount(null));

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName || "")) {
        e.preventDefault();
        const searchInput = document.querySelector<HTMLInputElement | HTMLTextAreaElement>("textarea, input[type='text']");
        searchInput?.focus();
      } else if (["1", "2", "3", "4", "5", "6"].includes(e.key) && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName || "")) {
        const tabs: ("chat" | "search" | "trending" | "favorites" | "stats" | "admin")[] = [
          "chat",
          "search",
          "trending",
          "favorites",
          "stats",
          "admin",
        ];
        const idx = parseInt(e.key, 10) - 1;
        if (tabs[idx]) {
          navigateTo({ type: "tab", name: tabs[idx] });
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const addToast = (text: string) => {
    soundFx.playSuccess();
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, text }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3200);
  };

  const handleSelectHistoryQuery = (query: string) => {
    soundFx.playClick();
    navigateTo({ type: "tab", name: "chat" });
    setTimeout(() => {
      const input = document.querySelector<HTMLTextAreaElement | HTMLInputElement>("textarea, input[type='text']");
      if (input) {
        input.value = query;
        input.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }, 100);
  };

  const currentTab = view.type === "tab" ? view.name : undefined;
  const isAdmin = Boolean(currentUser?.is_admin || (currentUser?.plan && ["admin", "internal"].includes(currentUser.plan.toLowerCase())));

  const baseNavTabs: { id: "chat" | "search" | "trending" | "favorites" | "stats" | "admin"; label: string; icon: IconName }[] = [
    { id: "chat", label: "AI Matcher", icon: "chat" },
    { id: "search", label: "Browse Memes", icon: "search" },
    { id: "trending", label: "Trending", icon: "trending" },
    { id: "favorites", label: "Saved", icon: "heart" },
    { id: "stats", label: "Analytics", icon: "stats" },
  ];

  const topNavTabs = isAdmin
    ? [...baseNavTabs, { id: "admin" as const, label: "Admin", icon: "settings" as IconName }]
    : baseNavTabs;

  return (
    <div className="app-container">
      {/* Skip Navigation Link for Screen Readers and Keyboard Navigation */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Interactive 3D Background Canvas */}
      <div className="bg-canvas-wrapper" aria-hidden="true">
        <Canvas3DBackground />
      </div>

      {/* Left Sidebar */}
      <Sidebar
        history={history}
        onSelectQuery={handleSelectHistoryQuery}
        onClearHistory={clearHistory}
        onRemoveItem={removeFromHistory}
        activeTab={currentTab}
        onNavigateTab={(tab) => navigateTo({ type: "tab", name: tab as any })}
        onSelectCategory={(cat) => navigateTo({ type: "tab", name: "search", category: cat })}
      />

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Top Header */}
        <header className="top-header" role="banner">
          {/* Quick Access Tabs */}
          <nav className="header-tab-bar" role="tablist" aria-label="Main Views">
            {topNavTabs.map((t) => {
              const active = currentTab === t.id;
              return (
                <button
                  key={t.id}
                  type="button"
                  role="tab"
                  id={`tab-${t.id}`}
                  aria-selected={active}
                  aria-controls={`panel-${t.id}`}
                  className={`header-tab-btn ${active ? "active" : ""}`}
                  onClick={() => navigateTo({ type: "tab", name: t.id })}
                >
                  <Icon
                    name={t.icon}
                    size={14}
                    color={active ? "#ffffff" : undefined}
                  />
                  <span>{t.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Controls */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "5px 12px",
                borderRadius: "var(--radius-sm)",
                backgroundColor: "var(--bg-card)",
                border: "1px solid var(--border-subtle)",
                fontSize: "0.78rem",
                color: "var(--text-secondary)",
              }}
            >
              <span
                style={{
                  width: "7px",
                  height: "7px",
                  borderRadius: "50%",
                  backgroundColor: "var(--accent-emerald)",
                  display: "inline-block",
                }}
              />
              <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>FastAPI v2.0</span>
              {memeCount !== null && (
                <span style={{ color: "var(--text-muted)" }}>• {memeCount} memes</span>
              )}
            </div>

            {/* Audio Effects Toggle */}
            <button
              type="button"
              onClick={toggleSound}
              title={audioEnabled ? "Tactile Audio: ON" : "Tactile Audio: OFF"}
              style={{
                background: "transparent",
                border: "1px solid var(--border-subtle)",
                borderRadius: "var(--radius-sm)",
                padding: "6px 10px",
                color: audioEnabled ? "var(--brand-primary)" : "var(--text-muted)",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "4px",
                fontSize: "0.76rem",
                fontWeight: 600,
                transition: "all var(--transition-fast)",
              }}
            >
              <Icon name={audioEnabled ? "volume" : "volume-x"} size={14} />
              <span style={{ display: "none" }}>Audio</span>
            </button>

            {/* User Account / Sign In Button */}
            <button
              type="button"
              onClick={() => {
                soundFx.playTap();
                setIsAuthModalOpen(true);
              }}
              title={currentUser ? `Signed in as ${currentUser.name || currentUser.email}` : "Sign In or Register"}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: currentUser ? "4px 10px 4px 6px" : "6px 12px",
                borderRadius: "var(--radius-sm)",
                border: currentUser ? "1px solid rgba(99, 102, 241, 0.4)" : "1px solid var(--border-subtle)",
                backgroundColor: currentUser ? "rgba(99, 102, 241, 0.12)" : "var(--bg-card)",
                color: "var(--text-primary)",
                cursor: "pointer",
                fontSize: "0.78rem",
                fontWeight: 600,
                transition: "all var(--transition-fast)",
              }}
            >
              {currentUser ? (
                <>
                  <div
                    style={{
                      width: "22px",
                      height: "22px",
                      borderRadius: "50%",
                      backgroundColor: "var(--brand-primary)",
                      color: "#fff",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "0.7rem",
                      fontWeight: 700,
                      overflow: "hidden",
                    }}
                  >
                    {currentUser.avatar_url ? (
                      <img src={currentUser.avatar_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    ) : (
                      (currentUser.name?.[0] || currentUser.email[0]).toUpperCase()
                    )}
                  </div>
                  <span style={{ maxWidth: "100px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {currentUser.name || currentUser.email.split("@")[0]}
                  </span>
                </>
              ) : (
                <>
                  <Icon name="user" size={13} color="var(--brand-primary)" />
                  <span>Sign In</span>
                </>
              )}
            </button>

            <ThemeToggle />
          </div>
        </header>

        {/* Dynamic Route Content with Framer Motion */}
        <main className="content-area" id="main-content" tabIndex={-1}>
          <Suspense fallback={<TabLoadingFallback />}>
            <AnimatePresence mode="wait">
              {view.type === "tab" && view.name === "chat" && (
                <motion.div
                  key="chat"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <ChatTab onToast={addToast} onSearchCompleted={addToHistory} />
                </motion.div>
              )}

              {view.type === "tab" && view.name === "search" && (
                <motion.div
                  key="search"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <SearchTab onToast={addToast} initialCategory={view.category} />
                </motion.div>
              )}

              {view.type === "tab" && view.name === "trending" && (
                <motion.div
                  key="trending"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <TrendingTab onToast={addToast} />
                </motion.div>
              )}

              {view.type === "tab" && view.name === "favorites" && (
                <motion.div
                  key="favorites"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <FavoritesTab onToast={addToast} />
                </motion.div>
              )}

              {view.type === "tab" && view.name === "stats" && (
                <motion.div
                  key="stats"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <StatsTab />
                </motion.div>
              )}

              {view.type === "tab" && view.name === "admin" && isAdmin && (
                <motion.div
                  key="admin"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <AdminTab onToast={addToast} />
                </motion.div>
              )}

              {view.type === "meme" && (
                <motion.div
                  key={`meme-${view.slug}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <MemeDetail
                    slug={view.slug}
                    onToast={addToast}
                    onBack={() => navigateTo({ type: "tab", name: "search" })}
                  />
                </motion.div>
              )}

              {view.type === "about" && (
                <motion.div
                  key="about"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <AboutView />
                </motion.div>
              )}

              {view.type === "privacy" && (
                <motion.div
                  key="privacy"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                >
                  <PrivacyView />
                </motion.div>
              )}
            </AnimatePresence>
          </Suspense>
        </main>

        {/* Global Footer */}
        <footer
          style={{
            marginTop: "auto",
            padding: "20px 36px",
            borderTop: "1px solid var(--border-subtle)",
            backgroundColor: "var(--bg-panel)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "16px",
            fontSize: "0.82rem",
            color: "var(--text-muted)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>MemeGPT</span>
            <span>• Multimodal Semantic Vector Search Engine</span>
          </div>

          <div style={{ display: "flex", gap: "18px", alignItems: "center" }}>
            <a
              href="#/about"
              onClick={(e) => {
                e.preventDefault();
                navigateTo({ type: "about" });
              }}
              style={{ color: "var(--text-secondary)", textDecoration: "none" }}
            >
              About System
            </a>
            <a
              href="#/privacy"
              onClick={(e) => {
                e.preventDefault();
                navigateTo({ type: "privacy" });
              }}
              style={{ color: "var(--text-secondary)", textDecoration: "none" }}
            >
              Privacy Policy
            </a>
            <a
              href="/landing.html"
              style={{ color: "var(--brand-primary)", textDecoration: "none", fontWeight: 600 }}
            >
              Marketing Page
            </a>
            <span style={{ fontSize: "0.78rem" }}>
              Press <kbd style={{ padding: "2px 6px", background: "var(--bg-card)", borderRadius: "4px", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>/</kbd> to search
            </span>
          </div>
        </footer>
      </div>

      {/* Interactive Toast Alerts with Spring Animation */}
      <div className="toast-container">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 16, scale: 0.94 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 12, scale: 0.94 }}
              transition={{ duration: 0.18 }}
              className="toast"
            >
              <Icon name="check" size={15} color="var(--accent-emerald)" />
              <span>{t.text}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* User Authentication & Profile Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        currentUser={currentUser}
        onAuthSuccess={(user) => {
          setCurrentUser(user);
          addToast(`Welcome, ${user.name || user.email}!`);
        }}
        onLogout={() => {
          setCurrentUser(null);
          addToast("Logged out successfully");
        }}
      />

      {/* Mobile Bottom Navigation Bar (RWD-01) */}
      <nav
        className="mobile-bottom-nav"
        role="navigation"
        aria-label="Mobile Navigation"
        style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          height: "56px",
          backgroundColor: "var(--bg-card)",
          borderTop: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-around",
          zIndex: 1000,
          backdropFilter: "blur(12px)",
        }}
      >
        {[
          { tab: "chat" as const, label: "Chat", icon: "sparkles" as const },
          { tab: "search" as const, label: "Search", icon: "search" as const },
          { tab: "trending" as const, label: "Trending", icon: "trending" as const },
          { tab: "favorites" as const, label: "Library", icon: "bookmark" as const },
        ].map(({ tab, label, icon }) => {
          const isActive = view.type === "tab" && view.name === tab;
          return (
            <button
              key={tab}
              type="button"
              onClick={() => navigateTo({ type: "tab", name: tab })}
              aria-label={label}
              style={{
                flex: 1,
                height: "100%",
                background: "transparent",
                border: "none",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: "2px",
                color: isActive ? "var(--brand-primary)" : "var(--text-muted)",
                fontSize: "0.7rem",
                fontWeight: isActive ? 700 : 500,
                cursor: "pointer",
              }}
            >
              <Icon name={icon} size={18} color={isActive ? "var(--brand-primary)" : "var(--text-muted)"} />
              <span>{label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
