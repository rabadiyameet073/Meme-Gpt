"""
MemeGPT Transactional Email API Router
Specification: 13_Monitoring_Analytics.md
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.email_service import (
    send_email,
    send_welcome_email,
    send_collection_share_email,
    send_magic_link_email,
    send_account_alert_email,
)

logger = logging.getLogger("memegpt.api.email")
router = APIRouter(prefix="/email", tags=["Transactional Email"])


class WelcomeEmailRequest(BaseModel):
    email: str = Field(..., description="Recipient email address")
    username: str = Field(..., description="Username or display name")


class ShareCollectionEmailRequest(BaseModel):
    to_email: str = Field(..., description="Recipient email address")
    sender_name: str = Field(..., description="Name of sender sharing the collection")
    collection_name: str = Field(..., description="Name of the collection being shared")
    share_url: str = Field(..., description="Attributed URL to view the collection")


class MagicLinkEmailRequest(BaseModel):
    to_email: str = Field(..., description="Recipient email address")
    magic_link: str = Field(..., description="Passwordless login URL")


class AlertEmailRequest(BaseModel):
    to_email: str = Field(..., description="Recipient email address")
    alert_title: str = Field(..., description="Short security or account alert title")
    alert_message: str = Field(..., description="Detailed alert message")


class GenericEmailRequest(BaseModel):
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field("MemeGPT Notification", description="Subject line")
    html_content: str = Field(..., description="HTML email body")


@router.post("/welcome", summary="Send welcome email")
async def api_send_welcome_email(req: WelcomeEmailRequest):
    """Sends new user welcome email via Resend."""
    sent = await send_welcome_email(req.email, req.username)
    return {
        "success": True,
        "delivered": sent,
        "message": "Welcome email dispatched" if sent else "Email skipped (RESEND_API_KEY optional in dev)",
        "recipient": req.email,
    }


@router.post("/share-collection", summary="Send collection share notification")
async def api_send_collection_share_email(req: ShareCollectionEmailRequest):
    """Sends shared collection notification email to recipient."""
    sent = await send_collection_share_email(
        to_email=req.to_email,
        sender_name=req.sender_name,
        collection_name=req.collection_name,
        share_url=req.share_url,
    )
    return {
        "success": True,
        "delivered": sent,
        "message": "Share notification dispatched" if sent else "Email skipped (RESEND_API_KEY optional in dev)",
        "recipient": req.to_email,
    }


@router.post("/magic-link", summary="Send magic login link email")
async def api_send_magic_link_email(req: MagicLinkEmailRequest):
    """Sends passwordless magic authentication link email."""
    sent = await send_magic_link_email(req.to_email, req.magic_link)
    return {
        "success": True,
        "delivered": sent,
        "message": "Magic link dispatched" if sent else "Email skipped (RESEND_API_KEY optional in dev)",
        "recipient": req.to_email,
    }


@router.post("/alert", summary="Send account or security alert email")
async def api_send_alert_email(req: AlertEmailRequest):
    """Sends account or security alert email."""
    sent = await send_account_alert_email(req.to_email, req.alert_title, req.alert_message)
    return {
        "success": True,
        "delivered": sent,
        "message": "Security alert dispatched" if sent else "Email skipped (RESEND_API_KEY optional in dev)",
        "recipient": req.to_email,
    }


@router.post("/test", summary="Send custom test email")
async def api_send_test_email(req: GenericEmailRequest):
    """Sends test email with custom subject and HTML content."""
    sent = await send_email(req.to_email, req.subject, req.html_content)
    return {
        "success": True,
        "delivered": sent,
        "message": "Test email dispatched" if sent else "Email skipped (RESEND_API_KEY optional in dev)",
        "recipient": req.to_email,
    }
