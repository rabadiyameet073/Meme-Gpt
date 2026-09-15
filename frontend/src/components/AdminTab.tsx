import { useState, useEffect } from "react";
import { api, type MemeRecord } from "../api";
import { Icon } from "./Icon";
import { soundFx } from "../lib/audio";

interface QueuedMeme extends MemeRecord {
  flag_count?: number;
  flags?: Array<{ reason: string; details?: string; created_at?: string }>;
  moderation_status?: string;
  preview_url?: string;
  imageRef?: string;
  gifRef?: string;
  formats?: { image?: string; gif?: string; video?: string; webp?: string };
}

export function AdminTab({ onToast }: { onToast: (m: string) => void }) {
  const [activeSubTab, setActiveSubTab] = useState<"inventory" | "moderation">("inventory");
  const [memes, setMemes] = useState<MemeRecord[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [queue, setQueue] = useState<QueuedMeme[]>([]);
  const [loadingQueue, setLoadingQueue] = useState(false);
  const [msg, setMsg] = useState("");
  const [msgType, setMsgType] = useState<"success" | "error">("success");

  // Zero-shot CLIP testing states
  const [classifyingId, setClassifyingId] = useState<string | null>(null);
  const [clipResults, setClipResults] = useState<
    Record<string, { is_nsfw: boolean; confidence: number; category: string }>
  >({});

  const [form, setForm] = useState({
    name: "",
    category: "work",
    dialogue: "",
    explanation: "",
    keywords: "",
    videoRef: "",
    gifRef: "",
  });

  const load = async () => {
    try {
      const res = await api.searchMemes("", "", 1, 100);
      setMemes(res.items || []);
      const cats = await api.categories();
      setCategories(cats || []);
    } catch {
      setMsg("FastAPI backend connection error.");
    }
  };

  const loadQueue = async () => {
    setLoadingQueue(true);
    try {
      const res = await api.getModerationQueue();
      setQueue(res.queue || []);
    } catch {
      onToast("Failed to fetch moderation queue");
    } finally {
      setLoadingQueue(false);
    }
  };

  useEffect(() => {
    load();
    loadQueue();
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg("");
    try {
      await api.createMeme({
        name: form.name,
        category: form.category,
        dialogue: form.dialogue,
        explanation: form.explanation,
        keywords: form.keywords.split(",").map((k) => k.trim()).filter(Boolean),
        videoRef: form.videoRef || undefined,
        gifRef: form.gifRef || undefined,
      });
      soundFx.playSuccess();
      setMsg("Meme added to database successfully!");
      setMsgType("success");
      onToast("Meme created successfully!");
      setForm({ name: "", category: "work", dialogue: "", explanation: "", keywords: "", videoRef: "", gifRef: "" });
      load();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed to add meme");
      setMsgType("error");
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Permanently delete this meme template from the database?")) return;
    try {
      await api.deleteMeme(id);
      soundFx.playClick();
      onToast("Meme deleted.");
      load();
    } catch {
      /* ignore */
    }
  };

  const handleReview = async (memeId: string, action: "approve" | "remove") => {
    try {
      await api.reviewMeme(memeId, action);
      if (action === "approve") {
        soundFx.playSuccess();
        onToast("Meme approved and restored to feeds.");
      } else {
        soundFx.playClick();
        onToast("Meme removed and suppressed from feeds.");
      }
      // Remove from local queue
      setQueue((prev) => prev.filter((m) => m.id !== memeId));
      load(); // Refresh inventory
    } catch {
      onToast("Moderation review action failed.");
    }
  };

  const handleTestNsfw = async (m: QueuedMeme) => {
    const mediaUrl =
      m.formats?.image ||
      m.formats?.gif ||
      m.preview_url ||
      m.imageRef ||
      m.gifRef ||
      "";

    if (!mediaUrl) {
      onToast("No media URL available to analyze.");
      return;
    }

    setClassifyingId(m.id);
    try {
      const result = await api.classifyImage(mediaUrl);
      setClipResults((prev) => ({
        ...prev,
        [m.id]: result,
      }));
      soundFx.playTap();
      onToast(
        result.is_nsfw
          ? `Warning: Flagged as NSFW (${Math.round(result.confidence * 100)}%)`
          : `Safe: Content verified clean (${Math.round(result.confidence * 100)}%)`
      );
    } catch {
      onToast("CLIP classification error.");
    } finally {
      setClassifyingId(null);
    }
  };

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
      {/* Header & Sub-tab Switcher */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
            <Icon name="settings" size={22} color="var(--brand-primary)" />
            Database & Content Moderation
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "4px" }}>
            Manage indexed reaction memes, register new templates, and review community-flagged content
          </p>
        </div>

        {/* Navigation Pills */}
        <div
          style={{
            display: "inline-flex",
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)",
            padding: "3px",
            gap: "4px",
          }}
        >
          <button
            type="button"
            onClick={() => {
              setActiveSubTab("inventory");
              soundFx.playTap();
            }}
            style={{
              padding: "7px 14px",
              fontSize: "0.82rem",
              fontWeight: 600,
              borderRadius: "var(--radius-xs)",
              border: "none",
              backgroundColor: activeSubTab === "inventory" ? "var(--brand-primary)" : "transparent",
              color: activeSubTab === "inventory" ? "#ffffff" : "var(--text-secondary)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              transition: "all var(--transition-fast)",
            }}
          >
            <Icon name="database" size={14} />
            Templates & Inventory
          </button>

          <button
            type="button"
            onClick={() => {
              setActiveSubTab("moderation");
              soundFx.playTap();
              loadQueue();
            }}
            style={{
              padding: "7px 14px",
              fontSize: "0.82rem",
              fontWeight: 600,
              borderRadius: "var(--radius-xs)",
              border: "none",
              backgroundColor: activeSubTab === "moderation" ? "var(--brand-primary)" : "transparent",
              color: activeSubTab === "moderation" ? "#ffffff" : "var(--text-secondary)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              transition: "all var(--transition-fast)",
            }}
          >
            <Icon name="shield" size={14} />
            Moderation Queue
            {queue.length > 0 && (
              <span
                style={{
                  backgroundColor: "var(--accent-rose)",
                  color: "#ffffff",
                  fontSize: "0.72rem",
                  padding: "1px 6px",
                  borderRadius: "10px",
                  fontWeight: 700,
                  marginLeft: "2px",
                }}
              >
                {queue.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* SUBTAB 1: Moderation Queue */}
      {activeSubTab === "moderation" && (
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "16px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>
                Pending Safety Review
              </span>
              <span
                style={{
                  fontSize: "0.78rem",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-xs)",
                  backgroundColor: queue.length > 0 ? "rgba(244, 63, 94, 0.12)" : "rgba(16, 185, 129, 0.12)",
                  color: queue.length > 0 ? "var(--accent-rose)" : "var(--accent-emerald)",
                  border: `1px solid ${queue.length > 0 ? "var(--accent-rose)" : "var(--accent-emerald)"}`,
                  fontWeight: 700,
                }}
              >
                {queue.length} {queue.length === 1 ? "meme requires review" : "memes require review"}
              </span>
            </div>

            <button
              type="button"
              onClick={loadQueue}
              disabled={loadingQueue}
              className="btn btn-secondary"
              style={{ padding: "6px 12px", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: "6px" }}
            >
              <Icon name="refresh" size={13} />
              {loadingQueue ? "Checking..." : "Refresh Queue"}
            </button>
          </div>

          {queue.length === 0 ? (
            <div
              style={{
                backgroundColor: "var(--bg-card)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-md)",
                padding: "48px 24px",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  width: "48px",
                  height: "48px",
                  borderRadius: "50%",
                  backgroundColor: "rgba(16, 185, 129, 0.12)",
                  color: "var(--accent-emerald)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 16px",
                }}
              >
                <Icon name="check" size={24} />
              </div>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "6px" }}>
                Queue is completely clear!
              </h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", maxWidth: "420px", margin: "0 auto" }}>
                No reaction memes have been flagged by the community or exceeded the automated safety review threshold.
              </p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {queue.map((m) => {
                const mediaUrl =
                  m.formats?.image ||
                  m.formats?.gif ||
                  m.preview_url ||
                  m.imageRef ||
                  m.gifRef;

                // Aggregate reasons
                const reasonCounts: Record<string, number> = {};
                (m.flags || []).forEach((f) => {
                  reasonCounts[f.reason] = (reasonCounts[f.reason] || 0) + 1;
                });
                const reasonsSummary = Object.entries(reasonCounts)
                  .map(([r, count]) => `${count} ${r}`)
                  .join(", ");

                const clip = clipResults[m.id];

                return (
                  <div
                    key={m.id}
                    style={{
                      backgroundColor: "var(--bg-card)",
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius-md)",
                      padding: "20px",
                      display: "flex",
                      gap: "20px",
                      flexWrap: "wrap",
                      alignItems: "flex-start",
                    }}
                  >
                    {/* Media Thumbnail */}
                    {mediaUrl ? (
                      <div
                        style={{
                          width: "160px",
                          height: "120px",
                          borderRadius: "var(--radius-xs)",
                          overflow: "hidden",
                          backgroundColor: "#000000",
                          border: "1px solid var(--border)",
                          flexShrink: 0,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <img
                          src={mediaUrl}
                          alt={m.name}
                          style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }}
                          onError={(e) => {
                            (e.target as HTMLElement).style.display = "none";
                          }}
                        />
                      </div>
                    ) : (
                      <div
                        style={{
                          width: "160px",
                          height: "120px",
                          borderRadius: "var(--radius-xs)",
                          backgroundColor: "var(--bg-panel)",
                          border: "1px dashed var(--border)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: "var(--text-muted)",
                          fontSize: "0.78rem",
                          flexShrink: 0,
                        }}
                      >
                        No Media Preview
                      </div>
                    )}

                    {/* Meme Info & Flag Breakdown */}
                    <div style={{ flex: 1, minWidth: "260px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                        <span
                          style={{
                            fontSize: "0.72rem",
                            padding: "2px 7px",
                            borderRadius: "var(--radius-xs)",
                            backgroundColor: "rgba(244, 63, 94, 0.15)",
                            color: "var(--accent-rose)",
                            fontWeight: 700,
                            textTransform: "uppercase",
                          }}
                        >
                          {m.moderation_status || "pending_review"}
                        </span>
                        <span
                          style={{
                            fontSize: "0.72rem",
                            padding: "2px 7px",
                            borderRadius: "var(--radius-xs)",
                            backgroundColor: "rgba(255, 170, 0, 0.12)",
                            color: "#ffaa00",
                            fontWeight: 700,
                          }}
                        >
                          {m.flag_count || (m.flags?.length ?? 1)} Community Flags
                        </span>
                        <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                          Category: {m.category}
                        </span>
                      </div>

                      <h4 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
                        {m.name}
                      </h4>

                      {m.dialogue && (
                        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", fontStyle: "italic", marginBottom: "8px" }}>
                          "{m.dialogue}"
                        </p>
                      )}

                      {/* Flags breakdown */}
                      <div
                        style={{
                          backgroundColor: "var(--bg-panel)",
                          padding: "8px 12px",
                          borderRadius: "var(--radius-xs)",
                          border: "1px solid var(--border-subtle)",
                          fontSize: "0.8rem",
                          marginBottom: "10px",
                        }}
                      >
                        <strong style={{ color: "var(--text-primary)" }}>Flag reasons: </strong>
                        <span style={{ color: "var(--accent-rose)", fontWeight: 600 }}>
                          {reasonsSummary || "User report"}
                        </span>
                        {m.flags && m.flags.length > 0 && m.flags[0].details && (
                          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
                            Latest note: "{m.flags[0].details}"
                          </div>
                        )}
                      </div>

                      {/* CLIP Classification Result Badge */}
                      {clip && (
                        <div
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            padding: "4px 10px",
                            borderRadius: "var(--radius-xs)",
                            backgroundColor: clip.is_nsfw ? "rgba(244, 63, 94, 0.14)" : "rgba(16, 185, 129, 0.14)",
                            border: `1px solid ${clip.is_nsfw ? "var(--accent-rose)" : "var(--accent-emerald)"}`,
                            color: clip.is_nsfw ? "var(--accent-rose)" : "var(--accent-emerald)",
                            fontSize: "0.8rem",
                            fontWeight: 600,
                            marginBottom: "10px",
                          }}
                        >
                          <Icon name={clip.is_nsfw ? "alert" : "check"} size={14} />
                          <span>
                            CLIP Zero-Shot: {clip.is_nsfw ? "NSFW DETECTED" : "CLEAN"} (
                            {Math.round(clip.confidence * 100)}% {clip.category})
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Action Controls */}
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "8px",
                        minWidth: "160px",
                        flexShrink: 0,
                      }}
                    >
                      <button
                        type="button"
                        onClick={() => handleTestNsfw(m)}
                        disabled={classifyingId === m.id}
                        className="btn btn-secondary"
                        style={{
                          padding: "8px 12px",
                          fontSize: "0.78rem",
                          fontWeight: 600,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "6px",
                        }}
                      >
                        <Icon name="sparkles" size={14} color="var(--accent-cyan)" />
                        {classifyingId === m.id ? "Analyzing CLIP..." : "Test CLIP NSFW"}
                      </button>

                      <button
                        type="button"
                        onClick={() => handleReview(m.id, "approve")}
                        style={{
                          backgroundColor: "rgba(16, 185, 129, 0.14)",
                          border: "1px solid var(--accent-emerald)",
                          color: "var(--accent-emerald)",
                          padding: "8px 12px",
                          borderRadius: "var(--radius-xs)",
                          fontSize: "0.78rem",
                          fontWeight: 600,
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "6px",
                        }}
                      >
                        <Icon name="check" size={14} />
                        Approve (Dismiss)
                      </button>

                      <button
                        type="button"
                        onClick={() => handleReview(m.id, "remove")}
                        style={{
                          backgroundColor: "rgba(244, 63, 94, 0.14)",
                          border: "1px solid var(--accent-rose)",
                          color: "var(--accent-rose)",
                          padding: "8px 12px",
                          borderRadius: "var(--radius-xs)",
                          fontSize: "0.78rem",
                          fontWeight: 600,
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "6px",
                        }}
                      >
                        <Icon name="trash" size={14} />
                        Remove (Suppress)
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* SUBTAB 2: Templates & Inventory */}
      {activeSubTab === "inventory" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
            gap: "24px",
          }}
        >
          {/* Form Panel */}
          <div
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-md)",
              padding: "24px",
            }}
          >
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Icon name="plus" size={16} color="var(--brand-primary)" />
              Add New Template
            </h3>

            {msg && (
              <div
                style={{
                  padding: "10px 14px",
                  borderRadius: "var(--radius-xs)",
                  backgroundColor: msgType === "success" ? "rgba(16, 185, 129, 0.12)" : "rgba(244, 63, 94, 0.12)",
                  border: `1px solid ${msgType === "success" ? "var(--accent-emerald)" : "var(--accent-rose)"}`,
                  color: msgType === "success" ? "var(--accent-emerald)" : "var(--accent-rose)",
                  fontSize: "0.85rem",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  marginBottom: "16px",
                }}
              >
                <Icon name={msgType === "success" ? "check" : "alert"} size={15} />
                <span>{msg}</span>
              </div>
            )}

            <form onSubmit={submit}>
              <div style={{ marginBottom: "14px" }}>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: "4px" }}>
                  Meme Name *
                </label>
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. This Is Fine"
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px",
                    backgroundColor: "var(--bg-input)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-xs)",
                    color: "var(--text-primary)",
                    fontFamily: "var(--font-body)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                />
              </div>

              <div style={{ marginBottom: "14px" }}>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: "4px" }}>
                  Category *
                </label>
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  style={{
                    width: "100%",
                    padding: "9px 12px",
                    backgroundColor: "var(--bg-input)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-xs)",
                    color: "var(--text-primary)",
                    fontFamily: "var(--font-body)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                >
                  {(categories.length ? categories : ["work", "coding", "startup", "college", "gaming", "bollywood"]).map((c) => (
                    <option key={c} value={c} style={{ background: "#10121e", color: "#ffffff" }}>
                      {c.replace(/_/g, " ").toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: "14px" }}>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: "4px" }}>
                  Catchphrase / Dialogue *
                </label>
                <input
                  value={form.dialogue}
                  onChange={(e) => setForm({ ...form, dialogue: e.target.value })}
                  placeholder="e.g. This is fine."
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px",
                    backgroundColor: "var(--bg-input)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-xs)",
                    color: "var(--text-primary)",
                    fontFamily: "var(--font-body)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                />
              </div>

              <div style={{ marginBottom: "14px" }}>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: "4px" }}>
                  Context Explanation *
                </label>
                <textarea
                  value={form.explanation}
                  onChange={(e) => setForm({ ...form, explanation: e.target.value })}
                  placeholder="Explain why and when this meme is applicable"
                  rows={2}
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px",
                    backgroundColor: "var(--bg-input)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-xs)",
                    color: "var(--text-primary)",
                    fontFamily: "var(--font-body)",
                    fontSize: "0.9rem",
                    outline: "none",
                    resize: "none",
                  }}
                />
              </div>

              <div style={{ marginBottom: "18px" }}>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 700, color: "var(--text-secondary)", marginBottom: "4px" }}>
                  Keywords (comma separated) *
                </label>
                <input
                  value={form.keywords}
                  onChange={(e) => setForm({ ...form, keywords: e.target.value })}
                  placeholder="dog, fire, room, cup, panic, calm"
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px",
                    backgroundColor: "var(--bg-input)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-xs)",
                    color: "var(--text-primary)",
                    fontFamily: "var(--font-body)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: "100%", padding: "10px" }}>
                <Icon name="plus" size={16} color="#ffffff" />
                Add Meme Record
              </button>
            </form>
          </div>

          {/* Inventory List Panel */}
          <div
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-md)",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Icon name="database" size={16} color="var(--accent-cyan)" />
              Database Inventory ({memes.length})
            </h3>

            <div
              style={{
                flex: 1,
                maxHeight: "520px",
                overflowY: "auto",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                paddingRight: "4px",
              }}
            >
              {memes.map((m) => (
                <div
                  key={m.id}
                  style={{
                    padding: "12px 14px",
                    borderRadius: "var(--radius-xs)",
                    backgroundColor: "var(--bg-panel)",
                    border: "1px solid var(--border-subtle)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: "0.9rem", color: "var(--text-primary)" }}>
                      {m.name}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "2px" }}>
                      <span style={{ textTransform: "capitalize" }}>{m.category}</span> • {m.usageCount || 0} uses
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => remove(m.id)}
                    style={{
                      backgroundColor: "rgba(244, 63, 94, 0.1)",
                      border: "1px solid var(--accent-rose)",
                      color: "var(--accent-rose)",
                      padding: "6px 10px",
                      borderRadius: "var(--radius-xs)",
                      fontSize: "0.75rem",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <Icon name="trash" size={12} />
                    Delete
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
