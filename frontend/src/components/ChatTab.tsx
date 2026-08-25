import { useState, useRef } from "react";
import { api, download, type MemeSearchResult } from "../api";
import { MemeCard } from "./MemeCard";
import { Icon } from "./Icon";
import { SkeletonGrid } from "./SkeletonCard";

const EXAMPLES = [
  "I worked 3 months on a project and accuracy is only 12%. Can you make it 100%?",
  "Client wants the full project delivered tomorrow morning.",
  "Production is down at 3 AM and git blame says it's my code.",
  "Manager says just fix this one tiny bug. PR has 800 file changes.",
  "First day at startup: we're agile, no deadlines. Day 2: feature needed by EOD.",
  "Studying for exam the night before: how hard can JEE/GATE be?",
  "HR sent a message saying 'Can we talk for 5 minutes?'",
  "Salary credited on 1st, account balance ₹142 by 5th.",
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
      onToast(`Matched in ${res.latencyMs}ms`);
      onSearchCompleted?.(q);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Is FastAPI running on port 8000?");
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

  const charCount = query.length;

  return (
    <div>
      {/* Input box */}
      <div className="input-wrapper">
        <textarea
          ref={taRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe your situation, problem, or vibe... (e.g. 'Production crashed at 3 AM and it's my code')"
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), submit())}
          maxLength={2000}
          rows={4}
        />
        <div className="input-actions">
          <span className="char-count">{charCount}/2000 · Enter to analyze, Shift+Enter for new line</span>
          <button className="btn-send" onClick={() => submit()} disabled={loading || !query.trim()}>
            {loading ? (
              <>
                <div
                  style={{
                    width: 14,
                    height: 14,
                    border: "2px solid #000",
                    borderTopColor: "transparent",
                    borderRadius: "50%",
                    animation: "spin 0.7s linear infinite",
                  }}
                />
                Analyzing...
              </>
            ) : (
              <>
                <Icon name="sparkles" size={15} /> Find Meme
              </>
            )}
          </button>
        </div>
      </div>

      {/* Example chips */}
      <div className="examples-section">
        <div className="examples-label">Try an example situation</div>
        <div className="examples-chips">
          {EXAMPLES.map((ex) => (
            <button key={ex} className="chip" onClick={() => submit(ex)} disabled={loading} title={ex}>
              {ex.length > 52 ? ex.slice(0, 50) + "…" : ex}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="error-box">
          <Icon name="alert" size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ marginTop: "24px" }}>
          <div className="loading-wrap" style={{ marginBottom: "16px" }}>
            <div className="spinner" />
            <div className="loading-text">Analyzing situation with Semantic Vector Engine…</div>
          </div>
          <SkeletonGrid count={3} />
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="results-section">
          {/* Query echo */}
          <div className="section-label">Your situation</div>
          <div className="query-echo">{lastQuery}</div>

          {/* Detected categories & tags */}
          {result.detectedCategories?.length > 0 && (
            <>
              <div className="section-label" style={{ marginTop: 16 }}>
                Detected Context
              </div>
              <div className="tag-list">
                {result.detectedCategories.map((c) => (
                  <span key={c} className="tag">
                    <Icon name="tag" size={12} /> {c.replace(/_/g, " ")}
                  </span>
                ))}
                {result.detectedTags?.map((t) => (
                  <span key={t} className="tag">
                    <Icon name="tag" size={12} /> {t}
                  </span>
                ))}
                <span className="latency">
                  <Icon name="clock" size={12} /> {result.latencyMs}ms
                </span>
              </div>
            </>
          )}

          {/* Primary match */}
          <div className="section-label" style={{ marginTop: 20 }}>
            <Icon name="trophy" size={14} /> Best Match
          </div>
          <MemeCard meme={result.primary} primary showConfidence onToast={onToast} />

          {/* Top 5 Matches (excl. primary) */}
          {result.topFive?.length > 1 && (
            <>
              <div className="section-label">Top Matches</div>
              {result.topFive.slice(1).map((m) => (
                <MemeCard key={m.id} meme={m} showConfidence onToast={onToast} />
              ))}
            </>
          )}

          {/* Alternatives */}
          {result.alternatives?.length > 0 && (
            <>
              <div className="section-label">Alternative Suggestions</div>
              {result.alternatives.map((m) => (
                <MemeCard key={m.id} meme={m} showConfidence onToast={onToast} />
              ))}
            </>
          )}

          {/* Viral suggestions */}
          {result.viralSuggestions?.length > 0 && (
            <>
              <div className="section-label">
                <Icon name="trending" size={14} /> Trending & Viral Memes
              </div>
              {result.viralSuggestions.map((m) => (
                <MemeCard key={m.id} meme={m} onToast={onToast} />
              ))}
            </>
          )}

          {/* Export bar */}
          <div className="section-label" style={{ marginTop: 20 }}>
            Export Result
          </div>
          <div className="export-row">
            <button className="btn-export" onClick={() => doExport("txt")}>
              <Icon name="file-text" size={14} /> Plain Text
            </button>
            <button className="btn-export" onClick={() => doExport("json")}>
              <Icon name="code" size={14} /> JSON Format
            </button>
            <button className="btn-export" onClick={() => doExport("markdown")}>
              <Icon name="file-text" size={14} /> Markdown
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
