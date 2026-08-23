"""Marketing & SEO/ASO API Router for MemeGPT.
Specification: 16_SEO_Marketing/App_Store_Optimization.md

Endpoints:
- GET  /api/v1/marketing/aso/ios
- GET  /api/v1/marketing/aso/google-play
- GET  /api/v1/marketing/aso/screenshots
- GET  /api/v1/marketing/aso/keywords
- GET  /api/v1/marketing/aso/ratings
- GET  /api/v1/marketing/aso/practices
- POST /api/v1/marketing/aso/evaluate-rating-prompt
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.aso_service import (
    get_ios_app_store_listing,
    get_google_play_listing,
    get_screenshot_strategy,
    get_keyword_research_matrix,
    get_rating_prompt_strategy,
    get_aso_best_practices,
    evaluate_rating_prompt_eligibility,
)

router = APIRouter(prefix="/marketing", tags=["SEO & Marketing"])


class RatingPromptEvaluationRequest(BaseModel):
    searches_count: int = Field(default=0, ge=0, description="Total successful searches performed by user")
    downloads_count: int = Field(default=0, ge=0, description="Total memes downloaded by user")
    shares_count: int = Field(default=0, ge=0, description="Total memes shared by user")
    days_since_last_prompt: int = Field(default=35, ge=0, description="Days elapsed since the last rating prompt")
    last_action_was_error: bool = Field(default=False, description="Whether the most recent user action resulted in an error")


@router.get("/aso/ios", summary="Get iOS App Store listing metadata")
def get_ios_listing():
    """Retrieve iOS App Store title, subtitle, categories, keywords field, and full description."""
    return {
        "success": True,
        **get_ios_app_store_listing(),
    }


@router.get("/aso/google-play", summary="Get Google Play Store listing metadata")
def get_play_listing():
    """Retrieve Google Play title, short description, category, and tags."""
    return {
        "success": True,
        **get_google_play_listing(),
    }


@router.get("/aso/screenshots", summary="Get 5-screenshot visual strategy")
def get_screenshots():
    """Retrieve screenshot sequence, focal elements, and conversion messages."""
    return {
        "success": True,
        **get_screenshot_strategy(),
    }


@router.get("/aso/keywords", summary="Get ASO keyword research & search volume")
def get_keywords():
    """Retrieve tracked keywords, monthly search volume, competition, and targeting strategy."""
    return {
        "success": True,
        **get_keyword_research_matrix(),
    }


@router.get("/aso/ratings", summary="Get in-app rating prompt strategy")
def get_ratings():
    """Retrieve rating prompt triggers and safety rules."""
    return {
        "success": True,
        **get_rating_prompt_strategy(),
    }


@router.get("/aso/practices", summary="Get 6 ASO best practices")
def get_practices():
    """Retrieve 6 App Store Optimization best practices."""
    return {
        "success": True,
        **get_aso_best_practices(),
    }


@router.post("/aso/evaluate-rating-prompt", summary="Evaluate user rating prompt eligibility")
def check_rating_prompt(body: RatingPromptEvaluationRequest):
    """Evaluate whether client app should trigger an in-app rating prompt based on engagement and cooldown rules."""
    return {
        "success": True,
        **evaluate_rating_prompt_eligibility(
            searches_count=body.searches_count,
            downloads_count=body.downloads_count,
            shares_count=body.shares_count,
            days_since_last_prompt=body.days_since_last_prompt,
            last_action_was_error=body.last_action_was_error,
        ),
    }


# ── Launch Strategy Endpoints (16_SEO_Marketing/Launch_Strategy.md) ──────────

from app.services.launch_strategy_service import (
    get_launch_timeline,
    get_launch_channels,
    get_pre_launch_checklist,
    get_launch_day_schedule,
    get_launch_kpis,
    get_post_launch_priorities,
    evaluate_launch_readiness,
)


class LaunchReadinessRequest(BaseModel):
    checked_items: Optional[List[str]] = Field(default=None, description="List of completed checklist item IDs")


@router.get("/launch/timeline", summary="Get 3-phase launch timeline")
def get_timeline():
    """Retrieve Pre-Launch, Launch Week, and Post-Launch Gantt chart timeline."""
    return {
        "success": True,
        **get_launch_timeline(),
    }


@router.get("/launch/channels", summary="Get 7 launch channel playbooks")
def get_channels():
    """Retrieve actions and expected visitor traffic across Product Hunt, Reddit, Twitter, Hacker News, Dev.to, LinkedIn, Reels."""
    return {
        "success": True,
        **get_launch_channels(),
    }


@router.get("/launch/checklist", summary="Get 18-point pre-launch checklist")
def get_checklist(category: Optional[str] = None):
    """Retrieve pre-launch verification checklist filtered by 'technical', 'content', or 'seo'."""
    return {
        "success": True,
        **get_pre_launch_checklist(category=category),
    }


@router.get("/launch/schedule", summary="Get hour-by-hour launch day schedule")
def get_schedule():
    """Retrieve launch day timetable from 08:00 AM Product Hunt submission to 10:00 PM hotfix review."""
    return {
        "success": True,
        **get_launch_day_schedule(),
    }


@router.get("/launch/kpis", summary="Get launch week KPI benchmark targets")
def get_kpis():
    """Retrieve 7 benchmark launch week success metrics with tracking sources."""
    return {
        "success": True,
        **get_launch_kpis(),
    }


@router.get("/launch/priorities", summary="Get 5 post-launch execution priorities")
def get_priorities():
    """Retrieve Weeks 1-4 post-launch priorities covering bug fixing, feature requests, SEO blog, and indexing."""
    return {
        "success": True,
        **get_post_launch_priorities(),
    }


@router.post("/launch/evaluate-readiness", summary="Evaluate launch readiness gate")
def evaluate_readiness(body: LaunchReadinessRequest):
    """Evaluate pre-launch checklist completion and determine whether all critical gates are satisfied."""
    return {
        "success": True,
        **evaluate_launch_readiness(checked_items=body.checked_items),
    }


# ── Marketing Plan Endpoints (16_SEO_Marketing/Marketing_Plan.md) ───────────

from app.services.marketing_plan_service import (
    get_marketing_funnel,
    get_channel_strategy,
    get_reddit_targets,
    get_product_hunt_playbook,
    get_content_calendar,
    simulate_viral_growth,
)


class ViralGrowthSimulationRequest(BaseModel):
    initial_dau: int = Field(default=100, ge=1, description="Initial baseline DAU count")
    viral_k_factor: float = Field(default=1.15, ge=0.0, description="Viral coefficient / K-factor per user")
    days: int = Field(default=30, ge=1, le=365, description="Number of simulation days")


@router.get("/plan/funnel", summary="Get 4-phase marketing growth funnel")
def get_funnel():
    """Retrieve 4 marketing funnel phases from Soft Launch (100 DAU) to Scaled Growth (50,000 DAU)."""
    return {
        "success": True,
        **get_marketing_funnel(),
    }


@router.get("/plan/channels", summary="Get channel strategy & traffic attribution mix")
def get_channel_mix():
    """Retrieve $0 acquisition budget channel mix: SEO (50%), ASO (25%), Word of Mouth (15%), Content (5%), API (5%)."""
    return {
        "success": True,
        **get_channel_strategy(),
    }


@router.get("/plan/reddit", summary="Get targeted subreddit community matrix")
def get_subreddits():
    """Retrieve 5 key target subreddits with customized post angles and 22.85M combined audience reach."""
    return {
        "success": True,
        **get_reddit_targets(),
    }


@router.get("/plan/product-hunt", summary="Get Product Hunt launch execution playbook")
def get_ph_playbook():
    """Retrieve Product Hunt launch timing (Tuesday), submission assets, response SLA, and Top 5 target."""
    return {
        "success": True,
        **get_product_hunt_playbook(),
    }


@router.get("/plan/content-calendar", summary="Get Month 1 content publishing calendar")
def get_calendar():
    """Retrieve 6 strategic content drops across Reddit, Product Hunt, Twitter, Dev.to, and SEO blog."""
    return {
        "success": True,
        **get_content_calendar(),
    }


@router.post("/plan/simulate-growth", summary="Simulate viral growth trajectory")
def simulate_growth(body: ViralGrowthSimulationRequest):
    """Simulate projected daily active users (DAU) based on initial traffic and viral K-factor sharing loops."""
    return {
        "success": True,
        **simulate_viral_growth(
            initial_dau=body.initial_dau,
            viral_k_factor=body.viral_k_factor,
            days=body.days,
        ),
    }


# ── Manifest & Health Endpoints (16_SEO_Marketing/README.md) ───────────────

from app.services.marketing_manifest_service import (
    get_marketing_section_manifest,
    get_marketing_posture_summary,
    get_marketing_subsystem_health,
)


@router.get("/manifest", summary="Get Section 16S documentation manifest")
def get_manifest():
    """Retrieve complete catalog and navigation metadata for Section 16S (SEO & Marketing)."""
    return {
        "success": True,
        **get_marketing_section_manifest(),
    }


@router.get("/posture", summary="Get consolidated SEO & marketing posture")
def get_posture():
    """Retrieve growth readiness, channel traffic mix, and DAU target milestones."""
    return {
        "success": True,
        **get_marketing_posture_summary(),
    }


@router.get("/health", summary="Get marketing subsystem diagnostic health")
def get_health():
    """Evaluate health and completeness of marketing campaigns, ASO strategies, and growth playbooks."""
    return {
        "success": True,
        **get_marketing_subsystem_health(),
    }


# ── SEO Strategy Endpoints (16_SEO_Marketing/SEO_Strategy.md) ──────────────

from app.services.seo_strategy_service import (
    get_root_seo_metadata,
    generate_meme_seo_metadata,
    generate_meme_jsonld,
    generate_xml_sitemap_sample,
    get_robots_txt_rules,
    get_core_web_vitals_benchmarks,
    get_seo_category_pages,
    generate_seo_blog_post_outline,
    get_seo_target_keywords,
    get_seo_monitoring_matrix,
    get_seo_best_practices,
    audit_core_web_vitals_compliance,
)


class MemeMetadataGenerationRequest(BaseModel):
    slug: str = Field(..., description="Unique meme URL slug")
    title: str = Field(..., description="Meme name or title")
    description: str = Field(..., description="Meme description")
    image_url: str = Field(..., description="Meme full-resolution image URL")
    keywords: Optional[List[str]] = Field(default=None, description="Custom keyword tags")


class MemeJsonLdGenerationRequest(BaseModel):
    slug: str = Field(..., description="Unique meme URL slug")
    name: str = Field(..., description="Meme name")
    description: str = Field(..., description="Meme description")
    image_url: str = Field(..., description="Meme full-resolution image URL")
    thumb_url: str = Field(..., description="Meme thumbnail URL")
    keywords: Optional[List[str]] = Field(default=None, description="Custom keyword tags")


class BlogPostOutlineRequest(BaseModel):
    topic: str = Field(..., description="Topic for weekly automated SEO blog post")


class CoreWebVitalsAuditRequest(BaseModel):
    lcp_ms: float = Field(..., ge=0, description="Largest Contentful Paint (ms)")
    fid_ms: float = Field(..., ge=0, description="First Input Delay (ms)")
    cls_score: float = Field(..., ge=0, description="Cumulative Layout Shift score")
    ttfb_ms: float = Field(..., ge=0, description="Time to First Byte (ms)")
    fcp_ms: float = Field(..., ge=0, description="First Contentful Paint (ms)")


@router.get("/seo/root-metadata", summary="Get root layout SEO metadata")
def get_root_metadata():
    """Retrieve Next.js 14 root metadata configuration."""
    return {
        "success": True,
        **get_root_seo_metadata(),
    }


@router.get("/seo/robots", summary="Get robots.txt crawler configuration")
def get_robots():
    """Retrieve robots.txt crawler rules and sitemap location."""
    return {
        "success": True,
        **get_robots_txt_rules(),
    }


@router.get("/seo/sitemap", summary="Get XML sitemap sample routes")
def get_sitemap(limit: int = 10):
    """Retrieve static and dynamic meme sitemap entries with priority scores."""
    return {
        "success": True,
        **generate_xml_sitemap_sample(limit=limit),
    }


@router.get("/seo/web-vitals", summary="Get Core Web Vitals benchmark standards")
def get_web_vitals():
    """Retrieve Google Core Web Vitals thresholds (LCP < 2.5s, FID < 100ms, CLS < 0.1, TTFB < 600ms, FCP < 1.8s)."""
    return {
        "success": True,
        **get_core_web_vitals_benchmarks(),
    }


@router.get("/seo/categories", summary="Get curated category landing pages")
def get_categories():
    """Retrieve category landing pages (Work Memes, Monday Memes, Programming Memes, Relationship Memes)."""
    return {
        "success": True,
        **get_seo_category_pages(),
    }


@router.get("/seo/keywords", summary="Get target SEO keywords & monthly search volume")
def get_seo_keywords():
    """Retrieve 8 target SEO keywords with 712,500 aggregate monthly searches."""
    return {
        "success": True,
        **get_seo_target_keywords(),
    }


@router.get("/seo/monitoring", summary="Get SEO monitoring matrix")
def get_monitoring():
    """Retrieve weekly and monthly SEO KPI monitoring cadence."""
    return {
        "success": True,
        **get_seo_monitoring_matrix(),
    }


@router.get("/seo/practices", summary="Get 7 SEO best practices")
def get_seo_practices():
    """Retrieve 7 SEO architectural best practices."""
    return {
        "success": True,
        **get_seo_best_practices(),
    }


@router.post("/seo/generate-meme-metadata", summary="Generate Next.js page metadata for individual meme")
def generate_metadata(body: MemeMetadataGenerationRequest):
    """Generate dynamic Next.js 14 Page metadata including title, description, OpenGraph, and canonical URL."""
    return {
        "success": True,
        "metadata": generate_meme_seo_metadata(
            slug=body.slug,
            title=body.title,
            description=body.description,
            image_url=body.image_url,
            keywords=body.keywords,
        ),
    }


@router.post("/seo/generate-jsonld", summary="Generate Schema.org ImageObject JSON-LD")
def generate_jsonld(body: MemeJsonLdGenerationRequest):
    """Generate Schema.org ImageObject structured data markup for rich snippet display in Google."""
    return {
        "success": True,
        "jsonld": generate_meme_jsonld(
            slug=body.slug,
            name=body.name,
            description=body.description,
            image_url=body.image_url,
            thumb_url=body.thumb_url,
            keywords=body.keywords,
        ),
    }


@router.post("/seo/generate-blog-outline", summary="Generate automated SEO blog post outline")
def generate_blog_outline(body: BlogPostOutlineRequest):
    """Generate weekly SEO listicle outline targeting long-tail meme queries."""
    return {
        "success": True,
        **generate_seo_blog_post_outline(topic=body.topic),
    }


@router.post("/seo/audit-web-vitals", summary="Audit Core Web Vitals performance compliance")
def audit_vitals(body: CoreWebVitalsAuditRequest):
    """Audit live client Core Web Vitals metrics against Google ranking thresholds."""
    return {
        "success": True,
        **audit_core_web_vitals_compliance(
            lcp_ms=body.lcp_ms,
            fid_ms=body.fid_ms,
            cls_score=body.cls_score,
            ttfb_ms=body.ttfb_ms,
            fcp_ms=body.fcp_ms,
        ),
    }
