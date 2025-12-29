"""
API Authentication Middleware
JWT-based authentication for FastAPI endpoints

SECURITY FIX: Implements proper authentication that was missing.
"""

import os
import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps

# Security scheme
security = HTTPBearer()

# Get secret key from environment (MUST be set in production)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

if not JWT_SECRET_KEY:
    # In development, generate a temporary key (NOT SECURE for production!)
    import secrets
    JWT_SECRET_KEY = secrets.token_hex(32)
    print("WARNING: JWT_SECRET_KEY not set in environment. Using temporary key (NOT SECURE for production!)")


def create_access_token(
    subject: str,
    role: str = "user",
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        subject: User identifier (e.g., user_id, vendor_name)
        role: User role (admin, vendor, analyst, user)
        additional_claims: Additional claims to include in token
        
    Returns:
        Encoded JWT token
    """
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    payload = {
        "sub": subject,
        "role": role,
        "exp": expiration,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def verify_api_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Verify JWT token for API access
    
    SECURITY FIX: Implements proper token verification.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    if not JWT_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY not configured"
        )
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        
        # Check required claims
        if "sub" not in payload or "role" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


def require_role(allowed_roles: list[str]):
    """
    Dependency to require specific role(s)
    
    Usage:
        @router.post("/endpoint", dependencies=[Depends(require_role(["admin", "vendor"]))])
    """
    async def role_checker(token_payload: Dict[str, Any] = Depends(verify_api_token)):
        user_role = token_payload.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}"
            )
        return token_payload
    
    return role_checker


# Convenience dependencies
verify_token = Depends(verify_api_token)
require_admin = Depends(require_role(["admin"]))
require_vendor = Depends(require_role(["admin", "vendor"]))
require_analyst = Depends(require_role(["admin", "vendor", "analyst"]))

