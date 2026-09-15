"""
MemeGPT Observability & Monitoring
Initializes Sentry SDK with FastAPI, SQLAlchemy, and Redis integrations.
"""
import logging
from typing import Any, Dict, Optional
from app.config import settings

logger = logging.getLogger("memegpt.monitoring")


def filter_transactions(event: Dict[str, Any], hint: Any = None) -> Optional[Dict[str, Any]]:
    """Exclude frequent health check pings and static favicon requests from consuming Sentry transaction quota."""
    url = event.get("transaction", "") or ""
    if "/health" in url or "/favicon.ico" in url or "health" in url.lower():
        return None
    return event


def init_monitoring():
    """Initializes Sentry SDK if SENTRY_DSN is configured."""
    dsn = getattr(settings, "SENTRY_DSN", "") or ""
    if not dsn or "xxxxxxxx" in dsn:
        logger.info("SENTRY_DSN not configured — skipping Sentry initialization.")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        integrations = [
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ]
        try:
            from sentry_sdk.integrations.redis import RedisIntegration
            integrations.append(RedisIntegration())
        except Exception:
            pass

        env = getattr(settings, "ENVIRONMENT", getattr(settings, "APP_ENV", "development"))
        sentry_sdk.init(
            dsn=dsn,
            environment=env,
            traces_sample_rate=0.2 if env == "production" else 1.0,
            profiles_sample_rate=0.1 if env == "production" else 0.0,
            integrations=integrations,
            before_send_transaction=filter_transactions,
            send_default_pii=False,
        )
        logger.info(f"Sentry initialized in environment: {env}")
    except Exception as e:
        logger.warning(f"Sentry initialization skipped: {e}")


def capture_exception(exc: Exception, **kwargs):
    """Safely capture an unhandled or handled exception to Sentry."""
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(exc, **kwargs)
    except Exception:
        pass


def capture_message(message: str, level: str = "info", **kwargs):
    """Safely capture a custom telemetry message to Sentry."""
    try:
        import sentry_sdk
        sentry_sdk.capture_message(message, level=level, **kwargs)
    except Exception:
        pass
