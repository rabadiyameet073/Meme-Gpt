import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { api, Meme } from "../api";
import { Icon } from "./Icon";
import { soundFx } from "../lib/audio";

export interface MemeDetailProps {
  slug: string;
  onBack?: () => void;
  onToast?: (msg: string) => void;
}

export function MemeDetail({ slug, onBack, onToast }: MemeDetailProps) {
  const [meme, setMeme] = useState<Meme | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<"image" | "gif" | "video" | "webp">("gif");

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    api
      .getMeme(slug)
      .then((data) => {
        if (isMounted) {
          setMeme(data);
          document.title = `${data.name} — MemeGPT`;
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Failed to load meme details");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
      document.title = "MemeGPT — AI Meme Search Engine";
    };
  }, [slug]);

  if (loading) {
    return (
      <div style={{ padding: "80px 20px", textAlign: "center" }}>
        <div
          style={{
            width: "40px",
            height: "40px",
            margin: "0 auto 16px",
            border: "3px solid var(--border)",
            borderTopColor: "var(--brand-primary)",
            borderRadius: "50%",
            animation: "spin 0.8s linear infinite",
          }}
        />
        <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>Loading meme details...</p>
      </div>
    );
  }

  if (error || !meme) {
    return (
      <div style={{ padding: "60px 20px", textAlign: "center", maxWidth: "480px", margin: "0 auto" }}>
        <div
          style={{
            width: "48px",
            height: "48px",
            borderRadius: "var(--radius-sm)",
            backgroundColor: "rgba(244, 63, 94, 0.1)",
            color: "var(--accent-rose)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 16px",
          }}
        >
          <Icon name="alert" size={24} />
        </div>
        <h3 style={{ fontSize: "1.2rem", marginBottom: "8px" }}>Meme Not Found</h3>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "20px" }}>
          {error || "The requested meme could not be located in our index."}
        </p>
        {onBack && (
          <button
            type="button"
            onClick={onBack}
            className="btn btn-secondary"
          >
            ← Back to Search
          </button>
        )}
      </div>
    );
  }

  const mediaUrl =
    meme.formats?.[selectedFormat] ||
    meme.formats?.image ||
    meme.formats?.gif ||
    meme.imageRef ||
    meme.gifRef;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ maxWidth: "860px", margin: "0 auto", paddingBottom: "40px" }}
    >
      {onBack && (
        <button
          type="button"
          onClick={() => {
            soundFx.playTap();
            onBack();
          }}
          className="btn btn-secondary"
          style={{ marginBottom: "20px", fontSize: "0.84rem" }}
        >
          ← Back to Catalog
        </button>
      )}

      <div
        style={{
          backgroundColor: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-md)",
          padding: "28px",
          boxShadow: "var(--shadow-md)",
        }}
      >
        {/* Title Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <span className="badge badge-category" style={{ marginBottom: "8px" }}>
              <Icon name="tag" size={11} /> {meme.category ? meme.category.replace(/_/g, " ") : "general"}
            </span>
            <h1 style={{ fontSize: "1.8rem", fontWeight: 800, margin: "4px 0 6px", color: "var(--text-primary)" }}>
              {meme.name}
            </h1>
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
              Slug: <code style={{ color: "var(--brand-primary)" }}>{meme.slug}</code>
            </p>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <button
              type="button"
              onClick={() => {
                soundFx.playClick();
                navigator.clipboard.writeText(window.location.href);
                onToast?.("Meme URL copied to clipboard!");
              }}
              className="btn btn-secondary"
              style={{ fontSize: "0.84rem" }}
            >
              <Icon name="share" size={14} /> Share Link
            </button>
          </div>
        </div>

        {/* Dialogue Quote Box */}
        {meme.dialogue && (
          <div
            className="card-dialogue"
            style={{
              fontSize: "1rem",
              padding: "12px 18px",
              margin: "18px 0",
              borderRadius: "var(--radius-sm)",
            }}
          >
            "{meme.dialogue}"
          </div>
        )}

        {/* Media Preview Box */}
        <div
          style={{
            margin: "20px 0",
            backgroundColor: "var(--bg-input)",
            borderRadius: "var(--radius-sm)",
            padding: "20px",
            textAlign: "center",
            minHeight: "280px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            border: "1px solid var(--border-subtle)",
          }}
        >
          {mediaUrl ? (
            <img
              src={mediaUrl}
              alt={meme.name}
              loading="lazy"
              decoding="async"
              style={{ maxHeight: "450px", maxWidth: "100%", objectFit: "contain", borderRadius: "var(--radius-xs)" }}
            />
          ) : (
            <span style={{ color: "var(--text-muted)" }}>Preview unavailable</span>
          )}
        </div>

        {/* Format Selector & Download Toolbar */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "14px",
            padding: "14px 18px",
            backgroundColor: "var(--bg-panel)",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border-subtle)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 700, textTransform: "uppercase" }}>
              Available Formats:
            </span>
            {(["image", "gif", "video", "webp"] as const).map((fmt) => (
              <button
                key={fmt}
                type="button"
                onClick={() => {
                  soundFx.playTap();
                  setSelectedFormat(fmt);
                }}
                style={{
                  padding: "4px 10px",
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  borderRadius: "var(--radius-xs)",
                  border: selectedFormat === fmt ? "1px solid var(--brand-primary)" : "1px solid var(--border)",
                  backgroundColor: selectedFormat === fmt ? "var(--brand-primary-subtle)" : "transparent",
                  color: selectedFormat === fmt ? "var(--brand-primary)" : "var(--text-secondary)",
                  cursor: "pointer",
                }}
              >
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>

          <a
            href={mediaUrl || "#"}
            download={`${meme.slug}.${selectedFormat}`}
            target="_blank"
            rel="noreferrer"
            className="btn btn-primary"
            onClick={() => soundFx.playSuccess()}
            style={{ textDecoration: "none", fontSize: "0.85rem" }}
          >
            <Icon name="download" size={15} color="#ffffff" />
            Download {selectedFormat.toUpperCase()}
          </a>
        </div>

        {/* Context & Description */}
        <div style={{ marginTop: "24px" }}>
          <h3 style={{ fontSize: "1.05rem", fontWeight: 700, marginBottom: "8px" }}>
            Context & Explanation
          </h3>
          <p style={{ color: "var(--text-secondary)", lineHeight: "1.6", fontSize: "0.92rem" }}>
            {meme.explanation || meme.description || "No context description available."}
          </p>

          {meme.tags && meme.tags.length > 0 && (
            <div style={{ marginTop: "18px" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "8px", fontWeight: 700, textTransform: "uppercase" }}>
                Tags & Descriptors:
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {meme.tags.map((tag: string) => (
                  <span
                    key={tag}
                    style={{
                      fontSize: "0.78rem",
                      padding: "4px 10px",
                      borderRadius: "var(--radius-xs)",
                      backgroundColor: "var(--bg-panel)",
                      border: "1px solid var(--border-subtle)",
                      color: "var(--text-secondary)",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
