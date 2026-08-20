import { useEffect } from "react";

export type FormatType = "gif" | "image" | "video" | "any";

export interface FormatSelectorProps {
  value: FormatType;
  onChange: (format: FormatType) => void;
  sticky?: boolean;
}

const STORAGE_KEY = "memegpt_format_preference";

const FORMAT_TIPS: Record<FormatType, string> = {
  gif: "Best for WhatsApp, Discord, Slack (1–5MB)",
  image: "Best for Instagram, email, blog (50–500KB)",
  video: "Best for TikTok, Reels, YouTube Shorts (2–10MB)",
  any: "Show memes across all formats",
};

export function FormatSelector({
  value,
  onChange,
  sticky = true,
}: FormatSelectorProps) {
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as FormatType | null;
    if (saved && ["gif", "image", "video", "any"].includes(saved) && saved !== value) {
      onChange(saved);
    }
  }, []);

  const handleSelect = (fmt: FormatType) => {
    onChange(fmt);
    try {
      localStorage.setItem(STORAGE_KEY, fmt);
    } catch {
      /* ignore */
    }
  };

  const formats: { id: FormatType; label: string; icon: string; tip: string }[] = [
    { id: "gif", label: "GIF", icon: "🎬", tip: "Best for WhatsApp, Discord, Slack" },
    { id: "image", label: "Image", icon: "🖼️", tip: "Best for Instagram, email, blog" },
    { id: "video", label: "Video", icon: "🎥", tip: "Best for TikTok, Reels, YouTube Shorts" },
    { id: "any", label: "All Formats", icon: "✨", tip: "Show all formats" },
  ];

  return (
    <div
      className="format-selector-bar"
      style={{
        position: sticky ? "sticky" : "static",
        top: sticky ? "12px" : "auto",
        zIndex: 10,
        display: "flex",
        flexDirection: "column",
        gap: "6px",
        padding: "10px 14px",
        background: "rgba(20, 20, 20, 0.85)",
        backdropFilter: "blur(12px)",
        border: "1px solid var(--border-subtle, #2a2a2a)",
        borderRadius: "10px",
        margin: "16px 0",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
        <span
          style={{
            fontSize: "0.82rem",
            fontWeight: 600,
            color: "var(--text-secondary, #a1a1aa)",
            marginRight: "4px",
          }}
        >
          Prefer:
        </span>
        {formats.map((fmt) => {
          const active = value === fmt.id;
          return (
            <button
              key={fmt.id}
              onClick={() => handleSelect(fmt.id)}
              title={fmt.tip}
              style={{
                padding: "6px 14px",
                fontSize: "0.82rem",
                fontWeight: 600,
                borderRadius: "7px",
                border: active
                  ? "1px solid var(--brand-purple, #7C3AED)"
                  : "1px solid rgba(255,255,255,0.08)",
                background: active
                  ? "var(--brand-purple, #7C3AED)"
                  : "rgba(255,255,255,0.03)",
                color: active ? "#ffffff" : "var(--text-secondary, #d4d4d8)",
                cursor: "pointer",
                transition: "all 0.15s ease",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <span>{fmt.icon}</span>
              <span>{fmt.label}</span>
              {active && <span style={{ fontSize: "0.75rem" }}>✓</span>}
            </button>
          );
        })}
      </div>

      {/* Platform Recommendation Tooltip Bar */}
      <div
        style={{
          fontSize: "0.75rem",
          color: "var(--brand-purple, #a855f7)",
          fontWeight: 500,
          display: "flex",
          alignItems: "center",
          gap: "6px",
          paddingLeft: "2px",
        }}
      >
        <span>💡 Recommendation:</span>
        <span style={{ color: "var(--text-muted, #94a3b8)" }}>{FORMAT_TIPS[value]}</span>
      </div>
    </div>
  );
}
