from typing import Optional

from fastapi import Path, Query

from app.config import get_settings
from app.core.cache import CacheManager
from app.services.festival_service import FestivalService

settings = get_settings()

# Singleton instances
_cache_manager = None
_festival_service = None


def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(default_ttl=settings.CACHE_TTL)
    return _cache_manager


def get_festival_service() -> FestivalService:
    """Get festival service instance."""
    global _festival_service
    if _festival_service is None:
        cache = get_cache_manager()
        _festival_service = FestivalService(cache_manager=cache)
    return _festival_service


# Path parameters
def year_path(
        year: int = Path(
            ...,
            ge=settings.MIN_YEAR,
            le=settings.MAX_YEAR,
            description="Year for which to fetch festivals",
            example=2025
        )
) -> int:
    """Validate year path parameter."""
    return year


def month_path(
        month: int = Path(
            ...,
            ge=settings.MIN_MONTH,
            le=settings.MAX_MONTH,
            description="Month number (1-12)",
            example=1
        )
) -> int:
    """Validate month path parameter."""
    return month


# Query parameters
def month_query(
        month: Optional[int] = Query(
            None,
            ge=settings.MIN_MONTH,
            le=settings.MAX_MONTH,
            description="Optional month filter (1-12)",
            example=1
        )
) -> Optional[int]:
    """Validate month query parameter."""
    return month
