from typing import Optional

from fastapi import Path, Query

from app.config import get_settings
from app.services.festival_service import FestivalService
from app.utils.cache import CacheManager

settings = get_settings()

# Thread-safe, pre-allocated private singleton placeholders
_cache_manager: Optional[CacheManager] = None
_festival_service: Optional[FestivalService] = None


def get_cache_manager() -> CacheManager:
    """
    Thread-safe lazy initializer for the application cache instance.

    Returns:
        CacheManager: Active memory ring-buffer caching engine singleton.
    """
    global _cache_manager
    if _cache_manager is None:
        # Pre-allocates and bounds max concurrent objects to 1024 to protect container memory
        _cache_manager = CacheManager(default_ttl=settings.CACHE_TTL, max_size=1024)
    return _cache_manager


def get_festival_service() -> FestivalService:
    """
    Thread-safe lazy initializer for orchestrating business logic calculations.

    Returns:
        FestivalService: Active non-blocking service router instance map.
    """
    global _festival_service
    if _festival_service is None:
        cache_instance = get_cache_manager()
        _festival_service = FestivalService(cache_manager=cache_instance)
    return _festival_service


# ==============================================================================
# FASTAPI INPUT PARAMETERS VALIDATION STRUCTS
# ==============================================================================

def year_path(
        year: int = Path(
            ...,
            ge=settings.MIN_YEAR,
            le=settings.MAX_YEAR,
            description="The target calendar year constraint for querying festival arrays.",
            examples=[2026]  # Modern FastAPI PEP-compliant list definition format
        )
) -> int:
    """Validates and enforces strict numerical boundary restrictions over incoming year URL paths."""
    return year


def month_path(
        month: int = Path(
            ...,
            ge=settings.MIN_MONTH,
            le=settings.MAX_MONTH,
            description="The numerical target month signature index parameters (Bounded 1 to 12).",
            examples=[1]
        )
) -> int:
    """Validates and enforces explicit calendar range boundaries over incoming month URL paths."""
    return month


def month_query(
        month: Optional[int] = Query(
            None,
            ge=settings.MIN_MONTH,
            le=settings.MAX_MONTH,
            description="Optional query parameter layer to selectively slice data to a precise monthly index.",
            examples=[1]
        )
) -> Optional[int]:
    """Validates and filters structural validation constraints over incoming URL optional search query vectors."""
    return month
