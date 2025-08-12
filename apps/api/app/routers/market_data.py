"""
Market Data API Router
Handles endpoints for market data ingestion and monitoring
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.market_data import (
    DataIngestionRequest, DataIngestionResponse, DataQualityMetrics,
    TimeFrame, DataMode, RateLimitStatus, DataSourceStatus
)
from app.services.market_data_service import market_data_service
from app.config import settings

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.post("/ingest", response_model=DataIngestionResponse)
async def ingest_market_data(
    request: DataIngestionRequest,
    background_tasks: BackgroundTasks
):
    """
    Initiate market data ingestion process
    
    This endpoint supports three modes:
    - batch: Historical data backfill
    - stream: Real-time streaming (runs in background)
    - spike: On-demand quick processing
    """
    try:
        if request.mode == DataMode.STREAM:
            # For streaming mode, process in background
            background_tasks.add_task(
                market_data_service.process_ingestion_request,
                request
            )
            return DataIngestionResponse(
                request_id="stream-" + str(datetime.utcnow().timestamp()),
                status="started",
                message="Streaming ingestion started in background",
                started_at=datetime.utcnow()
            )
        else:
            # For batch and spike modes, process synchronously
            response = await market_data_service.process_ingestion_request(request)
            return response
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/quality/{instrument}", response_model=DataQualityMetrics)
async def get_data_quality(
    instrument: str,
    timeframe: TimeFrame = Query(..., description="Timeframe to check")
):
    """
    Get data quality metrics for a specific instrument and timeframe
    """
    try:
        if instrument not in settings.SUPPORTED_INSTRUMENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported instrument: {instrument}"
            )
        
        metrics = await market_data_service.get_data_quality_metrics(
            instrument=instrument,
            timeframe=timeframe
        )
        return metrics
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/health")
async def get_market_data_health():
    """
    Get market data service health status including provider and rate limiting info
    """
    try:
        health_status = await market_data_service.get_health_status()
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }


@router.get("/instruments")
async def get_supported_instruments():
    """
    Get list of supported trading instruments
    """
    return {
        "instruments": settings.SUPPORTED_INSTRUMENTS,
        "total": len(settings.SUPPORTED_INSTRUMENTS)
    }


@router.get("/timeframes")
async def get_supported_timeframes():
    """
    Get list of supported timeframes
    """
    return {
        "timeframes": [tf.value for tf in TimeFrame],
        "total": len(TimeFrame)
    }


@router.get("/candles/{instrument}")
async def get_candles(
    instrument: str,
    timeframe: TimeFrame = Query(..., description="Candle timeframe"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, le=1000, description="Maximum number of candles to return")
):
    """
    Retrieve stored candles for an instrument
    """
    try:
        if instrument not in settings.SUPPORTED_INSTRUMENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported instrument: {instrument}"
            )
        
        # Default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # Query candles from Firestore
        from app.services.firestore_service import firestore_service
        
        query = (firestore_service.get_collection('market_data')
                .where('instrument', '==', instrument)
                .where('timeframe', '==', timeframe.value)
                .where('timestamp', '>=', start_date)
                .where('timestamp', '<=', end_date)
                .order_by('timestamp', direction='DESCENDING')
                .limit(limit))
        
        docs = query.stream()
        candles = []
        
        for doc in docs:
            candle_data = doc.to_dict()
            candles.append(candle_data)
        
        return {
            "instrument": instrument,
            "timeframe": timeframe.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "count": len(candles),
            "candles": candles
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/rate-limit")
async def get_rate_limit_status():
    """
    Get current rate limiting status
    """
    try:
        rate_limit = market_data_service.data_provider.rate_limiter.get_status()
        return rate_limit.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")