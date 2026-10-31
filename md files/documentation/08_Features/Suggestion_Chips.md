# MemeGPT — Suggestion Chips

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Specification for the suggestion chip system — pre-defined quick-search tags displayed below the search input to inspire and accelerate meme discovery.

---

## What Are Suggestion Chips

Visual buttons below the search input that users can tap for instant search:

```
[🤦 Monday vibe] [😤 Frustration] [🎉 Win] [💻 Programmer life] [🏠 WFH]
```

---

## Chip Categories

### Static Chips (Always Available)

| Chip | Query Sent | Emotion |
|---|---|---|
| 🤦 Monday vibe | "Monday morning feeling" | sadness |
| 😤 Frustration | "when everything goes wrong" | anger |
| 🎉 Win | "when you finally succeed" | joy |
| 💻 Programmer life | "when the code works on first try" | surprise |
| 🏠 WFH | "working from home struggles" | neutral |
| 😴 Tired | "when you haven't slept enough" | sadness |
| 🔥 Savage | "sarcastic comeback moment" | anger |
| 💀 Dead | "when something is too funny" | joy |

### Dynamic Chips (Time-Based)

| Time | Chips Shown |
|---|---|
| Monday 6-10 AM | [Monday morning] [Need coffee] [Back to work] |
| Friday 3-6 PM | [Friday feeling] [Weekend plans] [Almost there] |
| Weekend | [Weekend vibes] [Sunday scaries] [No work today] |
| Exam season | [Exam stress] [All-nighter] [Passing grade] |

---

## Implementation

```typescript
// components/search/SuggestionChips.tsx
const CHIPS = [
  { label: '🤦 Monday vibe', query: 'Monday morning feeling' },
  { label: '😤 Frustration', query: 'when everything goes wrong' },
  { label: '🎉 Win', query: 'when you finally succeed' },
  { label: '💻 Programmer life', query: 'when the code works on first try' },
  { label: '🏠 WFH', query: 'working from home struggles' },
]

export function SuggestionChips({ onSelect }: { onSelect: (query: string) => void }) {
  return (
    <div className="suggestion-chips" role="group" aria-label="Quick search suggestions">
      {CHIPS.map(chip => (
        <button
          key={chip.query}
          className="chip"
          onClick={() => onSelect(chip.query)}
        >
          {chip.label}
        </button>
      ))}
    </div>
  )
}
```

```css
.suggestion-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}
.chip {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}
.chip:hover {
  background: var(--brand-purple);
  color: white;
  border-color: var(--brand-purple);
}
```

---

## Best Practices

1. **Show 5-8 chips maximum** — too many = decision paralysis
2. **Use emoji prefixes** — adds visual personality, faster scanning
3. **Randomize order slightly** — prevents users from always picking the first one
4. **Track chip usage** — analytics show which chips drive engagement
5. **A/B test chip labels** — "Monday vibe" vs "Monday morning" vs "Mondays be like"

---

> **Related Documents:**
> - [Smart_Meme_Search.md](./Smart_Meme_Search.md) — Core search
> - [04_Frontend/Components.md](../04_Frontend/Components.md) — Component specs
