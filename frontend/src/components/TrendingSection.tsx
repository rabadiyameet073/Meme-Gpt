import { useState, useEffect } from "react";
import { api, MemeRecord } from "../api";
import { MemeCard } from "./MemeCard";

export interface TrendingSectionProps {
  onToast?: (msg: string) => void;
  onToggleFav?: (id: string) => void;
  favoriteIds?: Set<string>;
}

const CATEGORIES = [
  { id: "all", label: "All" },
  { id: "office", label: "Work & Office" },
  { id: "coding", label: "Programming" },
  { id: "startup", label: "Startup & AI" },
  { id: "gaming", label: "Gaming" },
  { id: "bollywood", label: "Bollywood" },
  { id: "college", label: "College & Exams" },
];

export function TrendingSection({
  onToast,
  onToggleFav,
  favoriteIds = new Set(),
}: TrendingSectionProps) {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [memes, setMemes] = useState<MemeRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .getTrending(selectedCategory === "all" ? "" : selectedCategory, 18)
      .then((res: any) => {
        if (!active) return;
        const list = Array.isArray(res) ? res : res?.items || res?.trending || [];
        setMemes(list);
      })
      .catch(() => {
        if (active) setMemes([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedCategory]);

  return (
    <div className="trending-section" style={{ marginTop: "24px" }}>
      <div
        className="category-chips-row"
        style={{
          display: "flex",
          gap: "8px",
          overflowX: "auto",
          paddingBottom: "10px",
          marginBottom: "18px",
        }}
      >
        {CATEGORIES.map((cat) => {
          const active = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              style={{
                padding: "6px 14px",
                fontSize: "0.82rem",
                fontWeight: 600,
                borderRadius: "20px",
                border: active
                  ? "1px solid var(--brand-purple, #7C3AED)"
                  : "1px solid rgba(255,255,255,0.08)",
                background: active
                  ? "var(--brand-purple, #7C3AED)"
                  : "rgba(255,255,255,0.04)",
                color: active ? "#ffffff" : "var(--text-secondary, #a1a1aa)",
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.15s ease",
              }}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: "16px",
          }}
        >
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div
              key={n}
              style={{
                height: "240px",
                borderRadius: "12px",
                background: "rgba(255,255,255,0.03)",
                animation: "pulse 1.5s infinite",
              }}
            />
          ))}
        </div>
      ) : memes.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "40px 20px",
            color: "var(--text-muted, #71717a)",
          }}
        >
          No trending memes in this category yet.
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
            gap: "18px",
          }}
        >
          {memes.map((meme) => (
            <MemeCard
              key={meme.id}
              meme={meme}
              isFav={favoriteIds.has(meme.id)}
              onToggleFav={onToggleFav}
              onToast={onToast}
            />
          ))}
        </div>
      )}
    </div>
  );
}
