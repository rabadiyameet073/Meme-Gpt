import { useState, useEffect } from "react";
import { api, type StatsResponse } from "../api";
import { Icon, type IconName } from "./Icon";

export function StatsTab() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .stats()
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-wrap">
        <div className="spinner" />
        <div className="loading-text">Fetching analytics from SQLite & FastAPI…</div>
      </div>
    );
  }

  const statItems: { icon: IconName; value: string | number; label: string }[] = stats
    ? [
        { icon: "mask", value: stats.totalMemes, label: "Memes in Database" },
        { icon: "search", value: stats.totalSearches, label: "Total AI Searches" },
        { icon: "sparkles", value: stats.totalUsage, label: "Meme Selections" },
        { icon: "thumb-up", value: stats.totalVotes, label: "User Feedback Votes" },
        { icon: "clock", value: `${stats.avgLatencyMs} ms`, label: "Avg AI Latency" },
      ]
    : [];

  return (
    <div>
      <div className="section-label">
        <Icon name="stats" size={14} /> System Performance & Usage Stats
      </div>
      {stats && (
        <div className="stats-grid">
          {statItems.map((item, idx) => (
            <div key={idx} className="stat-card">
              <div style={{ color: "var(--text-muted)", marginBottom: "4px" }}>
                <Icon name={item.icon} size={20} />
              </div>
              <span className="stat-card-value">{item.value}</span>
              <span className="stat-card-label">{item.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
