"""
Market Data Models
Defines Pydantic models for market data ingestion and validation
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator


class TimeFrame(str, Enum):
    """Supported timeframes for market data"""
    H1 = "H1"
    H4 = "H4"
    D = "D"  
    W = "W"


class DataMode(str, Enum):
    """Data ingestion modes"""
    BATCH = "batch"      # Historical data backfill
    STREAM = "stream"    # Real-time streaming
    SPIKE = "spike"      # On-demand spike processing


class MarketDataCandle(BaseModel):
    """Individual market data candle/bar"""
    instrument: str = Field(..., description="Trading instrument (e.g., EUR_USD)")
    timestamp: datetime = Field(..., description="Candle timestamp")
    timeframe: TimeFrame = Field(..., description="Data timeframe")
    
    # OHLC data
    open: Decimal = Field(..., description="Opening price", decimal_places=5)
    high: Decimal = Field(..., description="High price", decimal_places=5)
    low: Decimal = Field(..., description="Low price", decimal_places=5)
    close: Decimal = Field(..., description="Closing price", decimal_places=5)
    
    # Volume data
    volume: Optional[int] = Field(None, description="Trading volume")
    
    # Metadata
    complete: bool = Field(True, description="Whether candle is complete")
    data_source: str = Field("oanda", description="Data source provider")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('instrument')
    def validate_instrument(cls, v):
        """Validate instrument format"""
        if not v or '_' not in v:
            raise ValueError('Instrument must be in format CCY_CCY (e.g., EUR_USD)')
        parts = v.split('_')
        if len(parts) != 2 or len(parts[0]) != 3 or len(parts[1]) != 3:
            raise ValueError('Instrument must be in format CCY_CCY with 3-letter currency codes')
        return v.upper()
    
    @validator('open', 'high', 'low', 'close')
    def validate_prices(cls, v):
        """Validate price values are positive"""
        if v <= 0:
            raise ValueError('Price values must be positive')
        return v
    
    @validator('high')
    def validate_high_price(cls, v, values):
        """Validate high price is highest"""
        if 'open' in values and v < values['open']:
            raise ValueError('High price cannot be less than open price')
        if 'low' in values and v < values['low']:
            raise ValueError('High price cannot be less than low price')
        if 'close' in values and v < values['close']:
            raise ValueError('High price cannot be less than close price')
        return v
    
    @validator('low')  
    def validate_low_price(cls, v, values):
        """Validate low price is lowest"""
        if 'open' in values and v > values['open']:
            raise ValueError('Low price cannot be greater than open price')
        if 'close' in values and v > values['close']:
            raise ValueError('Low price cannot be greater than close price')
        return v


class MarketDataBatch(BaseModel):
    """Batch of market data candles"""
    instrument: str
    timeframe: TimeFrame
    candles: List[MarketDataCandle]
    total_count: int = Field(..., description="Total number of candles in batch")
    start_time: datetime = Field(..., description="Start time of batch")
    end_time: datetime = Field(..., description="End time of batch")
    
    @validator('candles')
    def validate_candles_not_empty(cls, v):
        """Ensure candles list is not empty"""
        if not v:
            raise ValueError('Candles list cannot be empty')
        return v
    
    @validator('total_count')
    def validate_total_count(cls, v, values):
        """Validate total count matches candles length"""
        if 'candles' in values and v != len(values['candles']):
            raise ValueError('Total count must match number of candles')
        return v


class DataIngestionRequest(BaseModel):
    """Request model for data ingestion"""
    instruments: List[str] = Field(..., description="List of instruments to ingest")
    timeframes: List[TimeFrame] = Field(..., description="List of timeframes to ingest")
    mode: DataMode = Field(..., description="Ingestion mode")
    
    # For historical data
    start_date: Optional[datetime] = Field(None, description="Start date for historical data")
    end_date: Optional[datetime] = Field(None, description="End date for historical data")
    
    # Processing options
    force_refresh: bool = Field(False, description="Force refresh existing data")
    validate_data: bool = Field(True, description="Enable data validation")
    store_raw: bool = Field(False, description="Store raw API responses")
    
    @validator('instruments')
    def validate_instruments(cls, v):
        """Validate instruments list"""
        if not v:
            raise ValueError('Instruments list cannot be empty')
        # Import here to avoid circular imports
        from app.config import settings
        invalid = [inst for inst in v if inst not in settings.SUPPORTED_INSTRUMENTS]
        if invalid:
            raise ValueError(f'Unsupported instruments: {invalid}')
        return v
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate end date is after start date"""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v


class DataIngestionResponse(BaseModel):
    """Response model for data ingestion"""
    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field(..., description="Ingestion status")
    message: str = Field(..., description="Status message")
    
    # Statistics
    instruments_processed: int = Field(0, description="Number of instruments processed")
    candles_ingested: int = Field(0, description="Number of candles ingested")
    candles_updated: int = Field(0, description="Number of candles updated")
    candles_failed: int = Field(0, description="Number of candles that failed validation")
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    processing_time_seconds: Optional[float] = Field(None, description="Total processing time")
    
    # Error handling
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")


class DataQualityMetrics(BaseModel):
    """Data quality metrics for market data"""
    instrument: str
    timeframe: TimeFrame
    total_candles: int
    complete_candles: int
    missing_periods: int
    duplicate_periods: int
    price_gaps: int
    volume_anomalies: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def completeness_ratio(self) -> float:
        """Calculate data completeness ratio"""
        if self.total_candles == 0:
            return 0.0
        return self.complete_candles / self.total_candles
    
    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-1)"""
        if self.total_candles == 0:
            return 0.0
        
        # Weighted quality score
        completeness = self.completeness_ratio
        missing_penalty = min(self.missing_periods / self.total_candles, 0.2)
        duplicate_penalty = min(self.duplicate_periods / self.total_candles, 0.1)
        gap_penalty = min(self.price_gaps / self.total_candles, 0.1)
        
        return max(0.0, completeness - missing_penalty - duplicate_penalty - gap_penalty)


class RateLimitStatus(BaseModel):
    """Rate limiting status"""
    requests_made: int
    requests_remaining: int
    reset_time: datetime
    current_window_start: datetime
    is_limited: bool = False
    
    @property
    def usage_percentage(self) -> float:
        """Calculate usage percentage"""
        total = self.requests_made + self.requests_remaining
        if total == 0:
            return 0.0
        return (self.requests_made / total) * 100


class DataSourceStatus(BaseModel):
    """Data source health status"""
    source_name: str
    is_available: bool
    last_check: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    rate_limit_status: Optional[RateLimitStatus] = None