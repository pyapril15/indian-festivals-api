import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Connect to the centralized engine logging console tracking channel
logger = logging.getLogger("uvicorn.error")


def setup_exception_handlers(app_instance: FastAPI) -> None:
    """
    Setup production-hardened globally intercepted security exception boundaries.

    Args:
        app_instance (FastAPI): Active structural FastAPI service runtime layout.
    """

    @app_instance.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exception_context: RequestValidationError):
        """Catches and clean-logs user input validation anomalies securely."""
        logger.warning(f"Bad incoming client metadata payload. Errors: {exception_context.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "The payload validation rules checked failed against schema requirements.",
                "errors": exception_context.errors()
            }
        )

    @app_instance.exception_handler(ValueError)
    async def value_error_handler(_request: Request, exception_context: ValueError):
        """Catches value manipulation anomalies safely without leaking backend stack traces."""
        logger.error(f"Internal computation validation constraint failure: {str(exception_context)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            # Production Security: Return a sanitized message to clients rather than a raw str(exc)
            content={"detail": "Provided functional request parameters contain an invalid value range configuration."}
        )

    @app_instance.exception_handler(Exception)
    async def general_exception_handler(_request: Request, exception_context: Exception):
        """Catches fatal exceptions gracefully to protect node clusters from execution drop-outs."""
        logger.error(
            f"Global intercept caught unhandled structural runtime exception: {str(exception_context)}",
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected system operations sequence error occurred. Core team alerted."}
        )
