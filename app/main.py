import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import router
from app.config import get_settings
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.rate_limiter import limiter
from app.models.schemas import HealthResponse

# Production Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("uvicorn.error")

settings = get_settings()


@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
    """Handles secure application initialization and graceful connection shutdowns."""
    logger.info(f"Initializing {settings.APP_NAME} v{settings.APP_VERSION} on Production Engine")
    yield
    logger.info(f"Initiating graceful cleanup sequence for {settings.APP_NAME}")


# Initialize Production-Hardened FastAPI Instance
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


# Core Security Header Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Relax CSP only for docs pages so Swagger/ReDoc CDNs can load scripts, styles, and images
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data: cdn.jsdelivr.net; "
            "connect-src 'self'"
        )
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
    return response


# DDOS Protection & Rate Limiting Error Handling (Warnings Fixed with _)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_request: Request, _exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down and try again later."},
        headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
    )


app.add_middleware(SlowAPIMiddleware)
setup_exception_handlers(app)

# Secure Cross-Origin Resource Sharing Layout
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Bandwidth Saver Optimization
app.add_middleware(GZipMiddleware, minimum_size=1000)


# High-Precision Performance Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info(f"Incoming Request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        logger.info(
            f"Response Status: {response.status_code} | "
            f"Latency: {process_time:.4f}s | "
            f"Path: {request.url.path}"
        )
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response
    except Exception as e:
        process_time = time.perf_counter() - start_time
        logger.error(f"Uncaught Runtime Exception: {str(e)} | Latency: {process_time:.4f}s")
        raise e


# Root Welcome Endpoint
@app.get("/", summary="Root Access", tags=["Status"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "operational"
    }


# Render Highly Critical Live Health Probe Line
@app.get("/health", response_model=HealthResponse, summary="Infrastructure Health Status", tags=["Status"])
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.APP_VERSION
    )


# Versioned API Business Endpoints Routing Map
app.include_router(router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        loop="uvloop"
    )
