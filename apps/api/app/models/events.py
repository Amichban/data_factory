"""
Event Detection System - Database Models
"""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import (
    Column, String, DateTime, Numeric, Integer, 
    ForeignKey, Index, CheckConstraint, Enum, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class NewResistanceEvent(Base):
    """Model for new resistance events detected in market data"""
    __tablename__ = "new_resistance_events"
    
    # Primary key
    original_event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Event properties
    event_type = Column(String(20), nullable=False, default='new_resistance')
    event_creation_date = Column(DateTime(timezone=True), nullable=False)
    granularity = Column(String(2), nullable=False)
    instrument = Column(String(10), nullable=False)
    
    # Price levels
    event_price_level = Column(Numeric(18, 6), nullable=False)
    atr_at_event = Column(Numeric(18, 6), nullable=False)
    volume_at_event = Column(Numeric(18, 2), nullable=True)
    
    # Rebound metrics
    new_resistance_negative_rebound = Column(Numeric(18, 6), nullable=False)
    new_resistance_negative_rebound_in_atr = Column(Numeric(18, 6), nullable=False)
    
    # Time properties
    day_of_week = Column(Integer, nullable=False)
    hour_of_day = Column(Integer, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    master_entry = relationship("SupportResistanceMaster", back_populates="resistance_event", uselist=False)
    features = relationship("ResistanceFeatures", back_populates="event", uselist=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('granularity IN (\'W\', \'D\', \'H4\', \'H1\')', name='check_granularity'),
        CheckConstraint('event_price_level > 0', name='check_positive_price'),
        CheckConstraint('atr_at_event > 0', name='check_positive_atr'),
        CheckConstraint('new_resistance_negative_rebound <= 0', name='check_negative_rebound'),
        CheckConstraint('day_of_week BETWEEN 0 AND 6', name='check_day_of_week'),
        CheckConstraint('hour_of_day BETWEEN 0 AND 23', name='check_hour_of_day'),
        Index('idx_events_instrument_granularity', 'instrument', 'granularity'),
        Index('idx_events_creation_date', 'event_creation_date'),
        Index('idx_events_price_level', 'event_price_level'),
    )


class SupportResistanceMaster(Base):
    """Master table for all support and resistance levels"""
    __tablename__ = "support_and_resistance_master"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    original_event_id = Column(UUID(as_uuid=True), ForeignKey('new_resistance_events.original_event_id'), nullable=False)
    event_type = Column(String(20), nullable=False)
    
    # Level tracking
    last_test_date = Column(DateTime(timezone=True), nullable=True)
    test_count = Column(Integer, default=0)
    breach_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default='active')
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resistance_event = relationship("NewResistanceEvent", back_populates="master_entry")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('status IN (\'active\', \'breached\', \'expired\')', name='check_status'),
    )


class ResistanceFeatures(Base):
    """Calculated features for resistance events"""
    __tablename__ = "resistance_features"
    
    feature_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('new_resistance_events.original_event_id'), nullable=False)
    feature_set_version = Column(Integer, default=1)
    
    # Distance features
    distance_from_last = Column(Numeric(18, 6), nullable=True)
    distance_in_atr = Column(Numeric(18, 6), nullable=True)
    distance_velocity = Column(Numeric(18, 6), nullable=True)
    
    # Time features
    time_between_events_hours = Column(Numeric(18, 2), nullable=True)
    time_since_last_hours = Column(Numeric(18, 2), nullable=True)
    frequency_pattern = Column(String(20), nullable=True)
    
    # Pattern features
    pattern_3_level = Column(String(3), nullable=True)
    pattern_4_level = Column(String(4), nullable=True)
    pattern_5_level = Column(String(5), nullable=True)
    pattern_6_level = Column(String(6), nullable=True)
    
    # Volume features
    volume_roc = Column(Numeric(18, 6), nullable=True)
    volume_trend = Column(String(20), nullable=True)
    
    # Advanced features
    urgency_level = Column(Integer, nullable=True)
    confidence_score = Column(Numeric(5, 4), nullable=True)
    
    # Rolling aggregations
    count_last_30 = Column(Integer, nullable=True)
    avg_distance_last_30 = Column(Numeric(18, 6), nullable=True)
    volatility_last_30 = Column(Numeric(18, 6), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("NewResistanceEvent", back_populates="features")
    
    # Indexes
    __table_args__ = (
        Index('idx_features_event', 'event_id'),
        Index('idx_features_version', 'feature_set_version'),
    )


class ProcessingState(Base):
    """Track processing state for each instrument/granularity"""
    __tablename__ = "processing_state"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    instrument = Column(String(10), nullable=False)
    granularity = Column(String(2), nullable=False)
    
    # Processing timestamps
    last_processed = Column(DateTime(timezone=True), nullable=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    consecutive_failures = Column(Integer, default=0)
    total_events_detected = Column(Integer, default=0)
    
    # Checkpoint data
    checkpoint_data = Column(String, nullable=True)  # JSON string for flexibility
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        Index('idx_processing_state', 'instrument', 'granularity', unique=True),
    )