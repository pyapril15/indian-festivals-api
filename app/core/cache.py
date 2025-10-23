import hashlib
import json
import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """In-memory cache manager with TTL support."""

    def __init__(self, default_ttl: int = 3600):
        """Initialize cache with default TTL."""
        self._cache = {}
        self.default_ttl = default_ttl

    @staticmethod
    def _generate_key(**kwargs) -> str:
        """Generate cache key from parameters."""
        key_string = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, **kwargs) -> Optional[Any]:
        """Get value from cache."""
        key = self._generate_key(**kwargs)

        if key in self._cache:
            value, expiry = self._cache[key]

            # Check if cache entry is still valid
            if time.time() < expiry:
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                # Remove expired entry
                del self._cache[key]
                logger.debug(f"Cache expired for key: {key}")

        logger.debug(f"Cache miss for key: {key}")
        return None

    def set(self, value: Any, ttl: Optional[int] = None, **kwargs) -> None:
        """Set value in cache with TTL."""
        key = self._generate_key(**kwargs)
        expiry = time.time() + (ttl or self.default_ttl)
        self._cache[key] = (value, expiry)
        logger.debug(f"Cache set for key: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time >= expiry
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)
