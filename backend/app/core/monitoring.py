"""
MemeGPT Observability & Monitoring
Initializes Sentry SDK with FastAPI, SQLAlchemy, and Redis integrations.
"""
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from app.config import settings

logger = logging.getLogger("memegpt.monitoring")


def filter_transactions(event, hint):
    """Exclude frequent health check pings from consuming Sentry transaction quota."""
    url = event.get("transaction", "")
    if "/health" in url or "/favicon.ico" in url:
        return None
    return event


def init_monitoring():
    dsn = getattr(settings, "SENTRY_DSN", "")
    if not dsn or "xxxxxxxx" in dsn:
        logger.info("SENTRY_DSN not configured — skipping Sentry initialization.")
        return

    try:
        integrations = [
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ]
        try:
            from sentry_sdk.integrations.redis import RedisIntegration
            integrations.append(RedisIntegration())
        except Exception:
            pass

        sentry_sdk.init(
            dsn=dsn,
            environment=getattr(settings, "APP_ENV", "development"),
            traces_sample_rate=0.2 if getattr(settings, "APP_ENV", "development") == "production" else 1.0,
            profiles_sample_rate=0.1 if getattr(settings, "APP_ENV", "development") == "production" else 0.0,
            integrations=integrations,
            before_send_transaction=filter_transactions,
        )
        logger.info(f"Sentry initialized in environment: {getattr(settings, 'APP_ENV', 'development')}")
    except Exception as e:
        logger.warning(f"Sentry initialization skipped: {e}")
