"""Add batch jobs tables

Revision ID: 002
Revises: 001
Create Date: 2025-08-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types for batch jobs
    op.execute("CREATE TYPE jobstatus AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled', 'paused')")
    op.execute("CREATE TYPE jobtype AS ENUM ('historical_backfill', 'resistance_detection', 'data_validation', 'reprocessing')")
    
    # Create batch_jobs table
    op.create_table(
        'batch_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_type', sa.Enum('historical_backfill', 'resistance_detection', 'data_validation', 'reprocessing', name='jobtype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', 'paused', name='jobstatus'), nullable=False),
        
        # Job configuration
        sa.Column('instruments', sa.JSON(), nullable=False),
        sa.Column('timeframes', sa.JSON(), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        
        # Processing configuration
        sa.Column('batch_size', sa.Integer(), nullable=False),
        sa.Column('concurrency_limit', sa.Integer(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        
        # Progress tracking
        sa.Column('total_items', sa.Integer(), nullable=False),
        sa.Column('processed_items', sa.Integer(), nullable=False),
        sa.Column('failed_items', sa.Integer(), nullable=False),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        
        # Resumable state
        sa.Column('checkpoint_data', sa.JSON(), nullable=True),
        sa.Column('last_processed_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_processed_instrument', sa.String(10), nullable=True),
        sa.Column('last_processed_timeframe', sa.String(5), nullable=True),
        
        # Performance metrics
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('items_per_second', sa.Float(), nullable=True),
        sa.Column('average_latency_ms', sa.Float(), nullable=True),
        
        # Error handling
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        
        # Results summary
        sa.Column('events_detected', sa.Integer(), nullable=True),
        sa.Column('events_stored', sa.Integer(), nullable=True),
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        
        # Scheduling
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=True),
        sa.Column('recurrence_pattern', sa.String(50), nullable=True),
        
        # Metadata
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id', name='pk_batch_jobs')
    )
    
    # Create indexes for batch_jobs
    op.create_index('idx_batch_jobs_status', 'batch_jobs', ['status'], unique=False)
    op.create_index('idx_batch_jobs_type_status', 'batch_jobs', ['job_type', 'status'], unique=False)
    op.create_index('idx_batch_jobs_created_at', 'batch_jobs', ['created_at'], unique=False)
    op.create_index('idx_batch_jobs_priority_status', 'batch_jobs', ['priority', 'status'], unique=False)
    op.create_index('idx_batch_jobs_scheduled_at', 'batch_jobs', ['scheduled_at'], unique=False)
    
    # Create batch_job_logs table
    op.create_table(
        'batch_job_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Log details
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        
        # Context
        sa.Column('instrument', sa.String(10), nullable=True),
        sa.Column('timeframe', sa.String(5), nullable=True),
        sa.Column('item_index', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id', name='pk_batch_job_logs')
    )
    
    # Create indexes for batch_job_logs
    op.create_index('idx_batch_job_logs_job_id', 'batch_job_logs', ['job_id'], unique=False)
    op.create_index('idx_batch_job_logs_timestamp', 'batch_job_logs', ['timestamp'], unique=False)
    op.create_index('idx_batch_job_logs_level', 'batch_job_logs', ['level'], unique=False)


def downgrade() -> None:
    # Drop indexes for batch_job_logs
    op.drop_index('idx_batch_job_logs_level', table_name='batch_job_logs')
    op.drop_index('idx_batch_job_logs_timestamp', table_name='batch_job_logs')
    op.drop_index('idx_batch_job_logs_job_id', table_name='batch_job_logs')
    
    # Drop batch_job_logs table
    op.drop_table('batch_job_logs')
    
    # Drop indexes for batch_jobs
    op.drop_index('idx_batch_jobs_scheduled_at', table_name='batch_jobs')
    op.drop_index('idx_batch_jobs_priority_status', table_name='batch_jobs')
    op.drop_index('idx_batch_jobs_created_at', table_name='batch_jobs')
    op.drop_index('idx_batch_jobs_type_status', table_name='batch_jobs')
    op.drop_index('idx_batch_jobs_status', table_name='batch_jobs')
    
    # Drop batch_jobs table
    op.drop_table('batch_jobs')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS jobtype")
    op.execute("DROP TYPE IF EXISTS jobstatus")