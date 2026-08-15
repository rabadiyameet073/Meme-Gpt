import { useState, useCallback, FormEvent, KeyboardEvent } from "react";

export interface SearchFormProps {
  onSubmit: (query: string, format: string) => void;
  loading: boolean;
  initialQuery?: string;
  initialFormat?: string;
}

export function SearchForm({
  onSubmit,
  loading,
  initialQuery = "",
  initialFormat = "gif",
}: SearchFormProps) {
  const [query, setQuery] = useState(initialQuery);
  const [format, setFormat] = useState(initialFormat);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    (e?: FormEvent) => {
      if (e) e.preventDefault();

      // Client-side validation
      const trimmed = query.trim();
      if (!trimmed) {
        setError("Please enter something to search for");
        return;
      }
      if (trimmed.length > 2000) {
        setError("Query must be under 2000 characters");
        return;
      }

      setError(null);
      onSubmit(trimmed, format);
    },
    [query, format, onSubmit]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <form
      onSubmit={handleSubmit}
      className={`search-form ${loading ? "is-loading" : ""}`}
      role="search"
      style={{
        background: "var(--bg-surface, #141414)",
        border: error
          ? "1px solid var(--error, #EF4444)"
          : loading
          ? "1px solid var(--brand-purple, #7C3AED)"
          : "1px solid var(--border-default, #2a2a2a)",
        borderRadius: "14px",
        padding: "18px",
        boxShadow: "0 8px 30px rgba(0,0,0,0.4)",
        transition: "all 0.25s ease",
      }}
    >
      <div className="search-form__input-group" style={{ position: "relative" }}>
        <textarea
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (error) setError(null);
          }}
          onKeyDown={handleKeyDown}
          placeholder="What's happening? 🤔 Type anything... (describe feelings, paste chats, quote movies)"
          disabled={loading}
          rows={3}
          maxLength={2000}
          aria-label="Meme search query"
          aria-invalid={!!error}
          aria-describedby={error ? "search-error" : undefined}
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
        <span
          className="char-count"
          style={{
            display: "block",
            textAlign: "right",
            fontSize: "0.78rem",
            color: query.length > 1800 ? "var(--brand-amber, #F59E0B)" : "var(--text-muted, #71717a)",
            marginTop: "4px",
          }}
        >
          {query.length}/2000
        </span>
      </div>

      {error && (
        <p
          id="search-error"
          className="form-error"
          role="alert"
          style={{
            color: "var(--error, #EF4444)",
            fontSize: "0.85rem",
            marginTop: "6px",
            marginBottom: "6px",
            fontWeight: 500,
          }}
        >
          ⚠️ {error}
        </p>
      )}

      <div
        className="search-form__actions"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "12px",
          paddingTop: "12px",
          borderTop: "1px solid rgba(255,255,255,0.06)",
          flexWrap: "wrap",
          gap: "10px",
        }}
      >
        <fieldset
          className="format-selector"
          aria-label="Format preference"
          style={{
            border: "none",
            padding: 0,
            margin: 0,
            display: "flex",
            gap: "8px",
            alignItems: "center",
          }}
        >
          <span style={{ fontSize: "0.8rem", color: "var(--text-secondary, #a1a1aa)", marginRight: "4px" }}>
            Format:
          </span>
          {["gif", "image", "video"].map((f) => {
            const active = format === f;
            return (
              <label
                key={f}
                style={{
                  padding: "4px 10px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  borderRadius: "6px",
                  border: active
                    ? "1px solid var(--brand-purple, #7C3AED)"
                    : "1px solid rgba(255,255,255,0.08)",
                  background: active
                    ? "var(--brand-purple, #7C3AED)"
                    : "rgba(255,255,255,0.03)",
                  color: active ? "#ffffff" : "var(--text-secondary, #d4d4d8)",
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  transition: "all 0.15s ease",
                }}
              >
                <input
                  type="radio"
                  name="format"
                  value={f}
                  checked={active}
                  onChange={(e) => setFormat(e.target.value)}
                  style={{ display: "none" }}
                />
                {f.toUpperCase()}
              </label>
            );
          })}
        </fieldset>

        <button
          type="submit"
          disabled={loading || !query.trim()}
          style={{
            background: loading
              ? "rgba(124, 58, 237, 0.4)"
              : query.trim()
              ? "var(--brand-purple, #7C3AED)"
              : "rgba(255,255,255,0.06)",
            color: "#ffffff",
            border: "none",
            borderRadius: "8px",
            padding: "8px 18px",
            fontWeight: 600,
            fontSize: "0.9rem",
            cursor: loading || !query.trim() ? "not-allowed" : "pointer",
            transition: "all 0.2s ease",
          }}
        >
          {loading ? "Finding your meme..." : "Search →"}
        </button>
      </div>
    </form>
  );
}
