"""
Events Router for Event Management REST API

Provides RESTful endpoints for event CRUD operations, filtering, and bulk operations.
"""

from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io
import json

from app.database import get_db
from app.services.event_service import EventService
from app.schemas.event_schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventFilter,
    EventListResponse,
    PaginationParams,
    EventSortField,
    SortOrder,
    BulkEventCreate,
    BulkEventResponse,
    EventExportRequest,
    EventType,
    TimeFrame,
    CandleData
)
from app.config import settings

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Event not found"}}
)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db)
) -> EventResponse:
    """
    Create a new resistance event.
    
    - **event_type**: Type of event detected
    - **instrument**: Trading instrument (e.g., EUR_USD)
    - **timeframe**: Data timeframe
    - **event_timestamp**: When the event occurred
    - **resistance_level**: Detected resistance level
    - **rebound_amplitude**: Size of the rebound
    - **rebound_percentage**: Rebound as percentage
    - **green_candle**: Green candle OHLC data
    - **red_candle**: Red candle OHLC data
    """
    if not settings.FEATURE_FLAGS.get('api_v1_enabled', True):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API is currently disabled"
        )
    
    service = EventService(db)
    event = await service.create_event(event_data)
    
    return EventResponse.model_validate(event)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> EventResponse:
    """
    Get a specific event by ID.
    
    Returns detailed information about a single resistance event.
    """
    service = EventService(db)
    event = await service.get_event(event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    return EventResponse.model_validate(event)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    update_data: EventUpdate,
    db: AsyncSession = Depends(get_db)
) -> EventResponse:
    """
    Update an existing event.
    
    Only metadata, notes, and tags can be updated.
    Market data fields are immutable.
    """
    service = EventService(db)
    event = await service.update_event(event_id, update_data)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    return EventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete an event.
    
    Permanently removes the event from the database.
    """
    service = EventService(db)
    deleted = await service.delete_event(event_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )


@router.get("/", response_model=EventListResponse)
async def list_events(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: EventSortField = Query(EventSortField.EVENT_TIMESTAMP, description="Sort field"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order"),
    
    # Filter parameters
    event_type: Optional[List[EventType]] = Query(None, description="Filter by event types"),
    instrument: Optional[List[str]] = Query(None, description="Filter by instruments"),
    timeframe: Optional[List[TimeFrame]] = Query(None, description="Filter by timeframes"),
    
    # Date range
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    
    # Value ranges
    min_resistance_level: Optional[float] = Query(None, description="Minimum resistance level"),
    max_resistance_level: Optional[float] = Query(None, description="Maximum resistance level"),
    min_rebound_percentage: Optional[float] = Query(None, description="Minimum rebound percentage"),
    max_rebound_percentage: Optional[float] = Query(None, description="Maximum rebound percentage"),
    
    # Time filters
    day_of_week: Optional[List[int]] = Query(None, description="Filter by days of week (0=Monday)"),
    hour_of_day: Optional[List[int]] = Query(None, description="Filter by hours of day"),
    
    db: AsyncSession = Depends(get_db)
) -> EventListResponse:
    """
    List events with advanced filtering and pagination.
    
    Supports filtering by:
    - Event type, instrument, timeframe
    - Date range
    - Resistance level range
    - Rebound percentage range
    - Day of week and hour of day
    
    Results are paginated and can be sorted by various fields.
    """
    # Build filter object
    filters = EventFilter(
        event_type=event_type,
        instrument=instrument,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        min_resistance_level=Decimal(str(min_resistance_level)) if min_resistance_level else None,
        max_resistance_level=Decimal(str(max_resistance_level)) if max_resistance_level else None,
        min_rebound_percentage=min_rebound_percentage,
        max_rebound_percentage=max_rebound_percentage,
        day_of_week=day_of_week,
        hour_of_day=hour_of_day
    )
    
    # Build pagination object
    pagination = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    service = EventService(db)
    events, total_count = await service.list_events(filters, pagination)
    
    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size
    
    return EventListResponse(
        items=[EventResponse.model_validate(event) for event in events],
        total=total_count,
        page=page,
        page_size=page_size,
        pages=total_pages
    )


@router.post("/bulk", response_model=BulkEventResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_events(
    bulk_data: BulkEventCreate,
    db: AsyncSession = Depends(get_db)
) -> BulkEventResponse:
    """
    Bulk create multiple events.
    
    Accepts up to 1000 events in a single request.
    Returns information about successfully created events and any errors.
    """
    if not settings.FEATURE_FLAGS.get('api_v1_enabled', True):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API is currently disabled"
        )
    
    service = EventService(db)
    created_events, errors = await service.bulk_create_events(bulk_data.events)
    
    return BulkEventResponse(
        created=len(created_events),
        failed=len(errors),
        errors=errors,
        event_ids=[event.id for event in created_events]
    )


@router.post("/export")
async def export_events(
    export_request: EventExportRequest,
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    Export events in various formats.
    
    Supports CSV, JSON, and Excel formats.
    Can apply filters before export.
    """
    service = EventService(db)
    events, _ = await service.list_events(export_request.filters)
    
    if export_request.format == "csv":
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                'id', 'event_type', 'instrument', 'timeframe',
                'event_timestamp', 'resistance_level', 'rebound_amplitude',
                'rebound_percentage', 'green_open', 'green_high', 'green_low',
                'green_close', 'red_open', 'red_high', 'red_low', 'red_close',
                'day_of_week', 'hour_of_day', 'detected_at'
            ]
        )
        writer.writeheader()
        
        for event in events:
            writer.writerow({
                'id': str(event.id),
                'event_type': event.event_type,
                'instrument': event.instrument,
                'timeframe': event.timeframe,
                'event_timestamp': event.event_timestamp.isoformat(),
                'resistance_level': float(event.resistance_level),
                'rebound_amplitude': float(event.rebound_amplitude),
                'rebound_percentage': event.rebound_percentage,
                'green_open': float(event.green_open),
                'green_high': float(event.green_high),
                'green_low': float(event.green_low),
                'green_close': float(event.green_close),
                'red_open': float(event.red_open),
                'red_high': float(event.red_high),
                'red_low': float(event.red_low),
                'red_close': float(event.red_close),
                'day_of_week': event.day_of_week,
                'hour_of_day': event.hour_of_day,
                'detected_at': event.detected_at.isoformat()
            })
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=events_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    
    elif export_request.format == "json":
        # Create JSON export
        export_data = []
        for event in events:
            event_dict = {
                'id': str(event.id),
                'event_type': event.event_type,
                'instrument': event.instrument,
                'timeframe': event.timeframe,
                'event_timestamp': event.event_timestamp.isoformat(),
                'resistance_level': float(event.resistance_level),
                'rebound_amplitude': float(event.rebound_amplitude),
                'rebound_percentage': event.rebound_percentage,
                'green_candle': {
                    'open': float(event.green_open),
                    'high': float(event.green_high),
                    'low': float(event.green_low),
                    'close': float(event.green_close),
                    'volume': event.green_volume
                },
                'red_candle': {
                    'open': float(event.red_open),
                    'high': float(event.red_high),
                    'low': float(event.red_low),
                    'close': float(event.red_close),
                    'volume': event.red_volume
                },
                'day_of_week': event.day_of_week,
                'hour_of_day': event.hour_of_day,
                'detected_at': event.detected_at.isoformat()
            }
            
            if export_request.include_metadata:
                event_dict['atr_value'] = float(event.atr_value) if event.atr_value else None
                event_dict['rebound_in_atr'] = event.rebound_in_atr
                event_dict['processing_latency_ms'] = event.processing_latency_ms
            
            export_data.append(event_dict)
        
        json_output = json.dumps(export_data, indent=2)
        
        return StreamingResponse(
            io.BytesIO(json_output.encode()),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=events_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported export format: {export_request.format}"
        )


@router.get("/search/by-resistance-level")
async def search_by_resistance_level(
    level: float = Query(..., description="Resistance level to search for"),
    tolerance: float = Query(0.0010, description="Tolerance for level matching (default 10 pips)"),
    instrument: Optional[str] = Query(None, description="Filter by instrument"),
    db: AsyncSession = Depends(get_db)
) -> List[EventResponse]:
    """
    Search for events near a specific resistance level.
    
    Finds all events where the resistance level is within the specified tolerance.
    Useful for identifying clusters of resistance at specific price levels.
    """
    min_level = Decimal(str(level - tolerance))
    max_level = Decimal(str(level + tolerance))
    
    filters = EventFilter(
        min_resistance_level=min_level,
        max_resistance_level=max_level,
        instrument=[instrument] if instrument else None
    )
    
    service = EventService(db)
    events, _ = await service.list_events(filters)
    
    return [EventResponse.model_validate(event) for event in events]


@router.get("/recent")
async def get_recent_events(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    instrument: Optional[str] = Query(None, description="Filter by instrument"),
    db: AsyncSession = Depends(get_db)
) -> List[EventResponse]:
    """
    Get recent events from the last N hours.
    
    Quick access to the most recent market events.
    Maximum lookback is 168 hours (1 week).
    """
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(hours=hours)
    
    filters = EventFilter(
        start_date=start_date,
        instrument=[instrument] if instrument else None
    )
    
    pagination = PaginationParams(
        page=1,
        page_size=100,
        sort_by=EventSortField.EVENT_TIMESTAMP,
        sort_order=SortOrder.DESC
    )
    
    service = EventService(db)
    events, _ = await service.list_events(filters, pagination)
    
    return [EventResponse.model_validate(event) for event in events]