import { useEffect, useState } from "react";
import { Meme } from "../lib/api";
import { Icon } from "./Icon";

export interface PreviewModalProps {
  meme: Meme;
  isOpen: boolean;
  onClose: () => void;
  onPrev?: () => void;
  onNext?: () => void;
  hasPrev?: boolean;
  hasNext?: boolean;
  onToast?: (msg: string) => void;
  onFavoriteToggle?: (meme: Meme) => void;
  isFavorited?: boolean;
}

export function PreviewModal({
  meme,
  isOpen,
  onClose,
  onPrev,
  onNext,
  hasPrev = false,
  hasNext = false,
  onToast,
  onFavoriteToggle,
  isFavorited = false,
}: PreviewModalProps) {
  const [selectedFormat, setSelectedFormat] = useState<"image" | "gif" | "video" | "webp">("gif");

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      } else if (e.key === "ArrowLeft" && hasPrev && onPrev) {
        e.preventDefault();
        onPrev();
      } else if (e.key === "ArrowRight" && hasNext && onNext) {
        e.preventDefault();
        onNext();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, onPrev, onNext, hasPrev, hasNext]);

  if (!isOpen || !meme) return null;

  const mediaUrl =
    meme.formats?.[selectedFormat] ||
    meme.formats?.image ||
    meme.formats?.gif ||
    meme.imageRef ||
    meme.gifRef;

  return (
    <div
      className="preview-modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="preview-meme-title"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.85)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        padding: "20px",
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="preview-modal-content glass-card"
        style={{
          maxWidth: "840px",
          width: "100%",
          maxHeight: "92vh",
          overflowY: "auto",
          background: "var(--bg-surface, #1A1A2E)",
          border: "1px solid var(--border-subtle, #334155)",
          borderRadius: "var(--radius-xl, 16px)",
          padding: "24px",
          position: "relative",
          boxShadow: "var(--shadow-lg, 0 10px 40px rgba(0, 0, 0, 0.5))",
        }}
      >
        {/* Header Bar */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
          <div>
            <h2 id="preview-meme-title" style={{ fontSize: "1.4rem", fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
              {meme.name}
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.82rem", marginTop: "2px" }}>
              Slug: <code style={{ color: "var(--text-accent, #A78BFA)" }}>{meme.slug}</code>
            </p>
          </div>

          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            {onFavoriteToggle && (
              <button
                onClick={() => onFavoriteToggle(meme)}
                aria-label="Toggle Favorite"
                style={{
                  background: isFavorited ? "rgba(239, 68, 68, 0.15)" : "rgba(255,255,255,0.05)",
                  border: isFavorited ? "1px solid var(--status-red, #ef4444)" : "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "8px",
                  color: isFavorited ? "var(--status-red, #ef4444)" : "var(--text-secondary)",
                  cursor: "pointer",
                }}
              >
                <Icon name="heart" size={16} />
              </button>
            )}
            <button
              onClick={onClose}
              aria-label="Close modal"
              style={{
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                padding: "8px 12px",
                color: "var(--text-secondary)",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.9rem",
              }}
            >
              ✕ Esc
            </button>
          </div>
        </div>

        {/* Media Preview */}
        <div
          style={{
            position: "relative",
            minHeight: "280px",
            maxHeight: "55vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(0, 0, 0, 0.4)",
            borderRadius: "12px",
            overflow: "hidden",
            margin: "12px 0",
          }}
        >
          {mediaUrl ? (
            <img
              src={mediaUrl}
              alt={meme.name}
              loading="lazy"
              decoding="async"
              style={{
                maxHeight: "52vh",
                maxWidth: "100%",
                objectFit: "contain",
                borderRadius: "8px",
              }}
            />
          ) : (
            <span style={{ color: "var(--text-muted)" }}>Preview media unavailable</span>
          )}

          {/* Navigation Arrows */}
          {hasPrev && onPrev && (
            <button
              onClick={onPrev}
              aria-label="Previous meme"
              style={{
                position: "absolute",
                left: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                background: "rgba(0, 0, 0, 0.7)",
                border: "1px solid rgba(255,255,255,0.15)",
                borderRadius: "50%",
                width: "40px",
                height: "40px",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
              }}
            >
              ←
            </button>
          )}

          {hasNext && onNext && (
            <button
              onClick={onNext}
              aria-label="Next meme"
              style={{
                position: "absolute",
                right: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                background: "rgba(0, 0, 0, 0.7)",
                border: "1px solid rgba(255,255,255,0.15)",
                borderRadius: "50%",
                width: "40px",
                height: "40px",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
              }}
            >
              →
            </button>
          )}
        </div>

        {/* Action Bar & Format Picker */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "12px",
            padding: "12px 16px",
            background: "rgba(255,255,255,0.03)",
            borderRadius: "10px",
            border: "1px solid var(--border)",
          }}
        >
          <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
            <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", fontWeight: 600 }}>FORMAT:</span>
            {(["image", "gif", "video", "webp"] as const).map((fmt) => (
              <button
                key={fmt}
                onClick={() => setSelectedFormat(fmt)}
                style={{
                  padding: "4px 10px",
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  borderRadius: "6px",
                  border: selectedFormat === fmt ? "1px solid var(--brand-purple, #7C3AED)" : "1px solid var(--border)",
                  background: selectedFormat === fmt ? "var(--brand-purple, #7C3AED)" : "transparent",
                  color: selectedFormat === fmt ? "#ffffff" : "var(--text-secondary)",
                  cursor: "pointer",
                }}
              >
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={() => {
                if (mediaUrl) {
                  navigator.clipboard.writeText(mediaUrl);
                  onToast?.("Media URL copied!");
                }
              }}
              className="btn-ghost"
              style={{ fontSize: "0.82rem", padding: "6px 12px", borderRadius: "8px" }}
            >
              <Icon name="copy" size={14} /> Copy URL
            </button>
            <a
              href={mediaUrl || "#"}
              download={`${meme.slug}.${selectedFormat}`}
              target="_blank"
              rel="noreferrer"
              className="btn-primary"
              style={{
                fontSize: "0.82rem",
                padding: "6px 16px",
                borderRadius: "8px",
                textDecoration: "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <Icon name="download" size={14} /> Download {selectedFormat.toUpperCase()}
            </a>
          </div>
        </div>

        {/* Explanation */}
        <p style={{ marginTop: "14px", color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: "1.5" }}>
          {meme.explanation || meme.description || "No description available."}
        </p>
      </div>
    </div>
  );
}
