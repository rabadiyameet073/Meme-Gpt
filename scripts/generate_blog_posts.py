"""
Blog integrity check for the MemeGPT web app.

The blog used to be generated twice: this script wrote markdown files into
``apps/web/content/blog`` while the Next.js app hard-coded its own posts in
``app/(marketing)/blog/[slug]/page.tsx`` and advertised a third list from the
sitemap. Nothing ever read the markdown, so the two sets drifted — the sitemap
claimed six posts, three of which rendered an invented placeholder article.

Blog content now lives in exactly two places, and this script is the gate that
keeps them identical:

  apps/web/lib/blog.ts                          -> BLOG_POSTS (title, date, slug)
  apps/web/app/(marketing)/blog/[slug]/page.tsx -> POSTS (rendered body)

Run it locally with ``python scripts/generate_blog_posts.py``; CI runs it as
part of the SEO checks. It exits non-zero on any drift, so a post can never be
listed without a body again.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "apps" / "web"
MANIFEST = WEB_DIR / "lib" / "blog.ts"
POST_PAGE = WEB_DIR / "app" / "(marketing)" / "blog" / "[slug]" / "page.tsx"
SITEMAP = WEB_DIR / "app" / "sitemap.ts"

# ``    slug: 'how-ai-...',`` inside BLOG_POSTS
MANIFEST_ENTRY = re.compile(
    r"slug:\s*'(?P<slug>[a-z0-9-]+)',\s*\n\s*title:\s*'(?P<title>[^']*)'"
    r"[\s\S]*?date:\s*'(?P<date>[^']*)'",
)
# ``  'how-ai-...': {``  (two-space indent = a POSTS key)
PAGE_ENTRY = re.compile(r"^  '(?P<slug>[a-z0-9-]+)': \{", re.MULTILINE)
PAGE_TITLE = re.compile(r"^\s{4}title: '(?P<title>[^']*)'", re.MULTILINE)
PAGE_DATE = re.compile(r"^\s{4}date: '(?P<date>[^']*)'", re.MULTILINE)


def _manifest_posts() -> dict[str, dict[str, str]]:
    text = MANIFEST.read_text(encoding="utf-8")
    return {
        match.group("slug"): {"title": match.group("title"), "date": match.group("date")}
        for match in MANIFEST_ENTRY.finditer(text)
    }


def _page_posts() -> dict[str, dict[str, str]]:
    """Map each POSTS key to the title/date declared inside its body."""
    text = POST_PAGE.read_text(encoding="utf-8")
    keys = list(PAGE_ENTRY.finditer(text))
    posts: dict[str, dict[str, str]] = {}
    for index, key in enumerate(keys):
        start = key.end()
        end = keys[index + 1].start() if index + 1 < len(keys) else len(text)
        body = text[start:end]
        title = PAGE_TITLE.search(body)
        date = PAGE_DATE.search(body)
        posts[key.group("slug")] = {
            "title": title.group("title") if title else "",
            "date": date.group("date") if date else "",
        }
    return posts


def _check_sitemap(problems: list[str]) -> None:
    text = SITEMAP.read_text(encoding="utf-8")
    if "lib/blog" not in text or "BLOG_POSTS" not in text:
        problems.append(
            "sitemap.ts must derive blog URLs from lib/blog.ts BLOG_POSTS, "
            "otherwise it advertises pages that do not exist"
        )


def _report(problems: list[str]) -> int:
    if not problems:
        return 0
    print("[FAIL] Blog manifest drift detected:", file=sys.stderr)
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    return 1


def main() -> int:
    manifest = _manifest_posts()
    pages = _page_posts()
    problems: list[str] = []

    if not manifest:
        problems.append(f"no posts found in {MANIFEST.relative_to(ROOT_DIR)}")
    if not pages:
        problems.append(f"no POSTS entries found in {POST_PAGE.relative_to(ROOT_DIR)}")

    for slug in sorted(set(manifest) - set(pages)):
        problems.append(f"{slug}: listed in BLOG_POSTS but has no rendered body")

    for slug in sorted(set(pages) - set(manifest)):
        problems.append(f"{slug}: has a body but is missing from BLOG_POSTS")

    for slug in sorted(set(manifest) & set(pages)):
        for field in ("title", "date"):
            listed = manifest[slug][field]
            rendered = pages[slug][field]
            if listed != rendered:
                problems.append(
                    f"{slug}: {field} differs between manifest ({listed!r}) "
                    f"and rendered post ({rendered!r})"
                )

    _check_sitemap(problems)

    if problems:
        return _report(problems)

    print(f"[OK] {len(manifest)} blog posts are consistent across manifest, page and sitemap:")
    for slug in sorted(manifest):
        print(f"     /blog/{slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
