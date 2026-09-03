import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { api, getSessionId, type MemeRecord } from "../api";
import { Icon, type IconName } from "./Icon";
import {
  copyMemeToClipboard as execCopyMeme,
  downloadMeme as execDownloadMeme,
  shareMeme as execShareMeme,
} from "../lib/clipboard";

const SESSION_ID = getSessionId();

const CATEGORIES: { id: string; label: string; icon: IconName }[] = [
  { id: "all", label: "All Trends", icon: "trending" },
  { id: "work", label: "Work & Office", icon: "office" },
  { id: "tech", label: "Tech & Coding", icon: "coding" },
  { id: "gaming", label: "Gaming", icon: "gaming" },
  { id: "relationships", label: "Relationships", icon: "relationship" },
  { id: "college", label: "College & Exams", icon: "college" },
  { id: "wholesome", label: "Wholesome", icon: "wholesome" },
];

const PERIODS = [
  { id: "24h", label: "Today (24h)" },
  { id: "7d", label: "This Week" },
  { id: "30d", label: "All-Time (30d)" },
];

export function TrendingTab({ onToast }: { onToast: (m: string) => void }) {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedPeriod, setSelectedPeriod] = useState("24h");
  const [memes, setMemes] = useState<MemeRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [votedMap, setVotedMap] = useState<Record<string, 1 | -1>>({});
  const [favMap, setFavMap] = useState<Record<string, boolean>>({});
  const [formatMap, setFormatMap] = useState<Record<string, "gif" | "image" | "video" | "webp">>({});

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    api
      .getTrending({
        category: selectedCategory === "all" ? "all" : selectedCategory,
        period: selectedPeriod,
        limit: 30,
      })
      .then((res: any) => {
        if (!isMounted) return;
        const list = Array.isArray(res)
          ? res
          : res?.data?.results || res?.results || res?.items || res?.trending || [];
        setMemes(list);
      })
      .catch(() => {
        if (isMounted) setMemes([]);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedCategory, selectedPeriod]);

  const handleVote = async (memeId: string, voteVal: 1 | -1) => {
    if (votedMap[memeId] === voteVal) return;
    setVotedMap((prev) => ({ ...prev, [memeId]: voteVal }));

    setMemes((prev) =>
      prev.map((m) => {
        if (m.id === memeId) {
          const upDiff = voteVal === 1 ? 1 : 0;
          const downDiff = voteVal === -1 ? 1 : 0;
          return {
            ...m,
            upvotes: (m.upvotes || 0) + upDiff,
            downvotes: (m.downvotes || 0) + downDiff,
          };
        }
        return m;
      })
    );

    try {
      await api.vote(memeId, voteVal, SESSION_ID);
      await api.sendFeedback(memeId, voteVal === 1 ? "upvote" : "downvote");
      onToast(voteVal === 1 ? "Upvoted trend" : "Downvoted trend");
    } catch {
      /* non-critical */
    }
  };

  const handleToggleFav = async (memeId: string) => {
    const next = !favMap[memeId];
    setFavMap((prev) => ({ ...prev, [memeId]: next }));
    try {
      await api.toggleFavorite(memeId, SESSION_ID);
      onToast(next ? "Saved to favorites" : "Removed from favorites");
    } catch {
      setFavMap((prev) => ({ ...prev, [memeId]: !next }));
    }
  };

  const handleFormatChange = (memeId: string, fmt: "gif" | "image" | "video" | "webp") => {
    setFormatMap((prev) => ({ ...prev, [memeId]: fmt }));
    api.sendFeedback(memeId, "format_change", fmt);
  };

  const handleCopy = async (meme: MemeRecord) => {
    const copyResult = await execCopyMeme(meme);
    if (copyResult === "image") {
      await api.sendFeedback(meme.id, "copy", "image");
      onToast("Meme image copied to clipboard!");
    } else if (copyResult === "url") {
      await api.sendFeedback(meme.id, "copy", "url");
      onToast("Meme URL copied!");
    } else {
      onToast("Dialogue copied to clipboard!");
    }
  };

  const handleDownload = (meme: MemeRecord, fmt: "gif" | "image" | "video" | "webp") => {
    execDownloadMeme(meme, fmt);
    api.sendFeedback(meme.id, "download", fmt);
    onToast(`Downloading ${fmt.toUpperCase()}...`);
  };

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
            <Icon name="trending" size={22} color="var(--brand-primary)" />
            Trending & Viral Memes
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "4px" }}>
            Real-time viral score velocity, community upvotes, and share telemetry
          </p>
        </div>

        {/* Time Period Filter Pills */}
        <div
          style={{
            display: "inline-flex",
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)",
            padding: "3px",
          }}
        >
          {PERIODS.map((period) => {
            const active = selectedPeriod === period.id;
            return (
              <button
                key={period.id}
                type="button"
                onClick={() => setSelectedPeriod(period.id)}
                style={{
                  padding: "6px 12px",
                  borderRadius: "var(--radius-xs)",
                  border: "none",
                  backgroundColor: active ? "var(--brand-primary)" : "transparent",
                  color: active ? "#ffffff" : "var(--text-secondary)",
                  cursor: "pointer",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                  transition: "all var(--transition-fast)",
                }}
              >
                {period.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Category Chips Bar */}
      <div className="chips-carousel" style={{ marginBottom: "24px" }}>
        {CATEGORIES.map((cat) => {
          const active = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              className={`chip-btn ${active ? "active" : ""}`}
              onClick={() => setSelectedCategory(cat.id)}
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

      {/* Content */}
      {loading ? (
        <div className="card-grid">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div
              key={n}
              style={{
                height: "320px",
                borderRadius: "var(--radius-md)",
                backgroundColor: "var(--bg-card)",
                border: "1px solid var(--border-subtle)",
              }}
            />
          ))}
        </div>
      ) : memes.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "60px 20px",
            backgroundColor: "var(--bg-card)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border)",
            color: "var(--text-secondary)",
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
            <Icon name="trending" size={24} />
          </div>
          <h3 style={{ fontSize: "1.15rem", marginBottom: "6px" }}>No trending memes in this category yet</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>
            Try switching to another category or period filter.
          </p>
        </div>
      ) : (
        <div className="card-grid">
          {memes.map((meme, idx) => {
            const currentFmt = formatMap[meme.id] || "image";
            const mediaUrl =
              meme.formats?.[currentFmt] ||
              meme.formats?.image ||
              meme.formats?.gif ||
              meme.preview_url ||
              meme.imageRef ||
              meme.gifRef;

            const isTop3 = idx < 3;
            const rankLabel = idx === 0 ? "#1 Top Viral" : idx === 1 ? "#2 Trending" : idx === 2 ? "#3 Rising" : `#${idx + 1}`;

            return (
              <motion.div
                key={meme.id}
                className={`meme-card ${idx === 0 ? "primary-match" : ""}`}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: Math.min(idx * 0.03, 0.2) }}
              >
                <div>
                  <div className="card-header">
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span
                        className="badge"
                        style={{
                          backgroundColor: isTop3 ? "var(--brand-primary-subtle)" : "var(--bg-panel)",
                          color: isTop3 ? "var(--brand-primary)" : "var(--text-secondary)",
                          border: isTop3 ? "1px solid var(--brand-primary)" : "1px solid var(--border)",
                          fontWeight: 700,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {rankLabel}
                      </span>
                      <span className="badge badge-category">
                        <Icon name="tag" size={11} /> {typeof meme.category === "string" ? meme.category.replace(/_/g, " ") : "general"}
                      </span>
                    </div>

                    {meme.viralScore !== undefined && (
                      <span
                        style={{
                          fontSize: "0.76rem",
                          fontWeight: 700,
                          fontFamily: "var(--font-mono)",
                          color: "var(--accent-emerald)",
                          display: "flex",
                          alignItems: "center",
                          gap: "4px",
                        }}
                      >
                        <Icon name="trending" size={12} /> {Math.round(meme.viralScore)} pts
                      </span>
                    )}
                  </div>

                  <h3 className="card-title">{meme.name}</h3>

                  {meme.dialogue && (
                    <div
                      className="card-dialogue"
                      onClick={() => handleCopy(meme)}
                      title="Click to copy dialogue"
                      style={{ cursor: "pointer" }}
                    >
                      "{meme.dialogue}"
                    </div>
                  )}

                  {meme.explanation && (
                    <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "12px", lineHeight: 1.45 }}>
                      {meme.explanation}
                    </p>
                  )}

                  {mediaUrl && (
                    <div className="card-media-box">
                      <img
                        src={mediaUrl}
                        alt={meme.name}
                        loading="lazy"
                        decoding="async"
                        onError={(e) => { (e.target as HTMLElement).style.display = "none"; }}
                      />
                    </div>
                  )}

                  {/* Format Pills */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                      margin: "10px 0 14px",
                    }}
                  >
                    <span style={{ fontSize: "0.7rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginRight: "4px" }}>
                      Format:
                    </span>
                    {(["image", "gif", "video", "webp"] as const).map((fmt) => (
                      <button
                        key={fmt}
                        type="button"
                        onClick={() => handleFormatChange(meme.id, fmt)}
                        style={{
                          padding: "3px 8px",
                          fontSize: "0.72rem",
                          fontWeight: 600,
                          borderRadius: "var(--radius-xs)",
                          border: currentFmt === fmt ? "1px solid var(--brand-primary)" : "1px solid var(--border)",
                          backgroundColor: currentFmt === fmt ? "var(--brand-primary-subtle)" : "transparent",
                          color: currentFmt === fmt ? "var(--brand-primary)" : "var(--text-secondary)",
                          cursor: "pointer",
                        }}
                      >
                        {fmt.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Footer Action Row */}
                <div style={{ paddingTop: "12px", borderTop: "1px solid var(--border-subtle)", marginTop: "8px" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "8px" }}>
                    <div style={{ display: "flex", gap: "6px" }}>
                      <button
                        type="button"
                        className={`btn btn-secondary ${votedMap[meme.id] === 1 ? "active" : ""}`}
                        onClick={() => handleVote(meme.id, 1)}
                        style={{
                          padding: "6px 10px",
                          fontSize: "0.78rem",
                          color: votedMap[meme.id] === 1 ? "var(--accent-emerald)" : undefined,
                          borderColor: votedMap[meme.id] === 1 ? "var(--accent-emerald)" : undefined,
                        }}
                      >
                        <Icon name="thumb-up" size={13} /> {meme.upvotes || 0}
                      </button>
                      <button
                        type="button"
                        className={`btn btn-secondary ${votedMap[meme.id] === -1 ? "active" : ""}`}
                        onClick={() => handleVote(meme.id, -1)}
                        style={{
                          padding: "6px 10px",
                          fontSize: "0.78rem",
                          color: votedMap[meme.id] === -1 ? "var(--accent-rose)" : undefined,
                          borderColor: votedMap[meme.id] === -1 ? "var(--accent-rose)" : undefined,
                        }}
                      >
                        <Icon name="thumb-down" size={13} />
                      </button>
                    </div>

                    <div style={{ display: "flex", gap: "6px", marginLeft: "auto" }}>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => handleToggleFav(meme.id)}
                        title="Save to Favorites"
                        style={{
                          padding: "6px 10px",
                          fontSize: "0.8rem",
                          color: favMap[meme.id] ? "var(--accent-rose)" : undefined,
                          borderColor: favMap[meme.id] ? "var(--accent-rose)" : undefined,
                        }}
                      >
                        <Icon name={favMap[meme.id] ? "heart-filled" : "heart"} size={13} color={favMap[meme.id] ? "var(--accent-rose)" : undefined} />
                      </button>

                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => execShareMeme(meme, undefined, onToast)}
                        style={{ padding: "6px 10px", fontSize: "0.8rem" }}
                      >
                        <Icon name="share" size={13} />
                      </button>

                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => handleCopy(meme)}
                        style={{ padding: "6px 12px", fontSize: "0.8rem", fontWeight: 600 }}
                      >
                        <Icon name="copy" size={13} /> Copy
                      </button>

                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => handleDownload(meme, currentFmt)}
                        style={{ padding: "6px 12px", fontSize: "0.8rem" }}
                      >
                        <Icon name="download" size={13} color="#ffffff" />
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
