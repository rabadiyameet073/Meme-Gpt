import { Icon } from "./Icon";

export function PrivacyView() {
  return (
    <div style={{ maxWidth: "860px", margin: "0 auto", paddingBottom: "40px" }}>
      <div
        style={{
          backgroundColor: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-md)",
          padding: "36px",
          boxShadow: "var(--shadow-md)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
          <div className="logo-icon-box" style={{ backgroundColor: "var(--accent-emerald)" }}>
            <Icon name="shield" size={18} color="#ffffff" />
          </div>
          <h1 style={{ fontSize: "1.8rem", fontWeight: 800, margin: 0, color: "var(--text-primary)" }}>
            Privacy Policy & Data Security
          </h1>
        </div>

        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "24px" }}>
          Last Updated: August 2026 • MemeGPT Architecture Standard
        </p>

        <div style={{ marginBottom: "24px" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "8px", color: "var(--text-primary)" }}>
            1. Zero-Tracking Architecture
          </h2>
          <p style={{ color: "var(--text-secondary)", lineHeight: "1.6", fontSize: "0.92rem" }}>
            MemeGPT is engineered from the ground up without mandatory user accounts, tracking pixels, or cross-site behavioral telemetry. Search queries are processed ephemerally for vector cosine matching and cached with cryptographic privacy hashes.
          </p>
        </div>

        <div style={{ marginBottom: "24px" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "8px", color: "var(--text-primary)" }}>
            2. Local Browser Storage
          </h2>
          <p style={{ color: "var(--text-secondary)", lineHeight: "1.6", fontSize: "0.92rem" }}>
            Bookmarked memes, custom collections, format preferences, and theme choices are stored strictly in your browser's private local storage (<code style={{ color: "var(--brand-primary)" }}>localStorage</code>) and are never uploaded or sold to advertising brokers.
          </p>
        </div>

        <div>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "8px", color: "var(--text-primary)" }}>
            3. Rate Limiting & Abuse Prevention
          </h2>
          <p style={{ color: "var(--text-secondary)", lineHeight: "1.6", fontSize: "0.92rem" }}>
            To safeguard API availability, requests are rate-limited via client IP headers without storing permanent identity logs.
          </p>
        </div>
      </div>
    </div>
  );
}
