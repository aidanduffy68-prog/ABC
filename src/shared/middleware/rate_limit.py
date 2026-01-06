"""
Rate Limiting Middleware
Prevents abuse and DoS attacks by limiting request rates

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import time
from typing import Dict, Optional
from functools import wraps
from collections import defaultdict
from flask import request, jsonify
from fastapi import Request, HTTPException, status
try:
    from starlette.middleware.base import BaseHTTPMiddleware
except ImportError:
    # Fallback for older FastAPI versions
    try:
        from fastapi.middleware.base import BaseHTTPMiddleware
    except ImportError:
        BaseHTTPMiddleware = None

# In-memory rate limit store (in production, use Redis)
_rate_limit_store: Dict[str, Dict[str, float]] = defaultdict(dict)


class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[Dict[str, int]]]:
        """
        Check if request is allowed
        
        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            
        Returns:
            (is_allowed, rate_limit_info)
        """
        now = time.time()
        key = identifier
        
        # Clean old entries
        if key in _rate_limit_store:
            _rate_limit_store[key] = {
                timestamp: count
                for timestamp, count in _rate_limit_store[key].items()
                if now - timestamp < self.window_seconds
            }
        
        # Count requests in current window
        current_count = sum(_rate_limit_store[key].values())
        
        if current_count >= self.max_requests:
            # Calculate reset time
            oldest_timestamp = min(_rate_limit_store[key].keys()) if _rate_limit_store[key] else now
            reset_time = int(oldest_timestamp + self.window_seconds)
            
            return False, {
                'limit': self.max_requests,
                'remaining': 0,
                'reset': reset_time,
                'retry_after': max(0, reset_time - int(now))
            }
        
        # Record this request
        _rate_limit_store[key][now] = _rate_limit_store[key].get(now, 0) + 1
        
        return True, {
            'limit': self.max_requests,
            'remaining': self.max_requests - current_count - 1,
            'reset': int(now + self.window_seconds)
        }


# Flask decorator for rate limiting
def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    Flask decorator to rate limit endpoints
    
    Usage:
        @app.route('/api/v1/endpoint')
        @rate_limit(max_requests=10, window_seconds=60)
        def endpoint():
            ...
    """
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP address)
            identifier = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown')
            
            is_allowed, rate_info = limiter.is_allowed(identifier)
            
            if not is_allowed:
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {rate_info["limit"]} per {window_seconds} seconds',
                    'retry_after': rate_info['retry_after']
                })
                response.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_info['reset'])
                response.headers['Retry-After'] = str(rate_info['retry_after'])
                return response, 429
            
            # Add rate limit headers to response
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response_obj, status_code = response
            else:
                response_obj = response
                status_code = 200
            
            if hasattr(response_obj, 'headers'):
                response_obj.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                response_obj.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response_obj.headers['X-RateLimit-Reset'] = str(rate_info['reset'])
            
            return response_obj, status_code if isinstance(response, tuple) else response
        
        return decorated_function
    return decorator


# FastAPI middleware for rate limiting
class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        if BaseHTTPMiddleware:
            # Use BaseHTTPMiddleware if available
            class _RateLimitMiddleware(BaseHTTPMiddleware):
                def __init__(self, app, limiter):
                    super().__init__(app)
                    self.limiter = limiter
                
                async def dispatch(self, request: Request, call_next):
                    # Get client identifier
                    identifier = request.client.host if request.client else 'unknown'
                    
                    is_allowed, rate_info = self.limiter.is_allowed(identifier)
                    
                    if not is_allowed:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail={
                                'error': 'Rate limit exceeded',
                                'message': f'Too many requests. Limit: {rate_info["limit"]} per {window_seconds} seconds',
                                'retry_after': rate_info['retry_after']
                            },
                            headers={
                                'X-RateLimit-Limit': str(rate_info['limit']),
                                'X-RateLimit-Remaining': str(rate_info['remaining']),
                                'X-RateLimit-Reset': str(rate_info['reset']),
                                'Retry-After': str(rate_info['retry_after'])
                            }
                        )
                    
                    response = await call_next(request)
                    
                    # Add rate limit headers
                    response.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                    response.headers['X-RateLimit-Reset'] = str(rate_info['reset'])
                    
                    return response
            
            self.middleware = _RateLimitMiddleware(app, RateLimiter(max_requests, window_seconds))
        else:
            # Fallback if BaseHTTPMiddleware not available
            self.middleware = None
            self.limiter = RateLimiter(max_requests, window_seconds)

