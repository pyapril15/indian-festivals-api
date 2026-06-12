# Schema & Data Models Documentation

The Indian Festivals API uses **Pydantic v2** for input validation, schema enforcement, and response serialization. All schemas are defined in [`app/models/schemas.py`](file:///e:/codeLabPraveen/own/program/python/prj/apis/indian-festivals-api/app/models/schemas.py).

---

## 1. Schema Configuration Rules

To optimize parsing speed and protect the API from input injection or payload bloat, all models utilize a standardized `model_config` (Pydantic `ConfigDict` configuration):

* **`frozen=True`**: Models are immutable. Immutable schemas compile to optimized bytecode, processing serialization up to 30% faster.
* **`extra="forbid"`** *(on input/validation models)*: Rejects requests that contain unrecognized fields, preventing parameter pollution attacks.
* **`extra="ignore"`** *(on response models)*: Silently ignores unknown attributes during response generation.
* **`str_strip_whitespace=True`**: Automatically trims leading and trailing whitespaces from strings (especially helpful during scraping).

---

## 2. Pydantic Models

### 1. `FestivalItem`
Represents an individual festival or holiday item.

```python
class FestivalItem(BaseModel):
    date: str = Field(..., description="Date of the festival")
    day: str = Field(..., description="Day of the week")
    name: str = Field(..., description="Name of the festival")
    month: Optional[str] = Field(None, description="Month name (for religious festivals)")
```

* **Attributes**:
  - `date`: Day of the month (e.g., `"1"`, `"14"`).
  - `day`: Weekday name (e.g., `"Wednesday"`, `"Thursday"`).
  - `name`: Human-readable festival name (e.g., `"New Year"`, `"Diwali"`).
  - `month`: Optional string representing the month name (populated only for religious endpoint groupings).
* **JSON Structure**:
  ```json
  {
    "date": "14",
    "day": "Wednesday",
    "name": "Makar Sankranti",
    "month": "January"
  }
  ```

---

### 2. `FestivalsResponse`
Standard response format for endpoint `/api/v1/festivals/{year}`.

```python
class FestivalsResponse(BaseModel):
    year: int = Field(..., description="Year of festivals")
    month: Optional[int] = Field(None, description="Month number if filtered")
    festivals: Dict[str, List[FestivalItem]] = Field(..., description="Festivals organized by month")
```

* **Attributes**:
  - `year`: Selected year integer (between `1900` and `2100`).
  - `month`: Optional month index if the request was filtered.
  - `festivals`: A dictionary mapping month names (keys) to arrays of `FestivalItem` models.
* **JSON Structure**:
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

### 3. `ReligiousFestivalsResponse`
Standard response format for endpoint `/api/v1/festivals/{year}/religious`.

```python
class ReligiousFestivalsResponse(BaseModel):
    year: int = Field(..., description="Year of festivals")
    month: Optional[int] = Field(None, description="Month number if filtered")
    religious_festivals: Dict[str, List[FestivalItem]] = Field(
        ..., 
        description="Religious festivals organized by religion"
    )
```

* **Attributes**:
  - `year`: Selected year integer.
  - `month`: Optional month index.
  - `religious_festivals`: A dictionary mapping religion categories (e.g., `"Hindu Festivals"`, `"Government Holidays"`, etc.) to arrays of `FestivalItem` models.
* **JSON Structure**:
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
          "month": "January"
        }
      ]
    }
  }
  ```

---

### 4. `HealthResponse`
Validation model representing system infrastructure health checks.

```python
class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status")
    timestamp: datetime = Field(..., description="Current server timezone timestamp")
    version: str = Field(..., description="API version track")
```

* **JSON Structure**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-06-12T13:42:21Z",
    "version": "1.0.1"
  }
  ```

---

### 5. `ErrorResponse`
Wrapper model returning standardized errors to consumers.

```python
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Target error diagnostic message")
    retry_after: Optional[int] = Field(None, description="Retry window countdown parameters in seconds")
```

* **JSON Structure**:
  ```json
  {
    "detail": "Too many requests. Please slow down and try again later.",
    "retry_after": 60
  }
  ```
