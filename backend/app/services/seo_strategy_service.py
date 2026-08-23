"""Search Engine Optimization (SEO) Strategy and Structured Data Service for MemeGPT.
Specification: 16_SEO_Marketing/SEO_Strategy.md

Covers:
- Technical SEO Architecture (Next.js 14 metadata, canonicals, OpenGraph, Twitter Cards, robots.txt)
- Individual Meme Page Programmatic SEO & JSON-LD (Schema.org ImageObject) generator
- Dynamic XML Sitemap generator engine
- Core Web Vitals standards & live performance compliance auditor
- Category Landing Pages & Automated LLM Blog Post Content Engine
- Target Keywords Matrix (712,500 total monthly search volume)
- SEO Monitoring Framework & 7 Best Practices
"""

from typing import Any, Dict, List, Optional


# ── 1. Root Layout SEO Metadata ────────────────────────────────────────────────

ROOT_SEO_METADATA = {
    "metadataBase": "https://memegpt.com",
    "title": {
        "default": "MemeGPT — AI Meme Finder & Recommender",
        "template": "%s | MemeGPT",
    },
    "description": (
        "Find the perfect meme for any situation using AI. Type anything — a conversation, "
        "a feeling, a situation — and get instant meme recommendations. Download GIF, PNG, or MP4."
    ),
    "keywords": [
        "AI meme finder", "meme recommender", "meme GPT", "find a meme",
        "meme generator AI", "best meme for situation", "download meme GIF",
        "meme search engine", "funny meme finder", "meme AI tool",
    ],
    "openGraph": {
        "type": "website",
        "locale": "en_US",
        "url": "https://memegpt.com",
        "siteName": "MemeGPT",
        "title": "MemeGPT — Find the Perfect Meme Instantly with AI",
        "description": "AI-powered meme recommendations. Type anything, get the perfect meme.",
        "images": [{"url": "/og-image.jpg", "width": 1200, "height": 630, "alt": "MemeGPT"}],
    },
    "twitter": {
        "card": "summary_large_image",
        "site": "@memegpt",
        "creator": "@memegpt",
        "title": "MemeGPT — AI Meme Finder",
        "description": "Type anything → get the perfect meme. Download as GIF, PNG, or MP4.",
        "images": ["/og-image.jpg"],
    },
    "robots": {
        "index": True,
        "follow": True,
        "googleBot": {"index": True, "follow": True, "max-image-preview": "large", "max-snippet": -1},
    },
    "canonical": "https://memegpt.com",
    "viewport": {
        "themeColor": "#7C3AED",
        "width": "device-width",
        "initialScale": 1.0,
    },
}


# ── 2. Core Web Vitals Benchmarks ─────────────────────────────────────────────

CORE_WEB_VITALS = [
    {"metric": "LCP", "name": "Largest Contentful Paint", "target": "< 2.5s", "target_ms": 2500, "implementation": "Next.js Image component with CDN WebP thumbnails"},
    {"metric": "FID", "name": "First Input Delay", "target": "< 100ms", "target_ms": 100, "implementation": "Zero blocking scripts, asynchronous hydration"},
    {"metric": "CLS", "name": "Cumulative Layout Shift", "target": "< 0.1", "target_score": 0.1, "implementation": "Fixed aspect-ratio containers preventing layout shift"},
    {"metric": "TTFB", "name": "Time to First Byte", "target": "< 600ms", "target_ms": 600, "implementation": "Vercel Edge Network global CDN caching"},
    {"metric": "FCP", "name": "First Contentful Paint", "target": "< 1.8s", "target_ms": 1800, "implementation": "Static generation + edge delivery"},
]


# ── 3. Category Landing Pages ─────────────────────────────────────────────────

CATEGORY_LANDING_PAGES = [
    {"title": "Best Work Memes", "url": "/memes/work-memes", "target_keyword": "work memes", "monthly_searches": 12000},
    {"title": "Monday Memes", "url": "/memes/monday-memes", "target_keyword": "monday memes", "monthly_searches": 8000},
    {"title": "Programming Memes", "url": "/memes/programming-memes", "target_keyword": "programmer memes", "monthly_searches": 6000},
    {"title": "Relationship Memes", "url": "/memes/relationship-memes", "target_keyword": "relationship memes", "monthly_searches": 5000},
]


# ── 4. Blog Topic Catalog ─────────────────────────────────────────────────────

BLOG_TOPICS = [
    "Monday Morning", "Work From Home", "Programmer", "Exam Season",
    "Friday Feeling", "Online Gaming", "Relationship", "Cricket Fans",
    "Startup Life", "College Student", "Remote Work", "AI and Tech",
]


# ── 5. Target Keyword Catalog ─────────────────────────────────────────────────

SEO_TARGET_KEYWORDS = [
    {"keyword": "meme generator", "monthly_searches": 450000, "difficulty": "Very High", "strategy": "Blog posts, meme pages"},
    {"keyword": "funny memes 2025", "monthly_searches": 180000, "difficulty": "High", "strategy": "Trending meme pages"},
    {"keyword": "ai meme generator", "monthly_searches": 40000, "difficulty": "Medium", "strategy": "Homepage"},
    {"keyword": "find a meme", "monthly_searches": 22000, "difficulty": "Low", "strategy": "Feature page"},
    {"keyword": "meme gpt", "monthly_searches": 8000, "difficulty": "Very Low", "strategy": "Brand keyword"},
    {"keyword": "download meme gif", "monthly_searches": 6000, "difficulty": "Very Low", "strategy": "Meme pages"},
    {"keyword": "best monday memes", "monthly_searches": 4500, "difficulty": "Low", "strategy": "Blog content"},
    {"keyword": "meme for situation", "monthly_searches": 2000, "difficulty": "Very Low", "strategy": "Homepage copy"},
]


# ── 6. SEO Monitoring Matrix & Best Practices ──────────────────────────────────

SEO_MONITORING = [
    {"metric": "Indexed pages", "tool": "Google Search Console", "frequency": "Weekly", "target": "10,000+ pages"},
    {"metric": "Organic traffic", "tool": "Umami Analytics", "frequency": "Daily", "target": "Growth month-over-month"},
    {"metric": "Core Web Vitals", "tool": "PageSpeed Insights", "frequency": "Monthly", "target": "All green (100% pass)"},
    {"metric": "Keyword rankings", "tool": "Free SERP tracker", "frequency": "Weekly", "target": "Top 10 for brand & long-tail terms"},
    {"metric": "Backlinks & domain authority", "tool": "Google Search Console", "frequency": "Monthly", "target": "Organic editorial backlinks"},
]

SEO_BEST_PRACTICES = [
    {"practice": "Unique metadata per meme", "details": "Every meme page contains unique title, description, and canonical URL."},
    {"practice": "Static Site Generation (SSG)", "details": "Use generateStaticParams to pre-render all 10,000+ meme pages at build time."},
    {"practice": "AI-generated alt text", "details": "Provides accessibility compliance and high ranking in Google Image Search."},
    {"practice": "Compressed OpenGraph cards", "details": "1200x630 images compressed under 200KB for instantaneous social preview rendering."},
    {"practice": "Deep internal linking", "details": "Cross-link individual meme pages with related memes, tags, and category hubs."},
    {"practice": "Permanent immutable URL slugs", "details": "Never mutate or delete URL slugs after initial indexing to preserve backlinks."},
    {"practice": "Search Console sitemap submission", "details": "Submit dynamic XML sitemap within 24 hours of release."},
]


# ── 7. Service Functions ──────────────────────────────────────────────────────

def get_root_seo_metadata() -> Dict[str, Any]:
    """Retrieve root layout SEO metadata specification."""
    return ROOT_SEO_METADATA


def generate_meme_seo_metadata(
    slug: str,
    title: str,
    description: str,
    image_url: str,
    keywords: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Generate Next.js 14 Page metadata for an individual static meme URL."""
    kw_list = keywords or []
    all_keywords = [f"{title} meme", f"{title} gif", f"{title} download", *kw_list, "meme download", "free meme"]

    return {
        "title": f"{title} Meme — Download GIF, PNG, MP4",
        "description": f"{description}. Download the {title} meme as GIF, PNG, or MP4. Free, no watermark.",
        "keywords": all_keywords,
        "openGraph": {
            "title": f"{title} Meme",
            "description": description,
            "images": [{"url": image_url, "width": 800, "height": 600}],
            "type": "article",
        },
        "alternates": {
            "canonical": f"https://memegpt.com/meme/{slug}",
        },
    }


def generate_meme_jsonld(
    slug: str,
    name: str,
    description: str,
    image_url: str,
    thumb_url: str,
    keywords: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Generate Schema.org ImageObject JSON-LD structured data."""
    kw_str = ", ".join(keywords) if keywords else f"{name} meme, funny meme"
    return {
        "@context": "https://schema.org",
        "@type": "ImageObject",
        "name": f"{name} Meme",
        "description": description,
        "contentUrl": image_url,
        "thumbnailUrl": thumb_url,
        "url": f"https://memegpt.com/meme/{slug}",
        "keywords": kw_str,
        "creator": {
            "@type": "Organization",
            "name": "MemeGPT",
            "url": "https://memegpt.com",
        },
    }


def generate_xml_sitemap_sample(limit: int = 10) -> Dict[str, Any]:
    """Generate dynamic XML sitemap sample with priority scoring."""
    base_url = "https://memegpt.com"
    static_routes = [
        {"url": f"{base_url}", "changeFrequency": "daily", "priority": 1.0},
        {"url": f"{base_url}/download", "changeFrequency": "weekly", "priority": 0.9},
        {"url": f"{base_url}/features", "changeFrequency": "monthly", "priority": 0.7},
        {"url": f"{base_url}/app", "changeFrequency": "daily", "priority": 0.9},
        {"url": f"{base_url}/app/trending", "changeFrequency": "hourly", "priority": 0.8},
        {"url": f"{base_url}/blog", "changeFrequency": "daily", "priority": 0.8},
    ]

    sample_memes = [
        {"slug": "drake-hotline-bling", "popularity": 0.95},
        {"slug": "distracted-boyfriend", "popularity": 0.92},
        {"slug": "two-buttons", "popularity": 0.88},
        {"slug": "woman-yelling-at-cat", "popularity": 0.85},
        {"slug": "expanding-brain", "popularity": 0.82},
    ][:limit]

    dynamic_routes = [
        {
            "url": f"{base_url}/meme/{m['slug']}",
            "changeFrequency": "monthly",
            "priority": round(min(0.9, 0.5 + m["popularity"] * 0.4), 2),
        }
        for m in sample_memes
    ]

    return {
        "sitemap_url": f"{base_url}/sitemap.xml",
        "total_static_routes": len(static_routes),
        "total_dynamic_sample_routes": len(dynamic_routes),
        "routes": [*static_routes, *dynamic_routes],
    }


def get_robots_txt_rules() -> Dict[str, Any]:
    """Retrieve robots.txt crawler configuration."""
    return {
        "sitemap": "https://memegpt.com/sitemap.xml",
        "rules": [
            {"user_agent": "*", "allow": "/"},
            {"user_agent": "*", "disallow": ["/api/", "/app/library", "/_next/"]},
        ],
    }


def get_core_web_vitals_benchmarks() -> Dict[str, Any]:
    """Retrieve Core Web Vitals targets."""
    return {
        "total_metrics": len(CORE_WEB_VITALS),
        "metrics": CORE_WEB_VITALS,
    }


def get_seo_category_pages() -> Dict[str, Any]:
    """Retrieve curated category landing pages."""
    return {
        "total_categories": len(CATEGORY_LANDING_PAGES),
        "categories": CATEGORY_LANDING_PAGES,
    }


def generate_seo_blog_post_outline(topic: str) -> Dict[str, Any]:
    """Generate SEO blog post outline and structure for automated content generation."""
    topic_clean = topic.strip()
    return {
        "target_topic": topic_clean,
        "title": f"Top 20 {topic_clean} Memes of This Week",
        "target_keyword": f"{topic_clean.lower()} memes",
        "structure": [
            {"section": "Introduction", "word_count": "~300 words", "tone": "Funny, relatable, internet-native"},
            {"section": "20 Meme Breakdowns", "format": "Meme Name + Why It's Funny + When To Use It", "items": 20},
            {"section": "Conclusion & CTA", "cta": "Try MemeGPT to find memes instantly for any situation"},
        ],
    }


def get_seo_target_keywords() -> Dict[str, Any]:
    """Retrieve target keywords with search volumes and strategies."""
    total_searches = sum(k["monthly_searches"] for k in SEO_TARGET_KEYWORDS)
    return {
        "total_keywords": len(SEO_TARGET_KEYWORDS),
        "aggregate_monthly_search_volume": total_searches,
        "keywords": SEO_TARGET_KEYWORDS,
    }


def get_seo_monitoring_matrix() -> Dict[str, Any]:
    """Retrieve SEO tracking cadence."""
    return {
        "total_monitors": len(SEO_MONITORING),
        "monitors": SEO_MONITORING,
    }


def get_seo_best_practices() -> Dict[str, Any]:
    """Retrieve 7 SEO best practices."""
    return {
        "total_practices": len(SEO_BEST_PRACTICES),
        "practices": SEO_BEST_PRACTICES,
    }


def audit_core_web_vitals_compliance(
    lcp_ms: float,
    fid_ms: float,
    cls_score: float,
    ttfb_ms: float,
    fcp_ms: float,
) -> Dict[str, Any]:
    """Audit live client performance against Google Core Web Vitals ranking criteria."""
    lcp_pass = lcp_ms <= 2500
    fid_pass = fid_ms <= 100
    cls_pass = cls_score <= 0.1
    ttfb_pass = ttfb_ms <= 600
    fcp_pass = fcp_ms <= 1800

    all_passed = lcp_pass and fid_pass and cls_pass and ttfb_pass and fcp_pass

    return {
        "verdict": "PASSED_GREEN" if all_passed else "NEEDS_OPTIMIZATION",
        "scores": {
            "lcp": {"value_ms": lcp_ms, "target_ms": 2500, "status": "PASS" if lcp_pass else "FAIL"},
            "fid": {"value_ms": fid_ms, "target_ms": 100, "status": "PASS" if fid_pass else "FAIL"},
            "cls": {"score": cls_score, "target_score": 0.1, "status": "PASS" if cls_pass else "FAIL"},
            "ttfb": {"value_ms": ttfb_ms, "target_ms": 600, "status": "PASS" if ttfb_pass else "FAIL"},
            "fcp": {"value_ms": fcp_ms, "target_ms": 1800, "status": "PASS" if fcp_pass else "FAIL"},
        },
    }
