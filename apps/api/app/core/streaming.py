"""
Core Streaming Infrastructure for Real-time Data Processing

Provides circuit breakers, retry logic, and connection management for streaming data.
"""

import asyncio
from typing import Dict, Any, Optional, Callable, List, AsyncIterator
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time
import structlog
from contextlib import asynccontextmanager

logger = structlog.get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: int = 60  # Seconds before attempting recovery
    success_threshold: int = 3  # Successful calls to close circuit
    timeout: float = 30.0  # Call timeout in seconds


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for fault tolerance.
    Prevents cascading failures by temporarily blocking calls to failing services.
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            name: Circuit breaker identifier
            config: Configuration settings
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change = datetime.utcnow()
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        async with self._lock:
            # Check circuit state
            if self.state == CircuitState.OPEN:
                if await self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.last_state_change = datetime.utcnow()
                    logger.info(f"Circuit breaker {self.name} entering half-open state")
                else:
                    raise Exception(f"Circuit breaker is OPEN")
        
        try:
            # Execute function with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            await self._on_success()
            return result
            
        except asyncio.TimeoutError as e:
            await self._on_failure()
            logger.error(f"Circuit breaker {self.name} timeout", error=str(e))
            raise
        except Exception as e:
            await self._on_failure()
            logger.error(f"Circuit breaker {self.name} failure", error=str(e))
            raise
    
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.last_state_change = datetime.utcnow()
                    logger.info(f"Circuit breaker {self.name} closed")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.success_count = 0
                self.last_state_change = datetime.utcnow()
                logger.warning(f"Circuit breaker {self.name} reopened")
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    self.last_state_change = datetime.utcnow()
                    logger.warning(f"Circuit breaker {self.name} opened after {self.failure_count} failures")
    
    async def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset"""
        if self.last_failure_time:
            elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
            return elapsed >= self.config.recovery_timeout
        return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_state_change': self.last_state_change.isoformat()
        }


class RetryPolicy:
    """
    Retry policy with exponential backoff and jitter.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry policy.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff (deprecated, use backoff_factor)
            backoff_factor: Backoff multiplier for exponential backoff
            jitter: Add random jitter to delays
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        # Support both exponential_base and backoff_factor
        self.exponential_base = backoff_factor if backoff_factor != 2.0 else exponential_base
        self.backoff_factor = self.exponential_base
        self.jitter = jitter
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{self.max_retries}",
                        error=str(e),
                        delay=delay
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All retry attempts failed",
                        attempts=self.max_retries + 1,
                        error=str(e)
                    )
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random())
        
        return delay


class StreamBuffer:
    """
    Memory-efficient circular buffer for streaming data.
    Prevents memory accumulation in long-running streams.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize stream buffer.
        
        Args:
            max_size: Maximum buffer size
        """
        self.max_size = max_size
        self._buffer: List[Any] = []
        self._items_added = 0
        self._items_dropped = 0
        self._lock = asyncio.Lock()
    
    async def add(self, item: Any) -> None:
        """Add item to buffer"""
        async with self._lock:
            self._buffer.append(item)
            self._items_added += 1
            
            # Remove oldest items if buffer exceeds max size
            if len(self._buffer) > self.max_size:
                removed = len(self._buffer) - self.max_size
                self._buffer = self._buffer[removed:]
                self._items_dropped += removed
                logger.debug(f"Buffer overflow, removed {removed} items")
    
    async def get_batch(self, batch_size: int) -> List[Any]:
        """Get batch of items from buffer"""
        async with self._lock:
            batch = self._buffer[:batch_size]
            self._buffer = self._buffer[batch_size:]
            return batch
    
    async def get_all(self) -> List[Any]:
        """Get all items from buffer"""
        async with self._lock:
            items = self._buffer.copy()
            self._buffer.clear()
            return items
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics"""
        return {
            'current_size': len(self._buffer),
            'max_size': self.max_size,
            'total_added': self._items_added,
            'total_dropped': self._items_dropped,
            'items_added': self._items_added,
            'items_dropped': self._items_dropped
        }
    
    def clear(self):
        """Clear the buffer"""
        self._buffer.clear()


class StreamConnection:
    """
    Manages streaming connection with automatic reconnection.
    """
    
    def __init__(
        self,
        name: str,
        connect_func: Callable,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize stream connection.
        
        Args:
            name: Connection identifier
            connect_func: Async function to establish connection
            circuit_breaker: Circuit breaker for fault tolerance
            retry_policy: Retry policy for reconnection
        """
        self.name = name
        self.connect_func = connect_func
        self.circuit_breaker = circuit_breaker or CircuitBreaker(f"{name}_circuit")
        self.retry_policy = retry_policy or RetryPolicy()
        self.connection = None
        self.is_connected = False
        self.reconnect_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._stop_event = asyncio.Event()
    
    async def connect(self) -> None:
        """Establish connection with circuit breaker and retry logic"""
        async with self._lock:
            if self.is_connected:
                return
            
            try:
                # Use circuit breaker for connection
                self.connection = await self.circuit_breaker.call(
                    self.retry_policy.execute,
                    self.connect_func
                )
                self.is_connected = True
                logger.info(f"Stream connection {self.name} established")
                
            except Exception as e:
                logger.error(f"Failed to establish stream connection {self.name}", error=str(e))
                raise
    
    async def disconnect(self) -> None:
        """Disconnect stream"""
        async with self._lock:
            if not self.is_connected:
                return
            
            self._stop_event.set()
            
            if self.reconnect_task:
                self.reconnect_task.cancel()
                try:
                    await self.reconnect_task
                except asyncio.CancelledError:
                    pass
            
            if self.connection:
                try:
                    if hasattr(self.connection, 'close'):
                        await self.connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection {self.name}", error=str(e))
            
            self.connection = None
            self.is_connected = False
            logger.info(f"Stream connection {self.name} disconnected")
    
    async def auto_reconnect(self) -> None:
        """Automatically reconnect on disconnection"""
        while not self._stop_event.is_set():
            if not self.is_connected:
                try:
                    await self.connect()
                except Exception as e:
                    logger.error(f"Reconnection failed for {self.name}", error=str(e))
                    await asyncio.sleep(10)  # Wait before retry
            else:
                await asyncio.sleep(1)  # Check connection status
    
    @asynccontextmanager
    async def stream(self) -> AsyncIterator:
        """
        Context manager for streaming data.
        
        Yields:
            Stream connection
        """
        await self.connect()
        
        # Start auto-reconnect task
        self.reconnect_task = asyncio.create_task(self.auto_reconnect())
        
        try:
            yield self.connection
        finally:
            await self.disconnect()
    
    def get_status(self) -> Dict[str, Any]:
        """Get connection status"""
        return {
            'name': self.name,
            'is_connected': self.is_connected,
            'circuit_breaker': self.circuit_breaker.get_state()
        }


class StreamProcessor:
    """
    Base class for stream processors with performance monitoring.
    """
    
    def __init__(self, name: str):
        """
        Initialize stream processor.
        
        Args:
            name: Processor identifier
        """
        self.name = name
        self.metrics = {
            'items_processed': 0,
            'items_failed': 0,
            'processing_time_total': 0.0,
            'last_processed': None
        }
        self._lock = asyncio.Lock()
    
    async def process(self, item: Any) -> Any:
        """
        Process a single stream item.
        
        Args:
            item: Item to process
            
        Returns:
            Processed result
        """
        start_time = time.time()
        
        try:
            result = await self._process_item(item)
            
            async with self._lock:
                self.metrics['items_processed'] += 1
                self.metrics['processing_time_total'] += time.time() - start_time
                self.metrics['last_processed'] = datetime.utcnow()
            
            return result
            
        except Exception as e:
            async with self._lock:
                self.metrics['items_failed'] += 1
            
            logger.error(f"Stream processor {self.name} failed", error=str(e))
            raise
    
    async def _process_item(self, item: Any) -> Any:
        """
        Process implementation (to be overridden).
        
        Args:
            item: Item to process
            
        Returns:
            Processed result
        """
        raise NotImplementedError
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        with self._lock:
            metrics = self.metrics.copy()
            
            if metrics['items_processed'] > 0:
                metrics['avg_processing_time'] = (
                    metrics['processing_time_total'] / metrics['items_processed']
                )
            else:
                metrics['avg_processing_time'] = 0
            
            if metrics['last_processed']:
                metrics['last_processed'] = metrics['last_processed'].isoformat()
            
            return metrics