from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class FestivalItem(BaseModel):
    """Individual festival item."""

    date: str = Field(..., description="Date of the festival")
    day: str = Field(..., description="Day of the week")
    name: str = Field(..., description="Name of the festival")
    month: Optional[str] = Field(None, description="Month name (for religious festivals)")

    model_config = ConfigDict(
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
    """Response model for festivals."""

    year: int = Field(..., description="Year of festivals")
    month: Optional[int] = Field(None, description="Month number if filtered")
    festivals: Dict[str, List[FestivalItem]] = Field(..., description="Festivals organized by month")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "year": 2025,
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
    """Response model for religious festivals."""

    year: int = Field(..., description="Year of festivals")
    month: Optional[int] = Field(None, description="Month number if filtered")
    religious_festivals: Dict[str, List[FestivalItem]] = Field(
        ...,
        description="Religious festivals organized by religion"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "year": 2025,
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
    """Health check response."""

    status: str = Field(..., description="API health status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-22T10:30:00.000Z",
                "version": "1.0.0"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")
    retry_after: Optional[int] = Field(None, description="Retry after seconds (for rate limiting)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "An error occurred",
                "retry_after": None
            }
        }
    )
