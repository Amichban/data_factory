"""
Statistics Router for Event Management REST API

Provides endpoints for event statistics, aggregations, and analytics.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.database import get_db
from app.services.event_service import EventService
from app.schemas.event_schemas import (
    EventFilter,
    EventStatistics,
    EventTimeSeries,
    EventAggregation,
    EventAggregationResponse,
    EventType,
    TimeFrame,
    EventHealthCheck
)
from app.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
    responses={503: {"description": "Service unavailable"}}
)


@router.get("/overview", response_model=EventStatistics)
async def get_statistics_overview(
    # Filter parameters
    event_type: Optional[List[EventType]] = Query(None, description="Filter by event types"),
    instrument: Optional[List[str]] = Query(None, description="Filter by instruments"),
    timeframe: Optional[List[TimeFrame]] = Query(None, description="Filter by timeframes"),
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    day_of_week: Optional[List[int]] = Query(None, description="Filter by days of week"),
    hour_of_day: Optional[List[int]] = Query(None, description="Filter by hours of day"),
    db: AsyncSession = Depends(get_db)
) -> EventStatistics:
    """
    Get comprehensive event statistics overview.
    
    Returns:
    - Total event count
    - Events breakdown by type, instrument, and timeframe
    - Average rebound metrics
    - Most active trading hours and days
    - Date range of events
    - Top resistance levels by frequency
    
    Can apply filters to get statistics for specific subsets of data.
    """
    # Build filter object
    filters = None
    if any([event_type, instrument, timeframe, start_date, end_date, day_of_week, hour_of_day]):
        filters = EventFilter(
            event_type=event_type,
            instrument=instrument,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            day_of_week=day_of_week,
            hour_of_day=hour_of_day
        )
    
    service = EventService(db)
    statistics = await service.get_statistics(filters)
    
    return statistics


@router.get("/time-series", response_model=EventTimeSeries)
async def get_time_series(
    interval: str = Query("day", pattern="^(hour|day|week)$", description="Time interval for grouping"),
    event_type: Optional[List[EventType]] = Query(None, description="Filter by event types"),
    instrument: Optional[List[str]] = Query(None, description="Filter by instruments"),
    timeframe: Optional[List[TimeFrame]] = Query(None, description="Filter by timeframes"),
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    db: AsyncSession = Depends(get_db)
) -> EventTimeSeries:
    """
    Get event time series data for charting.
    
    Groups events by the specified time interval and returns:
    - Timestamp for each interval
    - Average rebound value
    - Event count
    
    Useful for visualizing event patterns over time.
    """
    # Build filter object
    filters = None
    if any([event_type, instrument, timeframe, start_date, end_date]):
        filters = EventFilter(
            event_type=event_type,
            instrument=instrument,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
    
    service = EventService(db)
    time_series = await service.get_time_series(interval, filters)
    
    return time_series


@router.post("/aggregate", response_model=EventAggregationResponse)
async def aggregate_events(
    aggregation: EventAggregation,
    db: AsyncSession = Depends(get_db)
) -> EventAggregationResponse:
    """
    Perform custom aggregation on events.
    
    Allows grouping by multiple fields and calculating various metrics.
    
    **Group by fields:**
    - event_type
    - instrument
    - timeframe
    - day_of_week
    - hour_of_day
    
    **Available metrics:**
    - count: Number of events
    - avg_rebound: Average rebound percentage
    - max_rebound: Maximum rebound percentage
    - min_rebound: Minimum rebound percentage
    - avg_resistance: Average resistance level
    """
    service = EventService(db)
    result = await service.aggregate_events(aggregation)
    
    return EventAggregationResponse(
        groups=result['groups'],
        total_groups=result['total_groups'],
        query=aggregation
    )


@router.get("/by-instrument/{instrument}", response_model=Dict[str, Any])
async def get_instrument_statistics(
    instrument: str,
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed statistics for a specific instrument.
    
    Returns instrument-specific metrics including:
    - Event distribution by timeframe
    - Average resistance levels
    - Most active trading hours
    - Success rate metrics
    """
    filters = EventFilter(
        instrument=[instrument],
        start_date=start_date,
        end_date=end_date
    )
    
    service = EventService(db)
    stats = await service.get_statistics(filters)
    
    # Get time series for the instrument
    time_series = await service.get_time_series("day", filters)
    
    return {
        "instrument": instrument,
        "total_events": stats.total_events,
        "events_by_timeframe": stats.events_by_timeframe,
        "avg_rebound_percentage": stats.avg_rebound_percentage,
        "avg_rebound_amplitude": stats.avg_rebound_amplitude,
        "most_active_hour": stats.most_active_hour,
        "most_active_day": stats.most_active_day,
        "date_range": stats.date_range,
        "top_resistance_levels": stats.top_resistance_levels[:5],
        "daily_trend": [
            {
                "date": point.timestamp.isoformat(),
                "events": point.count,
                "avg_rebound": point.value
            }
            for point in time_series.data[-30:]  # Last 30 days
        ]
    }


@router.get("/performance-metrics", response_model=Dict[str, Any])
async def get_performance_metrics(
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get system performance metrics.
    
    Returns metrics about event detection performance:
    - Detection rate over time
    - Average processing latency
    - Event distribution patterns
    - System health indicators
    """
    filters = EventFilter(
        start_date=start_date,
        end_date=end_date
    ) if start_date or end_date else None
    
    service = EventService(db)
    
    # Get overall statistics
    stats = await service.get_statistics(filters)
    
    # Get hourly distribution
    hourly_aggregation = EventAggregation(
        group_by=["hour_of_day"],
        metrics=["count", "avg_rebound"],
        filters=filters
    )
    hourly_result = await service.aggregate_events(hourly_aggregation)
    
    # Get daily distribution
    daily_aggregation = EventAggregation(
        group_by=["day_of_week"],
        metrics=["count", "avg_rebound"],
        filters=filters
    )
    daily_result = await service.aggregate_events(daily_aggregation)
    
    return {
        "summary": {
            "total_events": stats.total_events,
            "date_range": stats.date_range,
            "avg_rebound_percentage": stats.avg_rebound_percentage,
            "unique_instruments": len(stats.events_by_instrument)
        },
        "event_distribution": {
            "by_type": stats.events_by_type,
            "by_instrument": stats.events_by_instrument,
            "by_timeframe": stats.events_by_timeframe
        },
        "temporal_patterns": {
            "hourly_distribution": sorted(
                hourly_result['groups'],
                key=lambda x: x['hour_of_day']
            ),
            "daily_distribution": sorted(
                daily_result['groups'],
                key=lambda x: x['day_of_week']
            ),
            "most_active_hour": stats.most_active_hour,
            "most_active_day": stats.most_active_day
        },
        "resistance_analysis": {
            "top_levels": stats.top_resistance_levels[:10],
            "avg_rebound_amplitude": stats.avg_rebound_amplitude
        }
    }


@router.get("/compare-instruments", response_model=Dict[str, Any])
async def compare_instruments(
    instruments: List[str] = Query(..., min_length=2, max_length=10, description="Instruments to compare"),
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare statistics across multiple instruments.
    
    Useful for identifying which instruments have the most reliable resistance patterns.
    """
    service = EventService(db)
    
    comparison_data = {}
    
    for instrument in instruments:
        filters = EventFilter(
            instrument=[instrument],
            start_date=start_date,
            end_date=end_date
        )
        
        stats = await service.get_statistics(filters)
        
        comparison_data[instrument] = {
            "total_events": stats.total_events,
            "avg_rebound_percentage": stats.avg_rebound_percentage,
            "avg_rebound_amplitude": float(stats.avg_rebound_amplitude) if stats.avg_rebound_amplitude else 0,
            "events_by_timeframe": stats.events_by_timeframe,
            "most_active_hour": stats.most_active_hour,
            "most_active_day": stats.most_active_day
        }
    
    # Calculate rankings
    rankings = {
        "by_event_count": sorted(
            instruments,
            key=lambda x: comparison_data[x]["total_events"],
            reverse=True
        ),
        "by_avg_rebound": sorted(
            instruments,
            key=lambda x: comparison_data[x]["avg_rebound_percentage"],
            reverse=True
        )
    }
    
    return {
        "instruments": comparison_data,
        "rankings": rankings,
        "date_range": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None
        }
    }


@router.get("/heatmap-data", response_model=Dict[str, Any])
async def get_heatmap_data(
    group_by: str = Query("hour_day", pattern="^(hour_day|instrument_timeframe)$", description="Grouping for heatmap"),
    metric: str = Query("count", pattern="^(count|avg_rebound)$", description="Metric to display"),
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get data formatted for heatmap visualization.
    
    Returns a 2D matrix of values suitable for heatmap charts.
    
    **Grouping options:**
    - hour_day: Hours (x-axis) vs Days of week (y-axis)
    - instrument_timeframe: Instruments (x-axis) vs Timeframes (y-axis)
    """
    filters = EventFilter(
        start_date=start_date,
        end_date=end_date
    ) if start_date or end_date else None
    
    service = EventService(db)
    
    if group_by == "hour_day":
        # Create hour x day heatmap
        aggregation = EventAggregation(
            group_by=["hour_of_day", "day_of_week"],
            metrics=["count", "avg_rebound"] if metric == "avg_rebound" else ["count"],
            filters=filters
        )
        
        result = await service.aggregate_events(aggregation)
        
        # Format as 2D matrix
        matrix = [[0 for _ in range(24)] for _ in range(7)]
        
        for group in result['groups']:
            hour = group['hour_of_day']
            day = group['day_of_week']
            value = group.get('avg_rebound', group.get('count', 0))
            matrix[day][hour] = value
        
        return {
            "type": "hour_day",
            "metric": metric,
            "data": matrix,
            "x_labels": [str(h) for h in range(24)],
            "y_labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        }
    
    else:  # instrument_timeframe
        aggregation = EventAggregation(
            group_by=["instrument", "timeframe"],
            metrics=["count", "avg_rebound"] if metric == "avg_rebound" else ["count"],
            filters=filters
        )
        
        result = await service.aggregate_events(aggregation)
        
        # Get unique instruments and timeframes
        instruments = sorted(set(g['instrument'] for g in result['groups']))
        timeframes = ["M1", "M5", "M15", "M30", "H1", "H4", "D", "W", "M"]
        
        # Create matrix
        matrix = [[0 for _ in range(len(instruments))] for _ in range(len(timeframes))]
        
        for group in result['groups']:
            try:
                i_idx = instruments.index(group['instrument'])
                t_idx = timeframes.index(group['timeframe'])
                value = group.get('avg_rebound', group.get('count', 0))
                matrix[t_idx][i_idx] = value
            except (ValueError, IndexError):
                continue
        
        return {
            "type": "instrument_timeframe",
            "metric": metric,
            "data": matrix,
            "x_labels": instruments,
            "y_labels": timeframes
        }


@router.get("/health", response_model=EventHealthCheck)
async def get_health_status(
    db: AsyncSession = Depends(get_db)
) -> EventHealthCheck:
    """
    Get health status of the event management system.
    
    Returns information about:
    - Service status
    - Database connectivity
    - Event processing status
    - Latest event timestamp
    """
    try:
        service = EventService(db)
        
        # Get latest event
        from app.schemas.event_schemas import EventSortField, SortOrder, PaginationParams
        
        pagination = PaginationParams(
            page=1,
            page_size=1,
            sort_by=EventSortField.EVENT_TIMESTAMP,
            sort_order=SortOrder.DESC
        )
        
        events, total = await service.list_events(None, pagination)
        latest_event = events[0].event_timestamp if events else None
        
        return EventHealthCheck(
            status="healthy",
            total_events=total,
            latest_event=latest_event,
            database_connected=True,
            processing_enabled=settings.FEATURE_FLAGS.get('resistance_detection_enabled', False)
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return EventHealthCheck(
            status="unhealthy",
            total_events=0,
            latest_event=None,
            database_connected=False,
            processing_enabled=False
        )