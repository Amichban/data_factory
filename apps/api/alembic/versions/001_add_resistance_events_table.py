"""Add resistance events table

Revision ID: 001
Revises: 
Create Date: 2025-08-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE eventtype AS ENUM ('new_resistance', 'new_support')")
    op.execute("CREATE TYPE timeframe AS ENUM ('H1', 'H4', 'D', 'W')")
    
    # Create resistance_events table
    op.create_table(
        'resistance_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.Enum('new_resistance', 'new_support', name='eventtype'), nullable=False),
        sa.Column('instrument', sa.String(length=10), nullable=False),
        sa.Column('timeframe', sa.Enum('H1', 'H4', 'D', 'W', name='timeframe'), nullable=False),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('green_open', sa.Float(), nullable=False),
        sa.Column('green_high', sa.Float(), nullable=False),
        sa.Column('green_low', sa.Float(), nullable=False),
        sa.Column('green_close', sa.Float(), nullable=False),
        sa.Column('green_volume', sa.Float(), nullable=True),
        sa.Column('red_open', sa.Float(), nullable=False),
        sa.Column('red_high', sa.Float(), nullable=False),
        sa.Column('red_low', sa.Float(), nullable=False),
        sa.Column('red_close', sa.Float(), nullable=False),
        sa.Column('red_volume', sa.Float(), nullable=True),
        sa.Column('resistance_level', sa.Float(), nullable=False),
        sa.Column('rebound_amplitude', sa.Float(), nullable=False),
        sa.Column('rebound_percentage', sa.Float(), nullable=False),
        sa.Column('atr_value', sa.Float(), nullable=True),
        sa.Column('rebound_in_atr', sa.Float(), nullable=True),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('hour_of_day', sa.Integer(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processing_latency_ms', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_resistance_events')
    )
    
    # Create indexes
    op.create_index('idx_resistance_events_instrument_timeframe', 'resistance_events', ['instrument', 'timeframe'], unique=False)
    op.create_index('idx_resistance_events_timestamp', 'resistance_events', ['event_timestamp'], unique=False)
    op.create_index('idx_resistance_events_instrument_timestamp', 'resistance_events', ['instrument', 'event_timestamp'], unique=False)
    op.create_index('idx_resistance_events_created_at', 'resistance_events', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_resistance_events_created_at', table_name='resistance_events')
    op.drop_index('idx_resistance_events_instrument_timestamp', table_name='resistance_events')
    op.drop_index('idx_resistance_events_timestamp', table_name='resistance_events')
    op.drop_index('idx_resistance_events_instrument_timeframe', table_name='resistance_events')
    
    # Drop table
    op.drop_table('resistance_events')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS timeframe")
    op.execute("DROP TYPE IF EXISTS eventtype")