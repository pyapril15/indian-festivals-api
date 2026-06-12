from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class FestivalItem(BaseModel):
    """Individual festival item definition."""

    date: str = Field(..., description="Date of the festival")
    day: str = Field(..., description="Day of the week")
    name: str = Field(..., description="Name of the festival")
    month: Optional[str] = Field(None, description="Month name (for religious festivals)")

    # Core engine configurations optimized for speed and safety
    model_config = ConfigDict(
        frozen=True,  # Immutable schemas process up to 30% faster
        extra="forbid",  # Drop attacks trying to send extra data variants
        str_strip_whitespace=True,  # Strips accidental scraper formatting whitespace automatically
        json_schema_extra={
            "example": {
                "date": "1",
                "day": "Wednesday",
                "name": "New Year",
                "month": "January"
            }
        }
    )


class FestivalsResponse(BaseModel):
    """Response model for standardized monthly festival outputs."""

    year: int = Field(..., description="Year of festivals")
    month: Optional[int] = Field(None, description="Month number if filtered")
    festivals: Dict[str, List[FestivalItem]] = Field(..., description="Festivals organized by month")

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",  # Ignores unknown attributes cleanly during response generation
        json_schema_extra={
            "example": {
                "year": 2026,
                "month": None,
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
        }
    )


class ReligiousFestivalsResponse(BaseModel):
    """Response model for religious categorization mapping outputs."""

    year: int = Field(..., description="Year of festivals")
    month: Optional[int] = Field(None, description="Month number if filtered")
    religious_festivals: Dict[str, List[FestivalItem]] = Field(
        ...,
        description="Religious festivals organized by religion"
    )

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
        json_schema_extra={
            "example": {
                "year": 2026,
                "month": None,
                "religious_festivals": {
                    "Hindu Festivals": [
                        {
                            "date": "14",
                            "day": "Tuesday",
                            "month": "January",
                            "name": "Pongal"
                        }
                    ]
                }
            }
        }
    )


class HealthResponse(BaseModel):
    """High-priority platform health state validation mapping."""

    status: str = Field(..., description="API health status")
    timestamp: datetime = Field(..., description="Current server timezone timestamp")
    version: str = Field(..., description="API version track")

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2026-06-12T11:57:00Z",
                "version": "1.0.1"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standardized operational error schema wrapper."""

    detail: str = Field(..., description="Target error diagnostic message")
    retry_after: Optional[int] = Field(None, description="Retry window countdown parameters in seconds")

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "detail": "Rate limit threshold breached. Too many concurrent attempts.",
                "retry_after": 60
            }
        }
    )
