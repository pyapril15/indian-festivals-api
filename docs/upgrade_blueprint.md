# Upgrade Blueprint: Migrating from 1.0.0 to 1.0.1

This document outlines the design decisions and architectural upgrades implemented in **version 1.0.1** to improve the performance, reliability, and security of the Indian Festivals API compared to the legacy version **1.0.0**.

---

## 🛠️ Detailed Migration Breakdown

### 1. Swapped pip & venv for uv (Package Infrastructure)
* **What changed**: Migrated environment and package specifications from standard `requirements.txt` and virtual environments to a modern `pyproject.toml` file managed entirely by **[uv](https://github.com/astral-sh/uv)** (a high-performance, Rust-based package manager).
* **Why it matters**: Dependency resolution and environments are now synchronized deterministically in milliseconds. Production deployments on Render use `uv sync --frozen --no-dev` for fast, reproducible builds.

---

### 2. Upgraded to fully Asynchronous I/O (The Engine)
* **What changed**: Removed the synchronous `requests` library completely and refactored [`app/services/scraper.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/services/scraper.py), [`app/services/festival_service.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/services/festival_service.py), and endpoint routes to use native, non-blocking `async/await` syntax with `httpx.AsyncClient`.
* **Why it matters**: In version 1.0.0, the entire web server would block (freeze) while waiting for AstroSage to respond to HTTP requests. In version 1.0.1, the API server handles incoming requests concurrently without thread contention.

---

### 3. Added Thread-Safe, Auto-Expiring Caching (Performance)
* **What changed**: Replaced direct storage calls with a bounded `CacheManager` using `cachetools.TTLCache` (limited to `1024` items to prevent RAM bloat). We fixed custom TTL crashes by wrapping cached payloads inside a 3-tuple format `(value, expiry, "custom_expiry")` to safely store dynamic item-level expirations.
* **Why it matters**: This reduces external scraping operations to zero for active cache keys. Festivals are served instantly out of RAM, dropping response latency from seconds to milliseconds.

---

### 4. Hardened Security & Proxy-Aware Rate Limiting (Defense)
* **What changed**:
  - Replaced socket-based IP mapping with a custom `production_rate_limit_key` that reads the `X-Forwarded-For` proxy headers.
  - Added clean exception handlers mapping `ValueError` and `RequestValidationError` to sanitize public responses.
  - Configured strict, immutable Pydantic models (`frozen=True`, `extra="forbid"`, `str_strip_whitespace=True`).
* **Why it matters**: Rate limiters in version 1.0.0 would mistake reverse proxy hosts (e.g. Render's load balancer) as a single client and block all global users. The new middleware tracks individual visitor IPs safely. Public responses no longer leak stack traces or raw database field names.

---

### 5. Fixed Namespace Shadowing & Incompatibilities (Stability)
* **What changed**:
  - Updated Pydantic/FastAPI JSON schema definitions to use modern, standard PEP examples arrays (`examples=[X]` instead of legacy `example=X`).
  - Resolved middleware exceptions in `slowapi` by explicitly declaring endpoint request signatures (`request: Request`) and using `# noinspection PyUnusedLocal` flags to keep IDE analysis clean.
* **Why it matters**: Eliminates FastAPI startup crashes, guaranteeing the service compiles cleanly across local dev environments (Windows) and production environments (Linux).

---

## 📂 Codebase Checklist Comparison

| File | Legacy State (1.0.0) | Upgraded State (1.0.1) |
| :--- | :--- | :--- |
| [`app/utils/cache.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/utils/cache.py) | Custom TTL overrode read-only global cache properties, causing errors. | Uses 3-tuple payload encapsulation to track custom TTLs independently. |
| [`app/services/scraper.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/services/scraper.py) | Synchronous scraping blocks execution thread. | Fully async requests with connection timeouts using `httpx.AsyncClient`. |
| [`app/services/festival_service.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/services/festival_service.py) | Synchronous scraper calls. | Non-blocking `async/await` service layer coordinating cache and scraper. |
| [`app/models/schemas.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/models/schemas.py) | Mutable models; legacy Pydantic example keywords. | Immutable models (`frozen=True`) with automatic whitespace stripping and standard `examples` arrays. |
| [`app/middleware/rate_limiter.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/middleware/rate_limiter.py) | Standard socket IP limiter with short duration suffix format. | Proxy-aware IP resolver (reads `X-Forwarded-For`) with full `seconds` suffix. |
| [`app/middleware/error_handler.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/middleware/error_handler.py) | Lacked comprehensive ValueError/RequestValidationError intercepts. | Sanitized global JSON exception mappings to prevent internal trace leakages. |
| [`app/api/routes.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/api/routes.py) | Synchronous endpoints; short-suffix rate limit string format causing crashes. | Non-blocking async endpoints decorated with fixed `seconds` rate-limit strings. |
| [`app/api/dependencies.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/api/dependencies.py) | Standard query/path extraction parameters. | Standardized dependencies with bounds validations and lazy-loaded singletons. |
| `API_ENDPOINTS_DOCUMENTATION.txt` | Raw text file at root. | Deleted in favor of a detailed markdown documentation directory. |
| `pyproject.toml` | Lacked dependencies specification. | Modern packaging setup utilizing conditional `uvloop` injections for Linux platforms. |
| `README.md` | Legacy instructions and structure. | Up-to-date documentation indexes, `uv` instructions, and `1.0.1` changelog. |
