#!/usr/bin/env python3
"""
Test script for Synthetic vs Artificial data detection workflow

Tests:
1. /foundry/scan-hash-mismatches - Scan for artificial (bad) data
2. /commit-on-chain - Commit verified classification to blockchain

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import requests
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

API_BASE_URL = "http://localhost:8000"


def test_scan_foundry():
    """Test scanning Foundry compilation for hash mismatches"""
    print("=" * 80)
    print("TEST 1: Scan Foundry for Synthetic vs Artificial Data")
    print("=" * 80)
    print()
    
    url = f"{API_BASE_URL}/foundry/scan-hash-mismatches"
    
    payload = {
        "compilation_id": "abc_verification_output",
        "dataset_path": "gh_systems/intelligence_compilations"
    }
    
    print(f"Request: POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Response received:")
        print(json.dumps(result, indent=2))
        print()
        
        print(f"📊 Summary:")
        print(f"   Total records: {result.get('total_records', 0)}")
        print(f"   ✅ Synthetic (good): {result.get('synthetic_count', 0)}")
        print(f"   ❌ Artificial (bad): {result.get('artificial_count', 0)}")
        print()
        
        if result.get('artificial_count', 0) > 0:
            print("⚠️  Artificial (bad) data detected:")
            for record in result.get('artificial_records', [])[:3]:  # Show first 3
                print(f"   - Block {record.get('block_height')}: {record.get('issue')}")
            print()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        print(f"   Start with: python api/abc_verification_service.py")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response.status_code == 503:
            print("   Note: Foundry client not available (expected in dev)")
        print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_commit_synthetic():
    """Test committing synthetic (good) data to blockchain"""
    print("=" * 80)
    print("TEST 2: Commit Synthetic (Good) Data to Blockchain")
    print("=" * 80)
    print()
    
    url = f"{API_BASE_URL}/commit-on-chain"
    
    # Use test data from video script (synthetic - hash matches)
    payload = {
        "block_data": {
            "block_height": 825000,
            "block_hash": "94f84c7be087799b54c3e4adce1f9012a7e3c8d4b6f5a2e1c9d8b7a6f5e4d3c2",
            "timestamp": 1735689600,
            "tx_count": 2453,
            "transactions": "[{\"txid\":\"abc123\",\"value\":0.5}]"
        },
        "abc_receipt_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b",
        "human_analyst": "analyst_001",
        "data_classification": "synthetic",
        "verification_notes": "Hash matches - legitimate synthetic data for AML training"
    }
    
    print(f"Request: POST {url}")
    print(f"Classification: {payload['data_classification']} (good)")
    print()
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Response received:")
        print(json.dumps(result, indent=2))
        print()
        
        print(f"📊 Summary:")
        print(f"   ✅ Committed: {result.get('committed', False)}")
        print(f"   Classification: {result.get('data_classification')} (good)")
        print(f"   Receipt ID: {result.get('receipt_id', 'N/A')}")
        print(f"   TX Hash: {result.get('tx_hash', 'N/A')}")
        print(f"   Publicly verifiable: {result.get('publicly_verifiable', False)}")
        print()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_commit_artificial():
    """Test committing artificial (bad) data to blockchain"""
    print("=" * 80)
    print("TEST 3: Commit Artificial (Bad) Data to Blockchain")
    print("=" * 80)
    print()
    
    url = f"{API_BASE_URL}/commit-on-chain"
    
    # Use test data with mismatched hash (artificial - hash doesn't match)
    payload = {
        "block_data": {
            "block_height": 835023,
            "block_hash": "7ef012d1074743443383c1",
            "timestamp": 2268429478,
            "tx_count": 2069,
            "transactions": "[{\"txid\":\"defi_layering_835023_1\",\"pattern\":\"defi_layering\",\"value\":84.17}]"
        },
        "abc_receipt_hash": "WRONG_HASH_TO_SIMULATE_ARTIFICIAL_DATA",
        "human_analyst": "analyst_001",
        "data_classification": "artificial",
        "verification_notes": "Hash mismatch detected - artificial (bad) data injection in DeFi layering transaction"
    }
    
    print(f"Request: POST {url}")
    print(f"Classification: {payload['data_classification']} (bad)")
    print()
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Response received:")
        print(json.dumps(result, indent=2))
        print()
        
        print(f"📊 Summary:")
        print(f"   ✅ Committed: {result.get('committed', False)}")
        print(f"   Classification: {result.get('data_classification')} (bad)")
        print(f"   Receipt ID: {result.get('receipt_id', 'N/A')}")
        print(f"   TX Hash: {result.get('tx_hash', 'N/A')}")
        print(f"   Publicly verifiable: {result.get('publicly_verifiable', False)}")
        print()
        print("💡 Note: This documents the artificial (bad) data on-chain")
        print("   so AI systems can filter it out and resolve the bottleneck.")
        print()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_classification():
    """Test validation of data_classification field"""
    print("=" * 80)
    print("TEST 4: Validate Data Classification (Should Fail)")
    print("=" * 80)
    print()
    
    url = f"{API_BASE_URL}/commit-on-chain"
    
    payload = {
        "block_data": {
            "block_height": 825000,
            "block_hash": "94f84c7be087799b54c3e4adce1f9012a7e3c8d4b6f5a2e1c9d8b7a6f5e4d3c2",
            "timestamp": 1735689600,
            "tx_count": 2453,
            "transactions": "[{\"txid\":\"abc123\",\"value\":0.5}]"
        },
        "abc_receipt_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b",
        "human_analyst": "analyst_001",
        "data_classification": "invalid",  # Should fail
        "verification_notes": "Testing validation"
    }
    
    print(f"Request: POST {url}")
    print(f"Classification: {payload['data_classification']} (invalid - should fail)")
    print()
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 400:
            print("✅ Validation working correctly:")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'N/A')}")
            print()
            return True
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print()
    print("🧪 Testing Synthetic vs Artificial Data Detection Workflow")
    print()
    
    results = []
    
    # Test 1: Scan Foundry
    results.append(("Scan Foundry", test_scan_foundry()))
    print()
    
    # Test 2: Commit Synthetic (good)
    results.append(("Commit Synthetic", test_commit_synthetic()))
    print()
    
    # Test 3: Commit Artificial (bad)
    results.append(("Commit Artificial", test_commit_artificial()))
    print()
    
    # Test 4: Validation
    results.append(("Validate Classification", test_invalid_classification()))
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

