import logging

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_ipaddr

from app.config import get_settings

# Connect to core system output streams
logger = logging.getLogger("uvicorn.error")
settings = get_settings()


def production_rate_limit_key(request: Request) -> str:
    """
    Production-hardened rate limiting key generator.
    Safely inspects X-Forwarded-For proxy headers injected by Render's routing layers.
    """
    # 1. Look for the X-Forwarded-For header chain injected by the cloud proxy
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        # The first element in the comma-separated chain is the true client origin IP
        client_ip = forwarded_for.split(",")[0].strip()
        logger.debug(f"Rate limiting key resolved via proxy context: {client_ip}")
        return client_ip

    # 2. Local Fallback: If no proxy header exists, fall back to base client host socket mapping
    fallback_ip = get_ipaddr(request) or "127.0.0.1"
    logger.debug(f"Rate limiting key resolved via direct socket address: {fallback_ip}")
    return fallback_ip


# Create and pre-configure the unified global Limiter instance
# Explicitly uses the production-ready string format layout matching Pydantic metrics
limiter = Limiter(
    key_func=production_rate_limit_key,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds"]
)


class RateLimiter:
    """Production wrapper providing decoupled utility access to the application limiter instance."""

    def __init__(self):
        self._limiter = limiter

    def get_limiter(self) -> Limiter:
        """Returns the fully initialized, isolated global rate limiter container instance."""
        return self._limiter
