import { useState, useEffect } from "react";
import { api, type MemeRecord } from "../api";
import { Icon } from "./Icon";
import { soundFx } from "../lib/audio";

export function AdminTab({ onToast }: { onToast: (m: string) => void }) {
  const [memes, setMemes] = useState<MemeRecord[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [msg, setMsg] = useState("");
  const [msgType, setMsgType] = useState<"success" | "error">("success");
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

  useEffect(() => {
    load();
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

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
          <Icon name="settings" size={22} color="var(--brand-primary)" />
          Database Management & Admin
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "4px" }}>
          Register new reaction memes, configure dialogues, and manage indexed records
        </p>
      </div>

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
    </div>
  );
}
