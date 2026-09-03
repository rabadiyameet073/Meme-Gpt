import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { api, type MemeRecord } from "../api";
import { MemeCard } from "./MemeCard";
import { Icon, type IconName } from "./Icon";

export interface SearchTabProps {
  onToast: (m: string) => void;
  initialCategory?: string;
}

const POPULAR_CATEGORIES: { id: string; label: string; icon: IconName }[] = [
  { id: "", label: "All Categories", icon: "grid" },
  { id: "work", label: "Work & Office", icon: "office" },
  { id: "tech", label: "Tech & Coding", icon: "coding" },
  { id: "gaming", label: "Gaming", icon: "gaming" },
  { id: "relationships", label: "Relationships", icon: "relationship" },
  { id: "wholesome", label: "Wholesome", icon: "wholesome" },
  { id: "tv", label: "TV & Cinema", icon: "tv" },
  { id: "sports", label: "Sports", icon: "sports" },
];

export function SearchTab({ onToast, initialCategory = "" }: SearchTabProps) {
  const [q, setQ] = useState("");
  const [category, setCategory] = useState(initialCategory);
  const [page, setPage] = useState(1);
  const [results, setResults] = useState<MemeRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  useEffect(() => {
    if (initialCategory) {
      setCategory(initialCategory);
    }
  }, [initialCategory]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const res = await api.searchMemes(q, category, page, 24);
      setResults(res.items || []);
      setTotal(res.total || 0);
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
    }, 250);
    return () => clearTimeout(t);
  }, [q, category, page]);

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
      {/* Search Header */}
      <div style={{ marginBottom: "20px" }}>
        <h2 style={{ fontSize: "1.4rem", fontWeight: 700, marginBottom: "4px" }}>
          Browse & Discover Memes
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem" }}>
          Explore indexed templates across categories, dialogues, and emotion tags
        </p>
      </div>

      {/* Search Bar & View Controls */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          alignItems: "center",
          marginBottom: "16px",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            flex: 1,
            minWidth: "280px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)",
            padding: "8px 14px",
          }}
        >
          <Icon name="search" size={16} color="var(--text-muted)" />
          <input
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setPage(1);
            }}
            placeholder="Search by keyword, catchphrase, dialogue, or emotion..."
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              color: "var(--text-primary)",
              fontFamily: "var(--font-body)",
              fontSize: "0.92rem",
            }}
          />
          {q && (
            <button
              type="button"
              onClick={() => {
                setQ("");
                setPage(1);
              }}
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                padding: "2px",
              }}
            >
              <Icon name="x" size={14} />
            </button>
          )}
        </div>

        {/* View Mode Toggle */}
        <div
          style={{
            display: "inline-flex",
            backgroundColor: "var(--bg-panel)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)",
            padding: "3px",
          }}
        >
          <button
            type="button"
            onClick={() => setViewMode("grid")}
            style={{
              padding: "6px 12px",
              borderRadius: "var(--radius-xs)",
              border: "none",
              backgroundColor: viewMode === "grid" ? "var(--brand-primary)" : "transparent",
              color: viewMode === "grid" ? "#ffffff" : "var(--text-secondary)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              fontSize: "0.8rem",
              fontWeight: 600,
            }}
          >
            <Icon name="grid" size={14} /> Grid
          </button>
          <button
            type="button"
            onClick={() => setViewMode("list")}
            style={{
              padding: "6px 12px",
              borderRadius: "var(--radius-xs)",
              border: "none",
              backgroundColor: viewMode === "list" ? "var(--brand-primary)" : "transparent",
              color: viewMode === "list" ? "#ffffff" : "var(--text-secondary)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              fontSize: "0.8rem",
              fontWeight: 600,
            }}
          >
            <Icon name="list" size={14} /> Compact
          </button>
        </div>
      </div>

      {/* Category Chips Bar */}
      <div className="chips-carousel" style={{ marginBottom: "20px" }}>
        {POPULAR_CATEGORIES.map((cat) => {
          const active = category === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              className={`chip-btn ${active ? "active" : ""}`}
              onClick={() => {
                setCategory(cat.id);
                setPage(1);
              }}
            >
              <Icon
                name={cat.icon}
                size={14}
                color={active ? "var(--brand-primary)" : "var(--text-muted)"}
              />
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>

      {/* Results Header Count */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "0.82rem",
          color: "var(--text-muted)",
          marginBottom: "14px",
          fontWeight: 600,
        }}
      >
        <span>
          {loading ? "Searching memes..." : `${total} memes found`}
        </span>
        {category && (
          <button
            type="button"
            onClick={() => setCategory("")}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--brand-primary)",
              cursor: "pointer",
              fontSize: "0.8rem",
              fontWeight: 600,
            }}
          >
            Clear category filter
          </button>
        )}
      </div>

      {/* Loading Skeletons */}
      {loading ? (
        <div className="card-grid">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div
              key={n}
              style={{
                height: "300px",
                borderRadius: "var(--radius-md)",
                backgroundColor: "var(--bg-card)",
                border: "1px solid var(--border-subtle)",
              }}
            />
          ))}
        </div>
      ) : results.length === 0 ? (
        /* Empty State */
        <div
          style={{
            textAlign: "center",
            padding: "60px 20px",
            backgroundColor: "var(--bg-card)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border)",
          }}
        >
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "var(--brand-primary-subtle)",
              color: "var(--brand-primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 16px",
            }}
          >
            <Icon name="search" size={24} />
          </div>
          <h3 style={{ fontSize: "1.15rem", marginBottom: "6px" }}>No memes found</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", maxWidth: "380px", margin: "0 auto 16px" }}>
            We couldn't find any memes matching your criteria. Try different search terms or clear your active filters.
          </p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setQ("");
              setCategory("");
            }}
          >
            Reset Filters
          </button>
        </div>
      ) : (
        /* Meme Results Grid */
        <motion.div
          className={viewMode === "grid" ? "card-grid" : "card-list"}
          style={
            viewMode === "list"
              ? { display: "flex", flexDirection: "column", gap: "12px" }
              : undefined
          }
        >
          {results.map((m) => (
            <MemeCard key={m.id} meme={m} onToast={onToast} />
          ))}
        </motion.div>
      )}

      {/* Pagination Controls */}
      {total > 24 && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "12px",
            marginTop: "36px",
            paddingTop: "20px",
            borderTop: "1px solid var(--border)",
          }}
        >
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
            disabled={page === 1}
            style={{ opacity: page === 1 ? 0.4 : 1, cursor: page === 1 ? "not-allowed" : "pointer" }}
          >
            Previous
          </button>
          <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)", fontWeight: 600 }}>
            Page {page} of {Math.ceil(total / 24)}
          </span>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 24 >= total}
            style={{
              opacity: page * 24 >= total ? 0.4 : 1,
              cursor: page * 24 >= total ? "not-allowed" : "pointer",
            }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
