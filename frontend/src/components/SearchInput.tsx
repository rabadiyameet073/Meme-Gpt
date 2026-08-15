import { useState, useCallback, KeyboardEvent } from "react";

export interface SearchInputProps {
  onSearch: (query: string) => void;
  loading: boolean;
  maxLength?: number;
  placeholder?: string;
  initialValue?: string;
}

export function SearchInput({
  onSearch,
  loading,
  maxLength = 2000,
  placeholder = "What's happening? 🤔 Type anything... (paste chats, describe feelings, quote movies)",
  initialValue = "",
}: SearchInputProps) {
  const [value, setValue] = useState(initialValue);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && value.trim()) {
        e.preventDefault();
        onSearch(value.trim());
      }
    },
    [value, onSearch]
  );

  const handleTriggerSearch = () => {
    if (value.trim() && !loading) {
      onSearch(value.trim());
    }
  };

  return (
    <div
      className={`search-input-wrapper ${loading ? "is-loading" : ""}`}
      style={{
        background: "var(--bg-surface, #141414)",
        border: loading ? "1px solid var(--brand-purple, #7C3AED)" : "1px solid var(--border-default, #2a2a2a)",
        borderRadius: "14px",
        padding: "16px",
        boxShadow: loading
          ? "0 0 20px rgba(124, 58, 237, 0.25)"
          : "0 8px 30px rgba(0,0,0,0.4)",
        transition: "all 0.25s ease",
      }}
    >
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value.slice(0, maxLength))}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={loading}
        rows={3}
        aria-label="Meme search input"
        style={{
          width: "100%",
          background: "transparent",
          border: "none",
          outline: "none",
          color: "var(--text-primary, #F5F5F5)",
          fontSize: "1.05rem",
          lineHeight: "1.5",
          resize: "none",
          fontFamily: "var(--font-sans, inherit)",
        }}
      />
      <div
        className="search-input-footer"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "10px",
          paddingTop: "10px",
          borderTop: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        <span
          className="char-count"
          style={{
            fontSize: "0.8rem",
            color: value.length > maxLength * 0.9 ? "var(--brand-amber, #F59E0B)" : "var(--text-muted, #71717a)",
            fontWeight: 500,
          }}
        >
          {value.length}/{maxLength}
        </span>
        <button
          onClick={handleTriggerSearch}
          disabled={loading || !value.trim()}
          style={{
            background: loading
              ? "rgba(124, 58, 237, 0.4)"
              : value.trim()
              ? "var(--brand-purple, #7C3AED)"
              : "rgba(255,255,255,0.06)",
            color: "#ffffff",
            border: "none",
            borderRadius: "8px",
            padding: "8px 18px",
            fontWeight: 600,
            fontSize: "0.9rem",
            cursor: loading || !value.trim() ? "not-allowed" : "pointer",
            transition: "all 0.2s ease",
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
          }}
        >
          {loading ? "Finding your meme..." : "⌘ + Enter to Search →"}
        </button>
      </div>
    </div>
  );
}
