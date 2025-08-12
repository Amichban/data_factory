"""
Health check router.

This module contains health check endpoints for monitoring application status,
database connectivity, and system health.
"""

import platform
import psutil
import structlog
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.services.firestore_service import firestore_service

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns basic application status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "app_name": settings.APP_NAME,
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check endpoint.
    
    Returns comprehensive health information including database connectivity,
    system resources, and application metrics.
    """
    try:
        # Database connectivity check
        db_status = "unhealthy"
        db_response_time = None
        
        try:
            start_time = datetime.utcnow()
            result = await db.execute(text("SELECT 1"))
            await result.fetchone()
            end_time = datetime.utcnow()
            db_response_time = (end_time - start_time).total_seconds() * 1000  # ms
            db_status = "healthy"
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            db_status = f"unhealthy: {str(e)}"

        # Firestore connectivity check (if enabled)
        firestore_status = "disabled"
        firestore_details = {}
        
        if settings.FIRESTORE_ENABLED:
            try:
                firestore_health = firestore_service.health_check()
                firestore_status = firestore_health.get("status", "unknown")
                firestore_details = firestore_health
            except Exception as e:
                logger.error("Firestore health check failed", error=str(e))
                firestore_status = "unhealthy"
                firestore_details = {"error": str(e)}
        
        # System information
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health_data = {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.VERSION,
            "app_name": settings.APP_NAME,
            "environment": {
                "debug": settings.DEBUG,
                "testing": settings.TESTING,
            },
            "database": {
                "status": db_status,
                "response_time_ms": db_response_time,
            },
            "firestore": firestore_details if firestore_details else {"status": firestore_status},
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_usage_percent": cpu_usage,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round(disk.used / disk.total * 100, 2),
                },
            },
        }

        # Return error status if database is unhealthy
        if db_status != "healthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_data
            )

        return health_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Health check failed"
            }
        )


@router.get("/health/liveness")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.
    
    Returns 200 if the application is running and can handle requests.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/readiness")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """
    Kubernetes readiness probe endpoint.
    
    Returns 200 if the application is ready to receive traffic.
    Checks database connectivity and other critical dependencies.
    """
    try:
        # Check database connectivity
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": "healthy"
            }
        }
    except Exception as e:
        logger.error("Readiness probe failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": {
                    "database": "unhealthy"
                }
            }
        )