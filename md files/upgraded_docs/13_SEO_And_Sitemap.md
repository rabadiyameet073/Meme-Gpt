# 13 — SEO & Sitemap
# robots.txt, sitemap.xml, OG Tags, schema.org

> **Gap Source:** Section 13 of GAP_ANALYSIS_FULL.md  
> **Priority:** P2  
> **Files to create:**  
> - `d:\Meme GPT\frontend\public\robots.txt`  
> - `d:\Meme GPT\backend\app\api\v1\sitemap.py` (dynamic sitemap)  
> - Update `d:\Meme GPT\frontend\index.html` (meta tags)  
> - Update `d:\Meme GPT\backend\app\api\v1\memes.py` (add meta tags endpoint)

---

## WHAT IS MISSING

- No `robots.txt` in frontend/public/
- No sitemap.xml  
- Single shared `<title>` for ALL pages (not per-meme)
- No Open Graph tags
- No Twitter Card tags
- No schema.org ImageObject markup
- App is Vite SPA → no SSR → Google can't crawl meme pages

---

## APPROACH: Hybrid SEO

Since the app is Vite SPA (not Next.js), we use a **hybrid approach**:
1. Static `robots.txt` + `sitemap.xml` served from FastAPI
2. Per-meme OG tags via FastAPI HTML endpoint (for link previews)
3. Default meta tags in `index.html` for the SPA shell

---

## FILE 1 — `robots.txt`

**Create** `d:\Meme GPT\frontend\public\robots.txt`:

```
User-agent: *
Allow: /

# Disallow admin and API paths
Disallow: /api/
Disallow: /admin/
Disallow: /api/v1/

# Sitemap location
Sitemap: https://app.memegpt.com/sitemap.xml

# Crawl rate (optional — reduces server load)
Crawl-delay: 1
```

---

## FILE 2 — Dynamic Sitemap (FastAPI)

**Create** `d:\Meme GPT\backend\app\api\v1\sitemap.py`:

```python
"""
MemeGPT — Dynamic Sitemap Generator.
Serves /sitemap.xml listing all meme pages.
Also serves /robots.txt if not already served by frontend.
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
    memes = db.query(Meme).with_entities(Meme.slug, Meme.updated_at).all()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    url_entries = []

    # Static pages
    static_pages = [
        ("", "1.0", "daily"),
        ("trending", "0.8", "hourly"),
        ("categories", "0.7", "daily"),
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
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(url_entries)}
</urlset>"""

    return Response(
        content=xml,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/robots.txt", response_class=Response, include_in_schema=False)
def get_robots():
    """Serve robots.txt from backend (as fallback)."""
    content = f"""User-agent: *
Allow: /

Disallow: /api/
Disallow: /admin/

Sitemap: {APP_BASE}/sitemap.xml
Crawl-delay: 1
"""
    return Response(content=content, media_type="text/plain")


@router.get("/meme/{slug}/og", include_in_schema=False)
def get_meme_og_html(slug: str, db: Session = Depends(get_db)):
    """
    Returns an HTML page with full OG/Twitter meta tags for a meme.
    Used by social media crawlers (not shown to users — SPA handles UI).

    How to use:
    - Configure Cloudflare or Nginx to serve this for bots (user-agent check)
    - Or use as pre-render service for social link previews
    """
    meme = db.query(Meme).filter(Meme.slug == slug).first()

    if not meme:
        return Response(status_code=404)

    image_url = meme.thumb_url or meme.image_url or meme.image_ref or ""
    title = f"{meme.name} — MemeGPT"
    description = meme.explanation or f"Find the perfect meme for any situation with MemeGPT AI"
    page_url = f"{APP_BASE}/meme/{slug}"

    # Schema.org ImageObject
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
  <meta name="keywords" content="{', '.join(meme.keywords or [])}"/>
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

  <!-- Redirect to SPA after bot crawl -->
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
```

---

## FILE 3 — Update `index.html` Default Meta Tags

Update `d:\Meme GPT\frontend\index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>

  <!-- Primary SEO -->
  <title>MemeGPT — AI-Powered Meme Search Engine</title>
  <meta name="description" content="Find the perfect meme for any situation in seconds using AI. MemeGPT understands context, emotion, and humor to match you with exactly the right meme."/>
  <meta name="keywords" content="meme search, AI meme, meme generator, reaction memes, funny memes"/>

  <!-- Open Graph (default for app root) -->
  <meta property="og:type" content="website"/>
  <meta property="og:url" content="https://app.memegpt.com"/>
  <meta property="og:title" content="MemeGPT — AI-Powered Meme Search"/>
  <meta property="og:description" content="Find the perfect meme for any situation using AI"/>
  <meta property="og:image" content="https://app.memegpt.com/og-preview.jpg"/>
  <meta property="og:site_name" content="MemeGPT"/>

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:site" content="@memegpt"/>
  <meta name="twitter:title" content="MemeGPT — AI Meme Search"/>
  <meta name="twitter:description" content="Find the perfect meme for any situation using AI"/>
  <meta name="twitter:image" content="https://app.memegpt.com/og-preview.jpg"/>

  <!-- PWA -->
  <link rel="manifest" href="/manifest.json"/>
  <meta name="theme-color" content="#7C3AED"/>
  <meta name="apple-mobile-web-app-capable" content="yes"/>
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
  <link rel="apple-touch-icon" href="/icons/icon-192.png"/>

  <!-- Preconnect to CDN -->
  <link rel="preconnect" href="https://cdn.memegpt.com"/>
  <link rel="dns-prefetch" href="https://cdn.memegpt.com"/>

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="/icons/icon-192.png"/>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
```

---

## FILE 4 — Register Sitemap Routes in `main.py`

```python
from app.api.v1.sitemap import router as sitemap_router

# Register at app level (not /api/v1 prefix)
app.include_router(sitemap_router)
```

---

## VERIFICATION

```bash
# Test sitemap
curl http://localhost:8000/sitemap.xml
# Should return XML with all meme URLs

# Test robots.txt
curl http://localhost:8000/robots.txt

# Test meme OG page
curl http://localhost:8000/meme/drake-pointing/og
# Should return HTML with OG meta tags
```
