"""
Event Models for Resistance Event Detection System
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class Granularity(str, Enum):
    """Time granularity options"""
    H1 = "H1"  # Hourly
    H4 = "H4"  # 4-hour
    D = "D"    # Daily
    W = "W"    # Weekly


class EventType(str, Enum):
    """Event type options"""
    NEW_RESISTANCE = "new_resistance"
    NEW_SUPPORT = "new_support"  # For future implementation


class ResistanceEvent(BaseModel):
    """Resistance Event Model"""
    
    # Core fields
    original_event_id: str = Field(..., description="Unique identifier for the event")
    event_type: EventType = Field(default=EventType.NEW_RESISTANCE)
    event_creation_date: datetime = Field(..., description="UTC datetime when the event occurs")
    granularity: Granularity = Field(..., description="Time granularity")
    instrument: str = Field(..., description="Instrument symbol (e.g., EUR_USD)")
    
    # Event properties
    event_price_level: float = Field(..., description="Level at which the event happened")
    atr_at_event: float = Field(..., description="ATR level at event creation")
    volume_at_event: float = Field(..., description="Volume at event creation")
    new_resistance_negative_rebound: float = Field(..., description="Amplitude of rebound (close - high)")
    new_resistance_negative_rebound_in_atr: float = Field(..., description="Rebound in ATR terms")
    
    # Temporal properties
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    hours_of_day: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    
    # Metadata
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @validator('new_resistance_negative_rebound')
    def validate_negative_rebound(cls, v):
        if v > 0:
            raise ValueError("new_resistance_negative_rebound should be negative or zero")
        return v
    
    @validator('new_resistance_negative_rebound_in_atr')
    def validate_negative_rebound_atr(cls, v):
        if v > 0:
            raise ValueError("new_resistance_negative_rebound_in_atr should be negative or zero")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketData(BaseModel):
    """Market Data Model (OHLCV)"""
    
    instrument: str = Field(..., description="Trading pair (e.g., EUR_USD)")
    granularity: Granularity = Field(..., description="Time frame")
    timestamp: datetime = Field(..., description="Candle timestamp")
    
    # OHLCV data
    candle: Dict[str, float] = Field(..., description="OHLC candle data")
    
    # Optional bid/ask/mid prices
    bid: Optional[Dict[str, float]] = None
    ask: Optional[Dict[str, float]] = None
    mid: Optional[Dict[str, float]] = None
    
    @validator('candle')
    def validate_candle(cls, v):
        required_keys = {'open', 'high', 'low', 'close', 'volume'}
        if not all(key in v for key in required_keys):
            raise ValueError(f"Candle must contain: {required_keys}")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EventFilter(BaseModel):
    """Filter parameters for querying events"""
    
    instrument: Optional[str] = None
    granularity: Optional[Granularity] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_type: Optional[EventType] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class EventStatistics(BaseModel):
    """Statistics for resistance events"""
    
    total_events: int
    events_by_instrument: Dict[str, int]
    events_by_granularity: Dict[str, int]
    average_rebound: float
    average_atr: float
    most_active_hour: int
    most_active_day: int


class Configuration(BaseModel):
    """System configuration model"""
    
    supported_instruments: List[str] = Field(
        default=[
            "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD",
            "USD_CAD", "USD_CHF", "NZD_USD", "EUR_GBP",
            "EUR_JPY", "GBP_JPY", "AUD_JPY", "EUR_AUD",
            "EUR_CHF", "GBP_CHF", "AUD_NZD", "EUR_NZD",
            "GBP_AUD", "GBP_NZD", "USD_MXN", "USD_NOK",
            "USD_SEK", "USD_SGD", "USD_TRY", "USD_ZAR",
            "SPX500_USD", "NAS100_USD", "UK100_GBP", "DE30_EUR", "JP225_USD"
        ]
    )
    supported_granularities: List[Granularity] = Field(
        default=[Granularity.H1, Granularity.H4, Granularity.D, Granularity.W]
    )
    batch_size: int = Field(default=500, ge=1, le=10000)
    processing_concurrency: int = Field(default=4, ge=1, le=16)
    feature_flags: Dict[str, bool] = Field(
        default={
            "firestore_enabled": True,
            "market_data_enabled": False,
            "resistance_detection_enabled": False,
            "batch_processing_enabled": False,
            "spike_detection_enabled": False,
            "api_v1_enabled": True
        }
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }