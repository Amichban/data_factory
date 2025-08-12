"""
Event Service Layer for Event Management REST API

Provides business logic for event CRUD operations, filtering, aggregation, and statistics.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import structlog
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.resistance_event import ResistanceEvent
from app.schemas.event_schemas import (
    EventCreate,
    EventUpdate,
    EventFilter,
    PaginationParams,
    EventSortField,
    SortOrder,
    EventStatistics,
    EventTimeSeries,
    TimeSeriesPoint,
    EventAggregation,
    EventType,
    TimeFrame
)
from app.database import AsyncSessionLocal

logger = structlog.get_logger(__name__)


class EventService:
    """
    Service layer for event management operations.
    Handles business logic for CRUD, filtering, and analytics.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize event service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def create_event(self, event_data: EventCreate) -> ResistanceEvent:
        """
        Create a new event.
        
        Args:
            event_data: Event creation data
            
        Returns:
            Created event
        """
        try:
            # Create event instance
            event = ResistanceEvent(
                event_type=event_data.event_type.value,
                instrument=event_data.instrument,
                timeframe=event_data.timeframe.value,
                event_timestamp=event_data.event_timestamp,
                green_open=event_data.green_candle.open,
                green_high=event_data.green_candle.high,
                green_low=event_data.green_candle.low,
                green_close=event_data.green_candle.close,
                green_volume=event_data.green_candle.volume,
                red_open=event_data.red_candle.open,
                red_high=event_data.red_candle.high,
                red_low=event_data.red_candle.low,
                red_close=event_data.red_candle.close,
                red_volume=event_data.red_candle.volume,
                resistance_level=event_data.resistance_level,
                rebound_amplitude=event_data.rebound_amplitude,
                rebound_percentage=event_data.rebound_percentage,
                atr_value=event_data.atr_value,
                rebound_in_atr=event_data.rebound_in_atr,
                day_of_week=event_data.day_of_week,
                hour_of_day=event_data.hour_of_day,
                detected_at=datetime.utcnow()
            )
            
            self.session.add(event)
            await self.session.commit()
            await self.session.refresh(event)
            
            logger.info(
                "Event created",
                event_id=str(event.id),
                instrument=event.instrument,
                event_type=event.event_type
            )
            
            return event
            
        except Exception as e:
            await self.session.rollback()
            logger.error("Failed to create event", error=str(e))
            raise
    
    async def get_event(self, event_id: UUID) -> Optional[ResistanceEvent]:
        """
        Get event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Event if found, None otherwise
        """
        query = select(ResistanceEvent).where(ResistanceEvent.id == event_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update_event(
        self,
        event_id: UUID,
        update_data: EventUpdate
    ) -> Optional[ResistanceEvent]:
        """
        Update an event.
        
        Args:
            event_id: Event ID
            update_data: Update data
            
        Returns:
            Updated event if found, None otherwise
        """
        event = await self.get_event(event_id)
        if not event:
            return None
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(event, field, value)
        
        event.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(event)
        
        logger.info("Event updated", event_id=str(event_id))
        return event
    
    async def delete_event(self, event_id: UUID) -> bool:
        """
        Delete an event.
        
        Args:
            event_id: Event ID
            
        Returns:
            True if deleted, False if not found
        """
        event = await self.get_event(event_id)
        if not event:
            return False
        
        await self.session.delete(event)
        await self.session.commit()
        
        logger.info("Event deleted", event_id=str(event_id))
        return True
    
    async def list_events(
        self,
        filters: Optional[EventFilter] = None,
        pagination: Optional[PaginationParams] = None
    ) -> Tuple[List[ResistanceEvent], int]:
        """
        List events with filtering and pagination.
        
        Args:
            filters: Filter criteria
            pagination: Pagination parameters
            
        Returns:
            Tuple of (events, total_count)
        """
        # Base query
        query = select(ResistanceEvent)
        
        # Apply filters
        if filters:
            conditions = []
            
            # Event type filter
            if filters.event_type:
                conditions.append(
                    ResistanceEvent.event_type.in_([et.value for et in filters.event_type])
                )
            
            # Instrument filter
            if filters.instrument:
                conditions.append(ResistanceEvent.instrument.in_(filters.instrument))
            
            # Timeframe filter
            if filters.timeframe:
                conditions.append(
                    ResistanceEvent.timeframe.in_([tf.value for tf in filters.timeframe])
                )
            
            # Date range filter
            if filters.start_date:
                conditions.append(ResistanceEvent.event_timestamp >= filters.start_date)
            if filters.end_date:
                conditions.append(ResistanceEvent.event_timestamp <= filters.end_date)
            
            # Value range filters
            if filters.min_resistance_level is not None:
                conditions.append(ResistanceEvent.resistance_level >= filters.min_resistance_level)
            if filters.max_resistance_level is not None:
                conditions.append(ResistanceEvent.resistance_level <= filters.max_resistance_level)
            if filters.min_rebound_percentage is not None:
                conditions.append(ResistanceEvent.rebound_percentage >= filters.min_rebound_percentage)
            if filters.max_rebound_percentage is not None:
                conditions.append(ResistanceEvent.rebound_percentage <= filters.max_rebound_percentage)
            
            # Time filters
            if filters.day_of_week:
                conditions.append(ResistanceEvent.day_of_week.in_(filters.day_of_week))
            if filters.hour_of_day:
                conditions.append(ResistanceEvent.hour_of_day.in_(filters.hour_of_day))
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar() or 0
        
        # Apply sorting
        if pagination:
            # Map sort field to column
            sort_column_map = {
                EventSortField.EVENT_TIMESTAMP: ResistanceEvent.event_timestamp,
                EventSortField.DETECTED_AT: ResistanceEvent.detected_at,
                EventSortField.RESISTANCE_LEVEL: ResistanceEvent.resistance_level,
                EventSortField.REBOUND_AMPLITUDE: ResistanceEvent.rebound_amplitude,
                EventSortField.REBOUND_PERCENTAGE: ResistanceEvent.rebound_percentage,
                EventSortField.INSTRUMENT: ResistanceEvent.instrument,
                EventSortField.TIMEFRAME: ResistanceEvent.timeframe,
            }
            
            sort_column = sort_column_map.get(
                pagination.sort_by,
                ResistanceEvent.event_timestamp
            )
            
            if pagination.sort_order == SortOrder.ASC:
                query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(sort_column))
            
            # Apply pagination
            offset = (pagination.page - 1) * pagination.page_size
            query = query.offset(offset).limit(pagination.page_size)
        else:
            # Default sorting
            query = query.order_by(desc(ResistanceEvent.event_timestamp))
        
        # Execute query
        result = await self.session.execute(query)
        events = result.scalars().all()
        
        return events, total_count
    
    async def get_statistics(
        self,
        filters: Optional[EventFilter] = None
    ) -> EventStatistics:
        """
        Get event statistics.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Event statistics
        """
        # Build base query with filters
        query = select(ResistanceEvent)
        if filters:
            query = self._apply_filters(query, filters)
        
        # Get all events for statistics
        result = await self.session.execute(query)
        events = result.scalars().all()
        
        if not events:
            return EventStatistics(
                total_events=0,
                events_by_type={},
                events_by_instrument={},
                events_by_timeframe={},
                avg_rebound_percentage=0.0,
                avg_rebound_amplitude=0.0,
                most_active_hour=None,
                most_active_day=None,
                date_range={'start': None, 'end': None},
                top_resistance_levels=[]
            )
        
        # Calculate statistics
        total_events = len(events)
        
        # Count by type
        events_by_type = {}
        for event in events:
            events_by_type[event.event_type] = events_by_type.get(event.event_type, 0) + 1
        
        # Count by instrument
        events_by_instrument = {}
        for event in events:
            events_by_instrument[event.instrument] = events_by_instrument.get(event.instrument, 0) + 1
        
        # Count by timeframe
        events_by_timeframe = {}
        for event in events:
            events_by_timeframe[event.timeframe] = events_by_timeframe.get(event.timeframe, 0) + 1
        
        # Calculate averages
        avg_rebound_percentage = sum(e.rebound_percentage for e in events) / total_events
        avg_rebound_amplitude = sum(float(e.rebound_amplitude) for e in events) / total_events
        
        # Find most active hour
        hours = {}
        for event in events:
            hours[event.hour_of_day] = hours.get(event.hour_of_day, 0) + 1
        most_active_hour = max(hours.keys(), key=hours.get) if hours else None
        
        # Find most active day
        days = {}
        for event in events:
            days[event.day_of_week] = days.get(event.day_of_week, 0) + 1
        most_active_day = max(days.keys(), key=days.get) if days else None
        
        # Get date range
        timestamps = [e.event_timestamp for e in events]
        date_range = {
            'start': min(timestamps) if timestamps else None,
            'end': max(timestamps) if timestamps else None
        }
        
        # Top resistance levels
        resistance_counts = {}
        for event in events:
            level = float(event.resistance_level)
            # Round to 4 decimal places for grouping
            level_key = round(level, 4)
            if level_key not in resistance_counts:
                resistance_counts[level_key] = {
                    'level': level_key,
                    'count': 0,
                    'instruments': set()
                }
            resistance_counts[level_key]['count'] += 1
            resistance_counts[level_key]['instruments'].add(event.instrument)
        
        # Get top 10 resistance levels
        top_levels = sorted(
            resistance_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        # Convert sets to lists for JSON serialization
        for level in top_levels:
            level['instruments'] = list(level['instruments'])
        
        return EventStatistics(
            total_events=total_events,
            events_by_type=events_by_type,
            events_by_instrument=events_by_instrument,
            events_by_timeframe=events_by_timeframe,
            avg_rebound_percentage=avg_rebound_percentage,
            avg_rebound_amplitude=avg_rebound_amplitude,
            most_active_hour=most_active_hour,
            most_active_day=most_active_day,
            date_range=date_range,
            top_resistance_levels=top_levels
        )
    
    async def get_time_series(
        self,
        interval: str = "day",
        filters: Optional[EventFilter] = None
    ) -> EventTimeSeries:
        """
        Get event time series data.
        
        Args:
            interval: Time interval (hour, day, week)
            filters: Optional filters
            
        Returns:
            Time series data
        """
        # Build query with filters
        query = select(ResistanceEvent)
        if filters:
            query = self._apply_filters(query, filters)
        
        result = await self.session.execute(query)
        events = result.scalars().all()
        
        if not events:
            return EventTimeSeries(
                interval=interval,
                data=[],
                total_events=0
            )
        
        # Group events by interval
        time_buckets = {}
        
        for event in events:
            # Determine bucket based on interval
            if interval == "hour":
                bucket = event.event_timestamp.replace(minute=0, second=0, microsecond=0)
            elif interval == "day":
                bucket = event.event_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            elif interval == "week":
                # Start of week (Monday)
                days_since_monday = event.event_timestamp.weekday()
                bucket = event.event_timestamp.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) - timedelta(days=days_since_monday)
            else:
                bucket = event.event_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if bucket not in time_buckets:
                time_buckets[bucket] = {
                    'count': 0,
                    'total_rebound': 0.0
                }
            
            time_buckets[bucket]['count'] += 1
            time_buckets[bucket]['total_rebound'] += event.rebound_percentage
        
        # Create time series points
        data_points = []
        for timestamp, metrics in sorted(time_buckets.items()):
            avg_rebound = metrics['total_rebound'] / metrics['count'] if metrics['count'] > 0 else 0
            data_points.append(
                TimeSeriesPoint(
                    timestamp=timestamp,
                    value=avg_rebound,
                    count=metrics['count']
                )
            )
        
        return EventTimeSeries(
            interval=interval,
            data=data_points,
            total_events=len(events)
        )
    
    async def aggregate_events(
        self,
        aggregation: EventAggregation
    ) -> Dict[str, Any]:
        """
        Perform custom aggregation on events.
        
        Args:
            aggregation: Aggregation parameters
            
        Returns:
            Aggregated results
        """
        # Build base query with filters
        query = select(ResistanceEvent)
        if aggregation.filters:
            query = self._apply_filters(query, aggregation.filters)
        
        result = await self.session.execute(query)
        events = result.scalars().all()
        
        if not events:
            return {
                'groups': [],
                'total_groups': 0
            }
        
        # Group events
        groups = {}
        for event in events:
            # Create group key
            group_key = []
            for field in aggregation.group_by:
                if field == 'event_type':
                    group_key.append(event.event_type)
                elif field == 'instrument':
                    group_key.append(event.instrument)
                elif field == 'timeframe':
                    group_key.append(event.timeframe)
                elif field == 'day_of_week':
                    group_key.append(event.day_of_week)
                elif field == 'hour_of_day':
                    group_key.append(event.hour_of_day)
            
            group_key_str = '|'.join(str(k) for k in group_key)
            
            if group_key_str not in groups:
                groups[group_key_str] = {
                    'key': dict(zip(aggregation.group_by, group_key)),
                    'events': []
                }
            
            groups[group_key_str]['events'].append(event)
        
        # Calculate metrics for each group
        aggregated_groups = []
        for group_data in groups.values():
            group_metrics = group_data['key'].copy()
            group_events = group_data['events']
            
            for metric in aggregation.metrics:
                if metric == 'count':
                    group_metrics['count'] = len(group_events)
                elif metric == 'avg_rebound':
                    group_metrics['avg_rebound'] = sum(
                        e.rebound_percentage for e in group_events
                    ) / len(group_events)
                elif metric == 'max_rebound':
                    group_metrics['max_rebound'] = max(
                        e.rebound_percentage for e in group_events
                    )
                elif metric == 'min_rebound':
                    group_metrics['min_rebound'] = min(
                        e.rebound_percentage for e in group_events
                    )
                elif metric == 'avg_resistance':
                    group_metrics['avg_resistance'] = sum(
                        float(e.resistance_level) for e in group_events
                    ) / len(group_events)
            
            aggregated_groups.append(group_metrics)
        
        # Sort by count (descending)
        aggregated_groups.sort(key=lambda x: x.get('count', 0), reverse=True)
        
        return {
            'groups': aggregated_groups,
            'total_groups': len(aggregated_groups)
        }
    
    async def bulk_create_events(
        self,
        events_data: List[EventCreate]
    ) -> Tuple[List[ResistanceEvent], List[Dict[str, Any]]]:
        """
        Bulk create events.
        
        Args:
            events_data: List of event creation data
            
        Returns:
            Tuple of (created_events, errors)
        """
        created_events = []
        errors = []
        
        for idx, event_data in enumerate(events_data):
            try:
                event = await self.create_event(event_data)
                created_events.append(event)
            except Exception as e:
                errors.append({
                    'index': idx,
                    'error': str(e),
                    'data': event_data.model_dump()
                })
                logger.error(f"Failed to create event at index {idx}", error=str(e))
        
        logger.info(
            f"Bulk event creation completed",
            created=len(created_events),
            failed=len(errors)
        )
        
        return created_events, errors
    
    def _apply_filters(self, query, filters: EventFilter):
        """
        Apply filters to a query.
        
        Args:
            query: SQLAlchemy query
            filters: Filter criteria
            
        Returns:
            Query with filters applied
        """
        conditions = []
        
        if filters.event_type:
            conditions.append(
                ResistanceEvent.event_type.in_([et.value for et in filters.event_type])
            )
        
        if filters.instrument:
            conditions.append(ResistanceEvent.instrument.in_(filters.instrument))
        
        if filters.timeframe:
            conditions.append(
                ResistanceEvent.timeframe.in_([tf.value for tf in filters.timeframe])
            )
        
        if filters.start_date:
            conditions.append(ResistanceEvent.event_timestamp >= filters.start_date)
        if filters.end_date:
            conditions.append(ResistanceEvent.event_timestamp <= filters.end_date)
        
        if filters.min_resistance_level is not None:
            conditions.append(ResistanceEvent.resistance_level >= filters.min_resistance_level)
        if filters.max_resistance_level is not None:
            conditions.append(ResistanceEvent.resistance_level <= filters.max_resistance_level)
        
        if filters.min_rebound_percentage is not None:
            conditions.append(ResistanceEvent.rebound_percentage >= filters.min_rebound_percentage)
        if filters.max_rebound_percentage is not None:
            conditions.append(ResistanceEvent.rebound_percentage <= filters.max_rebound_percentage)
        
        if filters.day_of_week:
            conditions.append(ResistanceEvent.day_of_week.in_(filters.day_of_week))
        if filters.hour_of_day:
            conditions.append(ResistanceEvent.hour_of_day.in_(filters.hour_of_day))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return query


async def get_event_service() -> EventService:
    """Get event service instance with database session"""
    async with AsyncSessionLocal() as session:
        return EventService(session)