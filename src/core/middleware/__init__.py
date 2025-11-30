"""
Security Middleware Package
Provides authentication, authorization, rate limiting, and log sanitization

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from .auth import (
    generate_token,
    verify_token,
    verify_fastapi_token,
    require_auth,
    require_role,
    AuthenticationError
)

from .rate_limit import (
    rate_limit,
    RateLimiter,
    RateLimitMiddleware
)

from .log_sanitizer import (
    sanitize_string,
    sanitize_dict,
    sanitize_json,
    safe_log
)

from .request_limits import (
    limit_request_size,
    check_request_size,
    RequestSizeLimitMiddleware
)

from .error_handler import (
    SecureErrorHandler,
    register_flask_error_handlers
)

from .audit_log import (
    AuditLogger,
    AuditEventType,
    AuditEvent,
    audit_logger,
    log_authentication_success,
    log_authentication_failure,
    log_authorization_denied,
    log_intelligence_compiled,
    log_federal_ai_scan
)

__all__ = [
    'generate_token',
    'verify_token',
    'verify_fastapi_token',
    'require_auth',
    'require_role',
    'AuthenticationError',
    'rate_limit',
    'RateLimiter',
    'RateLimitMiddleware',
    'sanitize_string',
    'sanitize_dict',
    'sanitize_json',
    'safe_log',
    'limit_request_size',
    'check_request_size',
    'RequestSizeLimitMiddleware',
    'SecureErrorHandler',
    'register_flask_error_handlers',
    'AuditLogger',
    'AuditEventType',
    'AuditEvent',
    'audit_logger',
    'log_authentication_success',
    'log_authentication_failure',
    'log_authorization_denied',
    'log_intelligence_compiled',
    'log_federal_ai_scan'
]

