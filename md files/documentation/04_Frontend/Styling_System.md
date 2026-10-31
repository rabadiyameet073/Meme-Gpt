# MemeGPT — Styling System

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete design system — CSS custom properties (tokens), component patterns, animations, responsive utilities, and dark mode implementation.

---

## Design Philosophy

MemeGPT's visual identity: **Dark, purple-accented, glassy, alive.** Every surface has subtle gradients, every interaction has smooth transitions. The UI should feel premium — like a modern SaaS tool, not a basic Bootstrap app.

---

## CSS Custom Properties (Design Tokens)

```css
/* globals.css — Design Token System */
:root {
  /* ── Brand Colors ── */
  --brand-purple: #7C3AED;
  --brand-purple-light: #8B5CF6;
  --brand-purple-dark: #6D28D9;
  --brand-gradient: linear-gradient(135deg, #7C3AED, #2563EB);
  
  /* ── Background Colors ── */
  --bg-dark: #0F0F23;
  --bg-surface: #1A1A2E;
  --bg-elevated: #16213E;
  --bg-card: rgba(26, 26, 46, 0.8);
  --bg-glass: rgba(26, 26, 46, 0.6);
  
  /* ── Text Colors ── */
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --text-accent: #A78BFA;
  
  /* ── Border Colors ── */
  --border-subtle: #334155;
  --border-hover: #475569;
  --border-focus: #7C3AED;
  
  /* ── Semantic Colors ── */
  --success: #22C55E;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #0EA5E9;
  
  /* ── Typography ── */
  --font-sans: 'Inter', 'SF Pro Display', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 2rem;      /* 32px */
  --text-4xl: 2.5rem;    /* 40px */
  
  /* ── Spacing ── */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  
  /* ── Border Radius ── */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
  
  /* ── Shadows ── */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 40px rgba(0, 0, 0, 0.5);
  --shadow-purple: 0 4px 20px rgba(124, 58, 237, 0.3);
  
  /* ── Transitions ── */
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;
}
```

---

## Glassmorphism Pattern

```css
.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}
```

---

## Component Styling Patterns

### MemeCard

```css
.meme-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}
.meme-card:hover {
  transform: translateY(-4px);
  border-color: var(--brand-purple);
  box-shadow: var(--shadow-purple);
}
```

### Button Variants

```css
.btn-primary {
  background: var(--brand-gradient);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-lg);
  font-weight: 600;
  transition: all var(--transition-fast);
}
.btn-primary:hover {
  filter: brightness(1.1);
  box-shadow: var(--shadow-purple);
}
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-md);
}
.btn-ghost:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}
```

---

## Animations

```css
/* Loading skeleton shimmer */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg,
    var(--bg-surface) 25%,
    var(--bg-elevated) 50%,
    var(--bg-surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

/* Fade in results */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.result-card {
  animation: fadeInUp 0.3s ease forwards;
}
.result-card:nth-child(2) { animation-delay: 0.05s; }
.result-card:nth-child(3) { animation-delay: 0.10s; }
.result-card:nth-child(4) { animation-delay: 0.15s; }
.result-card:nth-child(5) { animation-delay: 0.20s; }

/* Toast slide-in */
@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
.toast { animation: slideInRight 0.2s ease; }
```

---

## Responsive Utilities

```css
/* Mobile-first breakpoints */
@media (min-width: 640px)  { /* sm: Tablet */ }
@media (min-width: 1024px) { /* lg: Desktop */ }
@media (min-width: 1280px) { /* xl: Wide desktop */ }

/* Results grid */
.results-grid {
  display: grid;
  gap: var(--space-md);
  grid-template-columns: 1fr;                      /* Mobile: 1 col */
}
@media (min-width: 640px) {
  .results-grid { grid-template-columns: repeat(2, 1fr); }  /* Tablet: 2 */
}
@media (min-width: 1024px) {
  .results-grid { grid-template-columns: repeat(3, 1fr); }  /* Desktop: 3 */
}
```

---

## Best Practices

1. **Use CSS custom properties** — change theme by updating variables, not components
2. **Mobile-first breakpoints** — `min-width` not `max-width`
3. **No runtime CSS-in-JS** — CSS Modules or vanilla CSS for zero runtime overhead
4. **Consistent spacing scale** — always use `--space-*` tokens
5. **Transition everything** — hover, focus, active states should all animate smoothly
6. **Dark mode by default** — meme culture audience prefers dark themes

---

> **Related Documents:**
> - [Components.md](./Components.md) — Component specifications
> - [Frontend_Overview.md](./Frontend_Overview.md) — Frontend architecture
> - [04_Frontend/Performance.md](./Performance.md) — Web Vitals optimization
