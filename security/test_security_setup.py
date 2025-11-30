#!/usr/bin/env python3
"""
Test Security Setup
Verifies that security dependencies and configuration are properly set up
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_dependencies():
    """Test that security dependencies are installed"""
    print("Testing security dependencies...")
    
    try:
        import jwt
        print("  ✅ PyJWT installed")
    except ImportError:
        print("  ❌ PyJWT not installed - run: pip install PyJWT")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv installed")
    except ImportError:
        print("  ❌ python-dotenv not installed - run: pip install python-dotenv")
        return False
    
    return True

def test_environment_variables():
    """Test that required environment variables are set"""
    print("\nTesting environment variables...")
    
    required_vars = [
        'FLASK_SECRET_KEY',
        'DASHBOARD_SECRET_KEY',
        'JWT_SECRET'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: SET (length: {len(value)})")
        else:
            print(f"  ❌ {var}: NOT SET")
            all_set = False
    
    optional_vars = {
        'CORS_ALLOWED_ORIGINS': os.getenv('CORS_ALLOWED_ORIGINS', ''),
        'DEBUG': os.getenv('DEBUG', 'false'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'development'),
        'AUDIT_LOGGING_ENABLED': os.getenv('AUDIT_LOGGING_ENABLED', 'true')
    }
    
    print("\nOptional variables:")
    for var, value in optional_vars.items():
        status = "✅" if value else "⚠️"
        print(f"  {status} {var}: {value if value else '(not set)'}")
    
    return all_set

def test_security_modules():
    """Test that security modules can be imported"""
    print("\nTesting security modules...")
    
    sys.path.insert(0, '.')
    
    try:
        from src.core.middleware.auth import generate_token, verify_token
        print("  ✅ Authentication module")
    except Exception as e:
        print(f"  ❌ Authentication module: {e}")
        return False
    
    try:
        from src.core.middleware.rate_limit import rate_limit, RateLimiter
        print("  ✅ Rate limiting module")
    except Exception as e:
        print(f"  ❌ Rate limiting module: {e}")
        return False
    
    try:
        from src.core.middleware.log_sanitizer import safe_log
        print("  ✅ Log sanitization module")
    except Exception as e:
        print(f"  ❌ Log sanitization module: {e}")
        return False
    
    try:
        from src.core.middleware.audit_log import audit_logger
        print("  ✅ Audit logging module")
    except Exception as e:
        print(f"  ❌ Audit logging module: {e}")
        return False
    
    return True

def test_token_generation():
    """Test JWT token generation"""
    print("\nTesting JWT token generation...")
    
    try:
        from src.core.middleware.auth import generate_token, verify_token
        
        # Generate token
        token = generate_token('test_user', roles=['admin'])
        print(f"  ✅ Token generated: {token[:20]}...")
        
        # Verify token
        payload = verify_token(token)
        print(f"  ✅ Token verified: user_id={payload.get('user_id')}, roles={payload.get('roles')}")
        
        return True
    except Exception as e:
        print(f"  ❌ Token generation failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GH Systems ABC - Security Setup Test")
    print("=" * 50)
    
    deps_ok = test_dependencies()
    env_ok = test_environment_variables()
    modules_ok = test_security_modules()
    token_ok = test_token_generation() if deps_ok and env_ok else False
    
    print("\n" + "=" * 50)
    if deps_ok and env_ok and modules_ok and token_ok:
        print("✅ All security tests passed!")
        print("System is ready for secure deployment.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Review errors above.")
        sys.exit(1)

