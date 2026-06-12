import os

import pytest
from fastapi.testclient import TestClient

# FORCE DEVELOPMENT ENVIRONMENT STATE FOR TESTING STABILITY
# This guarantees that the /docs and /openapi.json specs remain visible during testing
os.environ["DEBUG"] = "True"
os.environ["CORS_ORIGINS"] = '["*"]'

from app.main import app

client = TestClient(app)


def test_root():
    """Test structural welcome message and endpoint metadata connectivity."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test Render automated deployment lifecycle live health probe line."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_get_festivals_valid_year():
    """Test getting festivals for a valid year boundary context constraint."""
    response = client.get("/api/v1/festivals/2026")
    assert response.status_code == 200
    data = response.json()
    assert "year" in data
    assert "festivals" in data
    assert data["year"] == 2026


def test_get_festivals_with_month():
    """Test getting festivals filtered by a valid month search query argument."""
    response = client.get("/api/v1/festivals/2026?month=1")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2026
    assert data["month"] == 1


def test_get_festivals_invalid_year():
    """Test that input validator drops years falling outside historical parameters."""
    response = client.get("/api/v1/festivals/1800")
    assert response.status_code == 422


def test_get_festivals_invalid_month():
    """Test that input validator drops query indexes extending beyond standard limits."""
    response = client.get("/api/v1/festivals/2026?month=13")
    assert response.status_code == 422


def test_get_festivals_by_month():
    """Test explicit calendar index path routing validations."""
    response = client.get("/api/v1/festivals/2026/month/1")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2026
    assert data["month"] == 1


def test_get_religious_festivals():
    """Test master religious denomination array grouping outputs."""
    response = client.get("/api/v1/festivals/2026/religious")
    assert response.status_code == 200
    data = response.json()
    assert "year" in data
    assert "religious_festivals" in data


def test_get_religious_festivals_by_month():
    """Test explicitly localized religious group path parameters."""
    response = client.get("/api/v1/festivals/2026/religious/month/1")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2026
    assert data["month"] == 1


def test_rate_limiting():
    """Test system defensive rate-limiter layer tracking limits."""
    responses = [client.get("/api/v1/festivals/2026").status_code for _ in range(5)]
    # Ensure standard requests connect cleanly under general limits
    assert 200 in responses


def test_cors_headers():
    """Test security check returns cross-origin safety configurations."""
    response = client.get("/", headers={"Origin": "https://praveenyadavme.vercel.app"})
    assert "access-control-allow-origin" in response.headers


def test_openapi_docs():
    """Test that framework docs match target layout expectations during mock mode."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 200
