# -*- coding: utf-8 -*-
"""
Test ABC Verification API
Quick test script to verify the API is working

Usage:
    python3 scripts/test_api.py
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_root():
    """Test root endpoint"""
    print("\nTesting / endpoint...")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
        data = response.json()
        print(f"   Service: {data.get('service')}")
        print(f"   Version: {data.get('version')}")
        return True
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False


def test_verify():
    """Test verification endpoint"""
    print("\nTesting /verify endpoint...")
    
    # Test data (from your CSV)
    test_request = {
        "block_data": {
            "block_height": 825000,
            "block_hash": "94f84c7be087799b54c3e4adce1f9012a7e3c8d4b6f5a2e1c9d8b7a6f5e4d3c2",
            "timestamp": 1735689600,
            "tx_count": 2453,
            "transactions": '[{"txid":"abc123","value":0.5}]'
        },
        "abc_receipt_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/verify",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Verification endpoint: {response.status_code}")
        result = response.json()
        
        if result.get("success"):
            verified = result["result"]["verified"]
            print(f"   Verified: {'✅ YES' if verified else '❌ NO'}")
            print(f"   Block height: {result['result']['block_height']}")
            print(f"   Message: {result['message']}")
            return verified
        else:
            print(f"❌ Verification failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Verification endpoint failed: {e}")
        return False


def test_batch():
    """Test batch verification endpoint"""
    print("\nTesting /verify/batch endpoint...")
    
    test_request = {
        "requests": [
            {
                "block_data": {
                    "block_height": 825000,
                    "block_hash": "94f84c7be087799b54c3e4adce1f9012a7e3c8d4b6f5a2e1c9d8b7a6f5e4d3c2",
                    "timestamp": 1735689600,
                    "tx_count": 2453,
                    "transactions": '[{"txid":"abc123","value":0.5}]'
                },
                "abc_receipt_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b"
            },
            {
                "block_data": {
                    "block_height": 825001,
                    "block_hash": "b1789a1a7aca6780a5646decd77c8e67c9d8b7a6f5e4d3c2a1b0c9d8e7f6a5b4",
                    "timestamp": 1735690200,
                    "tx_count": 2387,
                    "transactions": '[{"txid":"def456","value":1.2}]'
                },
                "abc_receipt_hash": "98b3e80720281074c8f05ac5cfb2d1cae23ab8eb1adf46fdfa57e39a6a96b6df"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_URL}/verify/batch",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Batch verification endpoint: {response.status_code}")
        result = response.json()
        
        print(f"   Total: {result['total']}")
        print(f"   Verified: {result['verified']}")
        print(f"   Failed: {result['failed']}")
        
        return result['verified'] == result['total']
        
    except Exception as e:
        print(f"❌ Batch verification failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("ABC Verification API Test")
    print("=" * 80)
    print(f"Testing API at: {API_URL}")
    print(f"Make sure the API is running: python3 api/abc_verification_service.py")
    print()
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Single Verification", test_verify()))
    results.append(("Batch Verification", test_batch()))
    
    # Summary
    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print()
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")
    
    return all_passed


if __name__ == "__main__":
    import sys
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

