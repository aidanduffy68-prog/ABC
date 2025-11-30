#!/usr/bin/env python3
"""
Test Deployment Readiness
Verifies core functionality and imports for deployment readiness

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing core module imports...")
    
    tests = [
        ("Threat Actor Schema", "src.schemas.threat_actor", "ThreatActor"),
        ("Ingestion Validator", "src.ingestion.validator", "IngestionValidator"),
        ("Graph Builder", "src.graph.builder", "ThreatIntelligenceGraph"),
        ("Compilation Engine", "src.core.nemesis.compilation_engine", "CompilationEngine"),
    ]
    
    passed = 0
    failed = 0
    
    for name, module_path, class_name in tests:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✅ {name}")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
        except AttributeError as e:
            print(f"  ❌ {name}: Class {class_name} not found - {e}")
            failed += 1
    
    return passed, failed

def test_security_middleware():
    """Test security middleware imports"""
    print("\nTesting security middleware...")
    
    tests = [
        ("Authentication", "src.core.middleware.auth", ["generate_token", "verify_token"]),
        ("Rate Limiting", "src.core.middleware.rate_limit", ["RateLimiter", "rate_limit"]),
        ("Log Sanitizer", "src.core.middleware.log_sanitizer", ["sanitize_string"]),
        ("Request Limits", "src.core.middleware.request_limits", ["RequestSizeLimitMiddleware"]),
        ("Error Handler", "src.core.middleware.error_handler", ["SecureErrorHandler"]),
        ("Audit Log", "src.core.middleware.audit_log", ["AuditLogger"]),
    ]
    
    passed = 0
    failed = 0
    
    for name, module_path, functions in tests:
        try:
            module = __import__(module_path, fromlist=functions)
            all_found = all(hasattr(module, func) for func in functions)
            if all_found:
                print(f"  ✅ {name}")
                passed += 1
            else:
                missing = [f for f in functions if not hasattr(module, f)]
                print(f"  ❌ {name}: Missing {missing}")
                failed += 1
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
    
    return passed, failed

def test_environment_variables():
    """Test that critical environment variables can be loaded"""
    print("\nTesting environment variables...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            "FLASK_SECRET_KEY",
            "JWT_SECRET",
        ]
        
        passed = 0
        failed = 0
        
        for var in required_vars:
            value = os.getenv(var)
            if value and len(value) >= 32:
                print(f"  ✅ {var} (length: {len(value)})")
                passed += 1
            else:
                print(f"  ⚠️  {var}: {'NOT SET' if not value else 'TOO SHORT'}")
                failed += 1
        
        return passed, failed
    except ImportError:
        print("  ⚠️  python-dotenv not installed (optional)")
        return 0, 0

def test_api_routes():
    """Test API route imports"""
    print("\nTesting API routes...")
    
    try:
        from src.api.routes.ingest import router
        print("  ✅ Ingest routes")
        return 1, 0
    except ImportError as e:
        print(f"  ❌ Ingest routes: {e}")
        return 0, 1

def main():
    """Run all deployment readiness tests"""
    print("=" * 60)
    print("GH Systems ABC - Deployment Readiness Test")
    print("=" * 60)
    print()
    
    total_passed = 0
    total_failed = 0
    
    # Test imports
    passed, failed = test_imports()
    total_passed += passed
    total_failed += failed
    
    # Test security middleware
    passed, failed = test_security_middleware()
    total_passed += passed
    total_failed += failed
    
    # Test environment variables
    passed, failed = test_environment_variables()
    total_passed += passed
    total_failed += failed
    
    # Test API routes
    passed, failed = test_api_routes()
    total_passed += passed
    total_failed += failed
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"Total: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed! System is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
