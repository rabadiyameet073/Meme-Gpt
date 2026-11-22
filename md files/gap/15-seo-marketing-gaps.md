# 15 — SEO, Marketing & ASO Gaps

**Source requirements:** `md files/documentation/16_SEO_Marketing/*` (SEO_Strategy, Marketing_Plan, Launch_Strategy, App_Store_Optimization), `md files/upgraded_docs/13_SEO_And_Sitemap.md`, `17_Landing_Page.md`, v1/v2 `05_*DEPLOYMENT_AND_LAUNCH.md`, `docs/ASO_Store_Listing.md`, `md files/project-vision/05-deploy-security-seo.md`
**Related:** [07-data-corpus-pipeline-gaps](07-data-corpus-pipeline-gaps.md) · [12-frontend-web-gaps](12-frontend-web-gaps.md) · [09-security-gaps](09-security-gaps.md) (SEC-09)

## Verified as implemented
Per-meme `generateMetadata` + OG/Twitter + JSON-LD (`apps/web/app/meme/[slug]/page.tsx:11-104`); `robots.ts` + `sitemap.ts`; 6 static blog posts with a real 404 for unknown slugs (`blog/[slug]/page.tsx:12,447`); blog sitemap entries from `BLOG_POSTS` (`lib/blog.ts`); static OG image; category pages.

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| SEO-01 | 10k+ programmatic meme pages in the sitemap (`SEO_Strategy.md:15,159`) | Incorrectly implemented | `sitemap.ts:18` requests `limit=50000`; the backend clamps to 100 (`memes.py:67`); the corpus is 145 anyway | Paginated slug endpoint + sitemap index (>50k URLs) | Critical |
| SEO-02 | Category hubs in the sitemap (`:226`) | Not implemented | `sitemap.ts:50-58` omits `/memes/[category]` | Add | High |
| SEO-03 | Unknown category → 404 | Incorrectly implemented | `memes.py:77-79` fallback + no `notFound()` in `memes/[category]/page.tsx`, which allows unlimited duplicate pages | Whitelist + `notFound()` | High |
| SEO-04 | Missing meme → 404 | Incorrectly implemented | Soft 404 at `meme/[slug]/page.tsx:47-60` | `notFound()` | High |
| SEO-05 | Canonical URLs (`:69,109,341`) | Not implemented | No `canonical` in `apps/web/app` | `alternates.canonical` | High |
| SEO-06 | robots.txt doesn't block rendering assets (`:174`) | Incorrectly implemented | `robots.ts:7` disallows `/_next/` | Allow `/_next/static`; merge the two rule groups | High |
| SEO-07 | Correct absolute URLs / verification | Incorrectly implemented | `layout.tsx:25` `metadataBase` falls back to `http://localhost:3000`; `:53` fake verification token | Prod fallback; omit the tag when unset | Medium |
| SEO-08 | Structured data completeness | Partially implemented | No BreadcrumbList on category/blog pages; XSS-unsafe JSON-LD (see [09](09-security-gaps.md) SEC-09) | Escape + add schemas | High |
| SEO-09 | Per-meme OG card 1200×630 (`:344`) | Not implemented | No `opengraph-image` route | `opengraph-image.tsx` | Medium |
| SEO-10 | Core Web Vitals: `next/image` (LCP <2.5s) | Partially implemented | Raw `<img>` at `MemeDetailClient.tsx:74`, `memes/[category]/page.tsx:132` (`Image` imported, unused) | `next/image` + `remotePatterns` | Medium |
| SEO-11 | Weekly LLM-written blog (`SEO_Strategy.md:235-239`) | Not implemented | `scripts/generate_blog_posts.py` is only a drift checker; no workflow runs it | Build the generator + review gate, or revise the doc | Medium |
| SEO-12 | One sitemap | Needs improvement | Backend `api/v1/sitemap.py:34-39` lists `/categories` and `/favorites` (no such Next routes) and uses `app.memegpt.com` | Retire the backend sitemap | Low |
| SEO-13 | Consistent ASO listing (`App_Store_Optimization.md`) | Incorrectly implemented | Three different titles/subtitles/categories across `docs/ASO_Store_Listing.md:10`, `aso_service.py:20-26`, `SEO_Strategy.md:285`; keyword "meme generator" is out of scope (vision §1.5) | One listing; drop "meme generator" | Medium |
| SEO-14 | Landing page claims are true (`upgraded_docs/17`) | Incorrectly implemented | "5,000+ memes" (`(marketing)/page.tsx:90,387`) | Live count | High |
| MKT-01 | Launch plan execution (Product Hunt, Reddit, etc., `Launch_Strategy.md`) | Not implemented (out of code scope) | Requires a deployed product ([20](20-ci-cd-deployment-gaps.md)) | Track in the roadmap | Low |
