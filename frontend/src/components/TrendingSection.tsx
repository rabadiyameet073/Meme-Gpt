import { useState, useEffect } from "react";
import { api, MemeRecord } from "../api";
import { MemeCard } from "./MemeCard";
import { Icon, type IconName } from "./Icon";

export interface TrendingSectionProps {
  onToast?: (msg: string) => void;
  onToggleFav?: (id: string) => void;
  favoriteIds?: Set<string>;
}

const CATEGORIES: { id: string; label: string; icon: IconName }[] = [
  { id: "all", label: "All Trends", icon: "trending" },
  { id: "work", label: "Work & Office", icon: "office" },
  { id: "coding", label: "Programming", icon: "coding" },
  { id: "startup", label: "Startup & AI", icon: "startup" },
  { id: "gaming", label: "Gaming", icon: "gaming" },
  { id: "bollywood", label: "Bollywood", icon: "bollywood" },
  { id: "college", label: "College & Exams", icon: "college" },
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
      .getTrending(selectedCategory === "all" ? "all" : selectedCategory, 18)
      .then((res: any) => {
        if (!active) return;
        const list = Array.isArray(res)
          ? res
          : res?.data?.results || res?.results || res?.items || res?.trending || [];
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
    <div style={{ marginTop: "24px" }}>
      {/* Category Chips Bar */}
      <div className="chips-carousel" style={{ marginBottom: "20px" }}>
        {CATEGORIES.map((cat) => {
          const active = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              onClick={() => setSelectedCategory(cat.id)}
              className={`chip-btn ${active ? "active" : ""}`}
            >
              <Icon name={cat.icon} size={14} color={active ? "#ffffff" : "var(--brand-cyan)"} />
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="card-grid">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div
              key={n}
              style={{
                height: "280px",
                borderRadius: "var(--radius-lg)",
                background: "var(--bg-card)",
                animation: "pulse 1.5s infinite",
              }}
            />
          ))}
        </div>
      ) : memes.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "48px 20px",
            background: "var(--bg-card)",
            borderRadius: "var(--radius-lg)",
            border: "1px solid var(--border)",
            color: "var(--text-muted)",
          }}
        >
          No trending memes found in this category.
        </div>
      ) : (
        <div className="card-grid">
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
