# API Endpoint Documentation

This document describes all available endpoints for the **Indian Festivals API**, including request parameters, sample requests/responses, rate limits, and client implementation examples.

---

## 1. Base URL

* **Local Development**: `http://localhost:8000`
* **Production**: `https://your-app-name.onrender.com` (CORS-enabled origins apply)
* **Interactive Docs**: `/docs` (Swagger UI) or `/redoc` (ReDoc) — *visible when `DEBUG=True`*

---

## 2. API Endpoints

### 1. Root Endpoint
Returns a welcome message and basic API status information.

* **URL**: `/`
* **Method**: `GET`
* **Query Parameters**: None
* **Sample Request**:
  ```bash
  curl http://localhost:8000/
  ```
* **Sample Response (200 OK)**:
  ```json
  {
    "message": "Welcome to Indian Festivals API",
    "version": "1.0.1",
    "status": "operational"
  }
  ```

---

### 2. Infrastructure Health Check
Returns the current health status of the application. Used by container platforms like Render for liveness/readiness probes.

* **URL**: `/health`
* **Method**: `GET`
* **Query Parameters**: None
* **Sample Request**:
  ```bash
  curl http://localhost:8000/health
  ```
* **Sample Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-06-12T13:42:21Z",
    "version": "1.0.1"
  }
  ```

---

### 3. Get All Festivals for a Year
Retrieves Indian festivals, holidays, and celebrations for a specific year, optionally filtered by month.

* **URL**: `/api/v1/festivals/{year}`
* **Method**: `GET`
* **Path Parameters**:
  - `year` *(integer, required)*: Year constraint (between `1900` and `2100`).
* **Query Parameters**:
  - `month` *(integer, optional)*: Month index (between `1` and `12`) to filter results.
* **Sample Request 1**: (Get all festivals for 2026)
  ```bash
  curl http://localhost:8000/api/v1/festivals/2026
  ```
* **Sample Response (200 OK)**:
  ```json
  {
    "year": 2026,
    "month": null,
    "festivals": {
      "January": [
        {
          "date": "1",
          "day": "Thursday",
          "name": "New Year"
        },
        {
          "date": "14",
          "day": "Wednesday",
          "name": "Pongal, Uttarayan, Makar Sankranti"
        }
      ],
      "February": [
        {
          "date": "19",
          "day": "Thursday",
          "name": "Maha Shivratri"
        }
      ]
    }
  }
  ```
* **Sample Request 2**: (Get January 2026 festivals via query parameter)
  ```bash
  curl http://localhost:8000/api/v1/festivals/2026?month=1
  ```
* **Sample Response (200 OK)**:
  ```json
  {
    "year": 2026,
    "month": 1,
    "festivals": {
      "January": [
        {
          "date": "1",
          "day": "Thursday",
          "name": "New Year"
        }
      ]
    }
  }
  ```

---

### 4. Get Festivals by Specific Month
Retrieves Indian festivals for a specific year and month using path parameters.

* **URL**: `/api/v1/festivals/{year}/month/{month}`
* **Method**: `GET`
* **Path Parameters**:
  - `year` *(integer, required)*: Year constraint (between `1900` and `2100`).
  - `month` *(integer, required)*: Month index (between `1` and `12`).
* **Sample Request**:
  ```bash
  curl http://localhost:8000/api/v1/festivals/2026/month/1
  ```
* **Sample Response (200 OK)**:
  *(Same format as Section 3, Request 2)*

---

### 5. Get Religious Festivals for a Year
Retrieves religious festivals and holidays categorized by faith denomination (e.g., Hindu Festivals, Government Holidays, Sikh Festivals, Christian Holidays, Islamic Holidays) for a year, optionally filtered by month.

* **URL**: `/api/v1/festivals/{year}/religious`
* **Method**: `GET`
* **Path Parameters**:
  - `year` *(integer, required)*: Year constraint (between `1900` and `2100`).
* **Query Parameters**:
  - `month` *(integer, optional)*: Month index (between `1` and `12`) to filter results.
* **Sample Request**:
  ```bash
  curl http://localhost:8000/api/v1/festivals/2026/religious?month=1
  ```
* **Sample Response (200 OK)**:
  ```json
  {
    "year": 2026,
    "month": 1,
    "religious_festivals": {
      "Hindu Festivals": [
        {
          "date": "14",
          "day": "Wednesday",
          "name": "Pongal",
          "month": null
        }
      ],
      "Government Holidays": [
        {
          "date": "26",
          "day": "Monday",
          "name": "Republic Day",
          "month": null
        }
      ],
      "Sikh Festivals": [
        {
          "date": "13",
          "day": "Tuesday",
          "name": "Lohri",
          "month": null
        }
      ],
      "Christian Holidays": [],
      "Islamic Holidays": []
    }
  }
  ```

---

### 6. Get Religious Festivals by Specific Month
Retrieves religious festivals for a specific month and year using path parameters.

* **URL**: `/api/v1/festivals/{year}/religious/month/{month}`
* **Method**: `GET`
* **Path Parameters**:
  - `year` *(integer, required)*: Year constraint (between `1900` and `2100`).
  - `month` *(integer, required)*: Month index (between `1` and `12`).
* **Sample Request**:
  ```bash
  curl http://localhost:8000/api/v1/festivals/2026/religious/month/1
  ```
* **Sample Response (200 OK)**:
  *(Same format as Section 5)*

---

## 3. Rate Limiting & Protection

The API implements defensive rate-limiting to guarantee fair usage and prevent denial-of-service (DoS) attacks.
* **Limit**: `100` requests per `60` seconds per client IP address.
* **Headers returned on every request**:
  - `X-RateLimit-Limit`: Maximum requests allowed per window.
  - `X-RateLimit-Remaining`: Number of requests remaining in the current window.
  - `X-RateLimit-Reset`: Unix timestamp when the current window resets.

### Exceeding the Limit (429 Too Many Requests)
When a client exceeds the limit, the API returns:
* **Status**: `429 Too Many Requests`
* **Headers**: `Retry-After` (seconds until client can retry)
* **Response Body**:
  ```json
  {
    "detail": "Too many requests. Please slow down and try again later.",
    "retry_after": 60
  }
  ```

---

## 4. Error Responses

* **400 Bad Request**: Value range validation issues.
  ```json
  {
    "detail": "Provided functional request parameters contain an invalid value range configuration."
  }
  ```
* **422 Unprocessable Entity**: Structural schema validation failed (e.g. wrong parameter types).
  ```json
  {
    "detail": "The payload validation rules checked failed against schema requirements.",
    "errors": [
      {
        "type": "greater_than_equal",
        "loc": ["path", "year"],
        "msg": "Input should be greater than or equal to 1900",
        "input": 1800
      }
    ]
  }
  ```
* **500 Internal Server Error**: Downstream failure or system error.
  ```json
  {
    "detail": "An unexpected system operations sequence error occurred. Core team alerted."
  }
  ```
