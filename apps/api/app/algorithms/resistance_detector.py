"""
Core Resistance Event Detection Algorithm

Detects resistance events when a green candle is followed by a red candle,
indicating potential resistance levels in the market.
"""

import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
import structlog

from app.models.market_data import MarketDataCandle, TimeFrame
from app.models.resistance_event import ResistanceEvent, EventType

logger = structlog.get_logger(__name__)


class ResistanceDetector:
    """
    Core algorithm for detecting resistance events in market data.
    
    A resistance event occurs when:
    1. Previous candle is green (close > open)
    2. Current candle is red (close < open)
    3. This indicates potential resistance at the green candle's high
    """
    
    def __init__(self, atr_period: int = 14):
        """
        Initialize the resistance detector.
        
        Args:
            atr_period: Period for ATR calculation (default 14)
        """
        self.atr_period = atr_period
        self.atr_cache: Dict[str, List[float]] = {}  # Cache ATR values per instrument
        
    def detect_resistance_events(
        self,
        candles: List[MarketDataCandle],
        instrument: str,
        timeframe: TimeFrame,
        feature_flag_enabled: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process a list of candles to detect resistance events.
        
        Args:
            candles: List of market data candles sorted by timestamp
            instrument: Trading instrument
            timeframe: Timeframe of the candles
            feature_flag_enabled: Whether resistance detection is enabled
            
        Returns:
            List of detected resistance events
        """
        if not feature_flag_enabled:
            logger.info("Resistance detection disabled by feature flag")
            return []
            
        if len(candles) < 2:
            logger.debug("Insufficient candles for resistance detection", count=len(candles))
            return []
        
        events = []
        processing_start = time.time()
        
        # Sort candles by timestamp to ensure correct order
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        
        # Calculate ATR values for the entire series
        atr_values = self._calculate_atr_series(sorted_candles)
        
        # Iterate through candles looking for green-to-red transitions
        for i in range(1, len(sorted_candles)):
            prev_candle = sorted_candles[i - 1]
            curr_candle = sorted_candles[i]
            
            # Check for resistance event pattern
            if self._is_resistance_event(prev_candle, curr_candle):
                candle_processing_start = time.time()
                
                # Get ATR value at this point
                atr_value = atr_values[i] if i < len(atr_values) else None
                
                # Create resistance event
                event = self._create_resistance_event(
                    prev_candle=prev_candle,
                    curr_candle=curr_candle,
                    instrument=instrument,
                    timeframe=timeframe,
                    atr_value=atr_value
                )
                
                # Calculate processing latency
                processing_latency_ms = (time.time() - candle_processing_start) * 1000
                event['processing_latency_ms'] = processing_latency_ms
                
                # Performance check: ensure < 100ms per candle
                if processing_latency_ms > 100:
                    logger.warning(
                        "Slow candle processing detected",
                        instrument=instrument,
                        timeframe=timeframe.value,
                        latency_ms=processing_latency_ms
                    )
                
                events.append(event)
                
                logger.info(
                    "Resistance event detected",
                    instrument=instrument,
                    timeframe=timeframe.value,
                    timestamp=curr_candle.timestamp.isoformat(),
                    resistance_level=event['resistance_level'],
                    latency_ms=processing_latency_ms
                )
        
        total_processing_time = (time.time() - processing_start) * 1000
        logger.info(
            "Resistance detection completed",
            instrument=instrument,
            timeframe=timeframe.value,
            candles_processed=len(candles),
            events_detected=len(events),
            total_time_ms=total_processing_time,
            avg_time_per_candle_ms=total_processing_time / len(candles) if candles else 0
        )
        
        return events
    
    def _is_resistance_event(self, prev_candle: MarketDataCandle, curr_candle: MarketDataCandle) -> bool:
        """
        Check if the transition from prev_candle to curr_candle represents a resistance event.
        
        Args:
            prev_candle: Previous candle (should be green)
            curr_candle: Current candle (should be red)
            
        Returns:
            True if this is a resistance event, False otherwise
        """
        # Previous candle must be green (close > open)
        is_prev_green = prev_candle.close > prev_candle.open
        
        # Current candle must be red (close < open)
        is_curr_red = curr_candle.close < curr_candle.open
        
        # Handle edge cases and market gaps
        # Check for significant time gap (more than expected for the timeframe)
        time_gap = (curr_candle.timestamp - prev_candle.timestamp).total_seconds()
        expected_gap = self._get_expected_time_gap(prev_candle.timeframe)
        
        # Allow up to 72x expected gap for weekends/holidays (72 hours for H1 over weekend)
        # This covers Friday evening to Monday morning gaps
        is_valid_gap = time_gap <= expected_gap * 72
        
        return is_prev_green and is_curr_red and is_valid_gap
    
    def _get_expected_time_gap(self, timeframe: TimeFrame) -> int:
        """
        Get expected time gap in seconds between candles for a given timeframe.
        
        Args:
            timeframe: Candle timeframe
            
        Returns:
            Expected gap in seconds
        """
        gaps = {
            TimeFrame.H1: 3600,      # 1 hour
            TimeFrame.H4: 14400,     # 4 hours
            TimeFrame.D: 86400,      # 1 day
            TimeFrame.W: 604800,     # 1 week
        }
        return gaps.get(timeframe, 3600)
    
    def _create_resistance_event(
        self,
        prev_candle: MarketDataCandle,
        curr_candle: MarketDataCandle,
        instrument: str,
        timeframe: TimeFrame,
        atr_value: Optional[float]
    ) -> Dict[str, Any]:
        """
        Create a resistance event from the candle data.
        
        Args:
            prev_candle: Green candle
            curr_candle: Red candle
            instrument: Trading instrument
            timeframe: Timeframe
            atr_value: ATR value at event time
            
        Returns:
            Dictionary representing the resistance event
        """
        # Resistance level is typically the high of the green candle
        resistance_level = float(prev_candle.high)
        
        # Calculate rebound amplitude (negative value)
        rebound_amplitude = float(curr_candle.close - curr_candle.high)
        
        # Calculate rebound percentage
        candle_range = float(curr_candle.high - curr_candle.low)
        rebound_percentage = (abs(rebound_amplitude) / candle_range * 100) if candle_range > 0 else 0
        
        # Calculate rebound in ATR terms
        rebound_in_atr = (abs(rebound_amplitude) / atr_value) if atr_value and atr_value > 0 else None
        
        # Extract time components
        day_of_week = curr_candle.timestamp.weekday()  # 0=Monday, 6=Sunday
        hour_of_day = curr_candle.timestamp.hour
        
        return {
            'event_type': EventType.NEW_RESISTANCE,
            'instrument': instrument,
            'timeframe': timeframe,
            'event_timestamp': curr_candle.timestamp,
            'green_open': float(prev_candle.open),
            'green_high': float(prev_candle.high),
            'green_low': float(prev_candle.low),
            'green_close': float(prev_candle.close),
            'green_volume': float(prev_candle.volume) if prev_candle.volume else None,
            'red_open': float(curr_candle.open),
            'red_high': float(curr_candle.high),
            'red_low': float(curr_candle.low),
            'red_close': float(curr_candle.close),
            'red_volume': float(curr_candle.volume) if curr_candle.volume else None,
            'resistance_level': resistance_level,
            'rebound_amplitude': rebound_amplitude,
            'rebound_percentage': rebound_percentage,
            'atr_value': atr_value,
            'rebound_in_atr': rebound_in_atr,
            'day_of_week': day_of_week,
            'hour_of_day': hour_of_day,
            'detected_at': datetime.utcnow()
        }
    
    def _calculate_atr_series(self, candles: List[MarketDataCandle]) -> List[float]:
        """
        Calculate ATR (Average True Range) values for a series of candles.
        
        Args:
            candles: List of candles sorted by timestamp
            
        Returns:
            List of ATR values corresponding to each candle
        """
        if not candles:
            return []
        
        atr_values = []
        true_ranges = []
        
        for i, candle in enumerate(candles):
            if i == 0:
                # First candle: TR = High - Low
                tr = float(candle.high - candle.low)
            else:
                prev_candle = candles[i - 1]
                # True Range = max of:
                # 1. Current High - Current Low
                # 2. abs(Current High - Previous Close)
                # 3. abs(Current Low - Previous Close)
                tr = max(
                    float(candle.high - candle.low),
                    abs(float(candle.high - prev_candle.close)),
                    abs(float(candle.low - prev_candle.close))
                )
            
            true_ranges.append(tr)
            
            # Calculate ATR using exponential moving average
            if i < self.atr_period - 1:
                # Not enough data for full ATR
                atr_values.append(sum(true_ranges) / len(true_ranges))
            elif i == self.atr_period - 1:
                # First full ATR calculation
                atr = sum(true_ranges[-self.atr_period:]) / self.atr_period
                atr_values.append(atr)
            else:
                # Subsequent ATR calculations using EMA
                prev_atr = atr_values[-1]
                atr = (prev_atr * (self.atr_period - 1) + tr) / self.atr_period
                atr_values.append(atr)
        
        return atr_values
    
    def process_single_candle_pair(
        self,
        prev_candle: MarketDataCandle,
        curr_candle: MarketDataCandle,
        instrument: str,
        timeframe: TimeFrame,
        atr_value: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single pair of candles for resistance detection.
        Useful for real-time processing.
        
        Args:
            prev_candle: Previous candle
            curr_candle: Current candle
            instrument: Trading instrument
            timeframe: Timeframe
            atr_value: Pre-calculated ATR value
            
        Returns:
            Resistance event if detected, None otherwise
        """
        if self._is_resistance_event(prev_candle, curr_candle):
            return self._create_resistance_event(
                prev_candle=prev_candle,
                curr_candle=curr_candle,
                instrument=instrument,
                timeframe=timeframe,
                atr_value=atr_value
            )
        return None