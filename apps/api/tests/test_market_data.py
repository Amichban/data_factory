"""
Market Data Service Tests
Comprehensive tests for market data ingestion pipeline
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List

from app.models.market_data import (
    MarketDataCandle, DataIngestionRequest, DataIngestionResponse, 
    TimeFrame, DataMode, DataQualityMetrics, RateLimitStatus, DataSourceStatus
)
from app.services.market_data_service import (
    MarketDataService, RateLimiter, OandaDataProvider
)
from app.tasks.data_ingestion import DataIngestionScheduler, AutomaticIngestionManager
from app.core.config import get_instrument_category, get_quality_rating


class TestMarketDataModels:
    """Test market data model validation"""
    
    def test_market_data_candle_validation(self):
        """Test candle data validation"""
        # Valid candle
        candle = MarketDataCandle(
            instrument="EUR_USD",
            timestamp=datetime.utcnow(),
            timeframe=TimeFrame.H1,
            open=Decimal("1.1000"),
            high=Decimal("1.1010"),
            low=Decimal("1.0990"),
            close=Decimal("1.1005")
        )
        assert candle.instrument == "EUR_USD"
        assert candle.timeframe == TimeFrame.H1
    
    def test_invalid_instrument_format(self):
        """Test invalid instrument format validation"""
        with pytest.raises(ValueError, match="Instrument must be in format CCY_CCY"):
            MarketDataCandle(
                instrument="INVALID",
                timestamp=datetime.utcnow(),
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1010"),
                low=Decimal("1.0990"),
                close=Decimal("1.1005")
            )
    
    def test_invalid_price_relationships(self):
        """Test invalid price relationship validation"""
        with pytest.raises(ValueError, match="High price cannot be less than"):
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=datetime.utcnow(),
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.0990"),  # High less than open
                low=Decimal("1.0980"),
                close=Decimal("1.1005")
            )
    
    def test_data_ingestion_request_validation(self):
        """Test ingestion request validation"""
        # Valid request
        request = DataIngestionRequest(
            instruments=["EUR_USD", "GBP_USD"],
            timeframes=[TimeFrame.H1, TimeFrame.D],
            mode=DataMode.BATCH,
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow()
        )
        assert len(request.instruments) == 2
        assert len(request.timeframes) == 2
    
    def test_invalid_date_range(self):
        """Test invalid date range validation"""
        with pytest.raises(ValueError, match="End date must be after start date"):
            DataIngestionRequest(
                instruments=["EUR_USD"],
                timeframes=[TimeFrame.H1],
                mode=DataMode.BATCH,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() - timedelta(days=1)  # End before start
            )


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter for testing"""
        return RateLimiter(max_requests=5, time_window=60)
    
    @pytest.mark.asyncio
    async def test_rate_limit_acquisition(self, rate_limiter):
        """Test rate limit acquisition"""
        # Should allow initial requests
        for i in range(5):
            assert await rate_limiter.acquire() == True
        
        # Should deny additional requests
        assert await rate_limiter.acquire() == False
    
    def test_rate_limit_status(self, rate_limiter):
        """Test rate limit status reporting"""
        status = rate_limiter.get_status()
        assert isinstance(status, RateLimitStatus)
        assert status.requests_made == 0
        assert status.requests_remaining == 5
        assert status.is_limited == False


class TestOandaDataProvider:
    """Test OANDA data provider"""
    
    @pytest.fixture
    def mock_oanda_provider(self):
        """Create mock OANDA provider"""
        with patch('app.services.market_data_service.settings') as mock_settings:
            mock_settings.OANDA_API_KEY = "test_key"
            mock_settings.OANDA_API_URL = "https://api-test.oanda.com"
            mock_settings.OANDA_STREAM_URL = "https://stream-test.oanda.com"
            mock_settings.MARKET_DATA_RATE_LIMIT = 100
            mock_settings.MARKET_DATA_RETRY_ATTEMPTS = 3
            mock_settings.MARKET_DATA_RETRY_DELAY = 0.1
            
            provider = OandaDataProvider()
            return provider
    
    @pytest.mark.asyncio
    async def test_historical_data_fetch(self, mock_oanda_provider):
        """Test historical data fetching"""
        # Mock response data
        mock_response_data = {
            'candles': [
                {
                    'complete': True,
                    'time': '2023-12-01T10:00:00Z',
                    'mid': {
                        'o': '1.1000',
                        'h': '1.1010',
                        'l': '1.0990',
                        'c': '1.1005'
                    },
                    'volume': 100
                }
            ]
        }
        
        # Mock the HTTP request
        with patch.object(mock_oanda_provider, '_make_request', 
                         new_callable=AsyncMock, return_value=mock_response_data):
            
            start_time = datetime.utcnow() - timedelta(days=1)
            end_time = datetime.utcnow()
            
            candles = await mock_oanda_provider.get_historical_data(
                instrument="EUR_USD",
                timeframe=TimeFrame.H1,
                start_time=start_time,
                end_time=end_time
            )
            
            assert len(candles) == 1
            assert candles[0].instrument == "EUR_USD"
            assert candles[0].open == Decimal("1.1000")
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_oanda_provider):
        """Test provider health check"""
        mock_response = {}
        
        with patch.object(mock_oanda_provider, '_make_request', 
                         new_callable=AsyncMock, return_value=mock_response):
            
            status = await mock_oanda_provider.check_health()
            
            assert isinstance(status, DataSourceStatus)
            assert status.source_name == 'oanda'
            assert status.is_available == True
            assert status.response_time_ms is not None


class TestMarketDataService:
    """Test market data service"""
    
    @pytest.fixture
    def mock_market_service(self):
        """Create mock market data service"""
        service = MarketDataService()
        
        # Mock the data provider
        service.data_provider = Mock()
        service.data_provider.get_historical_data = AsyncMock()
        service.data_provider.stream_real_time_data = AsyncMock()
        service.data_provider.check_health = AsyncMock()
        service.data_provider.close = AsyncMock()
        
        # Mock firestore
        service.firestore = Mock()
        service.firestore.get_collection = Mock()
        service.firestore.health_check = Mock(return_value={'status': 'healthy'})
        
        return service
    
    @pytest.mark.asyncio
    async def test_process_batch_ingestion(self, mock_market_service):
        """Test batch data ingestion processing"""
        # Mock historical data
        mock_candles = [
            MarketDataCandle(
                instrument="EUR_USD",
                timestamp=datetime.utcnow(),
                timeframe=TimeFrame.H1,
                open=Decimal("1.1000"),
                high=Decimal("1.1010"),
                low=Decimal("1.0990"),
                close=Decimal("1.1005")
            )
        ]
        
        mock_market_service.data_provider.get_historical_data.return_value = mock_candles
        
        # Mock storage
        with patch.object(mock_market_service, '_store_candle', new_callable=AsyncMock):
            request = DataIngestionRequest(
                instruments=["EUR_USD"],
                timeframes=[TimeFrame.H1],
                mode=DataMode.BATCH,
                start_date=datetime.utcnow() - timedelta(days=1),
                end_date=datetime.utcnow()
            )
            
            response = await mock_market_service.process_ingestion_request(request)
            
            assert response.status == 'completed'
            assert response.instruments_processed == 1
            assert response.candles_ingested == 1
    
    @pytest.mark.asyncio
    async def test_data_quality_metrics(self, mock_market_service):
        """Test data quality metrics calculation"""
        # Mock Firestore query results
        mock_query = Mock()
        mock_docs = [
            Mock(to_dict=lambda: {
                'timestamp': datetime.utcnow() - timedelta(hours=i),
                'complete': True,
                'close': 1.1000 + i * 0.0001,
                'open': 1.1000 + i * 0.0001 - 0.0001,
                'volume': 100
            }) for i in range(24)  # 24 hours of data
        ]
        
        mock_query.stream.return_value = mock_docs
        mock_market_service.firestore.get_collection.return_value.where.return_value.where.return_value.where.return_value.where.return_value.order_by.return_value = mock_query
        
        metrics = await mock_market_service.get_data_quality_metrics(
            instrument="EUR_USD",
            timeframe=TimeFrame.H1
        )
        
        assert isinstance(metrics, DataQualityMetrics)
        assert metrics.instrument == "EUR_USD"
        assert metrics.timeframe == TimeFrame.H1
        assert metrics.total_candles == 24
        assert metrics.complete_candles == 24
        assert metrics.completeness_ratio == 1.0
    
    @pytest.mark.asyncio
    async def test_health_status(self, mock_market_service):
        """Test service health status"""
        # Mock provider status
        mock_provider_status = DataSourceStatus(
            source_name='oanda',
            is_available=True,
            response_time_ms=100.0
        )
        mock_market_service.data_provider.check_health.return_value = mock_provider_status
        mock_market_service.data_provider.rate_limiter = Mock()
        mock_market_service.data_provider.rate_limiter.get_status.return_value = RateLimitStatus(
            requests_made=10,
            requests_remaining=90,
            reset_time=datetime.utcnow() + timedelta(minutes=1),
            current_window_start=datetime.utcnow() - timedelta(minutes=1)
        )
        
        health = await mock_market_service.get_health_status()
        
        assert health['status'] == 'healthy'
        assert 'data_provider' in health
        assert 'firestore' in health
        assert 'rate_limiting' in health


class TestDataIngestionScheduler:
    """Test data ingestion scheduler"""
    
    @pytest.fixture
    def scheduler(self):
        """Create scheduler for testing"""
        return DataIngestionScheduler()
    
    @pytest.mark.asyncio
    async def test_schedule_historical_backfill(self, scheduler):
        """Test scheduling historical backfill"""
        with patch('app.tasks.data_ingestion.market_data_service') as mock_service:
            mock_service.process_ingestion_request = AsyncMock(
                return_value=DataIngestionResponse(
                    request_id="test_id",
                    status="completed",
                    message="Test completed",
                    candles_ingested=100
                )
            )
            
            task_id = await scheduler.schedule_historical_backfill(
                instruments=["EUR_USD"],
                timeframes=[TimeFrame.H1],
                start_date=datetime.utcnow() - timedelta(days=1),
                end_date=datetime.utcnow(),
                priority=1
            )
            
            assert task_id is not None
            assert task_id in scheduler.running_tasks
            
            # Wait for task completion
            await asyncio.sleep(0.1)
    
    def test_task_status_tracking(self, scheduler):
        """Test task status tracking"""
        task_id = "test_task_id"
        task_info = {
            'task_id': task_id,
            'status': 'running',
            'created_at': datetime.utcnow()
        }
        
        scheduler.running_tasks[task_id] = task_info
        
        status = scheduler.get_task_status(task_id)
        assert status is not None
        assert status['task_id'] == task_id
        assert status['status'] == 'running'
    
    def test_cancel_task(self, scheduler):
        """Test task cancellation"""
        task_id = "test_task_id"
        task_info = {
            'task_id': task_id,
            'status': 'running',
            'created_at': datetime.utcnow()
        }
        
        scheduler.running_tasks[task_id] = task_info
        
        success = scheduler.cancel_task(task_id)
        assert success == True
        assert task_id not in scheduler.running_tasks
        assert len(scheduler.task_history) == 1


class TestAutomaticIngestionManager:
    """Test automatic ingestion manager"""
    
    @pytest.fixture
    def manager(self):
        """Create manager for testing"""
        return AutomaticIngestionManager()
    
    @pytest.mark.asyncio
    async def test_start_automatic_ingestion(self, manager):
        """Test starting automatic ingestion"""
        with patch.object(manager.scheduler, 'schedule_historical_backfill', new_callable=AsyncMock) as mock_backfill:
            with patch.object(manager.scheduler, 'schedule_real_time_ingestion', new_callable=AsyncMock) as mock_realtime:
                with patch.object(manager.scheduler, 'schedule_data_quality_check', new_callable=AsyncMock) as mock_quality:
                    
                    mock_backfill.return_value = "backfill_task_id"
                    mock_realtime.return_value = "realtime_task_id"
                    mock_quality.return_value = "quality_task_id"
                    
                    await manager.start_automatic_ingestion()
                    
                    assert manager._running == True
                    assert mock_backfill.called
                    assert mock_realtime.called
                    assert mock_quality.called
    
    def test_get_status(self, manager):
        """Test getting manager status"""
        status = manager.get_status()
        
        assert 'running' in status
        assert 'tasks' in status
        assert 'last_check' in status
        assert status['running'] == False


class TestCoreConfigHelpers:
    """Test core configuration helper functions"""
    
    def test_get_instrument_category(self):
        """Test instrument categorization"""
        assert get_instrument_category("EUR_USD") == "major"
        assert get_instrument_category("EUR_GBP") == "minor"
        assert get_instrument_category("USD_SEK") == "exotic"
        assert get_instrument_category("UNKNOWN_PAIR") == "unknown"
    
    def test_get_quality_rating(self):
        """Test quality rating assignment"""
        assert get_quality_rating(0.98) == "excellent"
        assert get_quality_rating(0.90) == "good"
        assert get_quality_rating(0.75) == "acceptable"
        assert get_quality_rating(0.55) == "poor"
        assert get_quality_rating(0.30) == "critical"


class TestIntegration:
    """Integration tests for the full pipeline"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_batch_processing(self):
        """Test end-to-end batch processing"""
        # This would be an integration test that requires actual services
        # Skipped in unit tests but important for full testing
        pytest.skip("Integration test - requires live services")
    
    @pytest.mark.asyncio  
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        # Test various failure scenarios and recovery
        pytest.skip("Integration test - requires live services")
    
    @pytest.mark.asyncio
    async def test_rate_limiting_compliance(self):
        """Test rate limiting compliance under load"""
        pytest.skip("Load test - requires extended runtime")


# Test fixtures and utilities
@pytest.fixture
def sample_candle_data():
    """Sample candle data for testing"""
    return {
        'instrument': 'EUR_USD',
        'timestamp': datetime.utcnow(),
        'timeframe': TimeFrame.H1,
        'open': Decimal('1.1000'),
        'high': Decimal('1.1010'),
        'low': Decimal('1.0990'),
        'close': Decimal('1.1005'),
        'volume': 100,
        'complete': True
    }


@pytest.fixture
def sample_ingestion_request():
    """Sample ingestion request for testing"""
    return DataIngestionRequest(
        instruments=['EUR_USD', 'GBP_USD'],
        timeframes=[TimeFrame.H1, TimeFrame.D],
        mode=DataMode.BATCH,
        start_date=datetime.utcnow() - timedelta(days=7),
        end_date=datetime.utcnow(),
        validate_data=True
    )


# Run tests with: pytest tests/test_market_data.py -v