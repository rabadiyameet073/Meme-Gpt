import { useState, useEffect } from "react";
import { api, type MemeRecord } from "../api";
import { Icon } from "./Icon";

export function TrendingTab({ onToast: _onToast }: { onToast: (m: string) => void }) {
  const [memes, setMemes] = useState<MemeRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .trending()
      .then(setMemes)
      .catch(() => setMemes([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-wrap">
        <div className="spinner" />
        <div className="loading-text">Fetching top trending memes…</div>
      </div>
    );
  }

  if (memes.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">
          <Icon name="trending" size={36} />
        </div>
        <p>No trending data yet. Use the search to generate usage trends!</p>
      </div>
    );
  }

  return (
    <div>
      <div className="section-label">
        <Icon name="trending" size={14} /> Most Used & Upvoted Memes
      </div>
      <div className="trending-grid">
        {memes.map((m, i) => (
          <div key={m.id} className="trending-card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div className="trending-rank">
                <Icon name="trophy" size={14} /> Rank #{i + 1}
              </div>
              <span className="badge badge-category">{m.category.replace(/_/g, " ")}</span>
            </div>
            <div className="trending-name">{m.name}</div>
            <div className="meme-dialogue" style={{ marginTop: 10, fontSize: "0.85rem" }}>
              "{m.dialogue}"
            </div>
            <div className="trending-stats">
              <span>
                <Icon name="bar-chart" size={13} /> {m.usageCount} uses
              </span>
              <span>
                <Icon name="thumb-up" size={13} /> {m.upvotes}
              </span>
              <span>
                <Icon name="thumb-down" size={13} /> {m.downvotes}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
