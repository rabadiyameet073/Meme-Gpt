import { Icon } from "./Icon";
import { SearchHistoryItem } from "../hooks/useSearchHistory";

interface SidebarProps {
  history: SearchHistoryItem[];
  onSelectQuery: (query: string) => void;
  onClearHistory: () => void;
  onRemoveItem: (query: string) => void;
  activeTab?: string;
  onNavigateTab?: (tab: string) => void;
}

export function Sidebar({
  history,
  onSelectQuery,
  onClearHistory,
  onRemoveItem,
  activeTab,
  onNavigateTab,
}: SidebarProps) {
  const navItems = [
    { id: "chat", label: "AI Search", icon: "search" },
    { id: "trending", label: "Trending", icon: "flame" },
    { id: "favorites", label: "Saved Memes", icon: "heart" },
    { id: "stats", label: "Platform Stats", icon: "bar-chart" },
    { id: "admin", label: "Admin Panel", icon: "settings" },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-section" style={{ marginBottom: "20px" }}>
        <div className="sidebar-label" style={{ marginBottom: "8px" }}>Menu</div>
        <ul className="sidebar-list">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                className={`sidebar-nav-btn ${activeTab === item.id ? "active" : ""}`}
                onClick={() => onNavigateTab && onNavigateTab(item.id)}
              >
                <Icon name={item.icon} size={15} />
                <span>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-header">
          <span className="sidebar-label">
            <Icon name="clock" size={13} /> Recent Searches
          </span>
          {history.length > 0 && (
            <button
              type="button"
              className="sidebar-clear"
              onClick={onClearHistory}
              title="Clear history"
            >
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
                  type="button"
                  className="sidebar-query"
                  onClick={() => onSelectQuery(item.query)}
                  title={item.query}
                >
                  <Icon name="search" size={12} />
                  <span>{item.query.length > 28 ? item.query.slice(0, 26) + "…" : item.query}</span>
                </button>
                <button
                  type="button"
                  className="sidebar-remove"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveItem(item.query);
                  }}
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
