import { Icon } from "./Icon";

export function AboutView() {
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
          <div className="logo-icon-box">
            <Icon name="sparkles" size={18} color="#ffffff" />
          </div>
          <h1 style={{ fontSize: "1.8rem", fontWeight: 800, margin: 0, color: "var(--text-primary)" }}>
            About MemeGPT
          </h1>
        </div>

        <p style={{ fontSize: "1.05rem", color: "var(--text-secondary)", lineHeight: "1.6", marginBottom: "28px" }}>
          MemeGPT is an advanced semantic meme discovery and conversational recommendation engine. It interprets nuanced situational text, emotional undertones, and pop culture contexts to instantly recommend the perfect meme for any real-world moment.
        </p>

        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
          <Icon name="zap" size={18} color="var(--brand-primary)" />
          <h2 style={{ fontSize: "1.15rem", fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
            Architectural Highlights
          </h2>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: "14px",
            marginBottom: "28px",
          }}
        >
          <div style={{ padding: "16px", borderRadius: "var(--radius-sm)", backgroundColor: "var(--bg-panel)", border: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 600, fontSize: "0.92rem", marginBottom: "4px" }}>
              <Icon name="clock" size={15} color="var(--accent-emerald)" />
              Sub-50ms Vector Retrieval
            </div>
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", margin: 0 }}>
              Real-time cosine similarity search across 384-dimensional dense semantic embeddings.
            </p>
          </div>

          <div style={{ padding: "16px", borderRadius: "var(--radius-sm)", backgroundColor: "var(--bg-panel)", border: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 600, fontSize: "0.92rem", marginBottom: "4px" }}>
              <Icon name="film" size={15} color="var(--accent-cyan)" />
              Multi-Format Engine
            </div>
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", margin: 0 }}>
              Instant generation and download pipeline for WebP, animated GIFs, MP4 video clips, and high-res PNGs.
            </p>
          </div>

          <div style={{ padding: "16px", borderRadius: "var(--radius-sm)", backgroundColor: "var(--bg-panel)", border: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 600, fontSize: "0.92rem", marginBottom: "4px" }}>
              <Icon name="shield" size={15} color="var(--accent-emerald)" />
              Zero-Tracking Privacy
            </div>
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", margin: 0 }}>
              No invasive tracking cookies, browser fingerprinting, or forced personal data collection.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
