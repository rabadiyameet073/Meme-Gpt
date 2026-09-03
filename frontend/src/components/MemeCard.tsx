import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import confetti from "canvas-confetti";
import { api, getSessionId, MemeMatch } from "../api";
import { Icon } from "./Icon";
import {
  copyMemeToClipboard as execCopyMeme,
  downloadMeme as execDownloadMeme,
  shareMeme as execShareMeme,
} from "../lib/clipboard";

const SESSION_ID = getSessionId();

export interface MemeCardProps {
  meme: MemeMatch;
  primary?: boolean;
  showConfidence?: boolean;
  isFav?: boolean;
  queryId?: string;
  onToggleFav?: (id: string) => void;
  onToast?: (msg: string) => void;
}

export function MemeCard({
  meme,
  primary,
  showConfidence,
  isFav,
  queryId,
  onToggleFav,
  onToast,
}: MemeCardProps) {
  const [vote, setVote] = useState<1 | -1 | null>(null);
  const [fav, setFav] = useState<boolean>(!!isFav);
  const [selectedFormat, setSelectedFormat] = useState<"gif" | "image" | "video" | "webp">("image");
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    setFav(!!isFav);
  }, [isFav]);

  const doVote = async (v: 1 | -1) => {
    if (vote === v) return;
    setVote(v);
    if (v === 1) {
      confetti({
        particleCount: 22,
        spread: 45,
        origin: { y: 0.85 },
        colors: ["#8D321F", "#C29B72", "#F1ECE6", "#035352"],
      });
    }
    try {
      await api.vote(meme.id, v, SESSION_ID);
      await api.sendFeedback(meme.id, v === 1 ? "upvote" : "downvote");
      onToast?.(v === 1 ? "Spot on! Upvoted match." : "Feedback recorded.");
    } catch {
      /* non-critical */
    }
  };

  const toggleFav = async () => {
    const next = !fav;
    setFav(next);
    if (next) {
      confetti({
        particleCount: 20,
        spread: 40,
        origin: { y: 0.85 },
        colors: ["#8D321F", "#C29B72", "#7D4047", "#F1ECE6"],
      });
    }
    try {
      await api.toggleFavorite(meme.id, SESSION_ID);
      onToggleFav?.(meme.id);
      onToast?.(next ? "Saved to your favorites!" : "Removed from favorites");
    } catch {
      setFav(!next);
    }
  };

  const handleFormatChange = (fmt: "gif" | "image" | "video" | "webp") => {
    setSelectedFormat(fmt);
    setImgError(false);
    api.sendFeedback(meme.id, "format_change", fmt);
  };

  const handleShare = async () => {
    await execShareMeme(
      meme,
      queryId,
      onToast,
      (_qid, mid, action) => {
        api.sendFeedback(mid, action);
      }
    );
  };

  const copyMeme = async () => {
    const copyResult = await execCopyMeme(meme);
    confetti({
      particleCount: 18,
      spread: 40,
      origin: { y: 0.8 },
      colors: ["#FF5500", "#10B981"],
    });
    if (copyResult === "image") {
      await api.sendFeedback(meme.id, "copy", "image");
      onToast?.("Meme image copied to clipboard!");
    } else if (copyResult === "url") {
      await api.sendFeedback(meme.id, "copy", "url");
      onToast?.("Meme URL copied!");
    } else {
      onToast?.("Dialogue copied to clipboard!");
    }
  };

  const downloadMeme = (format: "gif" | "image" | "video" | "webp") => {
    execDownloadMeme(meme, format);
    api.sendFeedback(meme.id, "download", format);
    onToast?.(`Downloading ${format.toUpperCase()}...`);
  };

  const pct = meme.confidence !== undefined ? Math.round(meme.confidence * 100) : null;
  const categoryStr = typeof meme.category === "string" ? meme.category.replace(/_/g, " ") : "general";

  const mediaUrl =
    (meme as any).formats?.[selectedFormat] ||
    (meme as any).formats?.image ||
    (meme as any).formats?.gif ||
    (meme as any).preview_url ||
    meme.imageRef ||
    meme.gifRef;

  return (
    <motion.div
      className={`meme-card ${primary ? "primary-match" : ""}`}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* Top Header */}
      <div>
        <div className="card-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="badge badge-category">
              <Icon name="tag" size={11} /> {categoryStr}
            </span>
            {primary && (
              <span className="badge badge-gold">
                <Icon name="sparkles" size={11} /> TOP MATCH
              </span>
            )}
            {meme.viralScore !== undefined && meme.viralScore > 0 && (
              <span
                className="badge"
                style={{
                  backgroundColor: "rgba(0, 180, 216, 0.12)",
                  color: "var(--accent-cyan)",
                  border: "1px solid var(--accent-cyan)",
                }}
              >
                <Icon name="trending" size={11} /> VIRAL
              </span>
            )}
          </div>

          {showConfidence && pct !== null && (
            <span
              style={{
                fontSize: "0.78rem",
                fontWeight: 700,
                fontFamily: "var(--font-mono)",
                color: pct >= 80 ? "var(--accent-emerald)" : pct >= 60 ? "var(--accent-cyan)" : "var(--text-secondary)",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              <Icon name="check" size={12} /> {pct}% Match
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="card-title">{meme.name}</h3>

        {/* Dialogue Quote */}
        {meme.dialogue && (
          <div
            className="card-dialogue"
            title="Click to copy dialogue"
            onClick={copyMeme}
            style={{ cursor: "pointer" }}
          >
            "{meme.dialogue}"
          </div>
        )}

        {/* Explanation */}
        {meme.explanation && (
          <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "12px", lineHeight: 1.45 }}>
            {meme.explanation}
          </p>
        )}

        {/* Media Preview */}
        {mediaUrl && !imgError && (
          <div className="card-media-box">
            <img
              src={mediaUrl}
              alt={meme.name}
              loading="lazy"
              decoding="async"
              onError={() => setImgError(true)}
            />
          </div>
        )}

        {/* Format Selector Pills */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "4px",
            margin: "10px 0 14px",
          }}
        >
          <span
            style={{
              fontSize: "0.7rem",
              fontWeight: 700,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              marginRight: "4px",
            }}
          >
            Format:
          </span>
          {(["image", "gif", "video", "webp"] as const).map((fmt) => (
            <button
              key={fmt}
              type="button"
              onClick={() => handleFormatChange(fmt)}
              style={{
                padding: "3px 8px",
                fontSize: "0.72rem",
                fontWeight: 600,
                borderRadius: "var(--radius-xs)",
                border: selectedFormat === fmt ? "1px solid var(--brand-primary)" : "1px solid var(--border)",
                backgroundColor: selectedFormat === fmt ? "var(--brand-primary-subtle)" : "transparent",
                color: selectedFormat === fmt ? "var(--brand-primary)" : "var(--text-secondary)",
                cursor: "pointer",
                transition: "all var(--transition-fast)",
              }}
            >
              {fmt.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Footer Action Row */}
      <div style={{ paddingTop: "12px", borderTop: "1px solid var(--border-subtle)", marginTop: "8px" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "8px",
          }}
        >
          {/* Vote Buttons */}
          <div style={{ display: "flex", gap: "6px" }}>
            <button
              type="button"
              className={`btn btn-secondary ${vote === 1 ? "active" : ""}`}
              onClick={() => doVote(1)}
              style={{
                padding: "6px 10px",
                fontSize: "0.78rem",
                color: vote === 1 ? "var(--accent-emerald)" : undefined,
                borderColor: vote === 1 ? "var(--accent-emerald)" : undefined,
              }}
              title="Spot on match"
            >
              <Icon name="thumb-up" size={13} /> Spot on
            </button>
            <button
              type="button"
              className={`btn btn-secondary ${vote === -1 ? "active" : ""}`}
              onClick={() => doVote(-1)}
              style={{
                padding: "6px 10px",
                fontSize: "0.78rem",
                color: vote === -1 ? "var(--accent-rose)" : undefined,
                borderColor: vote === -1 ? "var(--accent-rose)" : undefined,
              }}
              title="Not quite right"
            >
              <Icon name="thumb-down" size={13} />
            </button>
          </div>

          {/* Action Buttons */}
          <div style={{ display: "flex", gap: "6px", marginLeft: "auto" }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={toggleFav}
              title={fav ? "Remove from Favorites" : "Save to Favorites"}
              style={{
                padding: "6px 10px",
                fontSize: "0.8rem",
                color: fav ? "var(--accent-rose)" : undefined,
                borderColor: fav ? "var(--accent-rose)" : undefined,
              }}
            >
              <Icon name={fav ? "heart-filled" : "heart"} size={13} color={fav ? "var(--accent-rose)" : undefined} />
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleShare}
              title="Share meme link"
              style={{ padding: "6px 10px", fontSize: "0.8rem" }}
            >
              <Icon name="share" size={13} />
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={copyMeme}
              title="Copy meme"
              style={{ padding: "6px 12px", fontSize: "0.8rem", fontWeight: 600 }}
            >
              <Icon name="copy" size={13} /> Copy
            </button>

            <button
              type="button"
              className="btn btn-primary"
              onClick={() => downloadMeme(selectedFormat)}
              title="Download meme file"
              style={{ padding: "6px 12px", fontSize: "0.8rem" }}
            >
              <Icon name="download" size={13} color="#ffffff" />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
