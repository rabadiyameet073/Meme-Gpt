import { useState, useEffect } from "react";
import { api, type MemeRecord } from "../api";
import { Icon } from "./Icon";

export function AdminTab({ onToast }: { onToast: (m: string) => void }) {
  const [memes, setMemes] = useState<MemeRecord[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [msg, setMsg] = useState("");
  const [msgType, setMsgType] = useState<"success" | "error">("success");
  const [form, setForm] = useState({
    name: "",
    category: "funny",
    dialogue: "",
    explanation: "",
    keywords: "",
    videoRef: "",
    gifRef: "",
  });

  const load = async () => {
    try {
      const res = await api.searchMemes("", "", 1, 100);
      setMemes(res.items);
      const cats = await api.categories();
      setCategories(cats);
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
      setMsg("Meme added to database");
      setMsgType("success");
      onToast("Meme created successfully!");
      setForm({ name: "", category: "funny", dialogue: "", explanation: "", keywords: "", videoRef: "", gifRef: "" });
      load();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed to add meme");
      setMsgType("error");
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Delete this meme permanently from database?")) return;
    try {
      await api.deleteMeme(id);
      onToast("Meme deleted.");
      load();
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="admin-layout">
      {/* Form Panel */}
      <div className="admin-panel">
        <h2>
          <Icon name="plus" size={16} /> Add Meme Entry
        </h2>
        {msg && (
          <div className={msgType === "success" ? "success-msg" : "error-box"} style={{ marginBottom: 12 }}>
            <Icon name={msgType === "success" ? "check" : "alert"} size={15} />
            <span>{msg}</span>
          </div>
        )}
        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Meme Name *</label>
            <input
              className="form-input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="e.g. Aukat Me Reh"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Category *</label>
            <select
              className="form-input"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
            >
              {(categories.length ? categories : ["funny", "coding", "startup", "college", "office"]).map((c) => (
                <option key={c} value={c}>
                  {c.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Catchphrase / Dialogue *</label>
            <input
              className="form-input"
              value={form.dialogue}
              onChange={(e) => setForm({ ...form, dialogue: e.target.value })}
              placeholder="The iconic dialogue"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Context Explanation *</label>
            <textarea
              className="form-input"
              value={form.explanation}
              onChange={(e) => setForm({ ...form, explanation: e.target.value })}
              placeholder="Why this meme matches situations"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Keywords (comma separated) *</label>
            <input
              className="form-input"
              value={form.keywords}
              onChange={(e) => setForm({ ...form, keywords: e.target.value })}
              placeholder="bug, prod, deploy"
              required
            />
          </div>
          <button type="submit" className="btn-primary">
            Add Meme
          </button>
        </form>
      </div>

      {/* Inventory Panel */}
      <div className="admin-panel">
        <h2>
          <Icon name="file-text" size={16} /> Database Inventory ({memes.length})
        </h2>
        <div className="admin-list">
          {memes.map((m) => (
            <div key={m.id} className="admin-item">
              <div className="admin-item-info">
                <div className="admin-item-name">{m.name}</div>
                <div className="admin-item-sub">
                  {m.category} · {m.usageCount} uses
                </div>
              </div>
              <button className="btn-danger" onClick={() => remove(m.id)}>
                <Icon name="trash" size={13} /> Delete
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
