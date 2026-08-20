"""Webhook API Endpoints for MemeGPT.
Specification: 07_APIs/Webhooks.md
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field, HttpUrl

from app.core.auth import require_auth, AuthContext, optional_auth
from app.services.webhook_service import (
    register_webhook,
    list_webhooks,
    delete_webhook,
    dispatch_webhook_event,
    get_supported_webhook_events,
)

logger = logging.getLogger("memegpt.api.webhooks")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class WebhookRegistrationRequest(BaseModel):
    url: str = Field(..., description="Webhook destination URL (https recommended)")
    events: List[str] = Field(..., description="List of events to subscribe to (e.g. meme.trending, meme.new)")
    secret: str = Field(..., min_length=8, description="Secret used for HMAC-SHA256 signature verification")


class WebhookTestDispatchRequest(BaseModel):
    event: str = Field(..., description="Event name to test dispatch")
    data: Dict[str, Any] = Field(default_factory=dict, description="Test payload data")


@router.get("/events", summary="List supported webhook event types")
def list_events():
    """List all supported webhook event types and triggers."""
    return {
        "success": True,
        "events": get_supported_webhook_events(),
    }


@router.post("", summary="Register developer webhook endpoint")
def create_webhook(
    body: WebhookRegistrationRequest,
    auth: AuthContext = Depends(optional_auth),
):
    """Register a new webhook endpoint for developer API subscriptions."""
    owner_id = auth.user_id if (auth and auth.user_id) else ((auth.key_id[:12] if auth.key_id else "anonymous") if auth else "anonymous")
    try:
        wh = register_webhook(
            url=body.url,
            events=body.events,
            secret=body.secret,
            owner_id=owner_id,
        )
        return {
            "success": True,
            "webhook": wh,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", summary="List registered webhooks")
def get_webhooks(
    auth: AuthContext = Depends(optional_auth),
):
    """List all active webhooks registered by this developer/session."""
    owner_id = auth.user_id if (auth and auth.user_id) else (auth.key_id if (auth and auth.key_id) else None)
    webhooks = list_webhooks(owner_id=owner_id)
    return {
        "success": True,
        "webhooks": webhooks,
        "total": len(webhooks),
    }


@router.delete("/{webhook_id}", summary="Delete registered webhook")
def remove_webhook(
    webhook_id: str,
    auth: AuthContext = Depends(optional_auth),
):
    """Unsubscribe and delete a registered webhook."""
    owner_id = auth.user_id if (auth and auth.user_id) else (auth.key_id if (auth and auth.key_id) else None)
    deleted = delete_webhook(webhook_id=webhook_id, owner_id=owner_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")
    return {
        "success": True,
        "deleted_id": webhook_id,
    }


@router.post("/test-dispatch", summary="Simulate webhook event dispatch")
def test_dispatch(
    body: WebhookTestDispatchRequest,
    auth: AuthContext = Depends(optional_auth),
):
    """Simulate dispatching a webhook event to all subscribed endpoints."""
    owner_id = auth.user_id if auth and auth.user_id else None
    dispatched = dispatch_webhook_event(event=body.event, data=body.data, owner_id=owner_id)
    return {
        "success": True,
        "event": body.event,
        "dispatched_count": len(dispatched),
        "deliveries": dispatched,
    }
