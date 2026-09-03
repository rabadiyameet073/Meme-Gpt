import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, download, type MemeSearchResult, type MemeMatch } from "../api";
import { MemeCard } from "./MemeCard";
import { Icon, type IconName } from "./Icon";
import { Tilt3D } from "./Tilt3D";

const SITUATION_PROMPTS: { text: string; icon: IconName }[] = [
  { text: "Production crashed at 3 AM on a Friday and it's my code", icon: "alert" },
  { text: "Client wants full project delivered tomorrow morning with zero budget", icon: "office" },
  { text: "Studying whole syllabus one night before final exams", icon: "college" },
  { text: "Manager says just fix this tiny 1-line bug, PR has 800 file changes", icon: "coding" },
  { text: "HR sent a message saying 'Hey, do you have 5 minutes to talk?'", icon: "chat" },
  { text: "Salary credited on 1st, account balance ₹142 by 5th", icon: "stats" },
  { text: "Working at a fast-paced AI startup where everything is urgent", icon: "startup" },
  { text: "Carrying the entire squad in gaming and still losing", icon: "gaming" },
];

export function ChatTab({
  onToast,
  onSearchCompleted,
}: {
  onToast: (m: string) => void;
  onSearchCompleted?: (query: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<MemeSearchResult | null>(null);
  const [lastQuery, setLastQuery] = useState("");
  const [formatPref, setFormatPref] = useState<"gif" | "image" | "video" | "webp">("gif");
  const taRef = useRef<HTMLTextAreaElement>(null);

  const submit = async (text?: string) => {
    const q = (text ?? query).trim();
    if (!q || loading) return;
    setLoading(true);
    setError("");
    setLastQuery(q);
    setQuery("");
    setResult(null);
    taRef.current?.blur();
    try {
      const res = await api.analyze(q);
      setResult(res);
      onToast(`AI match generated in ${res.latencyMs || 24}ms!`);
      onSearchCompleted?.(q);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong connecting to the AI search service.");
    } finally {
      setLoading(false);
    }
  };

  const doExport = async (format: string) => {
    if (!result || !lastQuery) return;
    try {
      const { content, filename } = await api.export(lastQuery, format, result);
      download(content, filename);
      onToast(`Downloaded ${filename}`);
    } catch {
      setError("Export failed");
    }
  };

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
      {/* Hero Header */}
      <div className="search-hero">
        <div className="hero-tag">
          <Icon name="sparkles" size={14} color="var(--brand-primary)" />
          <span>Multimodal Neural Meme Recommendation Engine</span>
        </div>
        <h1 className="hero-title">
          Find the Exact Meme for Any Situation
        </h1>
        <p className="hero-subtitle">
          Describe any awkward conversation, coding disaster, startup pain, or emotional vibe in plain English.
        </p>

        {/* Prompt Console */}
        <div className="search-console-box">
          <div style={{ padding: "12px 16px 6px" }}>
            <textarea
              ref={taRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe your situation, problem, or emotion... (e.g. 'Senior dev watching junior push straight to main')"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit();
                }
              }}
              rows={3}
              style={{
                width: "100%",
                background: "transparent",
                border: "none",
                outline: "none",
                color: "var(--text-primary)",
                fontFamily: "var(--font-body)",
                fontSize: "1rem",
                resize: "none",
                lineHeight: 1.5,
              }}
            />
          </div>

          {/* Console Controls Row */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "10px 16px",
              borderTop: "1px solid var(--border-subtle)",
              backgroundColor: "var(--bg-panel)",
              flexWrap: "wrap",
              gap: "8px",
            }}
          >
            {/* Format Selection Switcher */}
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase" }}>
                Format:
              </span>
              {(["gif", "image", "video", "webp"] as const).map((fmt) => (
                <button
                  key={fmt}
                  type="button"
                  onClick={() => setFormatPref(fmt)}
                  style={{
                    padding: "4px 10px",
                    fontSize: "0.72rem",
                    fontWeight: 600,
                    borderRadius: "var(--radius-xs)",
                    border: formatPref === fmt ? "1px solid var(--brand-primary)" : "1px solid var(--border)",
                    backgroundColor: formatPref === fmt ? "var(--brand-primary-subtle)" : "transparent",
                    color: formatPref === fmt ? "var(--brand-primary)" : "var(--text-secondary)",
                    cursor: "pointer",
                    transition: "all var(--transition-fast)",
                  }}
                >
                  {fmt.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Submit Button & Shortcut Hint */}
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Press <kbd style={{ padding: "2px 5px", background: "var(--bg-input)", border: "1px solid var(--border)", borderRadius: "3px" }}>Enter ↵</kbd>
              </span>
              <button
                type="button"
                className="search-submit-btn"
                onClick={() => submit()}
                disabled={loading || !query.trim()}
                style={{ opacity: loading || !query.trim() ? 0.6 : 1 }}
              >
                {loading ? (
                  <>
                    <div
                      style={{
                        width: 14,
                        height: 14,
                        border: "2px solid #ffffff",
                        borderTopColor: "transparent",
                        borderRadius: "50%",
                        animation: "spin 0.7s linear infinite",
                      }}
                    />
                    Matching...
                  </>
                ) : (
                  <>
                    <Icon name="sparkles" size={15} color="#ffffff" />
                    Match Meme
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Example Situation Chips */}
        <div style={{ marginTop: "24px", textAlign: "left" }}>
          <div
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: "10px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Icon name="sparkles" size={13} color="var(--brand-primary)" />
            <span>Instant Situation Prompts:</span>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {SITUATION_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                className="chip-btn"
                onClick={() => submit(prompt.text)}
                disabled={loading}
              >
                <Icon name={prompt.icon} size={14} color="var(--text-muted)" />
                <span>{prompt.text.length > 46 ? prompt.text.slice(0, 44) + "…" : prompt.text}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Alert Box */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            padding: "14px 18px",
            borderRadius: "var(--radius-sm)",
            backgroundColor: "rgba(244, 63, 94, 0.1)",
            border: "1px solid var(--accent-rose)",
            color: "var(--accent-rose)",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            fontSize: "0.9rem",
            marginBottom: "24px",
          }}
        >
          <Icon name="alert" size={18} color="var(--accent-rose)" />
          <span>{error}</span>
        </motion.div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div style={{ padding: "40px 0", textAlign: "center" }}>
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
          <h3 style={{ fontSize: "1.05rem", color: "var(--text-primary)", marginBottom: "4px" }}>
            Running Semantic Embedding & Cosine Retrieval…
          </h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
            Evaluating context, dialogue emotion, and resonance
          </p>
        </div>
      )}

      {/* AI Recommendation Results Section */}
      <AnimatePresence>
        {result && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            style={{ marginTop: "16px" }}
          >
            {/* Situation Echo & Context Badge */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "12px",
                padding: "14px 18px",
                backgroundColor: "var(--bg-card)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--border)",
                marginBottom: "24px",
              }}
            >
              <div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase" }}>
                  Analyzed Situation
                </div>
                <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)", marginTop: "2px" }}>
                  "{lastQuery}"
                </div>
              </div>

              <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                {result.detectedCategories?.map((c: string) => (
                  <span key={c} className="badge badge-category">
                    <Icon name="tag" size={11} /> {c.replace(/_/g, " ")}
                  </span>
                ))}
                <span
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--accent-emerald)",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    fontWeight: 600,
                  }}
                >
                  <Icon name="clock" size={12} /> {result.latencyMs || 22}ms
                </span>
              </div>
            </div>

            {/* Best Match Hero Card with 3D Tilt */}
            {result.primary && (
              <div style={{ marginBottom: "32px" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    color: "var(--brand-primary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    marginBottom: "12px",
                  }}
                >
                  <Icon name="trophy" size={16} color="var(--brand-primary)" />
                  <span>Primary AI Recommendation:</span>
                </div>
                <Tilt3D maxTilt={6} perspective={1200}>
                  <MemeCard
                    meme={result.primary}
                    primary
                    showConfidence
                    queryId={(result as any).query_id || (result as any).queryId}
                    onToast={onToast}
                  />
                </Tilt3D>
              </div>
            )}

            {/* Alternative Matches Grid */}
            {result.topFive && result.topFive.length > 1 && (
              <div style={{ marginBottom: "32px" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    color: "var(--text-secondary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    marginBottom: "14px",
                  }}
                >
                  <Icon name="layers" size={16} />
                  <span>Alternative Top Matches:</span>
                </div>
                <div className="card-grid">
                  {result.topFive.slice(1).map((m: MemeMatch) => (
                    <MemeCard
                      key={m.id}
                      meme={m}
                      showConfidence
                      queryId={(result as any).query_id || (result as any).queryId}
                      onToast={onToast}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Additional Alternatives */}
            {result.alternatives && result.alternatives.length > 0 && (
              <div style={{ marginBottom: "32px" }}>
                <div
                  style={{
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    color: "var(--text-secondary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    marginBottom: "14px",
                  }}
                >
                  More Contextual Matches:
                </div>
                <div className="card-grid">
                  {result.alternatives.map((m: MemeMatch) => (
                    <MemeCard
                      key={m.id}
                      meme={m}
                      showConfidence
                      queryId={(result as any).query_id || (result as any).queryId}
                      onToast={onToast}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Export Toolbar */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "16px 20px",
                backgroundColor: "var(--bg-card)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--border)",
                marginTop: "24px",
                flexWrap: "wrap",
                gap: "12px",
              }}
            >
              <div>
                <span style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--text-primary)" }}>
                  Export Recommendation
                </span>
                <p style={{ fontSize: "0.76rem", color: "var(--text-muted)", margin: "2px 0 0" }}>
                  Save recommendation data as structured markdown, JSON, or text
                </p>
              </div>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => doExport("markdown")}
                  style={{ fontSize: "0.8rem" }}
                >
                  <Icon name="file-text" size={13} /> Markdown (.md)
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => doExport("json")}
                  style={{ fontSize: "0.8rem" }}
                >
                  <Icon name="code" size={13} /> JSON (.json)
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => doExport("txt")}
                  style={{ fontSize: "0.8rem" }}
                >
                  <Icon name="file-text" size={13} /> Text (.txt)
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
