import { useState, useEffect } from "react";
import { api, Meme } from "../api";
import { Icon } from "./Icon";

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
      <div style={{ padding: "60px 20px", textAlign: "center" }}>
        <div
          style={{
            width: "48px",
            height: "48px",
            margin: "0 auto 16px",
            border: "3px solid rgba(124, 58, 237, 0.2)",
            borderTopColor: "var(--brand-purple, #7C3AED)",
            borderRadius: "50%",
            animation: "spin 0.8s linear infinite",
          }}
        />
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Loading meme details...</p>
      </div>
    );
  }

  if (error || !meme) {
    return (
      <div style={{ padding: "40px 20px", textAlign: "center" }}>
        <p style={{ color: "var(--error, #EF4444)", fontSize: "1rem", marginBottom: "16px" }}>
          ⚠️ {error || "Meme not found"}
        </p>
        {onBack && (
          <button
            onClick={onBack}
            className="btn btn-secondary"
            style={{ padding: "8px 16px", borderRadius: "8px" }}
          >
            ← Go Back
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
    <div className="meme-detail-view" style={{ maxWidth: "800px", margin: "0 auto", padding: "20px 0" }}>
      {onBack && (
        <button
          onClick={onBack}
          style={{
            background: "none",
            border: "none",
            color: "var(--text-secondary)",
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "0.9rem",
            marginBottom: "18px",
          }}
        >
          ← Back to Search
        </button>
      )}

      <div
        style={{
          background: "var(--bg-surface, #141414)",
          border: "1px solid var(--border)",
          borderRadius: "16px",
          padding: "24px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <h1 style={{ fontSize: "1.6rem", fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
              {meme.name}
            </h1>
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginTop: "4px" }}>
              Slug: <code style={{ color: "var(--brand-purple, #A78BFA)" }}>{meme.slug}</code>
            </p>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={() => {
                navigator.clipboard.writeText(window.location.href);
                onToast?.("Link copied to clipboard!");
              }}
              className="btn btn-secondary"
              style={{ padding: "6px 12px", fontSize: "0.82rem", borderRadius: "8px" }}
            >
              <Icon name="link" size={14} /> Share Link
            </button>
          </div>
        </div>

        {/* Media Preview Container */}
        <div
          style={{
            margin: "20px 0",
            background: "rgba(0,0,0,0.3)",
            borderRadius: "12px",
            padding: "16px",
            textAlign: "center",
            minHeight: "260px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {mediaUrl ? (
            <img
              src={mediaUrl}
              alt={meme.name}
              loading="lazy"
              decoding="async"
              style={{ maxHeight: "420px", maxWidth: "100%", objectFit: "contain", borderRadius: "8px" }}
            />
          ) : (
            <span style={{ color: "var(--text-muted)" }}>Preview unavailable</span>
          )}
        </div>

        {/* Format Selector & Download */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "12px",
            padding: "12px 16px",
            background: "rgba(255,255,255,0.02)",
            borderRadius: "10px",
            border: "1px solid var(--border)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)", fontWeight: 600 }}>
              AVAILABLE FORMATS:
            </span>
            {(["image", "gif", "video", "webp"] as const).map((fmt) => (
              <button
                key={fmt}
                onClick={() => setSelectedFormat(fmt)}
                style={{
                  padding: "4px 10px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  borderRadius: "6px",
                  border: selectedFormat === fmt ? "1px solid var(--brand-purple, #7C3AED)" : "1px solid var(--border)",
                  background: selectedFormat === fmt ? "var(--brand-purple, #7C3AED)" : "transparent",
                  color: selectedFormat === fmt ? "#fff" : "var(--text-secondary)",
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
            style={{
              padding: "6px 16px",
              fontSize: "0.85rem",
              borderRadius: "8px",
              textDecoration: "none",
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Icon name="download" size={15} /> Download {selectedFormat.toUpperCase()}
          </a>
        </div>

        {/* Description & Tags */}
        <div style={{ marginTop: "24px" }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "8px", color: "var(--text-primary)" }}>
            Context & Explanation
          </h3>
          <p style={{ color: "var(--text-secondary)", lineHeight: "1.6", fontSize: "0.95rem" }}>
            {meme.explanation || meme.description || "No description provided."}
          </p>

          {meme.tags && meme.tags.length > 0 && (
            <div style={{ marginTop: "16px" }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "8px", fontWeight: 600 }}>
                TAGS & CATEGORIES:
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {meme.tags.map((tag) => (
                  <span
                    key={tag}
                    style={{
                      fontSize: "0.76rem",
                      padding: "3px 8px",
                      borderRadius: "6px",
                      background: "rgba(255,255,255,0.05)",
                      border: "1px solid var(--border)",
                      color: "var(--text-secondary)",
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
    </div>
  );
}
