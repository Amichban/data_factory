"""
Rate Limiting Middleware for Event Management API

Implements rate limiting using Redis for distributed rate limiting across multiple instances.
"""

import time
import hashlib
from typing import Optional, Tuple
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import structlog
import redis.asyncio as redis
from app.config import settings

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.
    
    Limits requests per IP address or API key.
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        redis_url: Optional[str] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
            redis_url: Redis connection URL for distributed rate limiting
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client = None
        
        # In-memory fallback for when Redis is unavailable
        self.local_cache = {}
        self.cache_cleanup_counter = 0
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response or rate limit error
        """
        # Skip rate limiting for health endpoints
        if request.url.path.endswith("/health"):
            return await call_next(request)
        
        # Get client identifier (IP or API key)
        client_id = self._get_client_id(request)
        
        # Check rate limits
        is_allowed, retry_after = await self._check_rate_limit(client_id)
        
        if not is_allowed:
            logger.warning(
                "Rate limit exceeded",
                client_id=client_id,
                path=request.url.path,
                retry_after=retry_after
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request.
        
        Args:
            request: Incoming request
            
        Returns:
            Client identifier string
        """
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Use IP address as fallback
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for X-Forwarded-For header (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        current_time = int(time.time())
        
        # Try Redis first
        if self.redis_client or self.redis_url:
            try:
                return await self._check_redis_rate_limit(client_id, current_time)
            except Exception as e:
                logger.error(f"Redis rate limit check failed: {e}, falling back to local cache")
        
        # Fallback to local cache
        return self._check_local_rate_limit(client_id, current_time)
    
    async def _check_redis_rate_limit(self, client_id: str, current_time: int) -> Tuple[bool, int]:
        """
        Check rate limit using Redis.
        
        Args:
            client_id: Client identifier
            current_time: Current timestamp
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        if not self.redis_client:
            self.redis_client = await redis.from_url(self.redis_url)
        
        # Keys for minute and hour windows
        minute_key = f"rate_limit:minute:{client_id}:{current_time // 60}"
        hour_key = f"rate_limit:hour:{client_id}:{current_time // 3600}"
        
        # Increment counters
        pipe = self.redis_client.pipeline()
        pipe.incr(minute_key)
        pipe.expire(minute_key, 60)
        pipe.incr(hour_key)
        pipe.expire(hour_key, 3600)
        
        minute_count, _, hour_count, _ = await pipe.execute()
        
        # Check limits
        if minute_count > self.requests_per_minute:
            retry_after = 60 - (current_time % 60)
            return False, retry_after
        
        if hour_count > self.requests_per_hour:
            retry_after = 3600 - (current_time % 3600)
            return False, retry_after
        
        return True, 0
    
    def _check_local_rate_limit(self, client_id: str, current_time: int) -> Tuple[bool, int]:
        """
        Check rate limit using local in-memory cache.
        
        Args:
            client_id: Client identifier
            current_time: Current timestamp
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        # Clean up old entries periodically
        self.cache_cleanup_counter += 1
        if self.cache_cleanup_counter % 100 == 0:
            self._cleanup_local_cache(current_time)
        
        # Initialize client data if not exists
        if client_id not in self.local_cache:
            self.local_cache[client_id] = {
                'minute_requests': [],
                'hour_requests': []
            }
        
        client_data = self.local_cache[client_id]
        
        # Remove old requests outside the windows
        client_data['minute_requests'] = [
            ts for ts in client_data['minute_requests']
            if ts > current_time - 60
        ]
        client_data['hour_requests'] = [
            ts for ts in client_data['hour_requests']
            if ts > current_time - 3600
        ]
        
        # Check minute limit
        if len(client_data['minute_requests']) >= self.requests_per_minute:
            oldest_minute = min(client_data['minute_requests'])
            retry_after = 60 - (current_time - oldest_minute)
            return False, max(1, retry_after)
        
        # Check hour limit
        if len(client_data['hour_requests']) >= self.requests_per_hour:
            oldest_hour = min(client_data['hour_requests'])
            retry_after = 3600 - (current_time - oldest_hour)
            return False, max(1, retry_after)
        
        # Add current request
        client_data['minute_requests'].append(current_time)
        client_data['hour_requests'].append(current_time)
        
        return True, 0
    
    def _cleanup_local_cache(self, current_time: int):
        """
        Clean up old entries from local cache.
        
        Args:
            current_time: Current timestamp
        """
        clients_to_remove = []
        
        for client_id, client_data in self.local_cache.items():
            # Remove if no recent requests
            if (not client_data['hour_requests'] or 
                max(client_data['hour_requests']) < current_time - 3600):
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self.local_cache[client_id]
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """
        Get remaining requests for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Number of remaining requests
        """
        current_time = int(time.time())
        
        if self.redis_client:
            try:
                minute_key = f"rate_limit:minute:{client_id}:{current_time // 60}"
                count = await self.redis_client.get(minute_key)
                if count:
                    return max(0, self.requests_per_minute - int(count))
            except:
                pass
        
        # Fallback to local cache
        if client_id in self.local_cache:
            minute_requests = self.local_cache[client_id]['minute_requests']
            recent_requests = [
                ts for ts in minute_requests
                if ts > current_time - 60
            ]
            return max(0, self.requests_per_minute - len(recent_requests))
        
        return self.requests_per_minute


class APIKeyRateLimiter:
    """
    Enhanced rate limiter for API key authentication with tiered limits.
    """
    
    TIER_LIMITS = {
        "free": {"per_minute": 30, "per_hour": 500, "per_day": 5000},
        "basic": {"per_minute": 60, "per_hour": 1000, "per_day": 10000},
        "pro": {"per_minute": 120, "per_hour": 2000, "per_day": 50000},
        "enterprise": {"per_minute": 600, "per_hour": 10000, "per_day": 500000}
    }
    
    @classmethod
    async def check_api_key_limit(
        cls,
        api_key: str,
        tier: str = "free"
    ) -> Tuple[bool, dict]:
        """
        Check rate limit for API key with tier-based limits.
        
        Args:
            api_key: API key
            tier: API tier (free, basic, pro, enterprise)
            
        Returns:
            Tuple of (is_allowed, limit_info)
        """
        limits = cls.TIER_LIMITS.get(tier, cls.TIER_LIMITS["free"])
        
        # Implementation would check against Redis or database
        # This is a placeholder
        return True, {
            "tier": tier,
            "limits": limits,
            "remaining": limits
        }