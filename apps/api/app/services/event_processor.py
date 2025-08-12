"""
Event Processor Service

Handles the processing and storage of resistance events detected by the algorithm.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import structlog
import uuid

from app.algorithms.resistance_detector import ResistanceDetector
from app.models.resistance_event import ResistanceEvent, EventType, TimeFrame
from app.models.market_data import MarketDataCandle
from app.database import AsyncSessionLocal
from app.config import settings

logger = structlog.get_logger(__name__)


class EventProcessor:
    """
    Service for processing and persisting resistance events.
    Coordinates between the detection algorithm and database storage.
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize the event processor.
        
        Args:
            db_session: Optional database session to use
        """
        self.detector = ResistanceDetector()
        self.db_session = db_session
        self._processing_stats = {
            'events_processed': 0,
            'events_stored': 0,
            'events_failed': 0,
            'last_processing_time': None
        }
    
    async def process_market_data_batch(
        self,
        candles: List[MarketDataCandle],
        instrument: str,
        timeframe: TimeFrame
    ) -> Dict[str, Any]:
        """
        Process a batch of market data candles for resistance events.
        
        Args:
            candles: List of market data candles
            instrument: Trading instrument
            timeframe: Timeframe of the data
            
        Returns:
            Processing result summary
        """
        start_time = datetime.utcnow()
        
        # Check feature flag
        feature_enabled = settings.FEATURE_FLAGS.get('resistance_detection_enabled', False)
        if not feature_enabled:
            logger.info("Resistance detection feature is disabled")
            return {
                'status': 'skipped',
                'reason': 'feature_disabled',
                'instrument': instrument,
                'timeframe': timeframe.value
            }
        
        try:
            # Detect resistance events
            detected_events = self.detector.detect_resistance_events(
                candles=candles,
                instrument=instrument,
                timeframe=timeframe,
                feature_flag_enabled=feature_enabled
            )
            
            if not detected_events:
                logger.info(
                    "No resistance events detected",
                    instrument=instrument,
                    timeframe=timeframe.value,
                    candles_processed=len(candles)
                )
                return {
                    'status': 'success',
                    'instrument': instrument,
                    'timeframe': timeframe.value,
                    'candles_processed': len(candles),
                    'events_detected': 0,
                    'events_stored': 0
                }
            
            # Store events in database
            stored_events = await self._store_events(detected_events)
            
            # Update processing stats
            self._processing_stats['events_processed'] += len(detected_events)
            self._processing_stats['events_stored'] += len(stored_events)
            self._processing_stats['events_failed'] += len(detected_events) - len(stored_events)
            self._processing_stats['last_processing_time'] = datetime.utcnow()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                "Market data batch processed successfully",
                instrument=instrument,
                timeframe=timeframe.value,
                candles_processed=len(candles),
                events_detected=len(detected_events),
                events_stored=len(stored_events),
                processing_time_seconds=processing_time
            )
            
            return {
                'status': 'success',
                'instrument': instrument,
                'timeframe': timeframe.value,
                'candles_processed': len(candles),
                'events_detected': len(detected_events),
                'events_stored': len(stored_events),
                'processing_time_seconds': processing_time,
                'stored_event_ids': [str(event.id) for event in stored_events]
            }
            
        except Exception as e:
            logger.error(
                "Error processing market data batch",
                instrument=instrument,
                timeframe=timeframe.value,
                error=str(e),
                exc_info=True
            )
            return {
                'status': 'error',
                'instrument': instrument,
                'timeframe': timeframe.value,
                'error': str(e)
            }
    
    async def _store_events(self, events: List[Dict[str, Any]]) -> List[ResistanceEvent]:
        """
        Store detected events in the database.
        
        Args:
            events: List of event dictionaries from the detector
            
        Returns:
            List of stored ResistanceEvent objects
        """
        stored_events = []
        
        # Use provided session or create new one
        if self.db_session:
            session = self.db_session
            should_close = False
        else:
            session = AsyncSessionLocal()
            should_close = True
        
        try:
            for event_data in events:
                try:
                    # Check if event already exists (avoid duplicates)
                    existing = await self._check_duplicate_event(
                        session=session,
                        instrument=event_data['instrument'],
                        timeframe=event_data['timeframe'],
                        timestamp=event_data['event_timestamp']
                    )
                    
                    if existing:
                        logger.debug(
                            "Skipping duplicate event",
                            instrument=event_data['instrument'],
                            timeframe=event_data['timeframe'].value,
                            timestamp=event_data['event_timestamp'].isoformat()
                        )
                        continue
                    
                    # Create new resistance event
                    event = ResistanceEvent(
                        event_type=event_data['event_type'],
                        instrument=event_data['instrument'],
                        timeframe=event_data['timeframe'],
                        event_timestamp=event_data['event_timestamp'],
                        green_open=event_data['green_open'],
                        green_high=event_data['green_high'],
                        green_low=event_data['green_low'],
                        green_close=event_data['green_close'],
                        green_volume=event_data['green_volume'],
                        red_open=event_data['red_open'],
                        red_high=event_data['red_high'],
                        red_low=event_data['red_low'],
                        red_close=event_data['red_close'],
                        red_volume=event_data['red_volume'],
                        resistance_level=event_data['resistance_level'],
                        rebound_amplitude=event_data['rebound_amplitude'],
                        rebound_percentage=event_data['rebound_percentage'],
                        atr_value=event_data['atr_value'],
                        rebound_in_atr=event_data['rebound_in_atr'],
                        day_of_week=event_data['day_of_week'],
                        hour_of_day=event_data['hour_of_day'],
                        detected_at=event_data['detected_at'],
                        processing_latency_ms=event_data.get('processing_latency_ms')
                    )
                    
                    session.add(event)
                    stored_events.append(event)
                    
                except Exception as e:
                    logger.error(
                        "Failed to store individual event",
                        error=str(e),
                        event_timestamp=event_data.get('event_timestamp'),
                        exc_info=True
                    )
            
            # Commit all events
            await session.commit()
            
            logger.info(
                "Events stored successfully",
                count=len(stored_events)
            )
            
        except Exception as e:
            logger.error(
                "Failed to commit events to database",
                error=str(e),
                exc_info=True
            )
            await session.rollback()
            stored_events = []
            
        finally:
            if should_close:
                await session.close()
        
        return stored_events
    
    async def _check_duplicate_event(
        self,
        session: AsyncSession,
        instrument: str,
        timeframe: TimeFrame,
        timestamp: datetime
    ) -> bool:
        """
        Check if an event already exists for the given parameters.
        
        Args:
            session: Database session
            instrument: Trading instrument
            timeframe: Timeframe
            timestamp: Event timestamp
            
        Returns:
            True if duplicate exists, False otherwise
        """
        query = select(ResistanceEvent).where(
            and_(
                ResistanceEvent.instrument == instrument,
                ResistanceEvent.timeframe == timeframe,
                ResistanceEvent.event_timestamp == timestamp
            )
        )
        
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_events(
        self,
        instrument: Optional[str] = None,
        timeframe: Optional[TimeFrame] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ResistanceEvent]:
        """
        Retrieve resistance events from the database with optional filters.
        
        Args:
            instrument: Filter by instrument
            timeframe: Filter by timeframe
            start_date: Filter events after this date
            end_date: Filter events before this date
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of resistance events
        """
        async with AsyncSessionLocal() as session:
            query = select(ResistanceEvent)
            
            # Apply filters
            conditions = []
            if instrument:
                conditions.append(ResistanceEvent.instrument == instrument)
            if timeframe:
                conditions.append(ResistanceEvent.timeframe == timeframe)
            if start_date:
                conditions.append(ResistanceEvent.event_timestamp >= start_date)
            if end_date:
                conditions.append(ResistanceEvent.event_timestamp <= end_date)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # Apply ordering, limit and offset
            query = query.order_by(ResistanceEvent.event_timestamp.desc())
            query = query.limit(limit).offset(offset)
            
            result = await session.execute(query)
            events = result.scalars().all()
            
            logger.info(
                "Retrieved resistance events",
                count=len(events),
                instrument=instrument,
                timeframe=timeframe.value if timeframe else None
            )
            
            return events
    
    async def get_event_statistics(
        self,
        instrument: Optional[str] = None,
        timeframe: Optional[TimeFrame] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about resistance events.
        
        Args:
            instrument: Filter by instrument
            timeframe: Filter by timeframe
            start_date: Filter events after this date
            end_date: Filter events before this date
            
        Returns:
            Dictionary containing event statistics
        """
        async with AsyncSessionLocal() as session:
            # Base query
            query = select(
                func.count(ResistanceEvent.id).label('total_events'),
                func.avg(ResistanceEvent.rebound_amplitude).label('avg_rebound'),
                func.avg(ResistanceEvent.atr_value).label('avg_atr'),
                func.avg(ResistanceEvent.processing_latency_ms).label('avg_latency_ms')
            )
            
            # Apply filters
            conditions = []
            if instrument:
                conditions.append(ResistanceEvent.instrument == instrument)
            if timeframe:
                conditions.append(ResistanceEvent.timeframe == timeframe)
            if start_date:
                conditions.append(ResistanceEvent.event_timestamp >= start_date)
            if end_date:
                conditions.append(ResistanceEvent.event_timestamp <= end_date)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await session.execute(query)
            stats = result.one()
            
            # Get distribution by hour and day
            hour_query = select(
                ResistanceEvent.hour_of_day,
                func.count(ResistanceEvent.id).label('count')
            )
            if conditions:
                hour_query = hour_query.where(and_(*conditions))
            hour_query = hour_query.group_by(ResistanceEvent.hour_of_day)
            
            hour_result = await session.execute(hour_query)
            hour_distribution = {row.hour_of_day: row.count for row in hour_result}
            
            day_query = select(
                ResistanceEvent.day_of_week,
                func.count(ResistanceEvent.id).label('count')
            )
            if conditions:
                day_query = day_query.where(and_(*conditions))
            day_query = day_query.group_by(ResistanceEvent.day_of_week)
            
            day_result = await session.execute(day_query)
            day_distribution = {row.day_of_week: row.count for row in day_result}
            
            return {
                'total_events': stats.total_events or 0,
                'average_rebound': float(stats.avg_rebound) if stats.avg_rebound else 0,
                'average_atr': float(stats.avg_atr) if stats.avg_atr else 0,
                'average_processing_latency_ms': float(stats.avg_latency_ms) if stats.avg_latency_ms else 0,
                'hour_distribution': hour_distribution,
                'day_distribution': day_distribution,
                'most_active_hour': max(hour_distribution, key=hour_distribution.get) if hour_distribution else None,
                'most_active_day': max(day_distribution, key=day_distribution.get) if day_distribution else None,
                'filters_applied': {
                    'instrument': instrument,
                    'timeframe': timeframe.value if timeframe else None,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get current processing statistics.
        
        Returns:
            Dictionary containing processing statistics
        """
        return self._processing_stats.copy()