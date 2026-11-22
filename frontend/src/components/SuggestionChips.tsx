import { useState, useEffect } from "react";
import { Icon, type IconName } from "./Icon";
import { api } from "../lib/api";

export interface SuggestionChipsProps {
  onSelect: (query: string) => void;
  disabled?: boolean;
}

interface ChipItem {
  label: string;
  query: string;
  icon: IconName;
}

const STATIC_CHIPS: ChipItem[] = [
  { label: "Monday Vibe", icon: "clock", query: "Monday morning feeling and low energy" },
  { label: "Code Works First Try", icon: "coding", query: "when the code works on first try without bugs" },
  { label: "Huge Win", icon: "trophy", query: "when you finally succeed after failing" },
  { label: "Startup Chaos", icon: "startup", query: "working at a fast paced AI startup" },
  { label: "Work From Home", icon: "office", query: "working from home daily struggles" },
  { label: "Exams One Night Before", icon: "college", query: "studying entire syllabus one night before exam" },
  { label: "Clutch Gaming Moment", icon: "gaming", query: "carrying the whole team to victory in gaming" },
  { label: "Extremely Relatable", icon: "sparkles", query: "this is so relatable it hurts" },
];

export function SuggestionChips({ onSelect, disabled }: SuggestionChipsProps) {
  const [chips, setChips] = useState<ChipItem[]>(STATIC_CHIPS);

  useEffect(() => {
    let active = true;
    api.getSuggestionChips(8)
      .then((res) => {
        if (active && res?.chips?.length) {
          const dynamicList: ChipItem[] = res.chips.map((c) => ({
            label: c.label,
            query: c.query,
            icon: "sparkles",
          }));
          setChips(dynamicList);
        }
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  return (
    <div style={{ margin: "18px 0 6px" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          fontSize: "0.76rem",
          fontWeight: 700,
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.06em",
          marginBottom: "10px",
        }}
      >
        <Icon name="sparkles" size={13} color="var(--brand-purple-light)" />
        <span>Instant AI Prompts:</span>
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
            key={`${chip.label}-${chip.query}`}
            onClick={() => onSelect(chip.query)}
            disabled={disabled}
            type="button"
            className="chip-btn"
            style={{
              padding: "6px 14px",
              fontSize: "0.82rem",
            }}
          >
            <Icon name={chip.icon} size={14} color="var(--brand-cyan)" />
            <span>{chip.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
