"""
Error Handling and Sanitization
Provides secure error messages that don't leak system information

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import os
import traceback
from typing import Optional, Dict, Any
from flask import jsonify
from fastapi import HTTPException, status

# SECURITY: Environment-based error detail level
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'
PRODUCTION_MODE = os.getenv('ENVIRONMENT', 'production').lower() == 'production'


class SecureErrorHandler:
    """Handles errors securely without leaking system information"""
    
    @staticmethod
    def sanitize_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sanitize error message for production
        
        Args:
            error: Exception object
            context: Additional context (request info, etc.)
            
        Returns:
            Sanitized error dictionary
        """
        error_type = type(error).__name__
        
        # In production, provide generic error messages
        if PRODUCTION_MODE and not DEBUG_MODE:
            # Generic error messages that don't leak information
            generic_errors = {
                'ValueError': 'Invalid input provided',
                'KeyError': 'Required field missing',
                'TypeError': 'Invalid data type',
                'AttributeError': 'Invalid operation',
                'PermissionError': 'Access denied',
                'AuthenticationError': 'Authentication failed',
                'FileNotFoundError': 'Resource not found',
                'ConnectionError': 'Service temporarily unavailable',
                'TimeoutError': 'Request timeout',
            }
            
            message = generic_errors.get(error_type, 'An error occurred')
            error_id = SecureErrorHandler._generate_error_id(error)
            
            return {
                'error': message,
                'error_type': 'internal_error',
                'error_id': error_id,
                'message': 'Please contact support with the error ID if this persists'
            }
        
        # In debug mode, provide more details (but still sanitized)
        else:
            # Sanitize the error message
            error_message = str(error)
            
            # Remove sensitive patterns
            from .log_sanitizer import sanitize_string
            sanitized_message = sanitize_string(error_message)
            
            return {
                'error': sanitized_message,
                'error_type': error_type,
                'message': 'An error occurred processing your request'
            }
    
    @staticmethod
    def _generate_error_id(error: Exception) -> str:
        """Generate unique error ID for tracking"""
        import hashlib
        import time
        
        error_str = f"{type(error).__name__}{str(error)}{time.time()}"
        return hashlib.sha256(error_str.encode()).hexdigest()[:16]
    
    @staticmethod
    def handle_flask_error(error: Exception) -> tuple:
        """
        Handle Flask error and return sanitized response
        
        Usage:
            @app.errorhandler(Exception)
            def handle_error(error):
                return SecureErrorHandler.handle_flask_error(error)
        """
        sanitized = SecureErrorHandler.sanitize_error(error)
        status_code = 500
        
        # Map specific errors to appropriate status codes
        if isinstance(error, ValueError):
            status_code = 400
        elif isinstance(error, PermissionError):
            status_code = 403
        elif isinstance(error, FileNotFoundError):
            status_code = 404
        elif isinstance(error, ConnectionError):
            status_code = 503
        elif isinstance(error, TimeoutError):
            status_code = 504
        
        # Log full error details server-side (for debugging)
        if DEBUG_MODE:
            import logging
            logging.error(f"Error: {error}", exc_info=True)
        
        return jsonify(sanitized), status_code
    
    @staticmethod
    def create_fastapi_exception(error: Exception, status_code: int = 500) -> HTTPException:
        """
        Create FastAPI HTTPException with sanitized error
        
        Usage:
            raise SecureErrorHandler.create_fastapi_exception(ValueError("Invalid input"))
        """
        sanitized = SecureErrorHandler.sanitize_error(error)
        
        return HTTPException(
            status_code=status_code,
            detail=sanitized
        )


# Flask error handlers
def register_flask_error_handlers(app):
    """
    Register secure error handlers for Flask app
    
    Usage:
        register_flask_error_handlers(app)
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'Invalid request format or parameters'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(413)
    def request_too_large(error):
        return jsonify({
            'error': 'Request too large',
            'message': 'Request payload exceeds maximum size'
        }), 413
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        return SecureErrorHandler.handle_flask_error(error)
    
    @app.errorhandler(Exception)
    def handle_all_errors(error):
        return SecureErrorHandler.handle_flask_error(error)

