import { useState, useEffect } from "react";
import { Icon } from "./Icon";

export interface SuggestionChipsProps {
  onSelect: (query: string) => void;
  disabled?: boolean;
}

interface ChipItem {
  label: string;
  query: string;
}

const STATIC_CHIPS: ChipItem[] = [
  { label: "🤦 Monday vibe", query: "Monday morning feeling" },
  { label: "😤 Frustration", query: "when everything goes wrong" },
  { label: "🎉 Win", query: "when you finally succeed" },
  { label: "💻 Programmer life", query: "when the code works on first try" },
  { label: "🏠 WFH", query: "working from home struggles" },
  { label: "😴 Tired", query: "when you haven't slept enough" },
  { label: "🔥 Savage", query: "sarcastic comeback moment" },
  { label: "💀 Dead", query: "when something is too funny" },
];

function getTimeBasedChips(): ChipItem[] {
  const now = new Date();
  const day = now.getDay(); // 0 is Sunday, 1 is Monday, 5 is Friday, 6 is Saturday
  const hour = now.getHours();

  if (day === 1 && hour >= 6 && hour <= 10) {
    return [
      { label: "☕ Monday morning", query: "Monday morning feeling" },
      { label: "☕ Need coffee", query: "need caffeine to survive" },
      { label: "💼 Back to work", query: "back to work reality check" },
    ];
  } else if (day === 5 && hour >= 15 && hour <= 18) {
    return [
      { label: "🍻 Friday feeling", query: "Friday afternoon celebration" },
      { label: "🌴 Weekend plans", query: "weekend ready" },
      { label: "⏳ Almost there", query: "almost the weekend clock watching" },
    ];
  } else if (day === 0 || day === 6) {
    return [
      { label: "🏖️ Weekend vibes", query: "relaxing weekend bliss" },
      { label: "😱 Sunday scaries", query: "Sunday night realizing tomorrow is Monday" },
      { label: "🛌 No work today", query: "sleeping in no alarms" },
    ];
  }
  return [];
}

export function SuggestionChips({ onSelect, disabled }: SuggestionChipsProps) {
  const [chips, setChips] = useState<ChipItem[]>([]);

  useEffect(() => {
    const dynamic = getTimeBasedChips();
    const dynamicQueries = new Set(dynamic.map((d) => d.query));
    const combined = [...dynamic, ...STATIC_CHIPS.filter((s) => !dynamicQueries.has(s.query))];
    setChips(combined.slice(0, 8)); // 5-8 chips maximum
  }, []);

  return (
    <div className="suggestion-chips-container" style={{ margin: "14px 0" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          fontSize: "0.78rem",
          fontWeight: 600,
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          marginBottom: "8px",
        }}
      >
        <Icon name="sparkles" size={14} /> Quick Situations:
      </div>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "8px",
        }}
        role="group"
        aria-label="Quick search suggestions"
      >
        {chips.map((chip) => (
          <button
            key={chip.query}
            onClick={() => onSelect(chip.query)}
            disabled={disabled}
            className="chip"
            style={{
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid var(--border)",
              borderRadius: "20px",
              padding: "6px 14px",
              fontSize: "0.82rem",
              color: "var(--text-secondary)",
              cursor: disabled ? "not-allowed" : "pointer",
              transition: "all var(--transition-fast, 0.15s ease)",
              textAlign: "left",
              whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => {
              if (!disabled) {
                e.currentTarget.style.borderColor = "var(--brand-purple, #7C3AED)";
                e.currentTarget.style.color = "#ffffff";
                e.currentTarget.style.background = "rgba(124, 58, 237, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (!disabled) {
                e.currentTarget.style.borderColor = "var(--border)";
                e.currentTarget.style.color = "var(--text-secondary)";
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)";
              }
            }}
          >
            {chip.label}
          </button>
        ))}
      </div>
    </div>
  );
}
