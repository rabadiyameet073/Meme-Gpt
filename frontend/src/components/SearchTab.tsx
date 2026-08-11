import { useState, useEffect } from "react";
import { api, type MemeRecord } from "../api";
import { MemeCard } from "./MemeCard";
import { Icon } from "./Icon";

export function SearchTab({ onToast }: { onToast: (m: string) => void }) {
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);
  const [results, setResults] = useState<MemeRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.categories().then(setCategories).catch(() => {});
  }, []);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const res = await api.searchMemes(q, category, page, 20);
      setResults(res.items);
      setTotal(res.total);
    } catch {
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const t = setTimeout(() => {
      fetchResults();
    }, 280);
    return () => clearTimeout(t);
  }, [q, category, page]);

  return (
    <div className="search-wrap">
      <div className="search-input-wrap">
        <span className="search-icon">
          <Icon name="search" size={16} />
        </span>
        <input
          className="search-input"
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setPage(1);
          }}
          placeholder="Search memes by name, catchphrase, or keyword..."
        />
      </div>

      <div className="filter-row">
        <select
          className="select-input"
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Categories ({categories.length})</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      <div className="results-count">{loading ? "Searching..." : `${total} memes found`}</div>

      {results.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-icon">
            <Icon name="search" size={36} />
          </div>
          <p>No memes matched your search. Try different keywords or clear filters.</p>
        </div>
      )}

      {results.map((m) => (
        <MemeCard key={m.id} meme={m} onToast={onToast} />
      ))}

      {total > 20 && (
        <div className="pagination-bar">
          <button
            className="pagination-btn"
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
            disabled={page === 1}
          >
            Previous
          </button>
          <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
            Page {page} of {Math.ceil(total / 20)}
          </span>
          <button
            className="pagination-btn"
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 20 >= total}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
