# Caching Architecture

The Indian Festivals API uses a production-grade, thread-safe, in-memory caching system to optimize performance, minimize external network requests, and prevent API rate-limiting from upstream providers.

---

## 1. Core Caching Engine

The cache is managed by the `CacheManager` class in [`app/utils/cache.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/utils/cache.py). It is built on top of the `cachetools.TTLCache` library.

### Key Characteristics
* **Size Bounded**: The cache has a maximum capacity of `1024` items by default (configurable via `max_size`). This bounds RAM consumption and prevents container memory exhaustion.
* **TTL Eviction**: Cached items automatically expire and are evicted after a time-to-live (TTL) threshold (default: 1 hour / 3600 seconds).
* **Thread Safety**: All read and write operations are synchronized using a `threading.RLock` (Reentrant Lock) to ensure safe access in concurrent multi-threaded execution environments (e.g., Uvicorn workers).

---

## 2. Key Generation

Cache keys are generated deterministically using the parameters passed to the `get` or `set` calls. 

```python
key_string = json.dumps(kwargs, sort_keys=True, default=str)
return hashlib.md5(key_string.encode("utf-8"), usedforsecurity=False).hexdigest()
```

1. **Serialization**: Query parameters (e.g., `type`, `year`, `month`) are serialized to a JSON string.
2. **Determinism**: Keys are sorted (`sort_keys=True`) so that parameters in any order produce the identical key.
3. **Hashing**: The serialized string is hashed using MD5 to produce a uniform 32-character hexadecimal key.

---

## 3. Custom Time-To-Live (TTL) Overrides

While the global cache operates on a default TTL, the `CacheManager` supports item-level custom TTL overrides. 

### How Custom TTL Works
When an item is stored with a specific `ttl`:
1. It calculates the absolute expiration timestamp (`time.time() + ttl`).
2. It wraps the payload, the expiration timestamp, and a verification flag inside a 3-tuple:
   `self._cache[key] = (value, expiry, "custom_expiry")`
3. Upon retrieval, if the 3-tuple is present and has the `"custom_expiry"` flag:
   - It checks if the current time exceeds the expiration timestamp.
   - If expired, it evicts the item from the cache and returns `None`.
   - If valid, it returns the unwrapped value payload.

---

## 4. API Usage Example

The service layer [`FestivalService`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/services/festival_service.py) interacts with the cache seamlessly:

```python
# 1. Generate parameters
cache_params = {"type": "festivals", "year": 2026, "month": 1}

# 2. Try fetching from cache
cached = self.cache.get(**cache_params)
if cached is not None:
    return cached

# 3. If Cache Miss, fetch from source
festivals = await scraper.get_festivals(month=1)

# 4. Save to cache
self.cache.set(value=festivals, ttl=3600, **cache_params)
```

---

## 5. Operations & Administration

The cache can be managed using the following methods:
* **`clear()`**: Instantly flushes all records from system memory.
* **`current_size()`**: Returns the count of active cached objects.
