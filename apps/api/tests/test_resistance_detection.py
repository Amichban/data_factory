"""
Comprehensive unit tests for resistance event detection algorithm
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
import uuid

from app.algorithms.resistance_detector import ResistanceDetector
from app.services.event_processor import EventProcessor
from app.models.market_data import MarketDataCandle, TimeFrame
from app.models.resistance_event import ResistanceEvent, EventType


class TestResistanceDetector:
    """Test suite for ResistanceDetector algorithm"""
    
    @pytest.fixture
    def detector(self):
        """Create a ResistanceDetector instance"""
        return ResistanceDetector(atr_period=14)
    
    @pytest.fixture
    def sample_candles(self):
        """Create sample market data candles for testing"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        candles = []
        
        # Create a sequence with resistance events
        prices = [
            (1.1000, 1.1050, 1.0980, 1.1040),  # Green candle
            (1.1040, 1.1060, 1.1020, 1.1025),  # Red candle - resistance event
            (1.1025, 1.1035, 1.1010, 1.1030),  # Green candle
            (1.1030, 1.1040, 1.1015, 1.1020),  # Red candle - resistance event
            (1.1020, 1.1025, 1.1005, 1.1010),  # Red candle
            (1.1010, 1.1030, 1.1000, 1.1025),  # Green candle
            (1.1025, 1.1035, 1.1010, 1.1015),  # Red candle - resistance event
        ]
        
        for i, (open_p, high, low, close) in enumerate(prices):
            candle = MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time + timedelta(hours=i),
                timeframe=TimeFrame.H1,
                open=Decimal(str(open_p)),
                high=Decimal(str(high)),
                low=Decimal(str(low)),
                close=Decimal(str(close)),
                volume=100000 + i * 1000,
                complete=True,
                data_source="test"
            )
            candles.append(candle)
        
        return candles
    
    def test_detect_resistance_events_basic(self, detector, sample_candles):
        """Test basic resistance event detection"""
        events = detector.detect_resistance_events(
            candles=sample_candles,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1
        )
        
        # Should detect 3 resistance events based on sample data
        assert len(events) == 3
        
        # Verify first event
        first_event = events[0]
        assert first_event['instrument'] == "EUR_USD"
        assert first_event['timeframe'] == TimeFrame.H1
        assert first_event['event_type'] == EventType.NEW_RESISTANCE
        assert first_event['resistance_level'] == 1.1050  # High of green candle
        assert first_event['rebound_amplitude'] < 0  # Should be negative
        
    def test_detect_resistance_events_no_events(self, detector):
        """Test when no resistance events are present"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        # All green candles - no resistance events
        candles = []
        for i in range(5):
            candle = MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time + timedelta(hours=i),
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1050"),
                low=Decimal("1.0980"),
                close=Decimal("1.1040"),  # Close > Open (green)
                volume=100000,
                complete=True,
                data_source="test"
            )
            candles.append(candle)
        
        events = detector.detect_resistance_events(
            candles=candles,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1
        )
        
        assert len(events) == 0
    
    def test_detect_resistance_events_insufficient_candles(self, detector):
        """Test with insufficient candles"""
        candle = MarketDataCandle(
            instrument="EUR_USD",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            timeframe=TimeFrame.H1,
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0980"),
            close=Decimal("1.1040"),
            volume=100000,
            complete=True,
            data_source="test"
        )
        
        events = detector.detect_resistance_events(
            candles=[candle],
            instrument="EUR_USD",
            timeframe=TimeFrame.H1
        )
        
        assert len(events) == 0
    
    def test_detect_resistance_events_with_gap(self, detector):
        """Test detection with market gaps"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        candles = [
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time,
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1050"),
                low=Decimal("1.0980"),
                close=Decimal("1.1040"),  # Green
                volume=100000,
                complete=True,
                data_source="test"
            ),
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time + timedelta(hours=5),  # 5 hour gap
                timeframe=TimeFrame.H1,
                open=Decimal("1.1040"),
                high=Decimal("1.1060"),
                low=Decimal("1.1020"),
                close=Decimal("1.1025"),  # Red
                volume=100000,
                complete=True,
                data_source="test"
            )
        ]
        
        events = detector.detect_resistance_events(
            candles=candles,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1
        )
        
        # Should detect event since 5 hour gap is within allowed range (72x for weekends)
        assert len(events) == 1
    
    def test_detect_resistance_events_feature_flag_disabled(self, detector):
        """Test with feature flag disabled"""
        candles = [Mock(spec=MarketDataCandle), Mock(spec=MarketDataCandle)]
        
        events = detector.detect_resistance_events(
            candles=candles,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1,
            feature_flag_enabled=False
        )
        
        assert len(events) == 0
    
    def test_atr_calculation(self, detector, sample_candles):
        """Test ATR calculation"""
        atr_values = detector._calculate_atr_series(sample_candles)
        
        assert len(atr_values) == len(sample_candles)
        # ATR values should be positive
        assert all(atr > 0 for atr in atr_values)
        
    def test_process_single_candle_pair(self, detector):
        """Test processing a single candle pair"""
        prev_candle = MarketDataCandle(
            instrument="EUR_USD",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            timeframe=TimeFrame.H1,
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0980"),
            close=Decimal("1.1040"),  # Green
            volume=100000,
            complete=True,
            data_source="test"
        )
        
        curr_candle = MarketDataCandle(
            instrument="EUR_USD",
            timestamp=datetime(2024, 1, 1, 13, 0, 0),
            timeframe=TimeFrame.H1,
            open=Decimal("1.1040"),
            high=Decimal("1.1060"),
            low=Decimal("1.1020"),
            close=Decimal("1.1025"),  # Red
            volume=100000,
            complete=True,
            data_source="test"
        )
        
        event = detector.process_single_candle_pair(
            prev_candle=prev_candle,
            curr_candle=curr_candle,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1,
            atr_value=0.0020
        )
        
        assert event is not None
        assert event['resistance_level'] == 1.1050
        assert event['rebound_amplitude'] < 0
        assert event['rebound_in_atr'] is not None
    
    def test_performance_benchmark(self, detector):
        """Test performance requirement: <100ms per candle"""
        import time
        
        # Generate 1000 candles
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        candles = []
        for i in range(1000):
            # Alternate between green and red for maximum events
            is_green = i % 2 == 0
            candle = MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time + timedelta(hours=i),
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1050"),
                low=Decimal("1.0980"),
                close=Decimal("1.1040") if is_green else Decimal("1.0990"),
                volume=100000,
                complete=True,
                data_source="test"
            )
            candles.append(candle)
        
        start_time = time.time()
        events = detector.detect_resistance_events(
            candles=candles,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1
        )
        elapsed_time = time.time() - start_time
        
        # Average time per candle should be < 100ms
        avg_time_per_candle = (elapsed_time * 1000) / len(candles)
        assert avg_time_per_candle < 100, f"Performance too slow: {avg_time_per_candle}ms per candle"


class TestEventProcessor:
    """Test suite for EventProcessor service"""
    
    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance"""
        return EventProcessor()
    
    @pytest.fixture
    def sample_candles(self):
        """Create sample candles for event processor testing"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        return [
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time,
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1050"),
                low=Decimal("1.0980"),
                close=Decimal("1.1040"),  # Green
                volume=100000,
                complete=True,
                data_source="test"
            ),
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time + timedelta(hours=1),
                timeframe=TimeFrame.H1,
                open=Decimal("1.1040"),
                high=Decimal("1.1060"),
                low=Decimal("1.1020"),
                close=Decimal("1.1025"),  # Red - resistance event
                volume=100000,
                complete=True,
                data_source="test"
            )
        ]
    
    @pytest.mark.asyncio
    async def test_process_market_data_batch(self, processor, sample_candles):
        """Test processing market data batch"""
        with patch('app.config.settings.FEATURE_FLAGS', {'resistance_detection_enabled': True}):
            with patch.object(processor, '_store_events', new_callable=AsyncMock) as mock_store:
                mock_store.return_value = [Mock(id=uuid.uuid4())]
                
                result = await processor.process_market_data_batch(
                    candles=sample_candles,
                    instrument="EUR_USD",
                    timeframe=TimeFrame.H1
                )
                
                assert result['status'] == 'success'
                assert result['candles_processed'] == 2
                assert result['events_detected'] == 1
                assert result['events_stored'] == 1
                mock_store.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_market_data_batch_feature_disabled(self, processor, sample_candles):
        """Test processing with feature flag disabled"""
        with patch('app.config.settings.FEATURE_FLAGS', {'resistance_detection_enabled': False}):
            result = await processor.process_market_data_batch(
                candles=sample_candles,
                instrument="EUR_USD",
                timeframe=TimeFrame.H1
            )
            
            assert result['status'] == 'skipped'
            assert result['reason'] == 'feature_disabled'
    
    @pytest.mark.asyncio
    async def test_process_market_data_batch_no_events(self, processor):
        """Test processing when no events are detected"""
        # All green candles
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        candles = [
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time + timedelta(hours=i),
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1050"),
                low=Decimal("1.0980"),
                close=Decimal("1.1040"),  # All green
                volume=100000,
                complete=True,
                data_source="test"
            )
            for i in range(3)
        ]
        
        with patch('app.config.settings.FEATURE_FLAGS', {'resistance_detection_enabled': True}):
            result = await processor.process_market_data_batch(
                candles=candles,
                instrument="EUR_USD",
                timeframe=TimeFrame.H1
            )
            
            assert result['status'] == 'success'
            assert result['events_detected'] == 0
            assert result['events_stored'] == 0
    
    @pytest.mark.asyncio
    async def test_process_market_data_batch_error_handling(self, processor, sample_candles):
        """Test error handling in batch processing"""
        with patch('app.config.settings.FEATURE_FLAGS', {'resistance_detection_enabled': True}):
            with patch.object(processor.detector, 'detect_resistance_events', side_effect=Exception("Test error")):
                result = await processor.process_market_data_batch(
                    candles=sample_candles,
                    instrument="EUR_USD",
                    timeframe=TimeFrame.H1
                )
                
                assert result['status'] == 'error'
                assert 'Test error' in result['error']
    
    def test_get_processing_stats(self, processor):
        """Test getting processing statistics"""
        stats = processor.get_processing_stats()
        
        assert 'events_processed' in stats
        assert 'events_stored' in stats
        assert 'events_failed' in stats
        assert 'last_processing_time' in stats
        assert stats['events_processed'] == 0
    
    @pytest.mark.asyncio
    async def test_check_duplicate_event(self, processor):
        """Test duplicate event checking"""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        is_duplicate = await processor._check_duplicate_event(
            session=mock_session,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1,
            timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        assert is_duplicate is False
        mock_session.execute.assert_called_once()


class TestResistanceEventModel:
    """Test suite for ResistanceEvent model"""
    
    def test_resistance_event_creation(self):
        """Test creating a resistance event"""
        event = ResistanceEvent(
            event_type=EventType.NEW_RESISTANCE,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1,
            event_timestamp=datetime(2024, 1, 1, 12, 0, 0),
            green_open=1.1000,
            green_high=1.1050,
            green_low=1.0980,
            green_close=1.1040,
            green_volume=100000,
            red_open=1.1040,
            red_high=1.1060,
            red_low=1.1020,
            red_close=1.1025,
            red_volume=100000,
            resistance_level=1.1050,
            rebound_amplitude=-0.0035,
            rebound_percentage=8.75,
            atr_value=0.0020,
            rebound_in_atr=1.75,
            day_of_week=0,
            hour_of_day=12
        )
        
        assert event.instrument == "EUR_USD"
        assert event.resistance_level == 1.1050
        assert event.rebound_amplitude < 0
    
    def test_resistance_event_to_dict(self):
        """Test converting resistance event to dictionary"""
        event = ResistanceEvent(
            id=uuid.uuid4(),
            event_type=EventType.NEW_RESISTANCE,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1,
            event_timestamp=datetime(2024, 1, 1, 12, 0, 0),
            green_open=1.1000,
            green_high=1.1050,
            green_low=1.0980,
            green_close=1.1040,
            red_open=1.1040,
            red_high=1.1060,
            red_low=1.1020,
            red_close=1.1025,
            resistance_level=1.1050,
            rebound_amplitude=-0.0035,
            rebound_percentage=8.75,
            day_of_week=0,
            hour_of_day=12,
            detected_at=datetime(2024, 1, 1, 12, 0, 1)
        )
        
        event_dict = event.to_dict()
        
        assert 'id' in event_dict
        assert event_dict['instrument'] == "EUR_USD"
        assert event_dict['resistance_level'] == 1.1050
        assert 'green_candle' in event_dict
        assert 'red_candle' in event_dict
        assert event_dict['green_candle']['high'] == 1.1050
        assert event_dict['red_candle']['close'] == 1.1025


class TestEdgeCases:
    """Test suite for edge cases and complex scenarios"""
    
    @pytest.fixture
    def detector(self):
        return ResistanceDetector()
    
    def test_weekend_gap_handling(self, detector):
        """Test handling of weekend gaps in forex data"""
        friday_close = datetime(2024, 1, 5, 21, 0, 0)  # Friday
        monday_open = datetime(2024, 1, 8, 0, 0, 0)   # Monday
        
        candles = [
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=friday_close,
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1050"),
                low=Decimal("1.0980"),
                close=Decimal("1.1040"),  # Green
                volume=100000,
                complete=True,
                data_source="test"
            ),
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=monday_open,
                timeframe=TimeFrame.H1,
                open=Decimal("1.1045"),
                high=Decimal("1.1055"),
                low=Decimal("1.1020"),
                close=Decimal("1.1025"),  # Red
                volume=100000,
                complete=True,
                data_source="test"
            )
        ]
        
        events = detector.detect_resistance_events(
            candles=candles,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1
        )
        
        # Should detect event despite weekend gap (within 2x expected gap)
        assert len(events) == 1
    
    def test_exact_open_close_equality(self, detector):
        """Test when open equals close (doji candle)"""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        candles = [
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time,
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1050"),
                low=Decimal("1.0980"),
                close=Decimal("1.1000"),  # Doji
                volume=100000,
                complete=True,
                data_source="test"
            ),
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=base_time + timedelta(hours=1),
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1020"),
                low=Decimal("1.0980"),
                close=Decimal("1.0990"),  # Red
                volume=100000,
                complete=True,
                data_source="test"
            )
        ]
        
        events = detector.detect_resistance_events(
            candles=candles,
            instrument="EUR_USD",
            timeframe=TimeFrame.H1
        )
        
        # Doji is neither green nor red, so no event
        assert len(events) == 0
    
    def test_all_timeframes(self, detector):
        """Test detection across all supported timeframes"""
        for timeframe in [TimeFrame.H1, TimeFrame.H4, TimeFrame.D, TimeFrame.W]:
            base_time = datetime(2024, 1, 1, 12, 0, 0)
            
            # Calculate appropriate time delta
            if timeframe == TimeFrame.H1:
                delta = timedelta(hours=1)
            elif timeframe == TimeFrame.H4:
                delta = timedelta(hours=4)
            elif timeframe == TimeFrame.D:
                delta = timedelta(days=1)
            else:  # W
                delta = timedelta(weeks=1)
            
            candles = [
                MarketDataCandle(
                    instrument="EUR_USD",
                    timestamp=base_time,
                    timeframe=timeframe,
                    open=Decimal("1.1000"),
                    high=Decimal("1.1050"),
                    low=Decimal("1.0980"),
                    close=Decimal("1.1040"),  # Green
                    volume=100000,
                    complete=True,
                    data_source="test"
                ),
                MarketDataCandle(
                    instrument="EUR_USD",
                    timestamp=base_time + delta,
                    timeframe=timeframe,
                    open=Decimal("1.1040"),
                    high=Decimal("1.1060"),
                    low=Decimal("1.1020"),
                    close=Decimal("1.1025"),  # Red
                    volume=100000,
                    complete=True,
                    data_source="test"
                )
            ]
            
            events = detector.detect_resistance_events(
                candles=candles,
                instrument="EUR_USD",
                timeframe=timeframe
            )
            
            assert len(events) == 1, f"Failed for timeframe {timeframe}"
            assert events[0]['timeframe'] == timeframe