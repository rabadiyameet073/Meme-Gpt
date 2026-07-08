import { useState, useEffect, useRef } from "react";
import { api, download, getSessionId, type MemeSearchResult, type MemeRecord } from "./api";

/* ── Constants ─────────────────────────────────────────────── */
const SESSION_ID = getSessionId();

const EXAMPLES = [
  "I worked 3 months on a project and accuracy is only 12%. Can you make it 100%?",
  "Client wants the full project delivered tomorrow.",
  "Production is down at 3 AM and it's definitely my code.",
  "Manager says just fix this one tiny bug. PR has 800 file changes.",
  "First day at startup: we're agile, no deadlines. Day 2: feature needed by EOD.",
  "Studying for exam the night before: how hard can it be?",
];

type Tab = "chat" | "search" | "trending" | "admin";

/* ── Meme Card ──────────────────────────────────────────────── */
interface MemeCardProps {
  meme: {
    id: string;
    name: string;
    category: string;
    dialogue: string;
    explanation: string;
    confidence?: number;
    videoRef?: string | null;
    gifRef?: string | null;
    viralScore?: number;
    usageCount?: number;
  };
  primary?: boolean;
  showConfidence?: boolean;
}

function MemeCard({ meme, primary, showConfidence }: MemeCardProps) {
  const [vote, setVote] = useState<1 | -1 | null>(null);

  const doVote = async (v: 1 | -1) => {
    if (vote === v) return;
    setVote(v);
    try {
      await api.vote(meme.id, v, SESSION_ID);
    } catch {
      /* non-critical */
    }
  };

  const pct = meme.confidence !== undefined ? Math.round(meme.confidence * 100) : null;

  return (
    <div className={`meme-card ${primary ? "primary" : ""}`}>
      <div className="meme-header">
        <div className="meme-name">{meme.name}</div>
        <div className="meme-badges">
          <span className="badge badge-category">{meme.category.replace(/_/g, " ")}</span>
          {showConfidence && pct !== null && (
            <span className="badge badge-confidence">✦ {pct}%</span>
          )}
          {meme.viralScore !== undefined && meme.viralScore > 0 && (
            <span className="badge badge-viral">🔥 viral</span>
          )}
        </div>
      </div>

      {showConfidence && pct !== null && (
        <div className="confidence-bar" title={`Confidence: ${pct}%`}>
          <div className="confidence-fill" style={{ width: `${pct}%` }} />
        </div>
      )}

      <div className="meme-dialogue">"{meme.dialogue}"</div>
      <div className="meme-explanation">{meme.explanation}</div>

      {(meme.videoRef || meme.gifRef || meme.usageCount !== undefined) && (
        <div className="meme-meta">
          {meme.usageCount !== undefined && (
            <span>📊 {meme.usageCount} uses</span>
          )}
          {meme.videoRef && (
            <span>🎬 <a href={meme.videoRef} target="_blank" rel="noopener noreferrer">Video ref</a></span>
          )}
          {meme.gifRef && (
            <span>🎞 <a href={meme.gifRef} target="_blank" rel="noopener noreferrer">GIF ref</a></span>
          )}
        </div>
      )}

      <div className="vote-row">
        <button
          className={`btn-vote up ${vote === 1 ? "voted" : ""}`}
          onClick={() => doVote(1)}
          title="Upvote"
        >
          👍 Spot on
        </button>
        <button
          className={`btn-vote down ${vote === -1 ? "voted" : ""}`}
          onClick={() => doVote(-1)}
          title="Downvote"
        >
          👎 Not quite
        </button>
      </div>
    </div>
  );
}

/* ── Chat Tab ───────────────────────────────────────────────── */
function ChatTab() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<MemeSearchResult | null>(null);
  const [lastQuery, setLastQuery] = useState("");
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
      setResult(await api.analyze(q));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const doExport = async (format: string) => {
    if (!result || !lastQuery) return;
    try {
      const { content, filename } = await api.export(lastQuery, format, result);
      download(content, filename);
    } catch {
      setError("Export failed");
    }
  };

  const charCount = query.length;

  return (
    <div>
      {/* Input box */}
      <div className="input-wrapper">
        <textarea
          ref={taRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe your situation, problem, or life event... (e.g. 'My code worked locally but fails in production')"
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), submit())}
          maxLength={2000}
          rows={4}
        />
        <div className="input-actions">
          <span className="char-count">{charCount}/2000 · Enter to send, Shift+Enter for newline</span>
          <button className="btn-send" onClick={() => submit()} disabled={loading || !query.trim()}>
            {loading ? (
              <>
                <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
                Analyzing...
              </>
            ) : (
              <>🎭 Find Meme</>
            )}
          </button>
        </div>
      </div>

      {/* Example chips */}
      <div className="examples-section">
        <div className="examples-label">Try an example</div>
        <div className="examples-chips">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              className="chip"
              onClick={() => submit(ex)}
              disabled={loading}
              title={ex}
            >
              {ex.length > 55 ? ex.slice(0, 52) + "…" : ex}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="error-box">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <div className="loading-text">Scanning meme database…</div>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="results-section">
          {/* Query echo */}
          <div className="section-label">Your situation</div>
          <div className="query-echo">{lastQuery}</div>

          {/* Detected categories */}
          {result.detectedCategories?.length > 0 && (
            <>
              <div className="section-label" style={{ marginTop: 16 }}>Detected context</div>
              <div className="tag-list">
                {result.detectedCategories.map((c) => (
                  <span key={c} className="tag">📌 {c.replace(/_/g, " ")}</span>
                ))}
                {result.detectedTags?.map((t) => (
                  <span key={t} className="tag">🏷 {t}</span>
                ))}
                <span className="latency">⚡ {result.latencyMs}ms</span>
              </div>
            </>
          )}

          {/* Best match */}
          <div className="section-label" style={{ marginTop: 20 }}>
            🏆 Best Match
          </div>
          <MemeCard meme={result.primary} primary showConfidence />

          {/* Top 5 */}
          {result.topFive?.length > 0 && (
            <>
              <div className="section-label">Top 5 Matches</div>
              {result.topFive.map((m) => (
                <MemeCard key={m.id} meme={m} showConfidence />
              ))}
            </>
          )}

          {/* Alternatives */}
          {result.alternatives?.length > 0 && (
            <>
              <div className="section-label">Alternative Memes</div>
              {result.alternatives.map((m) => (
                <MemeCard key={m.id} meme={m} showConfidence />
              ))}
            </>
          )}

          {/* Viral suggestions */}
          {result.viralSuggestions?.length > 0 && (
            <>
              <div className="section-label">🔥 Viral Meme Suggestions</div>
              {result.viralSuggestions.map((m) => (
                <MemeCard key={m.id} meme={m} />
              ))}
            </>
          )}

          {/* GIF suggestions */}
          {result.gifs?.length > 0 && (
            <>
              <div className="section-label">🎞 GIF Suggestions</div>
              <div className="gif-chips">
                {result.gifs.map((g, i) => (
                  <span key={i} className="gif-chip">{g}</span>
                ))}
              </div>
            </>
          )}

          {/* Export */}
          <div className="section-label" style={{ marginTop: 20 }}>Export Result</div>
          <div className="export-row">
            <button className="btn-export" onClick={() => doExport("txt")}>📄 TXT</button>
            <button className="btn-export" onClick={() => doExport("json")}>📦 JSON</button>
            <button className="btn-export" onClick={() => doExport("markdown")}>📝 Markdown</button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Search Tab ─────────────────────────────────────────────── */
function SearchTab() {
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");
  const [results, setResults] = useState<MemeRecord[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.categories().then(setCategories).catch(() => {});
    api.searchMemes().then(setResults).catch(() => {});
  }, []);

  useEffect(() => {
    const t = setTimeout(async () => {
      setLoading(true);
      try {
        setResults(await api.searchMemes(q, category));
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 320);
    return () => clearTimeout(t);
  }, [q, category]);

  return (
    <div className="search-wrap">
      <div className="search-input-wrap">
        <span className="search-icon">🔍</span>
        <input
          className="search-input"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by meme name, dialogue, or keyword…"
        />
      </div>

      <div className="filter-row">
        <select
          className="select-input"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}</option>
          ))}
        </select>
      </div>

      <div className="results-count">
        {loading ? "Searching…" : `${results.length} memes found`}
      </div>

      {results.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🃏</div>
          <p>No memes matched. Try a different search.</p>
        </div>
      )}

      {results.map((m) => (
        <div key={m.id} className="meme-card">
          <div className="meme-header">
            <div className="meme-name">{m.name}</div>
            <div className="meme-badges">
              <span className="badge badge-category">{m.category.replace(/_/g, " ")}</span>
              {m.usageCount > 0 && (
                <span className="badge" style={{ background: "rgba(139,92,246,0.12)", color: "#c4b5fd", border: "1px solid rgba(139,92,246,0.2)" }}>
                  📊 {m.usageCount}
                </span>
              )}
            </div>
          </div>
          <div className="meme-dialogue">"{m.dialogue}"</div>
          {m.explanation && <div className="meme-explanation">{m.explanation}</div>}
          {m.keywords?.length > 0 && (
            <div className="tag-list" style={{ marginTop: 10 }}>
              {m.keywords.map((k) => <span key={k} className="tag">#{k}</span>)}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/* ── Trending Tab ───────────────────────────────────────────── */
function TrendingTab() {
  const [memes, setMemes] = useState<MemeRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.trending()
      .then(setMemes)
      .catch(() => setMemes([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-wrap">
        <div className="spinner" />
        <div className="loading-text">Loading trending memes…</div>
      </div>
    );
  }

  if (memes.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📈</div>
        <p>No trending data yet. Start using MemeGPT to generate trends!</p>
      </div>
    );
  }

  return (
    <div>
      <div className="section-label">🔥 Most Used Memes</div>
      <div className="trending-grid">
        {memes.map((m, i) => (
          <div key={m.id} className="trending-card">
            <div className="trending-rank">
              Rank <span>#{i + 1}</span>
            </div>
            <div className="trending-name">{m.name}</div>
            <span className="badge badge-category" style={{ marginTop: 4 }}>{m.category.replace(/_/g, " ")}</span>
            <div className="meme-dialogue" style={{ marginTop: 10, fontSize: "0.82rem" }}>"{m.dialogue}"</div>
            <div className="trending-stats">
              <span>📊 {m.usageCount} uses</span>
              <span>👍 {m.upvotes}</span>
              <span>👎 {m.downvotes}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Admin Tab ──────────────────────────────────────────────── */
function AdminTab() {
  const [memes, setMemes] = useState<MemeRecord[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [msg, setMsg] = useState("");
  const [msgType, setMsgType] = useState<"success" | "error">("success");
  const [form, setForm] = useState({
    name: "", category: "funny", dialogue: "", explanation: "",
    keywords: "", videoRef: "", gifRef: "",
  });

  const load = () => {
    api.searchMemes().then(setMemes).catch(() => setMsg("Backend not reachable."));
    api.categories().then(setCategories).catch(() => {});
  };

  useEffect(() => { load(); }, []);

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
      setMsg("✅ Meme added successfully!");
      setMsgType("success");
      setForm({ name: "", category: "funny", dialogue: "", explanation: "", keywords: "", videoRef: "", gifRef: "" });
      load();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed to add meme");
      setMsgType("error");
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Delete this meme permanently?")) return;
    try {
      await api.deleteMeme(id);
      load();
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="admin-layout">
      {/* Add form */}
      <div className="admin-panel">
        <h2>➕ Add New Meme</h2>

        {msg && (
          <div className={msgType === "success" ? "success-msg" : "error-box"} style={{ marginBottom: 12 }}>
            {msg}
          </div>
        )}

        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Meme Name *</label>
            <input className="form-input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Aukat Me Reh" required />
          </div>
          <div className="form-group">
            <label className="form-label">Category *</label>
            <select className="form-input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {(categories.length ? categories : ["funny", "coding", "startup", "college", "office"]).map((c) => (
                <option key={c} value={c}>{c.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Dialogue *</label>
            <input className="form-input" value={form.dialogue} onChange={(e) => setForm({ ...form, dialogue: e.target.value })} placeholder="The meme's catchphrase" required />
          </div>
          <div className="form-group">
            <label className="form-label">Explanation *</label>
            <textarea className="form-input" value={form.explanation} onChange={(e) => setForm({ ...form, explanation: e.target.value })} placeholder="Why does this meme match the situation?" required />
          </div>
          <div className="form-group">
            <label className="form-label">Keywords (comma-separated) *</label>
            <input className="form-input" value={form.keywords} onChange={(e) => setForm({ ...form, keywords: e.target.value })} placeholder="deadline, pressure, client" required />
          </div>
          <div className="form-group">
            <label className="form-label">Video Reference (optional)</label>
            <input className="form-input" value={form.videoRef} onChange={(e) => setForm({ ...form, videoRef: e.target.value })} placeholder="https://..." />
          </div>
          <div className="form-group">
            <label className="form-label">GIF Reference (optional)</label>
            <input className="form-input" value={form.gifRef} onChange={(e) => setForm({ ...form, gifRef: e.target.value })} placeholder="https://..." />
          </div>
          <button type="submit" className="btn-primary">Add Meme to Database</button>
        </form>
      </div>

      {/* List */}
      <div className="admin-panel">
        <h2>📋 All Memes ({memes.length})</h2>
        <div className="admin-list">
          {memes.length === 0 && (
            <div className="empty-state" style={{ padding: 24 }}>
              <div className="empty-icon">🫙</div>
              <p>No memes yet. Add some!</p>
            </div>
          )}
          {memes.map((m) => (
            <div key={m.id} className="admin-item">
              <div className="admin-item-info">
                <div className="admin-item-name">{m.name}</div>
                <div className="admin-item-sub">
                  {m.category} · {m.usageCount} uses · {m.dialogue.slice(0, 40)}…
                </div>
              </div>
              <button className="btn-danger" onClick={() => remove(m.id)}>Delete</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Root App ───────────────────────────────────────────────── */
export default function App() {
  const [tab, setTab] = useState<Tab>("chat");
  const [memeCount, setMemeCount] = useState<number | null>(null);

  useEffect(() => {
    api.health().then((h) => setMemeCount(h.memeCount)).catch(() => {});
  }, []);

  const TABS: { id: Tab; icon: string; label: string }[] = [
    { id: "chat",     icon: "🎭", label: "Analyze" },
    { id: "search",   icon: "🔍", label: "Search"  },
    { id: "trending", icon: "🔥", label: "Trending" },
    { id: "admin",    icon: "⚙️",  label: "Admin"   },
  ];

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo">🎭</div>
          <div className="header-title">
            <h1>MemeGPT</h1>
            <p>Local AI-powered meme finder · FastAPI + React</p>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-pill">
            <span className="dot" />
            {memeCount !== null ? `${memeCount} memes loaded` : "Connecting…"}
          </div>
          <div className="stat-pill">⚡ Local · 100% Free</div>
        </div>
      </header>

      {/* Tab bar */}
      <nav className="tab-bar" role="tablist" aria-label="App navigation">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab-btn ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
            role="tab"
            aria-selected={tab === t.id}
            id={`tab-${t.id}`}
          >
            <span className="tab-icon">{t.icon}</span>
            {t.label}
          </button>
        ))}
      </nav>

      {/* Panels */}
      <main role="tabpanel" aria-labelledby={`tab-${tab}`}>
        {tab === "chat"     && <ChatTab />}
        {tab === "search"   && <SearchTab />}
        {tab === "trending" && <TrendingTab />}
        {tab === "admin"    && <AdminTab />}
      </main>
    </div>
  );
}
