# Indian Festivals API 🎉

A production-ready FastAPI service providing comprehensive information about Indian festivals, holidays, and
celebrations.

## 🌟 Features

- **No Authentication Required** - Public API for easy integration
- **Rate Limited** - 100 requests per minute per IP for fair usage
- **CORS Enabled** - Access from any origin
- **Cached Responses** - Fast performance with intelligent caching
- **Input Validation** - Robust validation using Pydantic
- **Health Checks** - Monitor API status
- **Comprehensive Documentation** - Auto-generated OpenAPI docs
- **Production Ready** - Configured for deployment on Render

## 📋 API Endpoints

### Base URL

```
Local: http://localhost:8000
Production: https://your-app.onrender.com
```

### Endpoints

#### 1. Get All Festivals in a Year

```http
GET /api/v1/festivals/{year}
```

**Parameters:**

- `year` (path, required): Year (1900-2100)
- `month` (query, optional): Month number (1-12)

**Example:**

```bash
curl "https://your-app.onrender.com/api/v1/festivals/2025"
curl "https://your-app.onrender.com/api/v1/festivals/2025?month=1"
```

**Response:**

```json
{
  "year": 2025,
  "month": null,
  "festivals": {
    "January": [
      {
        "date": "1",
        "day": "Wednesday",
        "name": "New Year"
      }
    ]
  }
}
```

---

#### 2. Get Festivals by Month

```http
GET /api/v1/festivals/{year}/month/{month}
```

**Parameters:**

- `year` (path, required): Year (1900-2100)
- `month` (path, required): Month number (1-12)

**Example:**

```bash
curl "https://your-app.onrender.com/api/v1/festivals/2025/month/1"
```

---

#### 3. Get Religious Festivals

```http
GET /api/v1/festivals/{year}/religious
```

**Parameters:**

- `year` (path, required): Year (1900-2100)
- `month` (query, optional): Month number (1-12)

**Example:**

```bash
curl "https://your-app.onrender.com/api/v1/festivals/2025/religious"
curl "https://your-app.onrender.com/api/v1/festivals/2025/religious?month=1"
```

**Response:**

```json
{
  "year": 2025,
  "month": null,
  "religious_festivals": {
    "Hindu Festivals": [
      {
        "date": "14",
        "day": "Tuesday",
        "month": "January",
        "name": "Pongal"
      }
    ],
    "Government Holidays": [],
    "Sikh Festivals": [],
    "Christian Holidays": []
  }
}
```

---

#### 4. Get Religious Festivals by Month

```http
GET /api/v1/festivals/{year}/religious/month/{month}
```

**Parameters:**

- `year` (path, required): Year (1900-2100)
- `month` (path, required): Month number (1-12)

**Example:**

```bash
curl "https://your-app.onrender.com/api/v1/festivals/2025/religious/month/1"
```

---

#### 5. Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-22T10:30:00.000Z",
  "version": "1.0.0"
}
```

---

#### 6. API Documentation

- **Swagger UI**: `https://your-app.onrender.com/docs`
- **ReDoc**: `https://your-app.onrender.com/redoc`
- **OpenAPI JSON**: `https://your-app.onrender.com/openapi.json`

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Local Development

1. **Clone the repository**

```bash
git clone https://github.com/pyapril15/indian-festivals-api.git
cd indian-festivals-api
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API**

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 📦 Project Structure

```
indian-festivals-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── festival_service.py # Business logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── dependencies.py     # Dependency injection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scraper.py          # Web scraping logic
│   │   └── cache.py            # Caching mechanism
│   └── middleware/
│       ├── __init__.py
│       ├── rate_limiter.py     # Rate limiting
│       └── error_handler.py    # Error handling
├── tests/
│   ├── __init__.py
│   └── test_api.py             # API tests
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version for Render
├── render.yaml                 # Render configuration
├── .gitignore
└── README.md
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```env
# Application
APP_NAME=Indian Festivals API
APP_VERSION=1.0.0
DEBUG=False

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Cache
CACHE_TTL=3600

# Server
HOST=0.0.0.0
PORT=8000
```

---

## 🌐 Deploy to Render

### Method 1: One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Method 2: Manual Deployment

1. **Create a Render account** at https://render.com

2. **Create a new Web Service**
    - Connect your GitHub repository
    - Choose "Python" as the environment

3. **Configure the service**
    - **Name**: indian-festivals-api
    - **Region**: Choose closest to your users
    - **Branch**: main
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
    - **Instance Type**: Free or Starter

4. **Environment Variables** (Optional)
    - Add any custom environment variables

5. **Deploy**
    - Click "Create Web Service"
    - Wait for deployment to complete

6. **Access your API**
    - Your API will be available at: `https://your-app-name.onrender.com`

---

## 📊 Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Limit**: 100 requests per minute per IP address
- **Response Headers**:
    - `X-RateLimit-Limit`: Maximum requests allowed
    - `X-RateLimit-Remaining`: Remaining requests
    - `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

**When rate limit exceeded:**

```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

---

## 🛡️ Security Features

1. **Input Validation**: All inputs validated using Pydantic
2. **Rate Limiting**: Prevents API abuse
3. **CORS Configuration**: Controlled cross-origin access
4. **Error Handling**: No sensitive information in error messages
5. **Timeout Protection**: Request timeouts prevent resource exhaustion
6. **Content Security**: Response validation

---

## 🧪 Testing

Run tests locally:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📈 Performance

- **Caching**: Responses cached for 1 hour
- **Async Processing**: Non-blocking operations
- **Connection Pooling**: Efficient HTTP requests
- **Response Compression**: Gzip compression enabled

---

## 🐛 Error Responses

### 400 Bad Request

```json
{
  "detail": "Month must be between 1 and 12"
}
```

### 404 Not Found

```json
{
  "detail": "No festivals found for the specified period"
}
```

### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

### 500 Internal Server Error

```json
{
  "detail": "An unexpected error occurred. Please try again later."
}
```

---

## 📝 Example Usage

### Python

```python
import requests

# Get all festivals for 2025
response = requests.get("https://your-app.onrender.com/api/v1/festivals/2025")
data = response.json()
print(data)

# Get January 2025 festivals
response = requests.get("https://your-app.onrender.com/api/v1/festivals/2025/month/1")
data = response.json()
print(data)
```

### JavaScript

```javascript
// Using fetch
fetch('https://your-app.onrender.com/api/v1/festivals/2025')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));

// Using axios
axios.get('https://your-app.onrender.com/api/v1/festivals/2025')
    .then(response => console.log(response.data))
    .catch(error => console.error('Error:', error));
```

### cURL

```bash
# Get all festivals
curl -X GET "https://your-app.onrender.com/api/v1/festivals/2025"

# Get religious festivals
curl -X GET "https://your-app.onrender.com/api/v1/festivals/2025/religious"

# Get festivals for specific month
curl -X GET "https://your-app.onrender.com/api/v1/festivals/2025?month=1"
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Festival data sourced from [Panchang AstroSage](https://panchang.astrosage.com/)
- Built with [FastAPI](https://fastapi.tiangolo.com/)

---

## 📞 Support

For issues and questions:

- Open an issue on GitHub
- Check the API documentation at `/docs`

---

## 🔄 Changelog

### Version 1.0.0 (2025-10-22)

- Initial release
- Basic festival API endpoints
- Rate limiting implementation
- Caching mechanism
- Production deployment configuration

---

**Made with ❤️ for the Indian community**

---

## 📂 Complete File Structure

Below are all the files you need to create for this project. Copy each file exactly as provided.