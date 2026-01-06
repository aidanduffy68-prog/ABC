"""
API Status and Readiness Endpoints
Comprehensive health and readiness checks for deployment monitoring

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import os
import sys

# Create router
router = APIRouter(prefix="/api/v1/status", tags=["status"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    
    Returns:
        Health status with timestamp
    """
    return {
        "status": "healthy",
        "service": "gh_systems_abc",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """
    Comprehensive readiness check
    
    Verifies all system components are operational:
    - Environment variables configured
    - Core modules importable
    - Security middleware loaded
    - Compilation engine initialized
    
    Returns:
        Readiness status with component checks
    """
    checks = {
        "overall": "ready",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    all_ready = True
    
    # Check environment variables
    env_check = {
        "status": "ready",
        "details": {}
    }
    required_vars = ["FLASK_SECRET_KEY", "JWT_SECRET"]
    for var in required_vars:
        value = os.getenv(var)
        if value and len(value) >= 32:
            env_check["details"][var] = "configured"
        else:
            env_check["details"][var] = "missing"
            env_check["status"] = "degraded"
            all_ready = False
    
    checks["components"]["environment"] = env_check
    
    # Check core modules
    module_check = {
        "status": "ready",
        "modules": {}
    }
    
    modules_to_check = [
        ("compilation_engine", "src.core.nemesis.compilation_engine", "ABCCompilationEngine"),
        ("auth", "src.core.middleware.auth", "generate_token"),
        ("rate_limit", "src.core.middleware.rate_limit", "RateLimiter"),
        ("schemas", "src.schemas.threat_actor", "ThreatActor"),
        ("validator", "src.ingestion.validator", "IngestionValidator"),
    ]
    
    for name, module_path, item_name in modules_to_check:
        try:
            module = __import__(module_path, fromlist=[item_name])
            getattr(module, item_name)
            module_check["modules"][name] = "loaded"
        except Exception as e:
            module_check["modules"][name] = f"error: {str(e)[:50]}"
            module_check["status"] = "degraded"
            all_ready = False
    
    checks["components"]["modules"] = module_check
    
    # Check compilation engine initialization
    engine_check = {
        "status": "ready",
        "details": {}
    }
    
    try:
        from src.verticals.ai_verification.core.nemesis.compilation_engine import ABCCompilationEngine
        engine = ABCCompilationEngine()
        engine_check["details"]["initialized"] = True
        engine_check["details"]["version"] = getattr(engine, 'engine_version', 'unknown')
    except Exception as e:
        engine_check["status"] = "error"
        engine_check["details"]["error"] = str(e)[:100]
        all_ready = False
    
    checks["components"]["compilation_engine"] = engine_check
    
    # Check security middleware
    security_check = {
        "status": "ready",
        "middleware": {}
    }
    
    security_modules = [
        ("auth", "src.core.middleware.auth"),
        ("rate_limit", "src.core.middleware.rate_limit"),
        ("log_sanitizer", "src.core.middleware.log_sanitizer"),
        ("request_limits", "src.core.middleware.request_limits"),
        ("error_handler", "src.core.middleware.error_handler"),
        ("audit_log", "src.core.middleware.audit_log"),
    ]
    
    for name, module_path in security_modules:
        try:
            __import__(module_path)
            security_check["middleware"][name] = "loaded"
        except Exception as e:
            security_check["middleware"][name] = f"error: {str(e)[:50]}"
            security_check["status"] = "degraded"
            all_ready = False
    
    checks["components"]["security"] = security_check
    
    # Set overall status
    if not all_ready:
        checks["overall"] = "degraded"
        return checks
    
    return checks


@router.get("/version", status_code=status.HTTP_200_OK)
async def version_info() -> Dict[str, Any]:
    """
    Get version and build information
    
    Returns:
        Version details
    """
    return {
        "version": "1.0.0",
        "service": "gh_systems_abc",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "timestamp": datetime.now().isoformat()
    }

