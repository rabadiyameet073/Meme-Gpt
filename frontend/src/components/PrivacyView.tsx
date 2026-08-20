export function PrivacyView() {
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
          Privacy Policy 🔒
        </h1>
        <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", lineHeight: "1.6", marginBottom: "20px" }}>
          Last Updated: August 2026
        </p>

        <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginTop: "20px", marginBottom: "8px", color: "var(--brand-purple, #A78BFA)" }}>
          1. Data We Do Not Collect
        </h3>
        <p style={{ color: "var(--text-secondary)", lineHeight: "1.6" }}>
          MemeGPT is built without mandatory user accounts, tracking cookies, or advertising identifiers. Search queries are processed in memory and aggregated anonymously for latency monitoring.
        </p>

        <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginTop: "20px", marginBottom: "8px", color: "var(--brand-purple, #A78BFA)" }}>
          2. Local Storage
        </h3>
        <p style={{ color: "var(--text-secondary)", lineHeight: "1.6" }}>
          Saved memes (Favorites) and format preferences are stored strictly in your local browser storage (`localStorage`) and are never synced to third-party databases without your consent.
        </p>
      </div>
    </div>
  );
}
