"""
SQLAlchemy model for Batch Processing Jobs
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum as SQLEnum, Text, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database import Base


class JobStatus(str, enum.Enum):
    """Batch job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class JobType(str, enum.Enum):
    """Batch job type enumeration"""
    HISTORICAL_BACKFILL = "historical_backfill"
    RESISTANCE_DETECTION = "resistance_detection"
    DATA_VALIDATION = "data_validation"
    REPROCESSING = "reprocessing"


class BatchJob(Base):
    """
    SQLAlchemy model for batch processing jobs.
    Tracks job execution, progress, and allows for resumable processing.
    """
    __tablename__ = "batch_jobs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job identification
    job_type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.PENDING)
    
    # Job configuration
    instruments = Column(JSON, nullable=False)  # List of instruments to process
    timeframes = Column(JSON, nullable=False)  # List of timeframes to process
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Processing configuration
    batch_size = Column(Integer, nullable=False, default=500)
    concurrency_limit = Column(Integer, nullable=False, default=4)
    priority = Column(Integer, nullable=False, default=5)  # 1-10, higher is more priority
    
    # Progress tracking
    total_items = Column(Integer, nullable=False, default=0)
    processed_items = Column(Integer, nullable=False, default=0)
    failed_items = Column(Integer, nullable=False, default=0)
    progress_percentage = Column(Float, nullable=False, default=0.0)
    
    # Resumable state
    checkpoint_data = Column(JSON)  # Store resumable state (last processed item, etc.)
    last_processed_timestamp = Column(DateTime(timezone=True))
    last_processed_instrument = Column(String(10))
    last_processed_timeframe = Column(String(5))
    
    # Performance metrics
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    processing_time_seconds = Column(Float)
    items_per_second = Column(Float)
    average_latency_ms = Column(Float)
    
    # Error handling
    error_message = Column(Text)
    error_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Results summary
    events_detected = Column(Integer, default=0)
    events_stored = Column(Integer, default=0)
    data_quality_score = Column(Float)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True))
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # cron expression if recurring
    
    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Indexes for query performance
    __table_args__ = (
        Index('idx_batch_jobs_status', 'status'),
        Index('idx_batch_jobs_type_status', 'job_type', 'status'),
        Index('idx_batch_jobs_created_at', 'created_at'),
        Index('idx_batch_jobs_priority_status', 'priority', 'status'),
        Index('idx_batch_jobs_scheduled_at', 'scheduled_at'),
    )
    
    def __repr__(self):
        return f"<BatchJob(id={self.id}, type={self.job_type}, status={self.status}, progress={self.progress_percentage:.1f}%)>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'job_type': self.job_type.value if self.job_type else None,
            'status': self.status.value if self.status else None,
            'instruments': self.instruments,
            'timeframes': self.timeframes,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'batch_size': self.batch_size,
            'concurrency_limit': self.concurrency_limit,
            'priority': self.priority,
            'progress': {
                'total_items': self.total_items,
                'processed_items': self.processed_items,
                'failed_items': self.failed_items,
                'percentage': self.progress_percentage
            },
            'performance': {
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'processing_time_seconds': self.processing_time_seconds,
                'items_per_second': self.items_per_second,
                'average_latency_ms': self.average_latency_ms
            },
            'results': {
                'events_detected': self.events_detected,
                'events_stored': self.events_stored,
                'data_quality_score': self.data_quality_score
            },
            'error_info': {
                'error_message': self.error_message,
                'error_count': self.error_count,
                'retry_count': self.retry_count
            } if self.error_message else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def update_progress(self, processed: int = 0, failed: int = 0):
        """Update job progress"""
        self.processed_items += processed
        self.failed_items += failed
        if self.total_items > 0:
            self.progress_percentage = (self.processed_items / self.total_items) * 100
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.retry_count < self.max_retries
    
    def is_resumable(self) -> bool:
        """Check if job is in a resumable state"""
        return self.status in [JobStatus.FAILED, JobStatus.PAUSED] and self.checkpoint_data is not None


class BatchJobLog(Base):
    """
    Detailed logging for batch job execution
    """
    __tablename__ = "batch_job_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Log details
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional structured data
    
    # Context
    instrument = Column(String(10))
    timeframe = Column(String(5))
    item_index = Column(Integer)
    
    # Indexes
    __table_args__ = (
        Index('idx_batch_job_logs_job_id', 'job_id'),
        Index('idx_batch_job_logs_timestamp', 'timestamp'),
        Index('idx_batch_job_logs_level', 'level'),
    )