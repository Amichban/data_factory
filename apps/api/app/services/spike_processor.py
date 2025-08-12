"""
Real-time Spike Detection Processor

Processes live market data streams for immediate resistance event detection.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Callable
import time
import structlog
from collections import deque

from app.core.streaming import (
    StreamProcessor,
    StreamBuffer,
    CircuitBreaker,
    RetryPolicy,
    CircuitBreakerConfig
)
from app.algorithms.resistance_detector import ResistanceDetector
from app.services.event_processor import EventProcessor
from app.models.market_data import MarketDataCandle, TimeFrame
from app.models.resistance_event import ResistanceEvent
from app.database import AsyncSessionLocal
from app.config import settings

logger = structlog.get_logger(__name__)


class SpikeDetectionMetrics:
    """
    Metrics tracker for spike detection performance.
    """
    
    def __init__(self):
        self.total_candles_received = 0
        self.total_events_detected = 0
        self.total_notifications_sent = 0
        self.processing_latencies = deque(maxlen=100)  # Keep last 100 latencies
        self.detection_latencies = deque(maxlen=100)
        self.last_update = datetime.utcnow()
        self.start_time = datetime.utcnow()
    
    def record_candle(self):
        """Record a received candle"""
        self.total_candles_received += 1
        self.last_update = datetime.utcnow()
    
    def record_event(self, latency_ms: float):
        """Record a detected event with latency"""
        self.total_events_detected += 1
        self.detection_latencies.append(latency_ms)
    
    def record_notification(self, latency_ms: float):
        """Record a sent notification with latency"""
        self.total_notifications_sent += 1
        self.processing_latencies.append(latency_ms)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'total_candles_received': self.total_candles_received,
            'total_events_detected': self.total_events_detected,
            'total_notifications_sent': self.total_notifications_sent,
            'avg_detection_latency_ms': sum(self.detection_latencies) / len(self.detection_latencies) if self.detection_latencies else 0,
            'avg_processing_latency_ms': sum(self.processing_latencies) / len(self.processing_latencies) if self.processing_latencies else 0,
            'max_detection_latency_ms': max(self.detection_latencies) if self.detection_latencies else 0,
            'candles_per_second': self.total_candles_received / uptime if uptime > 0 else 0,
            'events_per_minute': (self.total_events_detected / uptime) * 60 if uptime > 0 else 0,
            'last_update': self.last_update.isoformat(),
            'uptime_seconds': uptime
        }


class SpikeProcessor(StreamProcessor):
    """
    Real-time spike detection processor for live market data.
    Detects resistance events with <5 second latency requirement.
    """
    
    def __init__(
        self,
        instruments: Optional[List[str]] = None,
        timeframes: Optional[List[str]] = None,
        notification_callback: Optional[Callable] = None
    ):
        """
        Initialize spike processor.
        
        Args:
            instruments: List of instruments to monitor
            timeframes: List of timeframes to process
            notification_callback: Callback for event notifications
        """
        super().__init__(name="spike_processor")
        
        # Configuration
        self.instruments = instruments or settings.SUPPORTED_INSTRUMENTS
        self.timeframes = [TimeFrame(tf) for tf in (timeframes or ["H1", "H4"])]
        self.notification_callback = notification_callback
        
        # Core components
        self.detector = ResistanceDetector()
        self.event_processor = EventProcessor()
        self.buffer = StreamBuffer(max_size=500)
        self.metrics = SpikeDetectionMetrics()
        
        # Circuit breaker for data source
        self.circuit_breaker = CircuitBreaker(
            name="market_data_stream",
            config=CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                success_threshold=2,
                timeout=10.0
            )
        )
        
        # Retry policy for notifications
        self.retry_policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.5,
            max_delay=5.0
        )
        
        # State tracking
        self.last_candles: Dict[str, Dict[str, MarketDataCandle]] = {}
        self.active_streams: Set[str] = set()
        self._running = False
        self._tasks: List[asyncio.Task] = []
    
    async def start(self):
        """Start the spike processor"""
        if self._running:
            logger.warning("Spike processor already running")
            return
        
        # Check feature flag
        if not settings.FEATURE_FLAGS.get('spike_detection_enabled', False):
            logger.warning("Spike detection is disabled via feature flag")
            return
        
        self._running = True
        logger.info(
            "Starting spike processor",
            instruments=len(self.instruments),
            timeframes=[tf.value for tf in self.timeframes]
        )
        
        # Start processing tasks
        for instrument in self.instruments:
            for timeframe in self.timeframes:
                task = asyncio.create_task(
                    self._process_stream(instrument, timeframe)
                )
                self._tasks.append(task)
        
        # Start buffer processor
        buffer_task = asyncio.create_task(self._process_buffer())
        self._tasks.append(buffer_task)
        
        # Start metrics reporter
        metrics_task = asyncio.create_task(self._report_metrics())
        self._tasks.append(metrics_task)
    
    async def stop(self):
        """Stop the spike processor"""
        if not self._running:
            return
        
        logger.info("Stopping spike processor")
        self._running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        logger.info(
            "Spike processor stopped",
            metrics=self.metrics.get_stats()
        )
    
    async def _process_stream(self, instrument: str, timeframe: TimeFrame):
        """
        Process market data stream for a specific instrument and timeframe.
        
        Args:
            instrument: Trading instrument
            timeframe: Data timeframe
        """
        stream_key = f"{instrument}_{timeframe.value}"
        self.active_streams.add(stream_key)
        
        logger.info(f"Starting stream processor for {stream_key}")
        
        try:
            while self._running:
                try:
                    # Simulate receiving market data (replace with actual data source)
                    candle = await self._fetch_latest_candle(instrument, timeframe)
                    
                    if candle:
                        # Record metrics
                        self.metrics.record_candle()
                        
                        # Process candle for resistance detection
                        await self._process_candle(instrument, timeframe, candle)
                    
                    # Wait for next candle (adjust based on timeframe)
                    await asyncio.sleep(self._get_poll_interval(timeframe))
                    
                except Exception as e:
                    logger.error(
                        f"Error processing stream {stream_key}",
                        error=str(e),
                        exc_info=True
                    )
                    await asyncio.sleep(5)  # Brief pause on error
        
        finally:
            self.active_streams.discard(stream_key)
            logger.info(f"Stream processor stopped for {stream_key}")
    
    async def _process_candle(
        self,
        instrument: str,
        timeframe: TimeFrame,
        candle: MarketDataCandle
    ):
        """
        Process a single candle for spike detection.
        
        Args:
            instrument: Trading instrument
            timeframe: Data timeframe
            candle: Market data candle
        """
        start_time = time.time()
        
        # Initialize tracking if needed
        if instrument not in self.last_candles:
            self.last_candles[instrument] = {}
        
        # Get previous candle
        prev_candle = self.last_candles[instrument].get(timeframe.value)
        
        if prev_candle:
            # Detect resistance event
            event = self.detector.process_single_candle_pair(
                prev_candle=prev_candle,
                curr_candle=candle,
                instrument=instrument,
                timeframe=timeframe,
                atr_value=None  # Could calculate if needed
            )
            
            if event:
                detection_latency_ms = (time.time() - start_time) * 1000
                self.metrics.record_event(detection_latency_ms)
                
                # Add to buffer for batch processing
                await self.buffer.add({
                    'event': event,
                    'detected_at': datetime.utcnow(),
                    'latency_ms': detection_latency_ms
                })
                
                # Send immediate notification if enabled
                if settings.FEATURE_FLAGS.get('real_time_notifications', False):
                    await self._send_notification(event, detection_latency_ms)
                
                logger.info(
                    "Spike detected",
                    instrument=instrument,
                    timeframe=timeframe.value,
                    resistance_level=event['resistance_level'],
                    latency_ms=detection_latency_ms
                )
        
        # Update last candle
        self.last_candles[instrument][timeframe.value] = candle
    
    async def _process_buffer(self):
        """Process buffered events for storage"""
        while self._running:
            try:
                # Get batch from buffer
                batch = await self.buffer.get_batch(10)
                
                if batch:
                    # Store events in database
                    stored_count = 0
                    for item in batch:
                        try:
                            await self._store_event(item['event'])
                            stored_count += 1
                        except Exception as e:
                            logger.error(
                                "Failed to store event",
                                error=str(e),
                                exc_info=True
                            )
                    
                    if stored_count > 0:
                        logger.debug(f"Stored {stored_count} events from buffer")
                
                await asyncio.sleep(1)  # Process buffer every second
                
            except Exception as e:
                logger.error(
                    "Error processing buffer",
                    error=str(e),
                    exc_info=True
                )
                await asyncio.sleep(5)
    
    async def _store_event(self, event_data: Dict[str, Any]):
        """Store event in database"""
        async with AsyncSessionLocal() as session:
            event = ResistanceEvent(
                event_type=event_data['event_type'],
                instrument=event_data['instrument'],
                timeframe=event_data['timeframe'],
                event_timestamp=event_data['event_timestamp'],
                green_open=event_data['green_open'],
                green_high=event_data['green_high'],
                green_low=event_data['green_low'],
                green_close=event_data['green_close'],
                green_volume=event_data.get('green_volume'),
                red_open=event_data['red_open'],
                red_high=event_data['red_high'],
                red_low=event_data['red_low'],
                red_close=event_data['red_close'],
                red_volume=event_data.get('red_volume'),
                resistance_level=event_data['resistance_level'],
                rebound_amplitude=event_data['rebound_amplitude'],
                rebound_percentage=event_data['rebound_percentage'],
                atr_value=event_data.get('atr_value'),
                rebound_in_atr=event_data.get('rebound_in_atr'),
                day_of_week=event_data['day_of_week'],
                hour_of_day=event_data['hour_of_day'],
                detected_at=event_data['detected_at'],
                processing_latency_ms=event_data.get('processing_latency_ms')
            )
            
            session.add(event)
            await session.commit()
    
    async def _send_notification(self, event: Dict[str, Any], latency_ms: float):
        """
        Send real-time notification for detected event.
        
        Args:
            event: Detected event data
            latency_ms: Detection latency in milliseconds
        """
        notification_start = time.time()
        
        try:
            # Use retry policy for notifications
            await self.retry_policy.execute(
                self._deliver_notification,
                event,
                latency_ms
            )
            
            notification_latency = (time.time() - notification_start) * 1000
            self.metrics.record_notification(notification_latency)
            
            # Check if we meet <5 second requirement
            total_latency = latency_ms + notification_latency
            if total_latency > 5000:
                logger.warning(
                    "Latency requirement exceeded",
                    total_latency_ms=total_latency,
                    detection_ms=latency_ms,
                    notification_ms=notification_latency
                )
        
        except Exception as e:
            logger.error(
                "Failed to send notification after retries",
                error=str(e),
                exc_info=True
            )
    
    async def _deliver_notification(self, event: Dict[str, Any], latency_ms: float):
        """
        Deliver notification (actual implementation).
        
        Args:
            event: Event data
            latency_ms: Detection latency
        """
        if self.notification_callback:
            await self.notification_callback({
                'type': 'resistance_event',
                'data': event,
                'metadata': {
                    'detection_latency_ms': latency_ms,
                    'timestamp': datetime.utcnow().isoformat()
                }
            })
    
    async def _fetch_latest_candle(
        self,
        instrument: str,
        timeframe: TimeFrame
    ) -> Optional[MarketDataCandle]:
        """
        Fetch latest candle from market data source.
        
        Args:
            instrument: Trading instrument
            timeframe: Data timeframe
            
        Returns:
            Latest market data candle or None
        """
        # This is a placeholder - replace with actual market data source
        # For now, return None to simulate no new data
        return None
    
    def _get_poll_interval(self, timeframe: TimeFrame) -> float:
        """
        Get polling interval based on timeframe.
        
        Args:
            timeframe: Data timeframe
            
        Returns:
            Polling interval in seconds
        """
        intervals = {
            TimeFrame.H1: 60,    # Check every minute for hourly
            TimeFrame.H4: 300,   # Check every 5 minutes for 4-hour
            TimeFrame.D: 900,    # Check every 15 minutes for daily
            TimeFrame.W: 3600,   # Check every hour for weekly
        }
        return intervals.get(timeframe, 60)
    
    async def _report_metrics(self):
        """Periodically report metrics"""
        while self._running:
            try:
                await asyncio.sleep(30)  # Report every 30 seconds
                
                stats = self.metrics.get_stats()
                buffer_stats = self.buffer.get_stats()
                circuit_state = self.circuit_breaker.get_state()
                
                logger.info(
                    "Spike processor metrics",
                    detection_stats=stats,
                    buffer_stats=buffer_stats,
                    circuit_breaker=circuit_state,
                    active_streams=len(self.active_streams)
                )
                
            except Exception as e:
                logger.error(
                    "Error reporting metrics",
                    error=str(e),
                    exc_info=True
                )
    
    async def _process_item(self, item: Any) -> Any:
        """
        Process a stream item (implements base class method).
        
        Args:
            item: Stream item to process
            
        Returns:
            Processed result
        """
        # This method is called by the base StreamProcessor
        if isinstance(item, MarketDataCandle):
            # Determine instrument and timeframe from candle
            await self._process_candle(
                instrument=item.instrument,
                timeframe=item.timeframe,
                candle=item
            )
        return item
    
    def get_status(self) -> Dict[str, Any]:
        """Get current processor status"""
        return {
            'running': self._running,
            'active_streams': list(self.active_streams),
            'metrics': self.metrics.get_stats(),
            'buffer': self.buffer.get_stats(),
            'circuit_breaker': self.circuit_breaker.get_state(),
            'last_candles_count': sum(
                len(tfs) for tfs in self.last_candles.values()
            )
        }


# Global spike processor instance
_spike_processor: Optional[SpikeProcessor] = None


async def get_spike_processor(
    instruments: Optional[List[str]] = None,
    timeframes: Optional[List[str]] = None,
    notification_callback: Optional[Callable] = None
) -> SpikeProcessor:
    """Get or create the global spike processor instance"""
    global _spike_processor
    
    if _spike_processor is None:
        _spike_processor = SpikeProcessor(
            instruments=instruments,
            timeframes=timeframes,
            notification_callback=notification_callback
        )
    
    return _spike_processor


async def start_spike_detection(
    instruments: Optional[List[str]] = None,
    timeframes: Optional[List[str]] = None
):
    """Start spike detection processing"""
    processor = await get_spike_processor(
        instruments=instruments,
        timeframes=timeframes
    )
    await processor.start()
    return processor


async def stop_spike_detection():
    """Stop spike detection processing"""
    global _spike_processor
    if _spike_processor:
        await _spike_processor.stop()
        _spike_processor = None