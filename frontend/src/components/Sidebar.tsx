import { Icon, type IconName } from "./Icon";
import { SearchHistoryItem } from "../hooks/useSearchHistory";

interface SidebarProps {
  history: SearchHistoryItem[];
  onSelectQuery: (query: string) => void;
  onClearHistory: () => void;
  onRemoveItem: (query: string) => void;
  activeTab?: string;
  onNavigateTab?: (tab: string) => void;
  onSelectCategory?: (category: string) => void;
}

export function Sidebar({
  history,
  onSelectQuery,
  onClearHistory,
  onRemoveItem,
  activeTab = "chat",
  onNavigateTab,
  onSelectCategory,
}: SidebarProps) {
  const navItems: { id: string; label: string; icon: IconName; shortcut: string }[] = [
    { id: "chat", label: "AI Matcher", icon: "chat", shortcut: "1" },
    { id: "search", label: "Browse Memes", icon: "search", shortcut: "2" },
    { id: "trending", label: "Trending Feed", icon: "trending", shortcut: "3" },
    { id: "favorites", label: "Saved Memes", icon: "heart", shortcut: "4" },
    { id: "stats", label: "Platform Stats", icon: "stats", shortcut: "5" },
    { id: "admin", label: "Admin Panel", icon: "settings", shortcut: "6" },
  ];

  const quickCategories: { id: string; label: string; icon: IconName }[] = [
    { id: "work", label: "Work & Office", icon: "office" },
    { id: "tech", label: "Tech & Code", icon: "coding" },
    { id: "gaming", label: "Gaming", icon: "gaming" },
    { id: "relationships", label: "Relationships", icon: "relationship" },
    { id: "wholesome", label: "Wholesome", icon: "wholesome" },
    { id: "tv", label: "TV & Cinema", icon: "tv" },
  ];

  return (
    <aside className="sidebar">
      {/* Brand & Menu */}
      <div>
        {/* Brand Logo */}
        <div
          className="sidebar-logo"
          onClick={() => onNavigateTab && onNavigateTab("chat")}
        >
          <div className="logo-icon-box">
            <Icon name="sparkles" size={18} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center" }}>
              <span className="logo-text">MemeGPT</span>
              <span className="logo-badge">v2.0</span>
            </div>
            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginTop: "1px" }}>
              Semantic Meme Engine
            </div>
          </div>
        </div>

        {/* Navigation Section */}
        <div style={{ marginTop: "16px" }}>
          <div className="sidebar-section-title">
            <span>Main Menu</span>
          </div>
          <ul className="sidebar-nav">
            {navItems.map((item) => {
              const active = activeTab === item.id;
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    className={`sidebar-nav-item ${active ? "active" : ""}`}
                    onClick={() => onNavigateTab && onNavigateTab(item.id)}
                  >
                    <Icon
                      name={item.icon}
                      size={16}
                      color={active ? "var(--brand-primary)" : "var(--text-secondary)"}
                    />
                    <span>{item.label}</span>
                    <span className="sidebar-badge">{item.shortcut}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Quick Categories */}
        <div style={{ marginTop: "16px" }}>
          <div className="sidebar-section-title">
            <span>Categories</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
            {quickCategories.map((cat) => (
              <button
                key={cat.id}
                type="button"
                className="sidebar-nav-item"
                style={{ fontSize: "0.82rem", padding: "6px 10px" }}
                onClick={() => {
                  if (onNavigateTab) onNavigateTab("search");
                  if (onSelectCategory) onSelectCategory(cat.id);
                }}
              >
                <Icon name={cat.icon} size={14} color="var(--text-muted)" />
                <span>{cat.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Recent Searches */}
        <div style={{ marginTop: "16px" }}>
          <div className="sidebar-section-title">
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <Icon name="clock" size={12} />
              Recent Searches
            </span>
            {history.length > 0 && (
              <button
                type="button"
                onClick={onClearHistory}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "var(--text-muted)",
                  fontSize: "0.7rem",
                  cursor: "pointer",
                }}
              >
                Clear
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div style={{ padding: "8px 10px", fontSize: "0.76rem", color: "var(--text-muted)" }}>
              No recent searches
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              {history.slice(0, 5).map((item) => (
                <div key={item.timestamp} className="recent-search-pill">
                  <div
                    onClick={() => {
                      if (onNavigateTab) onNavigateTab("chat");
                      onSelectQuery(item.query);
                    }}
                    style={{
                      flex: 1,
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    <Icon name="search" size={11} color="var(--text-muted)" />
                    <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>
                      {item.query}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveItem(item.query);
                    }}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "var(--text-muted)",
                      cursor: "pointer",
                      padding: "2px",
                      lineHeight: 1,
                    }}
                  >
                    <Icon name="x" size={11} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer: Live Engine Status */}
      <div
        style={{
          padding: "12px",
          borderRadius: "var(--radius-sm)",
          backgroundColor: "var(--bg-card)",
          border: "1px solid var(--border-subtle)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
          <span
            style={{
              width: "7px",
              height: "7px",
              borderRadius: "50%",
              backgroundColor: "var(--accent-emerald)",
              display: "inline-block",
            }}
          />
          <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-primary)" }}>
            FastAPI Engine Active
          </span>
        </div>
        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
          Qdrant Dense Cosine (384-dim)
        </div>
      </div>
    </aside>
  );
}
