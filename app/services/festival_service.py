import logging
from typing import Dict, List, Optional

from app.config import get_settings
from app.core.cache import CacheManager
from app.core.scraper import IndianFestivalsScraper

logger = logging.getLogger(__name__)
settings = get_settings()


class FestivalService:
    """Service layer for festival operations."""

    def __init__(self, cache_manager: CacheManager):
        """Initialize festival service."""
        self.cache = cache_manager
        self.settings = settings

    def get_festivals(self, year: int, month: Optional[int] = None) -> Dict[str, List[Dict]]:
        """Get festivals with caching."""
        # Try to get from cache
        cached = self.cache.get(type="festivals", year=year, month=month)
        if cached is not None:
            return cached

        # Fetch from scraper
        try:
            scraper = IndianFestivalsScraper(
                year=year,
                timeout=self.settings.SCRAPER_TIMEOUT
            )
            festivals = scraper.get_festivals(month=month)

            # Cache the result
            self.cache.set(
                festivals,
                ttl=self.settings.CACHE_TTL,
                type="festivals",
                year=year,
                month=month
            )

            return festivals
        except Exception as e:
            logger.error(f"Error fetching festivals: {str(e)}")
            raise

    def get_religious_festivals(
            self,
            year: int,
            month: Optional[int] = None
    ) -> Dict[str, List[Dict]]:

        """Get religious festivals with caching."""
        # Try to get from cache
        cached = self.cache.get(type="religious", year=year, month=month)
        if cached is not None:
            return cached

        # Fetch from scraper
        try:
            scraper = IndianFestivalsScraper(
                year=year,
                timeout=self.settings.SCRAPER_TIMEOUT
            )
            religious_festivals = scraper.get_religious_festivals(month=month)

            # Cache the result
            self.cache.set(
                religious_festivals,
                ttl=self.settings.CACHE_TTL,
                type="religious",
                year=year,
                month=month
            )

            return religious_festivals
        except Exception as e:
            logger.error(f"Error fetching religious festivals: {str(e)}")
            raise
