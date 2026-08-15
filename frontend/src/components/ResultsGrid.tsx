import { MemeCard } from "./MemeCard";
import type { MemeMatch, MemeSearchResult } from "@/types";

export interface ResultsGridProps {
  results: MemeSearchResult;
  onToast?: (msg: string) => void;
  onToggleFav?: (id: string) => void;
  favoriteIds?: Set<string>;
}

export function ResultsGrid({
  results,
  onToast,
  onToggleFav,
  favoriteIds = new Set(),
}: ResultsGridProps) {
  const primary = results.primary;
  const topFive = results.topFive || [];
  const alternatives = results.alternatives || [];

  return (
    <div className="results-container" style={{ marginTop: "24px" }}>
      {/* ── Primary Best Match ───────────────────────────────────────── */}
      {primary && (
        <div className="primary-match-section" style={{ marginBottom: "28px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "12px",
            }}
          >
            <span
              style={{
                fontSize: "0.82rem",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "var(--brand-amber, #F59E0B)",
                background: "rgba(245, 158, 11, 0.12)",
                padding: "3px 8px",
                borderRadius: "5px",
                border: "1px solid rgba(245, 158, 11, 0.3)",
              }}
            >
              ⭐ Top Recommended Match
            </span>
            {results.latencyMs && (
              <span
                style={{
                  fontSize: "0.75rem",
                  color: "var(--text-muted, #71717a)",
                }}
              >
                Matched in {Math.round(results.latencyMs)}ms
              </span>
            )}
          </div>

          <MemeCard
            meme={primary}
            primary={true}
            showConfidence={true}
            isFav={favoriteIds.has(primary.id)}
            onToggleFav={onToggleFav}
            onToast={onToast}
          />
        </div>
      )}

      {/* ── Top Recommendations Grid ─────────────────────────────────── */}
      {topFive.length > 0 && (
        <div className="top-five-section" style={{ marginBottom: "28px" }}>
          <h3
            style={{
              fontSize: "1.1rem",
              fontWeight: 700,
              color: "var(--text-primary, #F5F5F5)",
              marginBottom: "14px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            🔥 Top Matches
          </h3>
          <div
            className="meme-grid"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
              gap: "18px",
            }}
          >
            {topFive.map((meme) => (
              <MemeCard
                key={meme.id}
                meme={meme}
                showConfidence={true}
                isFav={favoriteIds.has(meme.id)}
                onToggleFav={onToggleFav}
                onToast={onToast}
              />
            ))}
          </div>
        </div>
      )}

      {/* ── Alternatives ────────────────────────────────────────────── */}
      {alternatives.length > 0 && (
        <div className="alternatives-section">
          <h3
            style={{
              fontSize: "1rem",
              fontWeight: 600,
              color: "var(--text-secondary, #a1a1aa)",
              marginBottom: "12px",
            }}
          >
            💡 Related Alternatives
          </h3>
          <div
            className="alternatives-grid"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
              gap: "14px",
            }}
          >
            {alternatives.map((meme) => (
              <MemeCard
                key={meme.id}
                meme={meme}
                showConfidence={false}
                isFav={favoriteIds.has(meme.id)}
                onToggleFav={onToggleFav}
                onToast={onToast}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
