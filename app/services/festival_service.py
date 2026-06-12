import logging
from typing import Dict, List, Optional

from app.config import get_settings
from app.services.scraper import IndianFestivalsScraper
from app.utils.cache import CacheManager

logger = logging.getLogger("uvicorn.error")
settings = get_settings()


class FestivalService:
    """Production-grade asynchronous service layer for orchestrating cached festival operations."""

    def __init__(self, cache_manager: CacheManager):
        """
        Initialize festival service.

        Args:
            cache_manager (CacheManager): Active thread-safe cache buffer singleton.
        """
        self.cache = cache_manager
        self.settings = settings

    async def get_festivals(self, year: int, month: Optional[int] = None) -> Dict[str, List[Dict]]:
        """
        Retrieves monthly structured festival records from cache or asynchronous live scraper routines.
        """
        cache_params = {"type": "festivals", "year": year, "month": month}

        # 1. Thread-safe internal memory retrieval check
        cached = self.cache.get(**cache_params)
        if cached is not None:
            return cached

        # 2. Asynchronous execution loop if cache layer misses
        try:
            scraper = IndianFestivalsScraper(
                year=year,
                timeout=self.settings.SCRAPER_TIMEOUT
            )
            # Await the async scraper execution non-blockingly
            festivals = await scraper.get_festivals(month=month)

            # 3. Cache the valid returned result dictionary payload object
            if festivals:
                self.cache.set(
                    value=festivals,
                    ttl=self.settings.CACHE_TTL,
                    **cache_params
                )

            return festivals

        except RuntimeError as e:
            logger.error(f"Upstream provider connection termination during metadata parsing: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Uncaught processing failure inside festival pipeline layer: {str(e)}")
            raise RuntimeError("Internal core engine failure processing downstream collection sets.")

    async def get_religious_festivals(
            self,
            year: int,
            month: Optional[int] = None
    ) -> Dict[str, List[Dict]]:
        """
        Retrieves religious grouped collection arrays from cache layers or live processing engines.
        """
        cache_params = {"type": "religious", "year": year, "month": month}

        # 1. Thread-safe internal memory retrieval check
        cached = self.cache.get(**cache_params)
        if cached is not None:
            return cached

        # 2. Asynchronous execution loop if cache layer misses
        try:
            scraper = IndianFestivalsScraper(
                year=year,
                timeout=self.settings.SCRAPER_TIMEOUT
            )
            # Await the async scraper execution non-blockingly
            religious_festivals = await scraper.get_religious_festivals(month=month)

            # 3. Cache the valid returned result dictionary payload object
            if religious_festivals:
                self.cache.set(
                    value=religious_festivals,
                    ttl=self.settings.CACHE_TTL,
                    **cache_params
                )

            return religious_festivals

        except RuntimeError as e:
            logger.error(f"Upstream connection mapping timeout handling religious array sets: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Uncaught processing execution exception inside religious service stream: {str(e)}")
            raise RuntimeError("Internal core engine failure processing downstream collection sets.")
