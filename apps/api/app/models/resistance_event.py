"""
SQLAlchemy model for Resistance Events
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.database import Base


class EventType(str, enum.Enum):
    """Event type enumeration"""
    NEW_RESISTANCE = "new_resistance"
    NEW_SUPPORT = "new_support"


class TimeFrame(str, enum.Enum):
    """Supported timeframes"""
    H1 = "H1"
    H4 = "H4"
    D = "D"
    W = "W"


class ResistanceEvent(Base):
    """
    SQLAlchemy model for resistance events detected when a green candle
    is followed by a red candle, indicating potential resistance level
    """
    __tablename__ = "resistance_events"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    event_type = Column(SQLEnum(EventType), nullable=False, default=EventType.NEW_RESISTANCE)
    instrument = Column(String(10), nullable=False)
    timeframe = Column(SQLEnum(TimeFrame), nullable=False)
    
    # Event timestamp and candle data
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Green candle (previous) OHLC data
    green_open = Column(Float, nullable=False)
    green_high = Column(Float, nullable=False)
    green_low = Column(Float, nullable=False)
    green_close = Column(Float, nullable=False)
    green_volume = Column(Float)
    
    # Red candle (current) OHLC data  
    red_open = Column(Float, nullable=False)
    red_high = Column(Float, nullable=False)
    red_low = Column(Float, nullable=False)
    red_close = Column(Float, nullable=False)
    red_volume = Column(Float)
    
    # Calculated resistance metrics
    resistance_level = Column(Float, nullable=False)  # Typically the green candle's high
    rebound_amplitude = Column(Float, nullable=False)  # red_close - red_high (negative value)
    rebound_percentage = Column(Float, nullable=False)  # Percentage of rebound relative to range
    
    # Technical indicators at event time
    atr_value = Column(Float)  # Average True Range value
    rebound_in_atr = Column(Float)  # Rebound expressed in ATR units
    
    # Market context
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    hour_of_day = Column(Integer, nullable=False)  # 0-23
    
    # Processing metadata
    detected_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    processing_latency_ms = Column(Float)  # Time taken to detect the event
    
    # Tracking
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Indexes for query performance
    __table_args__ = (
        Index('idx_resistance_events_instrument_timeframe', 'instrument', 'timeframe'),
        Index('idx_resistance_events_timestamp', 'event_timestamp'),
        Index('idx_resistance_events_instrument_timestamp', 'instrument', 'event_timestamp'),
        Index('idx_resistance_events_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ResistanceEvent(id={self.id}, instrument={self.instrument}, timeframe={self.timeframe}, timestamp={self.event_timestamp})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'event_type': self.event_type.value if self.event_type else None,
            'instrument': self.instrument,
            'timeframe': self.timeframe.value if self.timeframe else None,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'green_candle': {
                'open': self.green_open,
                'high': self.green_high,
                'low': self.green_low,
                'close': self.green_close,
                'volume': self.green_volume
            },
            'red_candle': {
                'open': self.red_open,
                'high': self.red_high,
                'low': self.red_low,
                'close': self.red_close,
                'volume': self.red_volume
            },
            'resistance_level': self.resistance_level,
            'rebound_amplitude': self.rebound_amplitude,
            'rebound_percentage': self.rebound_percentage,
            'atr_value': self.atr_value,
            'rebound_in_atr': self.rebound_in_atr,
            'day_of_week': self.day_of_week,
            'hour_of_day': self.hour_of_day,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'processing_latency_ms': self.processing_latency_ms
        }