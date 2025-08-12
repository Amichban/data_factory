"""
Market Data Service Module
Handles market data ingestion, processing, and storage with rate limiting and error handling
"""

import asyncio
import aiohttp
import uuid
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, AsyncGenerator, Tuple
from contextlib import asynccontextmanager

from app.config import settings
from app.models.market_data import (
    MarketDataCandle, MarketDataBatch, DataIngestionRequest, DataIngestionResponse,
    DataQualityMetrics, RateLimitStatus, DataSourceStatus, TimeFrame, DataMode
)
from app.services.firestore_service import firestore_service

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire rate limit permission"""
        async with self.lock:
            now = datetime.utcnow()
            # Remove requests older than the time window
            self.requests = [req for req in self.requests if (now - req).seconds < self.time_window]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def get_status(self) -> RateLimitStatus:
        """Get current rate limit status"""
        now = datetime.utcnow()
        # Clean old requests
        self.requests = [req for req in self.requests if (now - req).seconds < self.time_window]
        
        requests_made = len(self.requests)
        requests_remaining = max(0, self.max_requests - requests_made)
        window_start = now - timedelta(seconds=self.time_window)
        
        # Calculate reset time (when oldest request expires)
        if self.requests:
            oldest_request = min(self.requests)
            reset_time = oldest_request + timedelta(seconds=self.time_window)
        else:
            reset_time = now + timedelta(seconds=self.time_window)
        
        return RateLimitStatus(
            requests_made=requests_made,
            requests_remaining=requests_remaining,
            reset_time=reset_time,
            current_window_start=window_start,
            is_limited=requests_remaining == 0
        )


class OandaDataProvider:
    """OANDA API data provider with rate limiting and error handling"""
    
    def __init__(self):
        self.api_key = settings.OANDA_API_KEY
        self.api_url = settings.OANDA_API_URL
        self.stream_url = settings.OANDA_STREAM_URL
        self.rate_limiter = RateLimiter(
            max_requests=settings.MARKET_DATA_RATE_LIMIT,
            time_window=60
        )
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept-Datetime-Format': 'RFC3339',
                'Content-Type': 'application/json'
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited HTTP request with retry logic"""
        for attempt in range(settings.MARKET_DATA_RETRY_ATTEMPTS):
            try:
                # Check rate limit
                if not await self.rate_limiter.acquire():
                    logger.warning("Rate limit exceeded, waiting...")
                    await asyncio.sleep(settings.MARKET_DATA_RETRY_DELAY * (attempt + 1))
                    continue
                
                session = await self._get_session()
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        logger.warning(f"Rate limited by API, attempt {attempt + 1}")
                        await asyncio.sleep(settings.MARKET_DATA_RETRY_DELAY * (attempt + 1))
                        continue
                    else:
                        response.raise_for_status()
                        
            except aiohttp.ClientError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt == settings.MARKET_DATA_RETRY_ATTEMPTS - 1:
                    raise
                await asyncio.sleep(settings.MARKET_DATA_RETRY_DELAY * (attempt + 1))
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == settings.MARKET_DATA_RETRY_ATTEMPTS - 1:
                    raise
                await asyncio.sleep(settings.MARKET_DATA_RETRY_DELAY * (attempt + 1))
        
        raise Exception(f"Failed to make request after {settings.MARKET_DATA_RETRY_ATTEMPTS} attempts")
    
    async def get_historical_data(
        self, 
        instrument: str, 
        timeframe: TimeFrame,
        start_time: datetime,
        end_time: datetime,
        count: Optional[int] = None
    ) -> List[MarketDataCandle]:
        """Fetch historical market data"""
        try:
            url = f"{self.api_url}/v3/instruments/{instrument}/candles"
            
            params = {
                'granularity': timeframe.value,
                'from': start_time.isoformat() + 'Z',
                'to': end_time.isoformat() + 'Z'
            }
            
            if count:
                params['count'] = count
            
            logger.info(f"Fetching historical data for {instrument} {timeframe.value} from {start_time} to {end_time}")
            
            response_data = await self._make_request(url, params)
            candles = []
            
            for candle_data in response_data.get('candles', []):
                if not candle_data['complete']:
                    continue  # Skip incomplete candles
                
                mid = candle_data['mid']
                candle = MarketDataCandle(
                    instrument=instrument,
                    timestamp=datetime.fromisoformat(candle_data['time'].replace('Z', '+00:00')),
                    timeframe=timeframe,
                    open=Decimal(mid['o']),
                    high=Decimal(mid['h']),
                    low=Decimal(mid['l']),
                    close=Decimal(mid['c']),
                    volume=candle_data.get('volume', 0),
                    complete=candle_data['complete'],
                    data_source='oanda'
                )
                candles.append(candle)
            
            logger.info(f"Retrieved {len(candles)} candles for {instrument} {timeframe.value}")
            return candles
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {instrument} {timeframe.value}: {e}")
            raise
    
    async def stream_real_time_data(
        self, 
        instruments: List[str]
    ) -> AsyncGenerator[MarketDataCandle, None]:
        """Stream real-time market data"""
        url = f"{self.stream_url}/v3/accounts/{settings.OANDA_ACCOUNT_ID}/pricing/stream"
        params = {'instruments': ','.join(instruments)}
        
        session = await self._get_session()
        
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Stream connection failed: {response.status}")
                
                async for line in response.content:
                    if line:
                        try:
                            data = await line.json()
                            if data.get('type') == 'PRICE':
                                # Convert price data to candle format (simplified)
                                # In real implementation, you'd need to aggregate ticks into candles
                                yield self._price_to_candle(data)
                        except Exception as e:
                            logger.error(f"Error processing stream data: {e}")
                            
        except Exception as e:
            logger.error(f"Error in data stream: {e}")
            raise
    
    def _price_to_candle(self, price_data: Dict[str, Any]) -> MarketDataCandle:
        """Convert price tick to candle format (simplified)"""
        # This is a simplified conversion - real implementation would aggregate ticks
        instrument = price_data['instrument']
        timestamp = datetime.fromisoformat(price_data['time'].replace('Z', '+00:00'))
        
        # Use mid price for simplicity
        if 'closeoutBid' in price_data and 'closeoutAsk' in price_data:
            price = (Decimal(price_data['closeoutBid']) + Decimal(price_data['closeoutAsk'])) / 2
        else:
            price = Decimal(price_data.get('price', '0'))
        
        return MarketDataCandle(
            instrument=instrument,
            timestamp=timestamp,
            timeframe=TimeFrame.H1,  # Default to H1 for real-time
            open=price,
            high=price,
            low=price,
            close=price,
            complete=False,
            data_source='oanda'
        )
    
    async def check_health(self) -> DataSourceStatus:
        """Check OANDA API health"""
        start_time = datetime.utcnow()
        
        try:
            url = f"{self.api_url}/v3/accounts"
            response_data = await self._make_request(url, {})
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return DataSourceStatus(
                source_name='oanda',
                is_available=True,
                response_time_ms=response_time,
                rate_limit_status=self.rate_limiter.get_status()
            )
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return DataSourceStatus(
                source_name='oanda',
                is_available=False,
                response_time_ms=response_time,
                error_message=str(e),
                rate_limit_status=self.rate_limiter.get_status()
            )


class MarketDataService:
    """Main service for market data operations"""
    
    def __init__(self):
        self.data_provider = OandaDataProvider()
        self.firestore = firestore_service
    
    async def process_ingestion_request(self, request: DataIngestionRequest) -> DataIngestionResponse:
        """Process a data ingestion request"""
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        response = DataIngestionResponse(
            request_id=request_id,
            status='processing',
            message='Starting data ingestion',
            started_at=start_time
        )
        
        try:
            logger.info(f"Processing ingestion request {request_id}: {request.mode.value} mode")
            
            if request.mode == DataMode.BATCH:
                await self._process_batch_ingestion(request, response)
            elif request.mode == DataMode.STREAM:
                await self._process_stream_ingestion(request, response)
            elif request.mode == DataMode.SPIKE:
                await self._process_spike_ingestion(request, response)
            
            response.completed_at = datetime.utcnow()
            response.processing_time_seconds = (response.completed_at - response.started_at).total_seconds()
            response.status = 'completed'
            response.message = f'Ingestion completed successfully. Processed {response.candles_ingested} candles.'
            
        except Exception as e:
            logger.error(f"Error processing ingestion request {request_id}: {e}")
            response.status = 'failed'
            response.message = f'Ingestion failed: {str(e)}'
            response.errors.append(str(e))
            response.completed_at = datetime.utcnow()
            response.processing_time_seconds = (response.completed_at - response.started_at).total_seconds()
        
        return response
    
    async def _process_batch_ingestion(self, request: DataIngestionRequest, response: DataIngestionResponse):
        """Process batch/historical data ingestion"""
        start_date = request.start_date or datetime.utcnow() - timedelta(days=30)
        end_date = request.end_date or datetime.utcnow()
        
        # Validate date range
        if (end_date - start_date).days > settings.MAX_HISTORICAL_DAYS:
            raise ValueError(f"Date range cannot exceed {settings.MAX_HISTORICAL_DAYS} days")
        
        # Check if we have OANDA credentials
        if not settings.OANDA_API_KEY:
            response.status = 'skipped'
            response.message = 'No OANDA API key configured. Using existing Firestore data.'
            response.warnings.append('Data ingestion requires OANDA API credentials')
            return
        
        for instrument in request.instruments:
            try:
                response.instruments_processed += 1
                
                for timeframe in request.timeframes:
                    candles = await self.data_provider.get_historical_data(
                        instrument=instrument,
                        timeframe=timeframe,
                        start_time=start_date,
                        end_time=end_date
                    )
                    
                    # Validate and store candles
                    for candle in candles:
                        try:
                            if request.validate_data:
                                self._validate_candle_data(candle)
                            
                            await self._store_candle(candle)
                            response.candles_ingested += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to store candle for {instrument}: {e}")
                            response.candles_failed += 1
                            response.errors.append(f"Failed to store {instrument} candle: {str(e)}")
                    
                    # Update progress
                    logger.info(f"Completed {instrument} {timeframe.value}: {len(candles)} candles")
                    
            except Exception as e:
                logger.error(f"Error processing instrument {instrument}: {e}")
                response.errors.append(f"Failed to process {instrument}: {str(e)}")
    
    async def _process_stream_ingestion(self, request: DataIngestionRequest, response: DataIngestionResponse):
        """Process real-time streaming data ingestion"""
        logger.info(f"Starting stream ingestion for {len(request.instruments)} instruments")
        
        try:
            async for candle in self.data_provider.stream_real_time_data(request.instruments):
                try:
                    if request.validate_data:
                        self._validate_candle_data(candle)
                    
                    await self._store_candle(candle)
                    response.candles_ingested += 1
                    
                    # Log progress periodically
                    if response.candles_ingested % 100 == 0:
                        logger.info(f"Processed {response.candles_ingested} streaming candles")
                        
                except Exception as e:
                    logger.error(f"Failed to process streaming candle: {e}")
                    response.candles_failed += 1
                    response.errors.append(f"Streaming candle error: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Stream ingestion error: {e}")
            raise
    
    async def _process_spike_ingestion(self, request: DataIngestionRequest, response: DataIngestionResponse):
        """Process on-demand spike data ingestion"""
        # For spike mode, get the latest few candles for quick processing
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)  # Last 24 hours
        
        for instrument in request.instruments:
            try:
                response.instruments_processed += 1
                
                for timeframe in request.timeframes:
                    candles = await self.data_provider.get_historical_data(
                        instrument=instrument,
                        timeframe=timeframe,
                        start_time=start_time,
                        end_time=end_time,
                        count=50  # Limit for spike processing
                    )
                    
                    # Process only the most recent candles
                    recent_candles = sorted(candles, key=lambda x: x.timestamp, reverse=True)[:10]
                    
                    for candle in recent_candles:
                        try:
                            if request.validate_data:
                                self._validate_candle_data(candle)
                            
                            await self._store_candle(candle)
                            response.candles_ingested += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to store spike candle for {instrument}: {e}")
                            response.candles_failed += 1
                    
                    logger.info(f"Spike processing completed for {instrument} {timeframe.value}")
                    
            except Exception as e:
                logger.error(f"Error in spike processing for {instrument}: {e}")
                response.errors.append(f"Spike processing failed for {instrument}: {str(e)}")
    
    def _validate_candle_data(self, candle: MarketDataCandle):
        """Validate candle data quality"""
        # Check for reasonable price values
        if candle.high < candle.low:
            raise ValueError(f"High price {candle.high} is less than low price {candle.low}")
        
        if candle.open < 0 or candle.close < 0:
            raise ValueError("Prices cannot be negative")
        
        # Check for reasonable price ranges (basic sanity check)
        price_range = float(candle.high - candle.low)
        avg_price = float((candle.high + candle.low) / 2)
        
        if price_range / avg_price > 0.1:  # 10% range seems too high for most instruments
            raise ValueError(f"Unusual price range detected: {price_range / avg_price * 100:.2f}%")
    
    async def _store_candle(self, candle: MarketDataCandle):
        """Store candle data in Firestore"""
        try:
            # Convert candle to dict for storage
            candle_data = {
                'instrument': candle.instrument,
                'timestamp': candle.timestamp,
                'timeframe': candle.timeframe.value,
                'open': float(candle.open),
                'high': float(candle.high),
                'low': float(candle.low),
                'close': float(candle.close),
                'volume': candle.volume,
                'complete': candle.complete,
                'data_source': candle.data_source,
                'created_at': candle.created_at
            }
            
            # Store in market_data collection with composite key
            doc_id = f"{candle.instrument}_{candle.timeframe.value}_{int(candle.timestamp.timestamp())}"
            collection_ref = self.firestore.get_collection('market_data')
            doc_ref = collection_ref.document(doc_id)
            
            # Check if document exists
            existing_doc = doc_ref.get()
            if existing_doc.exists:
                # Update existing document
                doc_ref.update(candle_data)
                logger.debug(f"Updated existing candle: {doc_id}")
            else:
                # Create new document
                doc_ref.set(candle_data)
                logger.debug(f"Created new candle: {doc_id}")
                
        except Exception as e:
            logger.error(f"Failed to store candle {candle.instrument}: {e}")
            raise
    
    async def get_data_quality_metrics(self, instrument: str, timeframe: TimeFrame) -> DataQualityMetrics:
        """Calculate data quality metrics for an instrument/timeframe"""
        try:
            # Query candles from the last 30 days
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)
            
            query = (self.firestore.get_collection('market_data')
                    .where('instrument', '==', instrument)
                    .where('timeframe', '==', timeframe.value)
                    .where('timestamp', '>=', start_time)
                    .where('timestamp', '<=', end_time)
                    .order_by('timestamp'))
            
            docs = query.stream()
            candles = []
            
            for doc in docs:
                candle_data = doc.to_dict()
                candles.append(candle_data)
            
            # Calculate metrics
            total_candles = len(candles)
            complete_candles = sum(1 for c in candles if c.get('complete', True))
            
            # Check for duplicates and missing periods
            timestamps = [c['timestamp'] for c in candles]
            unique_timestamps = set(timestamps)
            duplicate_periods = len(timestamps) - len(unique_timestamps)
            
            # Simplified missing period detection
            missing_periods = 0
            if len(unique_timestamps) > 1:
                sorted_times = sorted(unique_timestamps)
                # Calculate expected intervals based on timeframe
                if timeframe == TimeFrame.H1:
                    expected_interval = timedelta(hours=1)
                elif timeframe == TimeFrame.H4:
                    expected_interval = timedelta(hours=4)
                elif timeframe == TimeFrame.D:
                    expected_interval = timedelta(days=1)
                else:  # Weekly
                    expected_interval = timedelta(days=7)
                
                for i in range(1, len(sorted_times)):
                    actual_gap = sorted_times[i] - sorted_times[i-1]
                    if actual_gap > expected_interval * 1.5:  # Allow some tolerance
                        missing_periods += 1
            
            # Price gap detection (simplified)
            price_gaps = 0
            for i in range(1, len(candles)):
                prev_close = candles[i-1].get('close', 0)
                curr_open = candles[i].get('open', 0)
                if abs(prev_close - curr_open) / prev_close > 0.05:  # 5% gap
                    price_gaps += 1
            
            # Volume anomaly detection
            volumes = [c.get('volume', 0) for c in candles if c.get('volume')]
            volume_anomalies = 0
            if volumes:
                avg_volume = sum(volumes) / len(volumes)
                volume_anomalies = sum(1 for v in volumes if v > avg_volume * 5 or v < avg_volume * 0.2)
            
            return DataQualityMetrics(
                instrument=instrument,
                timeframe=timeframe,
                total_candles=total_candles,
                complete_candles=complete_candles,
                missing_periods=missing_periods,
                duplicate_periods=duplicate_periods,
                price_gaps=price_gaps,
                volume_anomalies=volume_anomalies
            )
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics for {instrument} {timeframe.value}: {e}")
            raise
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall market data service health"""
        try:
            # Check Firestore health (primary data source)
            firestore_health = self.firestore.health_check()
            
            # For now, skip OANDA provider check since we're using Firestore
            # provider_status = await self.data_provider.check_health()
            
            overall_health = firestore_health['status'] == 'healthy'
            
            return {
                'status': 'healthy' if overall_health else 'degraded',
                'data_source': 'firestore',
                'firestore': firestore_health,
                'supported_instruments': settings.SUPPORTED_INSTRUMENTS,
                'supported_timeframes': [tf.value for tf in TimeFrame],
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Cleanup resources"""
        await self.data_provider.close()


# Singleton instance
market_data_service = MarketDataService()