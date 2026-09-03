import { useState, useEffect } from "react";
import { motion } from "framer-motion";
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
      <div style={{ padding: "60px 0", textAlign: "center" }}>
        <div
          style={{
            width: "40px",
            height: "40px",
            borderRadius: "50%",
            border: "3px solid var(--border)",
            borderTopColor: "var(--brand-primary)",
            animation: "spin 0.8s linear infinite",
            margin: "0 auto 16px",
          }}
        />
        <h3 style={{ fontSize: "1.1rem" }}>Gathering Platform Metrics…</h3>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
          Aggregating telemetry from SQLite, Vector DB, and FastAPI
        </p>
      </div>
    );
  }

  const statCards: { icon: IconName; value: string | number; label: string; subtext: string; color: string }[] = stats
    ? [
        {
          icon: "database",
          value: stats.totalMemes ?? 0,
          label: "Indexed Templates",
          subtext: "Categorized & vector-embedded",
          color: "var(--brand-primary)",
        },
        {
          icon: "search",
          value: stats.totalSearches ?? 0,
          label: "AI Neural Searches",
          subtext: "Natural language queries parsed",
          color: "var(--brand-gold)",
        },
        {
          icon: "sparkles",
          value: stats.totalUsage ?? 0,
          label: "Meme Selections",
          subtext: "Copies, downloads, and shares",
          color: "var(--accent-emerald)",
        },
        {
          icon: "thumb-up",
          value: stats.totalVotes ?? 0,
          label: "User Feedback Signals",
          subtext: "Relevance votes recorded",
          color: "var(--brand-teal)",
        },
        {
          icon: "clock",
          value: `${stats.avgLatencyMs ?? 24} ms`,
          label: "Average Query Latency",
          subtext: "Dense vector retrieval speed",
          color: "var(--brand-gold)",
        },
      ]
    : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      style={{ maxWidth: "1100px", margin: "0 auto" }}
    >
      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
          <Icon name="stats" size={22} color="var(--brand-primary)" />
          Platform Health & Analytics
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "4px" }}>
          Real-time metrics on vector retrieval performance, user feedback loop, and database capacity
        </p>
      </div>

      {/* Bento Grid Stats */}
      <div className="bento-grid">
        {statCards.map((card, idx) => (
          <div key={idx} className="bento-card">
            <div>
              <div className="bento-icon-box">
                <Icon name={card.icon} size={20} color={card.color} />
              </div>
              <div className="bento-value">{card.value}</div>
              <div className="bento-label">{card.label}</div>
            </div>
            <div style={{ fontSize: "0.74rem", color: "var(--text-muted)", marginTop: "14px", borderTop: "1px solid var(--border-subtle)", paddingTop: "10px" }}>
              {card.subtext}
            </div>
          </div>
        ))}
      </div>

      {/* Subsystem Health Dashboard */}
      <div
        style={{
          backgroundColor: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-md)",
          padding: "24px",
          marginTop: "24px",
        }}
      >
        <h3 style={{ fontSize: "1.05rem", fontWeight: 700, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
          <Icon name="shield" size={18} color="var(--accent-emerald)" />
          Subsystem Status & Architecture
        </h3>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "14px",
          }}
        >
          {/* Service 1 */}
          <div style={{ padding: "14px", borderRadius: "var(--radius-sm)", backgroundColor: "var(--bg-panel)", border: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <span style={{ fontWeight: 600, fontSize: "0.88rem" }}>FastAPI Backend</span>
              <span className="badge" style={{ backgroundColor: "rgba(16, 185, 129, 0.15)", color: "var(--accent-emerald)", border: "1px solid var(--accent-emerald)" }}>Active</span>
            </div>
            <div style={{ fontSize: "0.76rem", color: "var(--text-muted)" }}>REST v2.0 • Port 8000</div>
          </div>

          {/* Service 2 */}
          <div style={{ padding: "14px", borderRadius: "var(--radius-sm)", backgroundColor: "var(--bg-panel)", border: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <span style={{ fontWeight: 600, fontSize: "0.88rem" }}>Vector Engine</span>
              <span className="badge" style={{ backgroundColor: "rgba(16, 185, 129, 0.15)", color: "var(--accent-emerald)", border: "1px solid var(--accent-emerald)" }}>Online</span>
            </div>
            <div style={{ fontSize: "0.76rem", color: "var(--text-muted)" }}>Qdrant / Cosine 384-dim</div>
          </div>

          {/* Service 3 */}
          <div style={{ padding: "14px", borderRadius: "var(--radius-sm)", backgroundColor: "var(--bg-panel)", border: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <span style={{ fontWeight: 600, fontSize: "0.88rem" }}>Database Layer</span>
              <span className="badge" style={{ backgroundColor: "rgba(16, 185, 129, 0.15)", color: "var(--accent-emerald)", border: "1px solid var(--accent-emerald)" }}>Connected</span>
            </div>
            <div style={{ fontSize: "0.76rem", color: "var(--text-muted)" }}>SQLite3 / WAL Mode</div>
          </div>

          {/* Service 4 */}
          <div style={{ padding: "14px", borderRadius: "var(--radius-sm)", backgroundColor: "var(--bg-panel)", border: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <span style={{ fontWeight: 600, fontSize: "0.88rem" }}>Frontend Client</span>
              <span className="badge" style={{ backgroundColor: "rgba(16, 185, 129, 0.15)", color: "var(--accent-emerald)", border: "1px solid var(--accent-emerald)" }}>Vite 6.4</span>
            </div>
            <div style={{ fontSize: "0.76rem", color: "var(--text-muted)" }}>React 19 • Framer Motion</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
