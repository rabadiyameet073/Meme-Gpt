# 14 — UI/UX, Accessibility & Responsive Design Gaps

**Source requirements:** `md files/completion_fixes/11_Accessibility_A11y.md`, `md files/documentation/04_Frontend/Styling_System.md`, `Components.md`, `md files/upgraded_docs/10_Frontend_Missing_Features.md` §1/§3, v1/v2 `04_DESIGN_AND_DEVELOPMENT.md`
**Related:** [12-frontend-web-gaps](12-frontend-web-gaps.md) · [13-user-workflow-gaps](13-user-workflow-gaps.md) · [19-testing-gaps](19-testing-gaps.md)

> Contrast and motion items need an axe/Lighthouse run. They are marked **ASSUMPTION** where they could not be confirmed by reading code.

## Verified as implemented
Skip link (`frontend/src/App.tsx:189`, `index.css:885-897`); Escape closes modals (`AuthModal.tsx:49`, `PreviewModal.tsx:36`, `MemeModal.tsx:15-18`); votes use `aria-pressed`; `role="alert"` errors; collection dialog with `role="dialog"` + `aria-modal`; Vite light/dark theme.

## Accessibility
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| A11Y-01 | Nav links have accessible names (`completion_fixes/11` §2) | Incorrectly implemented | `apps/web/components/layout/Header.tsx:62-63`: the emoji is `aria-hidden` and the label is `hidden sm:inline`, so links have no name under 640px | `aria-label` / `sr-only` | High |
| A11Y-02 | Focus trap + focus restore in dialogs (§4.1) | Partially implemented | `frontend/src/hooks/useFocusTrap.ts` has zero callers | Apply it to every dialog | High |
| A11Y-03 | Live announcements for async results | Not implemented | No `aria-live` in the Vite components; no `aria-busy` on skeletons | Polite result count; chat-turn announcements | High |
| A11Y-04 | Correct ARIA patterns (§2.3) | Incorrectly implemented | Trending filter `role="tab"` without tabpanel/arrow keys (`trending/page.tsx:40-45`); `role="listitem"` on `<button>` (`SuggestionChips.tsx:29`); card Enter triggers a copy (`MemeCard.tsx:166-169`); search textarea `disabled` while loading, so focus is lost (`SearchInput.tsx:65`) | `aria-pressed` toggles; `<li>` wrappers; `readOnly` | Medium |
| A11Y-05 | AI alt text (§1) | Partially implemented | Vite uses `alt_text \|\| name`; apps/web `alt={meme.name}` only | Use `alt_text` everywhere; backfill ([07](07-data-corpus-pipeline-gaps.md) DATA-07) | Medium |
| A11Y-06 | `prefers-reduced-motion` (§5) | Not implemented | No query anywhere; canvas particles (`Canvas3DBackground.tsx:120`, `landing.html:~993-1030`), Framer Motion, `animate-float` | Guard all animation | Medium |
| A11Y-07 | Contrast ≥ 4.5:1 | ASSUMPTION – needs runtime validation | `text-neutral-600` on `neutral-950` in counters and the footer | axe/Lighthouse audit; fix the tokens | Medium |
| A11Y-08 | Automated a11y tests | Partially implemented | Vitest a11y tests exist in `frontend/src/tests/*`; none for apps/web; not in active CI | Add `jest-axe`/Playwright-axe to CI | Medium |

## Responsive design
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| RWD-01 | Mobile navigation (`Styling_System.md`, `upgraded_docs/10` §3) | Partially implemented | Vite: one breakpoint (`index.css:780`, 900px) hides `.sidebar` with no replacement, so history is unreachable on mobile; `landing.html:634-646` hides nav links with no hamburger; apps/web Sidebar `hidden lg:flex` (`Sidebar.tsx:36`) | Mobile drawer / bottom nav; add a 480px tier | High |
| RWD-02 | Consistent grids + 44px tap targets | Needs improvement | `SearchResults.tsx:29` `md:grid-cols-2` vs `sm:grid-cols-2` elsewhere; 4 `text-xs py-1.5` action buttons | Align breakpoints; min 44×44 targets | Medium |
| RWD-03 | Styling system adherence | Needs improvement | Vite uses heavy inline styles vs the documented token system | Move to CSS variables/Tailwind tokens | Low |

## UX
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| UX-01 | Friendly empty/error states | Partially implemented | See [13](13-user-workflow-gaps.md) WF-12 | — | High |
| UX-02 | Honest marketing copy | Incorrectly implemented | "5,000+ memes indexed" vs 145 actual | Live stats | High |
| UX-03 | Consistent visual identity across apps | Needs improvement | Vite and Next have different styles for the same components | Shared design tokens after D-1 | Low |
