"""
Pydantic schemas for Event Management REST API

Provides request/response models for event CRUD operations, filtering, and statistics.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID


class EventType(str, Enum):
    """Event type enumeration"""
    RESISTANCE_BOUNCE = "resistance_bounce"
    SUPPORT_BOUNCE = "support_bounce"
    BREAKOUT = "breakout"
    BREAKDOWN = "breakdown"
    SPIKE = "spike"


class TimeFrame(str, Enum):
    """Timeframe enumeration"""
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D = "D"
    W = "W"
    M = "M"


class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


class EventSortField(str, Enum):
    """Fields available for event sorting"""
    EVENT_TIMESTAMP = "event_timestamp"
    DETECTED_AT = "detected_at"
    RESISTANCE_LEVEL = "resistance_level"
    REBOUND_AMPLITUDE = "rebound_amplitude"
    REBOUND_PERCENTAGE = "rebound_percentage"
    INSTRUMENT = "instrument"
    TIMEFRAME = "timeframe"


class CandleData(BaseModel):
    """Candle OHLC data"""
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="High price")
    low: Decimal = Field(..., description="Low price")
    close: Decimal = Field(..., description="Closing price")
    volume: Optional[int] = Field(None, description="Trading volume")
    
    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: float(v)}
    )


class EventBase(BaseModel):
    """Base event schema"""
    event_type: EventType = Field(..., description="Type of event detected")
    instrument: str = Field(..., description="Trading instrument (e.g., EUR_USD)")
    timeframe: TimeFrame = Field(..., description="Data timeframe")
    event_timestamp: datetime = Field(..., description="When the event occurred in market data")
    
    resistance_level: Decimal = Field(..., description="Detected resistance level")
    rebound_amplitude: Decimal = Field(..., description="Size of the rebound")
    rebound_percentage: float = Field(..., description="Rebound as percentage")
    
    green_candle: CandleData = Field(..., description="Green candle data")
    red_candle: CandleData = Field(..., description="Red candle data")
    
    atr_value: Optional[Decimal] = Field(None, description="Average True Range value")
    rebound_in_atr: Optional[float] = Field(None, description="Rebound expressed in ATR units")
    
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday)")
    hour_of_day: int = Field(..., ge=0, le=23, description="Hour of day")
    
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
    )


class EventCreate(EventBase):
    """Schema for creating a new event"""
    pass


class EventUpdate(BaseModel):
    """Schema for updating an event"""
    metadata: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class EventInDB(EventBase):
    """Event schema with database fields"""
    id: UUID = Field(..., description="Event unique identifier")
    detected_at: datetime = Field(..., description="When the event was detected by the system")
    processing_latency_ms: Optional[float] = Field(None, description="Detection latency in milliseconds")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: lambda v: str(v),
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
    )


class EventResponse(EventInDB):
    """Event response schema for API"""
    pass


class EventFilter(BaseModel):
    """Advanced filtering options for events"""
    # Basic filters
    event_type: Optional[List[EventType]] = Field(None, description="Filter by event types")
    instrument: Optional[List[str]] = Field(None, description="Filter by instruments")
    timeframe: Optional[List[TimeFrame]] = Field(None, description="Filter by timeframes")
    
    # Date range filters
    start_date: Optional[datetime] = Field(None, description="Start of date range")
    end_date: Optional[datetime] = Field(None, description="End of date range")
    
    # Value range filters
    min_resistance_level: Optional[Decimal] = Field(None, description="Minimum resistance level")
    max_resistance_level: Optional[Decimal] = Field(None, description="Maximum resistance level")
    min_rebound_percentage: Optional[float] = Field(None, description="Minimum rebound percentage")
    max_rebound_percentage: Optional[float] = Field(None, description="Maximum rebound percentage")
    
    # Time filters
    day_of_week: Optional[List[int]] = Field(None, description="Filter by days of week")
    hour_of_day: Optional[List[int]] = Field(None, description="Filter by hours of day")
    
    # Metadata filters
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    has_notes: Optional[bool] = Field(None, description="Filter events with/without notes")
    
    @field_validator('day_of_week')
    def validate_day_of_week(cls, v):
        if v:
            for day in v:
                if not 0 <= day <= 6:
                    raise ValueError(f"Day of week must be between 0 and 6, got {day}")
        return v
    
    @field_validator('hour_of_day')
    def validate_hour_of_day(cls, v):
        if v:
            for hour in v:
                if not 0 <= hour <= 23:
                    raise ValueError(f"Hour of day must be between 0 and 23, got {hour}")
        return v
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
    )


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")
    sort_by: EventSortField = Field(EventSortField.EVENT_TIMESTAMP, description="Sort field")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")


class EventListResponse(BaseModel):
    """Paginated event list response"""
    items: List[EventResponse] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    
    model_config = ConfigDict(
        json_encoders={
            UUID: lambda v: str(v),
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
    )


class EventStatistics(BaseModel):
    """Event statistics schema"""
    total_events: int = Field(..., description="Total number of events")
    events_by_type: Dict[str, int] = Field(..., description="Event count by type")
    events_by_instrument: Dict[str, int] = Field(..., description="Event count by instrument")
    events_by_timeframe: Dict[str, int] = Field(..., description="Event count by timeframe")
    
    avg_rebound_percentage: float = Field(..., description="Average rebound percentage")
    avg_rebound_amplitude: float = Field(..., description="Average rebound amplitude")
    
    most_active_hour: Optional[int] = Field(None, description="Hour with most events")
    most_active_day: Optional[int] = Field(None, description="Day with most events")
    
    date_range: Dict[str, Optional[datetime]] = Field(..., description="Date range of events")
    
    top_resistance_levels: List[Dict[str, Any]] = Field(..., description="Top resistance levels by frequency")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class TimeSeriesPoint(BaseModel):
    """Time series data point"""
    timestamp: datetime = Field(..., description="Point timestamp")
    value: float = Field(..., description="Point value")
    count: int = Field(..., description="Number of events")
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class EventTimeSeries(BaseModel):
    """Event time series data"""
    interval: str = Field(..., description="Time interval (hour, day, week)")
    data: List[TimeSeriesPoint] = Field(..., description="Time series data points")
    total_events: int = Field(..., description="Total events in series")
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class EventAggregation(BaseModel):
    """Event aggregation request"""
    group_by: List[str] = Field(..., description="Fields to group by")
    metrics: List[str] = Field(..., description="Metrics to calculate")
    filters: Optional[EventFilter] = Field(None, description="Filters to apply")
    
    @field_validator('group_by')
    def validate_group_by(cls, v):
        valid_fields = ['event_type', 'instrument', 'timeframe', 'day_of_week', 'hour_of_day']
        for field in v:
            if field not in valid_fields:
                raise ValueError(f"Invalid group_by field: {field}")
        return v
    
    @field_validator('metrics')
    def validate_metrics(cls, v):
        valid_metrics = ['count', 'avg_rebound', 'max_rebound', 'min_rebound', 'avg_resistance']
        for metric in v:
            if metric not in valid_metrics:
                raise ValueError(f"Invalid metric: {metric}")
        return v


class EventAggregationResponse(BaseModel):
    """Event aggregation response"""
    groups: List[Dict[str, Any]] = Field(..., description="Aggregated groups")
    total_groups: int = Field(..., description="Total number of groups")
    query: EventAggregation = Field(..., description="Original aggregation query")
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class BulkEventCreate(BaseModel):
    """Schema for bulk event creation"""
    events: List[EventCreate] = Field(..., min_length=1, max_length=1000, description="Events to create")


class BulkEventResponse(BaseModel):
    """Response for bulk event creation"""
    created: int = Field(..., description="Number of events created")
    failed: int = Field(..., description="Number of events that failed")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error details for failed events")
    event_ids: List[UUID] = Field(..., description="IDs of created events")
    
    model_config = ConfigDict(
        json_encoders={UUID: lambda v: str(v)}
    )


class EventExportRequest(BaseModel):
    """Request for exporting events"""
    format: str = Field("csv", pattern="^(csv|json|excel)$", description="Export format")
    filters: Optional[EventFilter] = Field(None, description="Filters to apply")
    include_metadata: bool = Field(False, description="Include metadata in export")
    compress: bool = Field(False, description="Compress the export file")


class EventHealthCheck(BaseModel):
    """Event service health check response"""
    status: str = Field(..., description="Service status")
    total_events: int = Field(..., description="Total events in database")
    latest_event: Optional[datetime] = Field(None, description="Timestamp of latest event")
    database_connected: bool = Field(..., description="Database connection status")
    processing_enabled: bool = Field(..., description="Event processing status")
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat() if v else None}
    )