import { useState, useEffect } from "react";
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

  useEffect(() => {
    setFav(!!isFav);
  }, [isFav]);

  const doVote = async (v: 1 | -1) => {
    if (vote === v) return;
    setVote(v);
    try {
      await api.vote(meme.id, v, SESSION_ID);
      await api.sendFeedback(meme.id, v === 1 ? "upvote" : "downvote");
      onToast?.(v === 1 ? "Upvoted match" : "Downvoted match");
    } catch {
      /* non-critical */
    }
  };

  const toggleFav = async () => {
    const next = !fav;
    setFav(next);
    try {
      await api.toggleFavorite(meme.id, SESSION_ID);
      onToggleFav?.(meme.id);
      onToast?.(next ? "Saved to favorites" : "Removed from favorites");
    } catch {
      setFav(!next);
    }
  };

  const handleFormatChange = (fmt: "gif" | "image" | "video" | "webp") => {
    setSelectedFormat(fmt);
    api.sendFeedback(meme.id, "format_change", fmt);
  };

  const handleShare = async () => {
    await execShareMeme(
      meme,
      queryId,
      onToast,
      (qid, mid, action) => {
        api.sendFeedback(mid, action);
      }
    );
  };

  const copyMeme = async () => {
    const copyResult = await execCopyMeme(meme);
    if (copyResult === "image") {
      await api.sendFeedback(meme.id, "copy", "image");
      onToast?.("✓ Copied!");
    } else if (copyResult === "url") {
      await api.sendFeedback(meme.id, "copy", "url");
      onToast?.("✓ Copied!");
    } else {
      onToast?.("Could not copy to clipboard");
    }
  };

  const downloadMeme = (format: "gif" | "image" | "video" | "webp") => {
    execDownloadMeme(meme, format);
    api.sendFeedback(meme.id, "download", format);
    onToast?.("✓ Downloaded!");
  };

  const pct = meme.confidence !== undefined ? Math.round(meme.confidence * 100) : null;

  return (
    <div className={`meme-card ${primary ? "primary" : ""}`}>
      <div className="meme-header">
        <div className="meme-name">{meme.name}</div>
        <div className="meme-badges">
          <span className="badge badge-category">{meme.category.replace(/_/g, " ")}</span>
          {showConfidence && pct !== null && (
            <span className="badge badge-confidence">
              <Icon name="sparkles" size={12} /> {pct}% match
            </span>
          )}
          {meme.viralScore !== undefined && meme.viralScore > 0 && (
            <span className="badge badge-viral">
              <Icon name="trending" size={12} /> viral
            </span>
          )}
        </div>
      </div>

      {showConfidence && pct !== null && (
        <div className="confidence-bar" title={`Match Confidence: ${pct}%`}>
          <div className="confidence-fill" style={{ width: `${pct}%` }} />
        </div>
      )}

      <div
        className="meme-dialogue"
        title="Click to copy dialogue"
        onClick={copyMeme}
        style={{ cursor: "pointer" }}
      >
        "{meme.dialogue}"
      </div>
      <div className="meme-explanation">{meme.explanation}</div>

      {/* Visual Meme Media Preview */}
      {(() => {
        const mediaUrl = meme.formats?.[selectedFormat] || meme.formats?.image || meme.formats?.gif || meme.imageRef || meme.gifRef;
        if (!mediaUrl) return null;
        return (
          <div
            className="meme-media-container"
            style={{
              margin: "12px 0",
              borderRadius: "8px",
              overflow: "hidden",
              background: "rgba(255,255,255,0.03)",
              border: "1px solid var(--border)",
              textAlign: "center",
              minHeight: "180px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <img
              src={mediaUrl}
              alt={meme.name}
              loading="lazy"
              decoding="async"
              onError={(e) => { (e.target as HTMLElement).style.display = "none"; }}
              style={{ maxHeight: "280px", maxWidth: "100%", objectFit: "contain", borderRadius: "8px", display: "inline-block" }}
            />
          </div>
        );
      })()}

      <div className="format-selector-row" style={{ display: "flex", gap: "6px", margin: "12px 0 8px", flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontSize: "0.72rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginRight: "4px" }}>Format:</span>
        {(["image", "gif", "video", "webp"] as const).map((fmt) => (
          <button
            key={fmt}
            className={`btn-fmt ${selectedFormat === fmt ? "active" : ""}`}
            onClick={() => handleFormatChange(fmt)}
            style={{
              padding: "3px 9px",
              fontSize: "0.74rem",
              fontWeight: 600,
              borderRadius: "5px",
              border: selectedFormat === fmt ? "1px solid var(--text-primary)" : "1px solid var(--border)",
              background: selectedFormat === fmt ? "#27272a" : "transparent",
              color: selectedFormat === fmt ? "#ffffff" : "var(--text-secondary)",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            {fmt.toUpperCase()}
          </button>
        ))}
      </div>

      {(meme.videoRef || meme.gifRef || meme.usageCount !== undefined) && (
        <div className="meme-meta">
          {meme.usageCount !== undefined && (
            <span>
              <Icon name="bar-chart" size={13} /> {meme.usageCount} uses
            </span>
          )}
          {meme.videoRef && (
            <span>
              <Icon name="video" size={13} />{" "}
              <a href={meme.videoRef} target="_blank" rel="noopener noreferrer">
                Video reference
              </a>
            </span>
          )}
          {meme.gifRef && (
            <span>
              <Icon name="film" size={13} />{" "}
              <a href={meme.gifRef} target="_blank" rel="noopener noreferrer">
                GIF reference
              </a>
            </span>
          )}
        </div>
      )}

      <div className="vote-row">
        <button
          className={`btn-vote up ${vote === 1 ? "voted" : ""}`}
          onClick={() => doVote(1)}
          title="Upvote match"
        >
          <Icon name="thumb-up" size={14} /> Spot on
        </button>
        <button
          className={`btn-vote down ${vote === -1 ? "voted" : ""}`}
          onClick={() => doVote(-1)}
          title="Downvote match"
        >
          <Icon name="thumb-down" size={14} /> Not quite
        </button>

        <button
          className={`btn-action ${fav ? "active" : ""}`}
          onClick={toggleFav}
          title={fav ? "Remove from Favorites" : "Add to Favorites"}
          style={{ marginLeft: "auto" }}
        >
          <Icon name={fav ? "heart-filled" : "heart"} size={14} /> {fav ? "Saved" : "Favorite"}
        </button>

        <button className="btn-action" onClick={handleShare} title="Share meme link">
          <Icon name="share" size={14} /> Share
        </button>

        <button className="btn-action" onClick={copyMeme} title="Copy meme">
          <Icon name="copy" size={14} /> Copy
        </button>

        <button className="btn-action primary-action" onClick={() => downloadMeme(selectedFormat)} title="Download meme file">
          <Icon name="download" size={14} /> Download
        </button>
      </div>
    </div>
  );
}
