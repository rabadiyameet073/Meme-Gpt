"""Webhook Service for MemeGPT — registration, HMAC-SHA256 signature signing and verification, and event dispatching.
Specification: 07_APIs/Webhooks.md
"""

import hashlib
import hmac
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("memegpt.services.webhooks")

SUPPORTED_WEBHOOK_EVENTS = {
    "meme.trending": "Meme enters top-20 trending",
    "meme.new": "New meme indexed in database",
    "search.popular": "Query searched >100 times/day",
    "collection.updated": "Trending collection refreshed",
}

RETRY_SCHEDULE_SECONDS = [5, 30, 300]  # 3 retries with exponential backoff
DELIVERY_TIMEOUT_SECONDS = 10  # 10s response timeout

# In-memory store for registered webhooks (keyed by webhook_id)
_WEBHOOKS_DB: Dict[str, Dict[str, Any]] = {}


def get_supported_webhook_events() -> Dict[str, str]:
    """Return dictionary of supported webhook event types and descriptions."""
    return SUPPORTED_WEBHOOK_EVENTS.copy()


def generate_webhook_signature(payload_data: Dict[str, Any], secret: str) -> str:
    """Generate HMAC-SHA256 signature string in 'sha256=<hex_digest>' format."""
    canonical_json = json.dumps(payload_data, sort_keys=True, separators=(",", ":"))
    digest = hmac.new(
        key=secret.encode("utf-8"),
        msg=canonical_json.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
    return f"sha256={digest}"


def verify_webhook_signature(payload_data: Dict[str, Any], secret: str, signature_header: str) -> bool:
    """Verify HMAC-SHA256 signature using constant-time comparison."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    
    expected_sig = generate_webhook_signature(payload_data, secret)
    return hmac.compare_digest(expected_sig, signature_header)


def register_webhook(
    url: str,
    events: List[str],
    secret: str,
    owner_id: str = "anonymous",
) -> Dict[str, Any]:
    """Register a new developer webhook endpoint."""
    if not url.startswith(("http://", "https://")):
        raise ValueError("Invalid webhook URL. Must start with http:// or https://")

    # Validate event subscriptions
    for event in events:
        if event not in SUPPORTED_WEBHOOK_EVENTS:
            raise ValueError(f"Unsupported event '{event}'. Valid events: {list(SUPPORTED_WEBHOOK_EVENTS.keys())}")

    webhook_id = f"wh_{uuid.uuid4().hex[:12]}"
    record = {
        "id": webhook_id,
        "url": url,
        "events": events,
        "secret": secret,
        "owner_id": owner_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
    }
    _WEBHOOKS_DB[webhook_id] = record
    return {k: v for k, v in record.items() if k != "secret"}


def list_webhooks(owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List registered webhooks, optionally filtered by owner_id."""
    results = []
    for wh in _WEBHOOKS_DB.values():
        if owner_id is None or wh.get("owner_id") == owner_id:
            results.append({k: v for k, v in wh.items() if k != "secret"})
    return results


def delete_webhook(webhook_id: str, owner_id: Optional[str] = None) -> bool:
    """Delete a registered webhook by ID."""
    wh = _WEBHOOKS_DB.get(webhook_id)
    if not wh:
        return False
    if owner_id and wh.get("owner_id") != owner_id:
        return False
    del _WEBHOOKS_DB[webhook_id]
    return True


def create_webhook_payload(event: str, data: Dict[str, Any], secret: str) -> Dict[str, Any]:
    """Construct complete webhook payload with timestamp and signature."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raw_payload = {
        "event": event,
        "timestamp": timestamp,
        "data": data,
    }
    signature = generate_webhook_signature(raw_payload, secret)
    return {
        **raw_payload,
        "signature": signature,
    }


def dispatch_webhook_event(
    event: str,
    data: Dict[str, Any],
    owner_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Simulate asynchronous event dispatching to all subscribers of this event."""
    dispatched = []
    for wh in _WEBHOOKS_DB.values():
        if not wh.get("active", True):
            continue
        if owner_id and wh.get("owner_id") != owner_id:
            continue
        if event in wh.get("events", []):
            payload = create_webhook_payload(event=event, data=data, secret=wh["secret"])
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": payload["signature"],
                "X-Webhook-Event": event,
            }
            dispatched.append({
                "webhook_id": wh["id"],
                "url": wh["url"],
                "event": event,
                "payload": payload,
                "headers": headers,
                "retry_schedule_seconds": RETRY_SCHEDULE_SECONDS,
                "timeout_seconds": DELIVERY_TIMEOUT_SECONDS,
                "status": "delivered",
            })
    return dispatched
