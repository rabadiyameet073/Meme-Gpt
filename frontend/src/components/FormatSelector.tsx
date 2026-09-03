import { useEffect } from "react";
import { Icon, type IconName } from "./Icon";

export type FormatType = "gif" | "image" | "video" | "any";

export interface FormatSelectorProps {
  value: FormatType;
  onChange: (format: FormatType) => void;
  sticky?: boolean;
}

const STORAGE_KEY = "memegpt_format_preference";

const FORMAT_TIPS: Record<FormatType, string> = {
  gif: "Best for WhatsApp, Discord, Slack (1–5MB animated format)",
  image: "Best for Instagram, X/Twitter, and blogs (50–500KB PNG/JPG)",
  video: "Best for TikTok, Reels, YouTube Shorts (2–10MB MP4 clips)",
  any: "Show and rank memes across all formats",
};

export function FormatSelector({
  value,
  onChange,
  sticky = false,
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

  const formats: { id: FormatType; label: string; icon: IconName; tip: string }[] = [
    { id: "gif", label: "GIF", icon: "film", tip: "Best for WhatsApp, Discord, Slack" },
    { id: "image", label: "Image", icon: "image", tip: "Best for Instagram, email, blog" },
    { id: "video", label: "Video", icon: "video", tip: "Best for TikTok, Reels, YouTube Shorts" },
    { id: "any", label: "All Formats", icon: "sparkles", tip: "Show all formats" },
  ];

  return (
    <div
      style={{
        position: sticky ? "sticky" : "static",
        top: sticky ? "12px" : "auto",
        zIndex: 10,
        display: "flex",
        flexDirection: "column",
        gap: "6px",
        padding: "10px 14px",
        background: "var(--bg-card)",
        backdropFilter: "blur(16px)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-md)",
        margin: "16px 0",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
        <span
          style={{
            fontSize: "0.78rem",
            fontWeight: 700,
            color: "var(--text-muted)",
            textTransform: "uppercase",
            marginRight: "4px",
          }}
        >
          Format Preference:
        </span>
        {formats.map((fmt) => {
          const active = value === fmt.id;
          return (
            <button
              key={fmt.id}
              type="button"
              onClick={() => handleSelect(fmt.id)}
              title={fmt.tip}
              style={{
                padding: "6px 14px",
                fontSize: "0.82rem",
                fontWeight: 600,
                borderRadius: "var(--radius-sm)",
                border: active
                  ? "1px solid var(--brand-purple)"
                  : "1px solid var(--border)",
                background: active
                  ? "var(--brand-purple)"
                  : "rgba(255,255,255,0.03)",
                color: active ? "#ffffff" : "var(--text-secondary)",
                cursor: "pointer",
                transition: "all 0.15s ease",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <Icon name={fmt.icon} size={14} color={active ? "#ffffff" : "var(--brand-cyan)"} />
              <span>{fmt.label}</span>
            </button>
          );
        })}
      </div>

      <div
        style={{
          fontSize: "0.76rem",
          color: "var(--text-muted)",
          display: "flex",
          alignItems: "center",
          gap: "6px",
          marginTop: "2px",
        }}
      >
        <Icon name="info" size={13} color="var(--brand-purple-light)" />
        <span>{FORMAT_TIPS[value]}</span>
      </div>
    </div>
  );
}
