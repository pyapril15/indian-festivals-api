from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Application Setup
    APP_NAME: str = "Indian Festivals API"
    APP_VERSION: str = "1.0.1"
    APP_DESCRIPTION: str = "Comprehensive API for Indian festivals, holidays, and celebrations"
    DEBUG: bool = False

    # Server Infrastructure
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API Prefix Routing
    API_V1_PREFIX: str = "/api/v1"

    # Rate Limiting Defenses
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Cache Layer Lifespan
    CACHE_TTL: int = 3600  # 1 hour in seconds

    # Secure Cross-Origin Resource Sharing (CORS)
    CORS_ORIGINS: list[str] = ["https://praveenyadavme.vercel.app"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Web Scraper Performance Tuning
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_BASE_URL: str = "https://panchang.astrosage.com/calendars/indiancalendar"

    # Strict Validation Constraints
    MIN_YEAR: int = 1900
    MAX_YEAR: int = 2100
    MIN_MONTH: int = 1
    MAX_MONTH: int = 12

    # Pydantic v2 Modern Configuration Management
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Provides a thread-safe, cached singleton instance of application settings."""
    return Settings()
