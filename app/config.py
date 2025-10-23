from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Application
    APP_NAME: str = "Indian Festivals API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Comprehensive API for Indian festivals, holidays, and celebrations"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Cache
    CACHE_TTL: int = 3600  # 1 hour in seconds

    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Scraper
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_BASE_URL: str = "https://panchang.astrosage.com/calendars/indiancalendar"

    # Validation
    MIN_YEAR: int = 1900
    MAX_YEAR: int = 2100
    MIN_MONTH: int = 1
    MAX_MONTH: int = 12

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
