"""
Logging middleware for FastAPI.

This middleware provides structured logging for all HTTP requests and responses,
including request/response times, status codes, and error tracking.
"""

import time
import uuid
from typing import Callable
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Logs all incoming requests with timing information, status codes,
    and any errors that occur during processing.
    """

    def __init__(self, app, log_body: bool = False):
        """
        Initialize the logging middleware.
        
        Args:
            app: FastAPI application instance
            log_body: Whether to log request/response bodies (disabled by default for security)
        """
        super().__init__(app)
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log details.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The HTTP response
        """
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())
        
        # Start timing
        start_time = time.time()
        
        # Extract request information
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Remove sensitive headers
        sensitive_headers = {"authorization", "x-api-key", "cookie", "x-auth-token"}
        request_info["headers"] = {
            k: v if k.lower() not in sensitive_headers else "[REDACTED]"
            for k, v in request_info["headers"].items()
        }

        # Log request body if enabled (be careful with sensitive data)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_info["body_size"] = len(body)
                    # Don't log actual body content for security
                    # request_info["body"] = body.decode("utf-8")[:1000]  # First 1000 chars
            except Exception as e:
                request_info["body_read_error"] = str(e)

        # Log incoming request
        logger.info("Request started", **request_info)

        # Process request
        response = None
        error = None
        
        try:
            response = await call_next(request)
        except Exception as e:
            error = e
            logger.error(
                "Request failed with exception",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            # Re-raise the exception to let FastAPI handle it
            raise

        # Calculate response time
        process_time = time.time() - start_time

        # Extract response information
        response_info = {
            "request_id": request_id,
            "status_code": response.status_code if response else None,
            "response_time_ms": round(process_time * 1000, 2),
            "response_size": None,
        }

        # Get response size if available
        if response and hasattr(response, "headers"):
            content_length = response.headers.get("content-length")
            if content_length:
                response_info["response_size"] = int(content_length)

        # Determine log level based on status code
        if response:
            if response.status_code >= 500:
                log_level = "error"
            elif response.status_code >= 400:
                log_level = "warning"
            else:
                log_level = "info"
        else:
            log_level = "error"

        # Log response
        log_message = "Request completed"
        if error:
            log_message = "Request failed"
            response_info["error"] = str(error)

        getattr(logger, log_level)(log_message, **response_info)

        # Add request ID to response headers for tracing
        if response:
            response.headers["X-Request-ID"] = request_id

        return response