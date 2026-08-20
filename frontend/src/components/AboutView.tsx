export function AboutView() {
  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px 0" }}>
      <div
        style={{
          background: "var(--bg-surface, #141414)",
          border: "1px solid var(--border)",
          borderRadius: "16px",
          padding: "32px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
        }}
      >
        <h1 style={{ fontSize: "1.8rem", fontWeight: 700, marginBottom: "12px", color: "var(--text-primary)" }}>
          About MemeGPT 🎭
        </h1>
        <p style={{ fontSize: "1.05rem", color: "var(--text-secondary)", lineHeight: "1.6", marginBottom: "24px" }}>
          MemeGPT is an advanced semantic meme discovery and conversational matching engine. It interprets nuanced situational text, emotional undertones, and pop culture contexts to instantly recommend the perfect meme.
        </p>

        <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginTop: "24px", marginBottom: "12px", color: "var(--brand-purple, #A78BFA)" }}>
          🚀 Architectural Highlights
        </h3>
        <ul style={{ color: "var(--text-secondary)", lineHeight: "1.8", paddingLeft: "20px" }}>
          <li><strong>Sub-1.5s Latency Orchestrator:</strong> Real-time vector search & heuristic reranking.</li>
          <li><strong>Multimodal Format Support:</strong> Instant downloads for WebP, GIF, MP4 Video, and HD PNGs.</li>
          <li><strong>Hybrid Semantic Index:</strong> Powered by Qdrant vector embeddings and BM25 full-text indexing.</li>
          <li><strong>Zero-Tracking Privacy:</strong> No invasive tracking cookies or personal profile lock-in.</li>
        </ul>
      </div>
    </div>
  );
}
