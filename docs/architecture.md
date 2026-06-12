# System Architecture & Scraper Design

This document details the architectural decisions, pipeline workflows, scraping design, and defense mechanics of the **Indian Festivals API**.

---

## 1. Directory Structure

The project directory structure is designed to isolate concerns, separating routing from core business logic:

```
indian-festivals-api/
├── app/
│   ├── api/
│   │   ├── dependencies.py     # Thread-safe Cache & Service singleton injection
│   │   └── routes.py           # Endpoint declarations and path parameter validation
│   ├── middleware/
│   │   ├── error_handler.py    # Global exception mapping & JSON responses
│   │   └── rate_limiter.py     # Slowapi wrapper with proxy-aware IP resolution
│   ├── models/
│   │   └── schemas.py          # Strict Pydantic v2 payload models
│   ├── services/
│   │   ├── festival_service.py # Core service connecting cache and scraper
│   │   └── scraper.py          # Asynchronous BeautifulSoup HTML parser
│   ├── utils/
│   │   └── cache.py            # Thread-safe TTLCache with MD5 keys
│   ├── config.py               # Settings singleton via pydantic-settings
│   └── main.py                 # FastAPI application instance & initialization
├── docs/                       # Markdown documentation directory
│   ├── api.md
│   ├── cache.md
│   ├── schema.md
│   └── architecture.md
├── tests/
│   └── test_api.py             # Pytest endpoint test suite
├── .env                        # Local configurations (ignored by git)
├── .env.example                # Configuration templates
├── pyproject.toml              # Modern package specifications
└── render.yaml                 # Infrastructure-as-code for Render deployment
```

---

## 2. Scraping Engine & Color Classification

The scraping engine ([`app/services/scraper.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/services/scraper.py)) fetches data dynamically from AstroSage Panchang and parses the HTML response.

### 1. Asynchronous Retrieval
To prevent blocking FastAPI's main ASGI thread pool, the scraper uses `httpx.AsyncClient` inside an asynchronous execution context.

### 2. Table Scraping Workflow
1. The calendar page splits data into 12 tables (one for each month).
2. It locates the table headers `<thead>` to verify the month name (e.g. `"January 2026"`).
3. The scraper loops through each row `<tr>` inside `<tbody>`.
4. It extracts cells `<td>`:
   - Cell 1: Date & Day (e.g., `"14 Wednesday"`).
   - Cell 2: Festival Names.

### 3. Styled Color Classification
To group festivals by religion, AstroSage styles text elements using color styles. The API inspects the HTML child tags (`<a>` or `<b>`) and maps the text's inline CSS color attribute to a religion key:

```python
FESTIVAL_COLORS = {
    "#a60000": "Hindu Festivals",
    "#4A3475": "Government Holidays",
    "#556A21": "Sikh Festivals",
    "#d42426": "Christian Holidays",
    "#008000": "Islamic Holidays"
}
```

*Example Parsing Logic*:
```python
style = tag.get('style', '')  # e.g., "color:#a60000;"
color = style.split(':')[1].strip().split(';')[0].strip()  # Extracts "#a60000"
religion_group = FESTIVAL_COLORS.get(color)
```

---

## 3. Security & Operational Defense

1. **Proxy-Safe Client Identification**:
   In cloud environments (like Render or Heroku), APIs run behind reverse proxies. Checking `request.client.host` would rate-limit the proxy itself instead of the actual client. 
   [`app/middleware/rate_limiter.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/middleware/rate_limiter.py) resolves this by parsing the `X-Forwarded-For` header chain, extracting the first IP address in the chain (the true client's IP).

2. **Global Error Interception**:
   [`app/middleware/error_handler.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/middleware/error_handler.py) overrides default tracebacks:
   - Replaces tracebacks with generic, safe API messages (preventing sensitive system path leaks).
   - Captures client parameters out-of-range (`ValueError`) and returns `400 Bad Request`.
   - Safely logs critical exceptions to standard logging channels for operators.
