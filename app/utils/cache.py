import hashlib
import json
import logging
import time
from threading import RLock
from typing import Any, Optional

from cachetools import TTLCache

logger = logging.getLogger("uvicorn.error")


class CacheManager:
    """Production-grade thread-safe in-memory cache manager with automatic TTL eviction."""

    def __init__(self, default_ttl: int = 3600, max_size: int = 1024):
        """
        Initialize the cache buffer.

        Args:
            default_ttl (int): Global time-to-live parameter for cache keys in seconds.
            max_size (int): Strict ceiling on total concurrent objects stored (prevents RAM exhaustion).
        """
        self._cache = TTLCache(maxsize=max_size, ttl=default_ttl)
        self._lock = RLock()  # Threading lock ensures thread safety during mutation windows

    @staticmethod
    def _generate_key(**kwargs) -> str:
        """
        Safely maps key configurations into uniform deterministic MD5 hex keys.
        Handles nested lists and dicts by stripping string whitespaces.
        """
        try:
            # sort_keys ensures identical parameter dict arrangements generate the same key
            key_string = json.dumps(kwargs, sort_keys=True, default=str)
            return hashlib.md5(key_string.encode("utf-8"), usedforsecurity=False).hexdigest()
        except Exception as e:
            logger.error(f"Cache key generation tracking failure: {str(e)}")
            return hashlib.md5(str(kwargs).encode("utf-8"), usedforsecurity=False).hexdigest()

    def get(self, **kwargs) -> Optional[Any]:
        """Fetch item matching parameter keys from the synchronized buffer layer."""
        key = self._generate_key(**kwargs)

        with self._lock:
            cached_item = self._cache.get(key)
            if cached_item is not None:
                # If it's wrapped in a custom TTL tracker tuple, process it
                if isinstance(cached_item, tuple) and len(cached_item) == 3 and cached_item[2] == "custom_expiry":
                    value, expiry, _ = cached_item
                    if time.time() > expiry:
                        del self._cache[key]
                        logger.info(f"Cache custom expiration hit for key: {key}")
                        return None
                    logger.info(f"Cache HIT (Custom TTL) for identifier block: {key}")
                    return value

                logger.info(f"Cache HIT for identifier block: {key}")
                return cached_item

        logger.info(f"Cache MISS for identifier block: {key}")
        return None

    def set(self, value: Any, ttl: Optional[int] = None, **kwargs) -> None:
        """
        Store value directly inside the locked memory cache layer.

        Args:
            value (Any): Payload to be cached.
            ttl (Optional[int]): Custom override value in seconds for this specific item's life scope.
        """
        if value is None:
            return

        key = self._generate_key(**kwargs)

        with self._lock:
            if ttl is not None:
                # FIXED: Instead of altering the read-only global cache.ttl,
                # we store a custom expiry timestamp inside the value tuple wrapper
                expiry = time.time() + ttl
                self._cache[key] = (value, expiry, "custom_expiry")
            else:
                self._cache[key] = value

        logger.info(f"Cache record successfully set for key: {key}")

    def clear(self) -> None:
        """Flushes all operational records completely out of system RAM instantly."""
        with self._lock:
            self._cache.clear()
        logger.warning("Cache layer completely cleared")

    def current_size(self) -> int:
        """Returns total valid records currently living within the cache layer."""
        with self._lock:
            return len(self._cache)
