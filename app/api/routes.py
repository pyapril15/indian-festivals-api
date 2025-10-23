import logging
from typing import Optional, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.api.dependencies import (
    get_festival_service,
    year_path,
    month_path,
    month_query
)
from app.config import get_settings
from app.middleware.rate_limiter import limiter
from app.models.schemas import (
    FestivalsResponse,
    ReligiousFestivalsResponse,
    ErrorResponse,
    FestivalItem
)
from app.services.festival_service import FestivalService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


def convert_to_festival_items(festivals_dict: Dict[str, List[dict]]) -> Dict[str, List[FestivalItem]]:
    """Convert dictionary of festivals to FestivalItem objects."""
    result = {}
    for month_name, festivals in festivals_dict.items():
        result[month_name] = [FestivalItem(**festival) for festival in festivals]
    return result


@router.get(
    "/festivals/{year}",
    response_model=FestivalsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        404: {"model": ErrorResponse, "description": "No festivals found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get all festivals for a year",
    description="Retrieve all Indian festivals and holidays for a specific year, optionally filtered by month."
)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
async def get_festivals(
        request: Request,
        year: int = Depends(year_path),
        month: Optional[int] = Depends(month_query),
        service: FestivalService = Depends(get_festival_service)
):
    """Get all festivals for a year, optionally filtered by month."""
    try:
        festivals = service.get_festivals(year=year, month=month)

        if not festivals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No festivals found for year {year}" + (f" and month {month}" if month else "")
            )

        # Convert to FestivalItem objects
        festivals_converted = convert_to_festival_items(festivals)

        return FestivalsResponse(
            year=year,
            month=month,
            festivals=festivals_converted
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_festivals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch festivals"
        )


@router.get(
    "/festivals/{year}/month/{month}",
    response_model=FestivalsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        404: {"model": ErrorResponse, "description": "No festivals found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get festivals for a specific month",
    description="Retrieve Indian festivals and holidays for a specific month and year."
)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
async def get_festivals_by_month(
        request: Request,
        year: int = Depends(year_path),
        month: int = Depends(month_path),
        service: FestivalService = Depends(get_festival_service)
):
    """Get festivals for a specific month."""
    try:
        festivals = service.get_festivals(year=year, month=month)

        if not festivals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No festivals found for {year}-{month:02d}"
            )

        # Convert to FestivalItem objects
        festivals_converted = convert_to_festival_items(festivals)

        return FestivalsResponse(
            year=year,
            month=month,
            festivals=festivals_converted
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_festivals_by_month: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch festivals"
        )


@router.get(
    "/festivals/{year}/religious",
    response_model=ReligiousFestivalsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        404: {"model": ErrorResponse, "description": "No festivals found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get religious festivals for a year",
    description="Retrieve religious festivals organized by religion (Hindu, Sikh, Christian, Government holidays, etc.)."
)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
async def get_religious_festivals(
        request: Request,
        year: int = Depends(year_path),
        month: Optional[int] = Depends(month_query),
        service: FestivalService = Depends(get_festival_service)
):
    """Get religious festivals for a year, optionally filtered by month."""
    try:
        religious_festivals = service.get_religious_festivals(year=year, month=month)

        # Check if any festivals were found
        has_festivals = any(festivals for festivals in religious_festivals.values())

        if not has_festivals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No religious festivals found for year {year}" + (f" and month {month}" if month else "")
            )

        # Convert to FestivalItem objects
        religious_festivals_converted = convert_to_festival_items(religious_festivals)

        return ReligiousFestivalsResponse(
            year=year,
            month=month,
            religious_festivals=religious_festivals_converted
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_religious_festivals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch religious festivals"
        )


@router.get(
    "/festivals/{year}/religious/month/{month}",
    response_model=ReligiousFestivalsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameters"},
        404: {"model": ErrorResponse, "description": "No festivals found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get religious festivals for a specific month",
    description="Retrieve religious festivals for a specific month and year, organized by religion."
)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
async def get_religious_festivals_by_month(
        request: Request,
        year: int = Depends(year_path),
        month: int = Depends(month_path),
        service: FestivalService = Depends(get_festival_service)
):
    """Get religious festivals for a specific month."""
    try:
        religious_festivals = service.get_religious_festivals(year=year, month=month)

        # Check if any festivals were found
        has_festivals = any(festivals for festivals in religious_festivals.values())

        if not has_festivals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No religious festivals found for {year}-{month:02d}"
            )

        # Convert to FestivalItem objects
        religious_festivals_converted = convert_to_festival_items(religious_festivals)

        return ReligiousFestivalsResponse(
            year=year,
            month=month,
            religious_festivals=religious_festivals_converted
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_religious_festivals_by_month: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch religious festivals"
        )
