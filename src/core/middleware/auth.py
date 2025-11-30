"""
Authentication and Authorization Middleware
Provides authentication and authorization for API endpoints

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import os
try:
    import jwt
except ImportError:
    try:
        import PyJWT as jwt
    except ImportError:
        # Fallback: JWT functionality will be disabled if library not available
        jwt = None
import time
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, g
from .audit_log import log_authentication_success, log_authentication_failure, log_authorization_denied
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta

# SECURITY: Use environment variable for JWT secret
JWT_SECRET = os.getenv('JWT_SECRET', os.urandom(32).hex())
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

# FastAPI security scheme
security = HTTPBearer()


class AuthenticationError(Exception):
    """Authentication error"""
    pass


def generate_token(user_id: str, roles: list = None) -> str:
    """
    Generate JWT token for user
    
    Args:
        user_id: User identifier
        roles: List of user roles
        
    Returns:
        JWT token string
    """
    if jwt is None:
        raise AuthenticationError("JWT library not available. Install PyJWT: pip install PyJWT")
    
    payload = {
        'user_id': user_id,
        'roles': roles or [],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid
    """
    if jwt is None:
        raise AuthenticationError("JWT library not available. Install PyJWT: pip install PyJWT")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


# FastAPI dependency for authentication
async def verify_fastapi_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to verify JWT token
    
    Usage:
        @router.post("/endpoint")
        async def endpoint(user: dict = Depends(verify_fastapi_token)):
            ...
    """
    try:
        payload = verify_token(credentials.credentials)
        return payload
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# Flask decorator for authentication
def require_auth(f):
    """
    Flask decorator to require authentication
    
    Usage:
        @app.route('/api/v1/endpoint')
        @require_auth
        def endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            payload = verify_token(token)
            
            # Store user info in Flask g for use in route
            g.user_id = payload.get('user_id')
            g.user_roles = payload.get('roles', [])
            
            # SECURITY: Audit log successful authentication
            log_authentication_success(
                user_id=g.user_id,
                ip_address=request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown')
            )
            
        except (IndexError, AuthenticationError) as e:
            # SECURITY: Audit log failed authentication
            log_authentication_failure(
                user_id=None,
                ip_address=request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown'),
                reason=str(e)
            )
            return jsonify({'error': 'Invalid token', 'detail': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*required_roles):
    """
    Flask decorator to require specific role(s)
    
    Usage:
        @app.route('/api/v1/admin')
        @require_auth
        @require_role('admin', 'operator')
        def admin_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated (should be set by @require_auth)
            if not hasattr(g, 'user_roles'):
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check if user has required role
            user_roles = g.user_roles or []
            if not any(role in user_roles for role in required_roles):
                # SECURITY: Audit log authorization denial
                log_authorization_denied(
                    user_id=g.user_id,
                    ip_address=request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown'),
                    resource=request.path,
                    required_roles=list(required_roles)
                )
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(required_roles),
                    'user_roles': user_roles
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

