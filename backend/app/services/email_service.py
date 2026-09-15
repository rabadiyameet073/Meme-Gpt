"""
MemeGPT Transactional Email Service
Powered by Resend API (3,000 free emails/month).
"""
import os
import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger("memegpt.email")


def get_resend_api_key() -> str:
    return os.getenv("RESEND_API_KEY") or getattr(settings, "RESEND_API_KEY", "") or ""


def get_from_email() -> str:
    return os.getenv("RESEND_FROM_EMAIL") or getattr(settings, "RESEND_FROM_EMAIL", "MemeGPT <notifications@memegpt.com>")


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    api_key = get_resend_api_key()
    if not api_key or "your_resend_key" in api_key:
        logger.info(f"RESEND_API_KEY not configured. Email to {to_email} skipped in local/dev mode.")
        return False

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": get_from_email(),
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


async def send_collection_share_email(to_email: str, sender_name: str, collection_name: str, share_url: str) -> bool:
    subject = f"{sender_name} shared a meme collection with you: '{collection_name}'"
    html = f"""
    <div style="font-family: sans-serif; background-color: #0f172a; color: #f8fafc; padding: 24px; border-radius: 12px;">
      <h1 style="color: #a855f7;">New Shared Collection</h1>
      <p style="font-size: 16px; line-height: 1.5;">
        <strong>{sender_name}</strong> has shared their meme collection <em>"{collection_name}"</em> with you!
      </p>
      <p style="margin-top: 16px;">
        <a href="{share_url}" style="display: inline-block; background-color: #7c3aed; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
          View Collection →
        </a>
      </p>
    </div>
    """
    return await send_email(to_email, subject, html)


async def send_magic_link_email(to_email: str, magic_link: str) -> bool:
    subject = "Sign in to MemeGPT — Your Magic Link"
    html = f"""
    <div style="font-family: sans-serif; background-color: #0f172a; color: #f8fafc; padding: 24px; border-radius: 12px;">
      <h1 style="color: #a855f7;">Sign in to MemeGPT</h1>
      <p style="font-size: 16px; line-height: 1.5;">
        Click the button below to sign in directly to your MemeGPT account. This link expires in 15 minutes.
      </p>
      <a href="{magic_link}" style="display: inline-block; background-color: #7c3aed; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 16px;">
        Sign In Now →
      </a>
    </div>
    """
    return await send_email(to_email, subject, html)


async def send_account_alert_email(to_email: str, alert_title: str, alert_message: str) -> bool:
    subject = f"MemeGPT Security Alert: {alert_title}"
    html = f"""
    <div style="font-family: sans-serif; background-color: #0f172a; color: #f8fafc; padding: 24px; border-radius: 12px;">
      <h1 style="color: #f43f5e;">Security Alert: {alert_title}</h1>
      <p style="font-size: 16px; line-height: 1.5;">
        {alert_message}
      </p>
      <p style="font-size: 14px; color: #94a3b8; margin-top: 20px;">
        If you did not perform this action, please reset your password immediately or contact support.
      </p>
    </div>
    """
    return await send_email(to_email, subject, html)
