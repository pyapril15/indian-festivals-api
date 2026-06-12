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

# Connect to the primary centralized logger channel
logger = logging.getLogger("uvicorn.error")
settings = get_settings()

router = APIRouter()

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def convert_to_festival_items(festivals_dict: Dict[str, List[dict]]) -> Dict[str, List[FestivalItem]]:
    """Converts raw dictionary responses efficiently into immutable validation-hardened FestivalItem models."""
    return {
        month_name: [FestivalItem(**festival) for festival in festivals]
        for month_name, festivals in festivals_dict.items()
    }


@router.get(
    "/festivals/{year}",
    response_model=FestivalsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameter boundaries"},
        404: {"model": ErrorResponse, "description": "No tracked data records matching constraints found"},
        429: {"model": ErrorResponse, "description": "Rate limit threshold breached"},
        500: {"model": ErrorResponse, "description": "Internal cluster runtime exception"}
    },
    summary="Get all festivals for a year",
    description="Retrieve all Indian festivals and holidays for a specific year, optionally filtered by month query parameters."
)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
# noinspection PyUnusedLocal
async def get_festivals(
        request: Request,
        year: int = Depends(year_path),
        month: Optional[int] = Depends(month_query),
        service: FestivalService = Depends(get_festival_service)
):
    """Retrieves yearly master lists using high-performance non-blocking async execution loops."""
    try:
        festivals = await service.get_festivals(year=year, month=month)

        if not festivals:
            if month:
                month_name = MONTH_NAMES.get(month, "January")
                festivals = {month_name: []}
            else:
                festivals = {}

        return FestivalsResponse(
            year=year,
            month=month,
            festivals=convert_to_festival_items(festivals)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fatal exception inside get_festivals endpoint block: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch targeted calendar metrics from core engine layers."
        )


@router.get(
    "/festivals/{year}/month/{month}",
    response_model=FestivalsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameter boundaries"},
        404: {"model": ErrorResponse, "description": "No tracked data records matching constraints found"},
        429: {"model": ErrorResponse, "description": "Rate limit threshold breached"},
        500: {"model": ErrorResponse, "description": "Internal cluster runtime exception"}
    },
    summary="Get festivals for a specific month",
    description="Retrieve Indian festivals and holidays targeted explicitly to a specific year and monthly integer path."
)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
# noinspection PyUnusedLocal
async def get_festivals_by_month(
        request: Request,
        year: int = Depends(year_path),
        month: int = Depends(month_path),
        service: FestivalService = Depends(get_festival_service)
):
    """Retrieves clean monthly calendar indexes non-blockingly."""
    try:
        festivals = await service.get_festivals(year=year, month=month)

        if not festivals:
            month_name = MONTH_NAMES.get(month, "January")
            festivals = {month_name: []}

        return FestivalsResponse(
            year=year,
            month=month,
            festivals=convert_to_festival_items(festivals)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fatal exception inside get_festivals_by_month endpoint block: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch targeted calendar metrics from core engine layers."
        )


@router.get(
    "/festivals/{year}/religious",
    response_model=ReligiousFestivalsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameter boundaries"},
        404: {"model": ErrorResponse, "description": "No tracked data records matching constraints found"},
        429: {"model": ErrorResponse, "description": "Rate limit threshold breached"},
        500: {"model": ErrorResponse, "description": "Internal cluster runtime exception"}
    },
    summary="Get religious festivals for a year",
    description="Retrieve religious festivals organized by localized beliefs (Hindu, Sikh, Christian, Islamic, or Gov Holidays)."
)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
# noinspection PyUnusedLocal
async def get_religious_festivals(
        request: Request,
        year: int = Depends(year_path),
        month: Optional[int] = Depends(month_query),
        service: FestivalService = Depends(get_festival_service)
):
    """Retrieves religious arrays mapped synchronously to multi-core workers."""
    try:
        religious_festivals = await service.get_religious_festivals(year=year, month=month)

        return ReligiousFestivalsResponse(
            year=year,
            month=month,
            religious_festivals=convert_to_festival_items(religious_festivals)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fatal exception inside get_religious_festivals endpoint block: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to isolate specialized religious collection groups safely."
        )


@router.get(
    "/festivals/{year}/religious/month/{month}",
    response_model=ReligiousFestivalsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid parameter boundaries"},
        404: {"model": ErrorResponse, "description": "No tracked data records matching constraints found"},
        429: {"model": ErrorResponse, "description": "Rate limit threshold breached"},
        500: {"model": ErrorResponse, "description": "Internal cluster runtime exception"}
    },
    summary="Get religious festivals for a specific month",
    description="Retrieve religious festivals grouped explicitly by faith denomination matching a specific year and month."
)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW} seconds")
# noinspection PyUnusedLocal
async def get_religious_festivals_by_month(
        request: Request,
        year: int = Depends(year_path),
        month: int = Depends(month_path),
        service: FestivalService = Depends(get_festival_service)
):
    """Retrieves specialized religious metadata sub-arrays safely."""
    try:
        religious_festivals = await service.get_religious_festivals(year=year, month=month)

        return ReligiousFestivalsResponse(
            year=year,
            month=month,
            religious_festivals=convert_to_festival_items(religious_festivals)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fatal exception inside get_religious_festivals_by_month endpoint block: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to isolate specialized religious collection groups safely."
        )
