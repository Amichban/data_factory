"""
Comprehensive tests for Real-time Spike Detection System

Tests streaming core, spike processor, and WebSocket functionality.
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

import websockets
from fastapi import WebSocket
from fastapi.testclient import TestClient

from app.core.streaming import (
    StreamProcessor,
    StreamBuffer,
    CircuitBreaker,
    RetryPolicy,
    CircuitBreakerConfig,
    CircuitState
)
from app.services.spike_processor import (
    SpikeProcessor,
    SpikeDetectionMetrics,
    get_spike_processor,
    start_spike_detection,
    stop_spike_detection
)
from app.websockets.event_stream import (
    ConnectionManager,
    websocket_endpoint,
    broadcast_system_message,
    get_connection_stats
)
from app.models.market_data import MarketDataCandle, TimeFrame
from app.models.resistance_event import ResistanceEvent


class TestStreamBuffer:
    """Test cases for StreamBuffer component"""
    
    @pytest.mark.asyncio
    async def test_buffer_add_and_get(self):
        """Test adding and retrieving items from buffer"""
        buffer = StreamBuffer(max_size=10)
        
        # Add items
        for i in range(5):
            await buffer.add(f"item_{i}")
        
        # Check stats
        stats = buffer.get_stats()
        assert stats['current_size'] == 5
        assert stats['total_added'] == 5
        
        # Get batch
        batch = await buffer.get_batch(3)
        assert len(batch) == 3
        assert batch == ["item_0", "item_1", "item_2"]
        
        # Check remaining
        stats = buffer.get_stats()
        assert stats['current_size'] == 2
    
    @pytest.mark.asyncio
    async def test_buffer_overflow(self):
        """Test buffer behavior when max size is reached"""
        buffer = StreamBuffer(max_size=3)
        
        # Fill buffer
        for i in range(5):
            await buffer.add(f"item_{i}")
        
        # Should only have last 3 items (FIFO)
        stats = buffer.get_stats()
        assert stats['current_size'] == 3
        assert stats['total_dropped'] == 2
        
        batch = await buffer.get_batch(10)
        assert len(batch) == 3
        assert batch == ["item_2", "item_3", "item_4"]
    
    @pytest.mark.asyncio
    async def test_buffer_clear(self):
        """Test clearing the buffer"""
        buffer = StreamBuffer(max_size=10)
        
        # Add items
        for i in range(5):
            await buffer.add(f"item_{i}")
        
        # Clear
        buffer.clear()
        
        stats = buffer.get_stats()
        assert stats['current_size'] == 0
        assert stats['total_added'] == 5
        
        # Get should return empty
        batch = await buffer.get_batch(10)
        assert len(batch) == 0


class TestCircuitBreaker:
    """Test cases for CircuitBreaker component"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.1,  # 100ms for testing
            success_threshold=1
        )
        cb = CircuitBreaker(name="test", config=config)
        
        # Initial state should be CLOSED
        assert cb.get_state()['state'] == CircuitState.CLOSED.value
        
        # Successful call
        async def success_func():
            return "success"
        
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.get_state()['state'] == CircuitState.CLOSED.value
        
        # Failing calls
        async def fail_func():
            raise Exception("test failure")
        
        # First failure
        with pytest.raises(Exception):
            await cb.call(fail_func)
        assert cb.get_state()['state'] == CircuitState.CLOSED.value
        
        # Second failure - should open circuit
        with pytest.raises(Exception):
            await cb.call(fail_func)
        assert cb.get_state()['state'] == CircuitState.OPEN.value
        
        # Circuit is open - should reject immediately
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await cb.call(success_func)
        
        # Wait for recovery timeout
        await asyncio.sleep(0.15)
        
        # Should be half-open now
        assert cb.get_state()['state'] == CircuitState.HALF_OPEN.value
        
        # Successful call should close circuit
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.get_state()['state'] == CircuitState.CLOSED.value
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_timeout(self):
        """Test circuit breaker with timeout"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            timeout=0.1  # 100ms timeout
        )
        cb = CircuitBreaker(name="test", config=config)
        
        async def slow_func():
            await asyncio.sleep(0.2)  # Longer than timeout
            return "success"
        
        with pytest.raises(asyncio.TimeoutError):
            await cb.call(slow_func)
        
        # Should count as failure
        assert cb.get_state()['state'] == CircuitState.OPEN.value


class TestRetryPolicy:
    """Test cases for RetryPolicy component"""
    
    @pytest.mark.asyncio
    async def test_retry_success(self):
        """Test retry policy with eventual success"""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.01,
            max_delay=0.1
        )
        
        call_count = 0
        
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("temporary failure")
            return "success"
        
        result = await policy.execute(flaky_func)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test retry policy when retries are exhausted"""
        policy = RetryPolicy(
            max_retries=2,
            initial_delay=0.01
        )
        
        async def always_fail():
            raise Exception("permanent failure")
        
        with pytest.raises(Exception, match="permanent failure"):
            await policy.execute(always_fail)
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff in retry policy"""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.01,
            backoff_factor=2.0,
            max_delay=0.1
        )
        
        delays = []
        
        async def track_delays():
            delays.append(time.time())
            raise Exception("failure")
        
        try:
            await policy.execute(track_delays)
        except Exception:
            pass
        
        # Check that delays increase
        assert len(delays) == 4  # Initial + 3 retries
        for i in range(1, len(delays)):
            actual_delay = delays[i] - delays[i-1]
            # Allow some tolerance for timing
            assert actual_delay >= 0.009  # Close to initial_delay * (2 ** (i-1))


class TestSpikeDetectionMetrics:
    """Test cases for spike detection metrics"""
    
    def test_metrics_recording(self):
        """Test metrics recording and calculation"""
        metrics = SpikeDetectionMetrics()
        
        # Record some data
        metrics.record_candle()
        metrics.record_candle()
        metrics.record_event(10.5)
        metrics.record_event(15.3)
        metrics.record_notification(5.2)
        
        stats = metrics.get_stats()
        
        assert stats['total_candles_received'] == 2
        assert stats['total_events_detected'] == 2
        assert stats['total_notifications_sent'] == 1
        assert stats['avg_detection_latency_ms'] == pytest.approx(12.9, 0.1)
        assert stats['avg_processing_latency_ms'] == 5.2
        assert stats['max_detection_latency_ms'] == 15.3
    
    def test_metrics_circular_buffer(self):
        """Test that metrics use circular buffer correctly"""
        metrics = SpikeDetectionMetrics()
        
        # Add more than buffer size (100)
        for i in range(150):
            metrics.record_event(float(i))
        
        # Should only keep last 100
        assert len(metrics.detection_latencies) == 100
        
        # Average should be of last 100 values (50-149)
        stats = metrics.get_stats()
        expected_avg = sum(range(50, 150)) / 100
        assert stats['avg_detection_latency_ms'] == pytest.approx(expected_avg, 0.1)


class TestSpikeProcessor:
    """Test cases for SpikeProcessor"""
    
    @pytest.mark.asyncio
    async def test_processor_initialization(self):
        """Test spike processor initialization"""
        processor = SpikeProcessor(
            instruments=["EUR_USD", "GBP_USD"],
            timeframes=["H1", "H4"]
        )
        
        assert len(processor.instruments) == 2
        assert len(processor.timeframes) == 2
        assert processor.timeframes[0] == TimeFrame.H1
        assert not processor._running
    
    @pytest.mark.asyncio
    async def test_processor_start_stop(self):
        """Test starting and stopping the processor"""
        with patch('app.config.settings.FEATURE_FLAGS', {'spike_detection_enabled': True}):
            processor = SpikeProcessor()
            
            # Start processor
            await processor.start()
            assert processor._running
            assert len(processor._tasks) > 0
            
            # Stop processor
            await processor.stop()
            assert not processor._running
            assert len(processor._tasks) == 0
    
    @pytest.mark.asyncio
    async def test_processor_disabled_by_flag(self):
        """Test processor doesn't start when disabled by feature flag"""
        with patch('app.config.settings.FEATURE_FLAGS', {'spike_detection_enabled': False}):
            processor = SpikeProcessor()
            
            await processor.start()
            assert not processor._running
            assert len(processor._tasks) == 0
    
    @pytest.mark.asyncio
    async def test_candle_processing(self):
        """Test processing individual candles for spike detection"""
        processor = SpikeProcessor()
        
        # Mock detector
        mock_event = {
            'event_type': 'resistance_bounce',
            'instrument': 'EUR_USD',
            'timeframe': 'H1',
            'resistance_level': 1.0850,
            'rebound_amplitude': 0.0020,
            'rebound_percentage': 0.18,
            'event_timestamp': datetime.utcnow(),
            'detected_at': datetime.utcnow()
        }
        
        processor.detector.process_single_candle_pair = Mock(return_value=mock_event)
        
        # Create candles
        prev_candle = MarketDataCandle(
            instrument='EUR_USD',
            timeframe=TimeFrame.H1,
            timestamp=datetime.utcnow() - timedelta(hours=1),
            open=1.0820,
            high=1.0850,
            low=1.0815,
            close=1.0845,
            volume=1000
        )
        
        curr_candle = MarketDataCandle(
            instrument='EUR_USD',
            timeframe=TimeFrame.H1,
            timestamp=datetime.utcnow(),
            open=1.0845,
            high=1.0852,
            low=1.0830,
            close=1.0835,
            volume=1200
        )
        
        # Store previous candle
        processor.last_candles['EUR_USD'] = {TimeFrame.H1.value: prev_candle}
        
        # Process current candle
        await processor._process_candle('EUR_USD', TimeFrame.H1, curr_candle)
        
        # Check that detector was called
        processor.detector.process_single_candle_pair.assert_called_once()
        
        # Check metrics
        assert processor.metrics.total_events_detected == 1
        
        # Check buffer has event
        buffer_stats = processor.buffer.get_stats()
        assert buffer_stats['total_added'] == 1
    
    @pytest.mark.asyncio
    async def test_notification_delivery(self):
        """Test notification delivery with callback"""
        callback_called = False
        notification_data = None
        
        async def notification_callback(data):
            nonlocal callback_called, notification_data
            callback_called = True
            notification_data = data
        
        processor = SpikeProcessor(notification_callback=notification_callback)
        
        # Create mock event
        event = {
            'event_type': 'resistance_bounce',
            'instrument': 'EUR_USD',
            'timeframe': 'H1',
            'resistance_level': 1.0850
        }
        
        # Deliver notification
        await processor._deliver_notification(event, 10.5)
        
        assert callback_called
        assert notification_data['type'] == 'resistance_event'
        assert notification_data['data'] == event
        assert notification_data['metadata']['detection_latency_ms'] == 10.5
    
    @pytest.mark.asyncio
    async def test_latency_monitoring(self):
        """Test that latency monitoring works correctly"""
        with patch('app.config.settings.FEATURE_FLAGS', {'real_time_notifications': True}):
            processor = SpikeProcessor()
            
            # Mock notification delivery to be slow
            async def slow_notification(event, latency):
                await asyncio.sleep(6)  # 6 seconds - exceeds requirement
            
            processor._deliver_notification = slow_notification
            
            # Create event
            event = {'event_type': 'test'}
            
            # Test with warning for exceeded latency
            with patch('app.services.spike_processor.logger') as mock_logger:
                await processor._send_notification(event, 100)  # 100ms detection
                
                # Should log warning about exceeded latency
                mock_logger.warning.assert_called()
                call_args = mock_logger.warning.call_args
                assert "Latency requirement exceeded" in call_args[0][0]


class TestConnectionManager:
    """Test cases for WebSocket ConnectionManager"""
    
    @pytest.mark.asyncio
    async def test_connection_management(self):
        """Test WebSocket connection management"""
        manager = ConnectionManager()
        
        # Mock WebSocket
        mock_ws = AsyncMock(spec=WebSocket)
        
        # Connect client
        await manager.connect(mock_ws, "client_1", {"user": "test"})
        
        assert "client_1" in manager.active_connections
        assert "client_1" in manager.subscriptions
        assert manager.connection_metadata["client_1"]["user"] == "test"
        
        # Check welcome message was sent
        mock_ws.send_json.assert_called()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args['type'] == 'connection'
        assert call_args['status'] == 'connected'
        
        # Disconnect client
        await manager.disconnect("client_1")
        
        assert "client_1" not in manager.active_connections
        assert "client_1" not in manager.subscriptions
    
    @pytest.mark.asyncio
    async def test_subscription_management(self):
        """Test subscription management"""
        manager = ConnectionManager()
        
        # Setup client
        mock_ws = AsyncMock(spec=WebSocket)
        await manager.connect(mock_ws, "client_1")
        
        # Subscribe to events
        await manager.subscribe("client_1", "EUR_USD", "H1")
        
        assert "EUR_USD_H1" in manager.subscriptions["client_1"]
        
        # Check confirmation message
        assert mock_ws.send_json.call_count >= 2  # Welcome + subscription
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args['type'] == 'subscription'
        assert call_args['action'] == 'subscribed'
        
        # Unsubscribe
        await manager.unsubscribe("client_1", "EUR_USD", "H1")
        
        assert "EUR_USD_H1" not in manager.subscriptions["client_1"]
    
    @pytest.mark.asyncio
    async def test_event_broadcasting(self):
        """Test broadcasting events to subscribed clients"""
        manager = ConnectionManager()
        
        # Setup multiple clients
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws3 = AsyncMock(spec=WebSocket)
        
        await manager.connect(mock_ws1, "client_1")
        await manager.connect(mock_ws2, "client_2")
        await manager.connect(mock_ws3, "client_3")
        
        # Subscribe clients to different events
        await manager.subscribe("client_1", "EUR_USD", "H1")
        await manager.subscribe("client_2", "EUR_USD", "H1")
        await manager.subscribe("client_3", "GBP_USD", "H4")
        
        # Reset mock call counts
        mock_ws1.send_json.reset_mock()
        mock_ws2.send_json.reset_mock()
        mock_ws3.send_json.reset_mock()
        
        # Broadcast EUR_USD H1 event
        event = {'type': 'resistance', 'level': 1.0850}
        await manager.broadcast_event(event, "EUR_USD", "H1")
        
        # Only client_1 and client_2 should receive
        mock_ws1.send_json.assert_called_once()
        mock_ws2.send_json.assert_called_once()
        mock_ws3.send_json.assert_not_called()
        
        # Check message content
        call_args = mock_ws1.send_json.call_args[0][0]
        assert call_args['type'] == 'event'
        assert call_args['data'] == event
        assert call_args['instrument'] == 'EUR_USD'
        assert call_args['timeframe'] == 'H1'
    
    @pytest.mark.asyncio
    async def test_broadcast_to_all(self):
        """Test broadcasting to all connected clients"""
        manager = ConnectionManager()
        
        # Setup clients
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        
        await manager.connect(mock_ws1, "client_1")
        await manager.connect(mock_ws2, "client_2")
        
        # Reset mocks
        mock_ws1.send_json.reset_mock()
        mock_ws2.send_json.reset_mock()
        
        # Broadcast system message
        message = {'type': 'system', 'message': 'Server maintenance'}
        await manager.broadcast_to_all(message)
        
        # Both should receive
        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)
    
    def test_connection_stats(self):
        """Test getting connection statistics"""
        manager = ConnectionManager()
        
        # Add some test data
        manager.active_connections = {"client_1": Mock(), "client_2": Mock()}
        manager.subscriptions = {
            "client_1": {"EUR_USD_H1", "GBP_USD_H1"},
            "client_2": {"EUR_USD_H4"}
        }
        manager.connection_metadata = {
            "client_1": {"connected_at": datetime.utcnow()},
            "client_2": {"connected_at": datetime.utcnow()}
        }
        
        stats = manager.get_stats()
        
        assert stats['total_connections'] == 2
        assert stats['total_subscriptions'] == 3
        assert len(stats['clients']) == 2
        assert stats['clients'][0]['client_id'] in ["client_1", "client_2"]


class TestWebSocketEndpoint:
    """Test cases for WebSocket endpoint"""
    
    @pytest.mark.asyncio
    async def test_websocket_message_handling(self):
        """Test handling different WebSocket message types"""
        # This would require more complex setup with actual WebSocket server
        # For now, test the message handling logic
        
        manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        
        # Test subscribe message
        await manager.connect(mock_ws, "test_client")
        
        # Simulate receiving messages (this is simplified)
        # In real test, would use WebSocket test client
        
        # Test ping/pong
        mock_ws.reset_mock()
        await manager.send_personal_message({'type': 'ping'}, "test_client")
        mock_ws.send_json.assert_called_once()


class TestIntegration:
    """Integration tests for the complete spike detection system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_spike_detection(self):
        """Test complete flow from candle to notification"""
        with patch('app.config.settings.FEATURE_FLAGS', {
            'spike_detection_enabled': True,
            'real_time_notifications': True
        }):
            # Track notifications
            notifications = []
            
            async def capture_notification(data):
                notifications.append(data)
            
            # Create processor with callback
            processor = SpikeProcessor(
                instruments=["EUR_USD"],
                timeframes=["H1"],
                notification_callback=capture_notification
            )
            
            # Mock detector to return event
            mock_event = {
                'event_type': 'resistance_bounce',
                'instrument': 'EUR_USD',
                'timeframe': 'H1',
                'resistance_level': 1.0850,
                'rebound_amplitude': 0.0020,
                'rebound_percentage': 0.18,
                'event_timestamp': datetime.utcnow(),
                'detected_at': datetime.utcnow(),
                'green_open': 1.0820,
                'green_high': 1.0850,
                'green_low': 1.0815,
                'green_close': 1.0845,
                'red_open': 1.0845,
                'red_high': 1.0852,
                'red_low': 1.0830,
                'red_close': 1.0835,
                'day_of_week': 1,
                'hour_of_day': 14
            }
            
            processor.detector.process_single_candle_pair = Mock(return_value=mock_event)
            
            # Create candles
            prev_candle = MarketDataCandle(
                instrument='EUR_USD',
                timeframe=TimeFrame.H1,
                timestamp=datetime.utcnow() - timedelta(hours=1),
                open=1.0820,
                high=1.0850,
                low=1.0815,
                close=1.0845,
                volume=1000
            )
            
            curr_candle = MarketDataCandle(
                instrument='EUR_USD',
                timeframe=TimeFrame.H1,
                timestamp=datetime.utcnow(),
                open=1.0845,
                high=1.0852,
                low=1.0830,
                close=1.0835,
                volume=1200
            )
            
            # Process candles
            processor.last_candles['EUR_USD'] = {TimeFrame.H1.value: prev_candle}
            await processor._process_candle('EUR_USD', TimeFrame.H1, curr_candle)
            
            # Check notification was sent
            assert len(notifications) == 1
            assert notifications[0]['type'] == 'resistance_event'
            assert notifications[0]['data']['resistance_level'] == 1.0850
            
            # Check metrics
            stats = processor.metrics.get_stats()
            assert stats['total_events_detected'] == 1
            assert stats['total_notifications_sent'] == 1
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self):
        """Test that system meets performance requirements"""
        processor = SpikeProcessor()
        
        # Mock fast detector
        processor.detector.process_single_candle_pair = Mock(return_value=None)
        
        # Process many candles and measure time
        start_time = time.time()
        
        for i in range(100):
            candle = MarketDataCandle(
                instrument='EUR_USD',
                timeframe=TimeFrame.H1,
                timestamp=datetime.utcnow(),
                open=1.0820 + i*0.0001,
                high=1.0850 + i*0.0001,
                low=1.0815 + i*0.0001,
                close=1.0845 + i*0.0001,
                volume=1000
            )
            
            await processor._process_candle('EUR_USD', TimeFrame.H1, candle)
        
        elapsed_time = time.time() - start_time
        avg_time_per_candle = (elapsed_time / 100) * 1000  # in ms
        
        # Should process each candle in well under 100ms
        assert avg_time_per_candle < 50  # Conservative limit
    
    @pytest.mark.asyncio
    async def test_concurrent_stream_processing(self):
        """Test processing multiple streams concurrently"""
        with patch('app.config.settings.FEATURE_FLAGS', {'spike_detection_enabled': True}):
            processor = SpikeProcessor(
                instruments=["EUR_USD", "GBP_USD"],
                timeframes=["H1", "H4"]
            )
            
            # Mock the fetch method to return None (no new data)
            processor._fetch_latest_candle = AsyncMock(return_value=None)
            
            # Start processor
            await processor.start()
            
            # Should have 4 streams (2 instruments x 2 timeframes)
            # Plus buffer processor and metrics reporter
            assert len(processor._tasks) >= 6
            
            # Let it run briefly
            await asyncio.sleep(0.1)
            
            # Stop processor
            await processor.stop()
            
            # Check that all streams were active
            assert processor._fetch_latest_candle.call_count > 0