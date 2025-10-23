from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.config import get_settings
from app.api.routes import router
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(_):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Rate limit: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW}s")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add rate limiter state and middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={
        "detail": "Rate limit exceeded. Please try again later.",
        "retry_after": 60
    },
    headers={"Retry-After": "60"}
))
app.add_middleware(SlowAPIMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} | "
        f"Time: {process_time:.3f}s | "
        f"Path: {request.url.path}"
    )

    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Include API routes
app.include_router(
    router,
    prefix=settings.API_V1_PREFIX,
    tags=["Festivals"]
)


# Root endpoint
@app.get(
    "/",
    summary="Root endpoint",
    description="Welcome endpoint with API information.",
    tags=["Root"]
)
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Indian Festivals API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": settings.API_V1_PREFIX
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )