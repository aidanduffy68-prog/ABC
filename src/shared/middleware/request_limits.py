"""
Request Size Limits Middleware
Prevents DoS attacks via large request payloads

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import os
from functools import wraps
from flask import request, jsonify
from fastapi import Request, HTTPException, status
try:
    from starlette.middleware.base import BaseHTTPMiddleware
except ImportError:
    try:
        from fastapi.middleware.base import BaseHTTPMiddleware
    except ImportError:
        BaseHTTPMiddleware = None

# SECURITY: Configurable request size limits
MAX_REQUEST_SIZE = int(os.getenv('MAX_REQUEST_SIZE_BYTES', 10 * 1024 * 1024))  # 10MB default
MAX_JSON_DEPTH = int(os.getenv('MAX_JSON_DEPTH', 10))  # Maximum JSON nesting depth


class RequestSizeLimitMiddleware:
    """FastAPI middleware to limit request size"""
    
    def __init__(self, app, max_size: int = MAX_REQUEST_SIZE):
        self.max_size = max_size
        if BaseHTTPMiddleware:
            # Create middleware class if BaseHTTPMiddleware available
            class _RequestSizeLimitMiddleware(BaseHTTPMiddleware):
                def __init__(self, app, max_size):
                    super().__init__(app)
                    self.max_size = max_size
                
                async def dispatch(self, request: Request, call_next):
                    # Check Content-Length header
                    content_length = request.headers.get('content-length')
                    if content_length:
                        try:
                            size = int(content_length)
                            if size > self.max_size:
                                raise HTTPException(
                                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                    detail={
                                        'error': 'Request too large',
                                        'message': f'Maximum request size is {self.max_size} bytes',
                                        'received': size,
                                        'limit': self.max_size
                                    }
                                )
                        except ValueError:
                            pass
                    
                    # Check actual body size if available
                    body = await request.body()
                    if len(body) > self.max_size:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail={
                                'error': 'Request too large',
                                'message': f'Maximum request size is {self.max_size} bytes',
                                'received': len(body),
                                'limit': self.max_size
                            }
                        )
                    
                    # Re-create request with body (FastAPI needs this)
                    async def receive():
                        return {'type': 'http.request', 'body': body}
                    
                    request._receive = receive
                    
                    return await call_next(request)
            
            self.middleware = _RequestSizeLimitMiddleware(app, max_size)
        else:
            self.middleware = None
    
    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail={
                            'error': 'Request too large',
                            'message': f'Maximum request size is {self.max_size} bytes',
                            'received': size,
                            'limit': self.max_size
                        }
                    )
            except ValueError:
                # Invalid content-length, let it through (will fail on read)
                pass
        
        # Check actual body size if available
        body = await request.body()
        if len(body) > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    'error': 'Request too large',
                    'message': f'Maximum request size is {self.max_size} bytes',
                    'received': len(body),
                    'limit': self.max_size
                }
            )
        
        # Re-create request with body (FastAPI needs this)
        async def receive():
            return {'type': 'http.request', 'body': body}
        
        request._receive = receive
        
        return await call_next(request)


# Flask decorator for request size limits
def limit_request_size(max_size: int = MAX_REQUEST_SIZE):
    """
    Flask decorator to limit request size
    
    Usage:
        @app.route('/api/v1/endpoint', methods=['POST'])
        @limit_request_size(max_size=5 * 1024 * 1024)  # 5MB
        def endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check Content-Length header
            content_length = request.headers.get('content-length')
            if content_length:
                try:
                    size = int(content_length)
                    if size > max_size:
                        return jsonify({
                            'error': 'Request too large',
                            'message': f'Maximum request size is {max_size} bytes',
                            'received': size,
                            'limit': max_size
                        }), 413
                except ValueError:
                    pass
            
            # Check actual content length if available
            if request.content_length and request.content_length > max_size:
                return jsonify({
                    'error': 'Request too large',
                    'message': f'Maximum request size is {max_size} bytes',
                    'received': request.content_length,
                    'limit': max_size
                }), 413
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# Flask before_request handler
def check_request_size():
    """Flask before_request handler to check request size globally"""
    content_length = request.headers.get('content-length')
    if content_length:
        try:
            size = int(content_length)
            if size > MAX_REQUEST_SIZE:
                return jsonify({
                    'error': 'Request too large',
                    'message': f'Maximum request size is {MAX_REQUEST_SIZE} bytes',
                    'received': size,
                    'limit': MAX_REQUEST_SIZE
                }), 413
        except ValueError:
            pass
    
    if request.content_length and request.content_length > MAX_REQUEST_SIZE:
        return jsonify({
            'error': 'Request too large',
            'message': f'Maximum request size is {MAX_REQUEST_SIZE} bytes',
            'received': request.content_length,
            'limit': MAX_REQUEST_SIZE
        }), 413
    
    return None

