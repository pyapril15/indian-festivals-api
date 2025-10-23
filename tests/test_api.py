from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_get_festivals_valid_year():
    """Test getting festivals for a valid year."""
    response = client.get("/api/v1/festivals/2025")
    assert response.status_code == 200
    data = response.json()
    assert "year" in data
    assert "festivals" in data
    assert data["year"] == 2025


def test_get_festivals_with_month():
    """Test getting festivals for a specific month."""
    response = client.get("/api/v1/festivals/2025?month=1")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2025
    assert data["month"] == 1


def test_get_festivals_invalid_year():
    """Test getting festivals with invalid year."""
    response = client.get("/api/v1/festivals/1800")
    assert response.status_code == 422


def test_get_festivals_invalid_month():
    """Test getting festivals with invalid month."""
    response = client.get("/api/v1/festivals/2025?month=13")
    assert response.status_code == 422


def test_get_festivals_by_month():
    """Test getting festivals by month endpoint."""
    response = client.get("/api/v1/festivals/2025/month/1")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2025
    assert data["month"] == 1


def test_get_religious_festivals():
    """Test getting religious festivals."""
    response = client.get("/api/v1/festivals/2025/religious")
    assert response.status_code == 200
    data = response.json()
    assert "year" in data
    assert "religious_festivals" in data


def test_get_religious_festivals_by_month():
    """Test getting religious festivals by month."""
    response = client.get("/api/v1/festivals/2025/religious/month/1")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2025
    assert data["month"] == 1


def test_rate_limiting():
    """Test rate limiting (simplified test)."""
    # This is a basic test - in production you'd want more comprehensive rate limit testing
    responses = []
    for _ in range(5):
        response = client.get("/api/v1/festivals/2025")
        responses.append(response.status_code)

    # At least some requests should succeed
    assert 200 in responses


def test_cors_headers():
    """Test CORS headers are present."""
    response = client.get("/", headers={"Origin": "http://example.com"})
    assert "access-control-allow-origin" in response.headers


def test_openapi_docs():
    """Test OpenAPI documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 200
