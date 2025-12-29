"""
Request/Response Logging Middleware
Logs API requests and responses for observability

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import time
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from src.shared.middleware.log_sanitizer import safe_log

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests and responses
    
    Logs:
    - Request method, path, query params
    - Response status code
    - Request duration
    - Client IP (if available)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        safe_log(
            logger,
            'info',
            'Request: %s %s | Client: %s | Query: %s',
            request.method,
            request.url.path,
            client_ip,
            str(request.query_params) if request.query_params else "none"
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            safe_log(
                logger,
                'error',
                'Request failed: %s %s | Duration: %.2fms | Error: %s',
                request.method,
                request.url.path,
                duration_ms,
                str(e)[:100]
            )
            raise
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        safe_log(
            logger,
            'info',
            'Response: %s %s | Status: %d | Duration: %.2fms',
            request.method,
            request.url.path,
            response.status_code,
            duration_ms
        )
        
        return response

