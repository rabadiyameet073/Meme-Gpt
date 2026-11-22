# 13 — User Workflow Gaps (end-to-end feature flows)

**Source requirements:** `md files/documentation/08_Features/*` (Smart_Search, Chat_Refinement, Suggestion_Chips, Favorites_Collections, Copy_Download, Share_Feature, Multi_Format, Trending_System), `md files/documentation/00_Project_Overview/Product_Workflow.md`, `md files/project-vision/01-vision-product.md`
**Related:** [12-frontend-web-gaps](12-frontend-web-gaps.md) · [05-trending-feedback-gaps](05-trending-feedback-gaps.md) · [03-search-api-gaps](03-search-api-gaps.md)

Status per workflow, as it currently works in **Vite** (`frontend/`) and **Next** (`apps/web/`):

| Workflow (vision priority) | Vite | Next | Overall |
|---|---|---|---|
| Smart search (P0) | ✅ | ✅ (contract bugs) | Partially implemented |
| Emotion detection (P0) | ✅ backend | ✅ backend | Fully implemented |
| Multi-format (P0) | ✅ | ⚠️ no WebP | Partially implemented |
| Copy / download (P0) | ✅ | ⚠️ | Partially implemented |
| Trending (P0) | ✅ | ⚠️ client-only, dev-text empty state | Partially implemented (backend scoring faked: [05](05-trending-feedback-gaps.md)) |
| Suggestion chips (P0) | ⚠️ static | ⚠️ static | Partially implemented |
| Feedback voting (P0) | ✅ | ⚠️ double-counted | Partially implemented |
| Favorites / collections (P1) | ✅ | ❌ can't save | Partially implemented |
| Accounts (P1) | ✅ (localStorage tokens) | ❌ | Partially implemented |
| Chat refinement (P2) | ✅ | ❌ | Partially implemented |
| Share with attribution | ⚠️ | ⚠️ | Partially implemented |
| Reverse image search (P2) | ❌ | ❌ | Not implemented |

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| WF-01 | Chat refinement (`Chat_Refinement.md`) | Partially implemented | Vite `ChatTab.tsx:57,76,278-335` calls `/v1/chat/refine`; none in apps/web; sessions are in-memory on the server (`_CHAT_SESSIONS`) and lost on restart | One surface; sessions in Redis; `aria-live` transcript; verify ordinal references ("the third one") (ASSUMPTION) | High |
| WF-02 | Dynamic, time-aware chips (`Suggestion_Chips.md:38-45`) | Partially implemented | Hardcoded lists in `frontend/src/components/SuggestionChips.tsx:14-23` and `apps/web/components/search/SuggestionChips.tsx:9-16`; backend `GET /chips/suggestions` (`suggestion_chips.py:19`) is never called | Fetch from the API with a static fallback | Medium |
| WF-03 | Chip label ≠ query (`Suggestion_Chips.md:27-36`) | Incorrectly implemented (apps/web) | The emoji label is sent as the query | `{label, query}` pairs | Low |
| WF-04 | Save to favorites (`Favorites_Collections.md`) | Not implemented (apps/web) | No save button; nothing writes `memegpt_saved_memes`, so `library/page.tsx:15,20` is always empty | Save + collection picker | Critical (if apps/web stays user-facing) |
| WF-05 | Recently Viewed (20) / Recently Copied (10) (`Favorites_Collections.md:70-74`) | Partially implemented | `frontend/src/lib/storage.ts:186` `recordRecentView` has no callers, so `FavoritesTab.tsx:120-136` stays empty | Call it from card, preview and detail | High |
| WF-06 | Favorites edge cases (`:80-85`): quota full, 200 cap, dedupe, collection delete → move to Favorites | Partially implemented | Quota warning and delete-migration not found (ASSUMPTION) | Implement + unit tests | Medium |
| WF-07 | Copy copies the image (`Copy_Download.md:13-48`) | Partially implemented | `MemeDetailClient.tsx:33` copies the page URL; GIF `ClipboardItem` falls back to the URL | PNG blob copy; GIF→PNG conversion | Medium |
| WF-08 | Download without redirect, filename `{slug}.{format}` | Incorrectly implemented | `useDownload.ts:27-31` cross-origin `<a download target=_blank>` is ignored by browsers; the backend redirects (ASSUMPTION – runtime) | `Content-Disposition` from the API or a same-origin proxy | Medium |
| WF-09 | Each signal recorded once with the real session | Incorrectly implemented | Double sends + `'anonymous'` session (see [05](05-trending-feedback-gaps.md) FB-04) | Fix | High |
| WF-10 | Share with `?ref=` attribution (`Share_Feature.md:24-33`) | Partially implemented | Both apps share `window.location.href`; backend `/share`, `/share/url/{slug}`, `/share/og` are unused | Use `/api/v1/share` | Medium |
| WF-11 | WebP + platform hints (`Multi_Format.md:9-22`) | Partially implemented | apps/web `FormatSelector.tsx:12-15` offers GIF/Image/Video only | Add WebP + hints | Low |
| WF-12 | No-results and error states (`Product_Workflow.md`) | Partially implemented | `SearchResults.tsx:43` returns `null`; trending empty state shows `python scripts/download_datasets.py` (`trending/page.tsx:86-91`) | User-facing empty states | High |
| WF-13 | Anonymous-first, no account required (vision §1.2) | Fully implemented | Search, trending and copy work without login | — | — |
| WF-14 | Server-side favorites sync for logged-in users | Partially implemented | `/favorites` endpoints exist; Vite favorites are localStorage only (ASSUMPTION – verify merge on login) | Merge local → server on login | Medium |
