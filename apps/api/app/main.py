"""
FastAPI main application module.

This module contains the FastAPI application instance with CORS configuration,
middleware setup, and route registration.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import create_tables
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import health, market_data, events, statistics
from app.services.firestore_service import firestore_service
from app.services.market_data_service import market_data_service


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting up application", app_name=settings.APP_NAME)
    try:
        await create_tables()
    except Exception as e:
        logger.warning(f"Could not create tables: {e}. Continuing without database.")
    
    # Initialize Firestore if enabled
    if settings.FIRESTORE_ENABLED:
        firestore_health = firestore_service.health_check()
        logger.info("Firestore initialized", status=firestore_health.get("status"))
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    # Clean up market data service
    await market_data_service.close()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="A production-ready FastAPI backend application",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
        docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
        redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    
    # Add rate limiting middleware
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.MARKET_DATA_RATE_LIMIT,
        requests_per_hour=settings.MARKET_DATA_RATE_LIMIT * 60,
        redis_url=settings.REDIS_URL
    )

    # Include routers
    app.include_router(
        health.router,
        prefix=settings.API_V1_STR,
        tags=["health"]
    )
    app.include_router(
        market_data.router,
        prefix=settings.API_V1_STR,
        tags=["market-data"]
    )
    
    # Include event management routers
    if settings.FEATURE_FLAGS.get('api_v1_enabled', True):
        app.include_router(
            events.router,
            prefix=settings.API_V1_STR,
            tags=["events"]
        )
        app.include_router(
            statistics.router,
            prefix=settings.API_V1_STR,
            tags=["statistics"]
        )

    @app.exception_handler(500)
    async def internal_server_error_handler(request, exc):
        """Handle internal server errors with proper logging."""
        logger.error(
            "Internal server error",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None,  # Use our custom logging configuration
    )