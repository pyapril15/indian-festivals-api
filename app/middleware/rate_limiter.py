from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

settings = get_settings()


def rate_limit_key(request: Request) -> str:
    """Generate rate limit key based on IP address."""
    return get_remote_address(request)


# Create rate limiter instance
limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds"]
)


class RateLimiter:
    """Rate limiter wrapper for easy access."""

    def __init__(self):
        self.limiter = limiter

    def get_limiter(self):
        """Get limiter instance."""
        return self.limiter
