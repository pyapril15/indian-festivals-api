import logging

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup custom exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(exc: RequestValidationError):
        """Handle validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": exc.errors()
            }
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(exc: ValueError):
        """Handle value errors."""
        logger.error(f"Value error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(exc: Exception):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Please try again later."}
        )
