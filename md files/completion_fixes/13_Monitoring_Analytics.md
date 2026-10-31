# 13 — Monitoring, Observability & Analytics Guide
> Setup Sentry error tracking, Umami privacy-friendly analytics, Resend email, and uptime monitoring.

---

## Problem Statement

The production requirements in `01_PRODUCT_AND_FEATURES.md` and `05_SEO_DEPLOYMENT_AND_LAUNCH.md` require:
1. **Error Tracking**: Sentry monitoring for FastAPI backend, Next.js web app, and Expo mobile app.
2. **Web Analytics**: Self-hosted or privacy-first Umami analytics (zero cookie banners needed).
3. **Transactional Email**: Resend API integration for account alerts, magic links, and collection sharing.
4. **Uptime & Health Checks**: 99.5% uptime monitoring with automated ping and alert channels.

---

## Step 1: Complete Backend Sentry Integration

### 1.1 Configure `backend/app/core/monitoring.py`

**File:** `backend/app/core/monitoring.py`

```python
"""
MemeGPT Observability & Monitoring
Initializes Sentry SDK with FastAPI, SQLAlchemy, and Redis integrations.
"""
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from app.core.config import settings

logger = logging.getLogger("memegpt.monitoring")

def init_monitoring():
    if not settings.SENTRY_DSN:
        logger.info("SENTRY_DSN not configured — skipping Sentry initialization.")
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.2 if settings.ENVIRONMENT == "production" else 1.0,
        profiles_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 0.0,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
        # Filter out noisy endpoints
        before_send_transaction=filter_transactions,
    )
    logger.info(f"Sentry initialized in environment: {settings.ENVIRONMENT}")

def filter_transactions(event, hint):
    """Exclude frequent health check pings from consuming Sentry transaction quota."""
    url = event.get("transaction", "")
    if "/health" in url or "/favicon.ico" in url:
        return None
    return event
```

Call `init_monitoring()` inside `backend/app/main.py` before application startup.

---

## Step 2: Umami Analytics Setup

### 2.1 Next.js Web App Integration (`apps/web`)

Add the Umami script to `apps/web/app/layout.tsx`:

```tsx
// In apps/web/app/layout.tsx
import Script from 'next/script';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const umamiWebsiteId = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID;
  const umamiHostUrl = process.env.NEXT_PUBLIC_UMAMI_HOST_URL || "https://analytics.umami.is/script.js";

  return (
    <html lang="en">
      <head>
        {umamiWebsiteId && (
          <Script
            src={umamiHostUrl}
            data-website-id={umamiWebsiteId}
            strategy="afterInteractive"
          />
        )}
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### 2.2 Vite SPA Integration (`frontend/`)

In `frontend/index.html`:

```html
<!-- Inside <head> -->
<script
  defer
  src="%VITE_UMAMI_HOST_URL%"
  data-website-id="%VITE_UMAMI_WEBSITE_ID%"
></script>
```

### 2.3 Custom Event Tracking Utility

**File:** `apps/web/lib/analytics.ts` and `frontend/src/lib/analytics.ts`:

```typescript
export function trackEvent(eventName: string, data?: Record<string, any>) {
  if (typeof window !== 'undefined' && (window as any).umami) {
    (window as any).umami.track(eventName, data);
  }
}

// Usage examples:
// trackEvent('meme_search', { query: 'boss friday', format: 'gif' });
// trackEvent('meme_download', { meme_slug: 'drake-pointing', format: 'mp4' });
// trackEvent('meme_share', { meme_slug: 'drake-pointing', channel: 'whatsapp' });
```

---

## Step 3: Resend Transactional Email Service

### 3.1 Backend Integration (`backend/app/services/email_service.py`)

**File:** `backend/app/services/email_service.py`

```python
"""
MemeGPT Transactional Email Service
Powered by Resend (3,000 free emails/month).
"""
import os
import httpx
import logging
from typing import Optional, Dict

logger = logging.getLogger("memegpt.email")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "MemeGPT <notifications@memegpt.com>")

async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set. Email not sent.")
        return False

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Resend error ({resp.status_code}): {resp.text}")
                return False
    except Exception as e:
        logger.exception(f"Failed to send email to {to_email}: {e}")
        return False

async def send_welcome_email(to_email: str, username: str):
    subject = "Welcome to MemeGPT — Your AI Meme Secret Weapon"
    html = f"""
    <div style="font-family: sans-serif; background-color: #0f172a; color: #f8fafc; padding: 24px; border-radius: 12px;">
      <h1 style="color: #a855f7;">Welcome to MemeGPT, {username}!</h1>
      <p style="font-size: 16px; line-height: 1.5;">
        You are now equipped to discover the perfect reaction meme in under 1.5 seconds.
      </p>
      <ul style="line-height: 1.8;">
        <li>🔍 Search by situation, conversation snippet, or emotional vibe</li>
        <li>💾 Download high-res GIF, PNG, WebP, or MP4</li>
        <li>📁 Organize favorites into shareable collections</li>
      </ul>
      <a href="https://memegpt.com/app" style="display: inline-block; background-color: #7c3aed; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 16px;">
        Start Searching Memes →
      </a>
    </div>
    """
    return await send_email(to_email, subject, html)
```

---

## Step 4: Uptime Monitoring & Heartbeats

### 4.1 Setup Better Stack / UptimeRobot Ping

1. Create a monitor on [Better Stack](https://betterstack.com) or [UptimeRobot](https://uptimerobot.com) (free tiers).
2. Monitor URL: `https://api.memegpt.com/api/v1/health`
3. Interval: **1 minute**
4. Expected HTTP Status: **200 OK**
5. Expected response contains: `"status": "ok"` or `"status": "healthy"`

### 4.2 GitHub Actions Scheduled Heartbeat

If third-party pingers are unavailable, the existing [.github/workflows/health_check.yml](file:///d:/Meme%20GPT/.github/workflows/health_check.yml) executes a 15-minute cron ping to both the API and Web App.

---

## Step 5: Verification Checklist

- [ ] Trigger an intentional exception in a test endpoint and confirm it appears in your Sentry dashboard.
- [ ] Inspect network tab on web app and confirm `https://analytics.umami.is/api/send` fires with page views and events.
- [ ] Send a test email using `send_welcome_email` and verify delivery in your inbox.
- [ ] Query `/api/v1/health` and verify all subsystems report healthy.
