"""
MemeGPT — Dynamic Sitemap & SEO Generator.
Serves /sitemap.xml listing all meme pages.
Also serves /robots.txt and /meme/{slug}/og for crawler link previews.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db, Meme
from app.config import settings

logger = logging.getLogger("memegpt.sitemap")
router = APIRouter(tags=["SEO"])

APP_BASE = getattr(settings, "APP_BASE_URL", "https://app.memegpt.com")


@router.get("/sitemap.xml", response_class=Response, include_in_schema=False)
def get_sitemap(db: Session = Depends(get_db)):
    """Generate XML sitemap for all meme pages."""
    try:
        memes = db.query(Meme).with_entities(Meme.slug, Meme.updated_at).all()
    except Exception:
        memes = []

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url_entries = []

    # Static pages
    static_pages = [
        ("", "1.0", "daily"),
        ("trending", "0.8", "hourly"),
        ("categories", "0.7", "daily"),
        ("favorites", "0.6", "weekly"),
    ]
    for path, priority, changefreq in static_pages:
        url = f"{APP_BASE}/{path}".rstrip("/")
        url_entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    # Meme pages
    for slug, updated_at in memes:
        if not slug:
            continue
        lastmod = updated_at.strftime("%Y-%m-%d") if updated_at else today
        url = f"{APP_BASE}/meme/{slug}"
        url_entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(url_entries)}
</urlset>"""

    return Response(
        content=xml,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/robots.txt", response_class=Response, include_in_schema=False)
def get_robots():
    """Serve robots.txt from backend."""
    content = f"""User-agent: *
Allow: /

Disallow: /api/
Disallow: /admin/
Disallow: /api/v1/

Sitemap: {APP_BASE}/sitemap.xml
Crawl-delay: 1
"""
    return Response(content=content, media_type="text/plain")


@router.get("/meme/{slug}/og", include_in_schema=False)
def get_meme_og_html(slug: str, db: Session = Depends(get_db)):
    """
    Returns an HTML page with full OG/Twitter meta tags for a meme.
    Used by social media crawlers for rich link previews.
    """
    meme = db.query(Meme).filter(Meme.slug == slug).first()

    if not meme:
        return Response(status_code=404, content="Meme not found", media_type="text/plain")

    image_url = meme.thumb_url or meme.image_url or meme.image_ref or ""
    title = f"{meme.name} — MemeGPT"
    description = meme.explanation or f"Find the perfect meme for any situation with MemeGPT AI"
    page_url = f"{APP_BASE}/meme/{slug}"

    keywords = meme.keywords_list() if hasattr(meme, "keywords_list") else []

    schema = f"""{{
    "@context": "https://schema.org",
    "@type": "ImageObject",
    "name": "{meme.name}",
    "description": "{description[:200]}",
    "contentUrl": "{image_url}",
    "url": "{page_url}",
    "creator": {{"@type": "Organization", "name": "MemeGPT"}}
  }}"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>

  <!-- Primary Meta -->
  <title>{title}</title>
  <meta name="description" content="{description[:160]}"/>
  <meta name="keywords" content="{', '.join(keywords)}"/>
  <link rel="canonical" href="{page_url}"/>

  <!-- Open Graph -->
  <meta property="og:type" content="website"/>
  <meta property="og:url" content="{page_url}"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{description[:160]}"/>
  <meta property="og:image" content="{image_url}"/>
  <meta property="og:image:width" content="1200"/>
  <meta property="og:image:height" content="630"/>
  <meta property="og:site_name" content="MemeGPT"/>
  <meta property="og:locale" content="en_US"/>

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:site" content="@memegpt"/>
  <meta name="twitter:title" content="{title}"/>
  <meta name="twitter:description" content="{description[:160]}"/>
  <meta name="twitter:image" content="{image_url}"/>

  <!-- Schema.org -->
  <script type="application/ld+json">{schema}</script>

  <!-- Redirect to SPA for human users -->
  <meta http-equiv="refresh" content="0;url={page_url}"/>
</head>
<body>
  <h1>{meme.name}</h1>
  <img src="{image_url}" alt="{meme.name}"/>
  <p>{description}</p>
  <a href="{APP_BASE}">More memes on MemeGPT</a>
</body>
</html>"""

    return Response(
        content=html,
        media_type="text/html",
        headers={"Cache-Control": "public, max-age=86400"},
    )
