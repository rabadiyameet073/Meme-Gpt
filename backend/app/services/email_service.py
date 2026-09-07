"""
MemeGPT Transactional Email Service
Powered by Resend API.
"""
import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger("memegpt.email")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "MemeGPT <notifications@memegpt.com>")


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    if not RESEND_API_KEY or "your_resend_key" in RESEND_API_KEY:
        logger.info(f"RESEND_API_KEY not configured. Email to {to_email} skipped in local mode.")
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


async def send_welcome_email(to_email: str, username: str) -> bool:
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
