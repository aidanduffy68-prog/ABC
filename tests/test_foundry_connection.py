#!/usr/bin/env python3
"""
Test Foundry API Connection
Tests ABC's connection to Palantir Foundry API (demo/staging environment)

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.nemesis.foundry_integration import FoundryConnector, FoundryIntegration, CompilationValidator


class MockFoundryConnector(FoundryConnector):
    """
    Mock Foundry connector for demo/testing without real API access.
    
    Returns sample Foundry compilation data for testing.
    """
    
    def get_compilation(self, compilation_id: str) -> dict:
        """Return mock compilation data."""
        print(f"🔧 MOCK MODE: Simulating Foundry compilation retrieval for: {compilation_id}")
        
        # Generate mock Foundry compilation
        mock_compilation = {
            "compilation_id": compilation_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "sources": [
                {"provider": "chainalysis", "dataset": "sanctions_list_v2"},
                {"provider": "trm_labs", "dataset": "threat_actors_q4"},
                {"provider": "ofac", "dataset": "sdn_list_current"},
                {"provider": "dhs", "dataset": "cyber_threats_classified"}
            ],
            "data_hash": "sha256:abc123def456789",
            "classification": "SBU",
            "compiled_data": {
                "threat_actors": [
                    {
                        "id": "actor_001",
                        "name": "Test Threat Actor",
                        "description": "Mock threat actor for testing",
                        "risk_level": "high",
                        "aliases": ["TestActor", "MockThreat"],
                        "associated_wallets": ["0x1234...", "0x5678..."]
                    }
                ],
                "wallet_addresses": [
                    {
                        "address": "0x1234567890abcdef",
                        "label": "Test Wallet",
                        "risk_score": 0.85,
                        "source_provider": "chainalysis"
                    }
                ],
                "coordination_networks": [
                    {
                        "source_entity": "actor_001",
                        "target_entity": "0x1234567890abcdef",
                        "relationship_type": "coordinates_with",
                        "confidence": 0.82
                    }
                ],
                "temporal_patterns": [
                    {
                        "pattern_type": "transaction_timing",
                        "description": "Synchronized transaction patterns detected",
                        "confidence": 0.75
                    }
                ]
            }
        }
        
        # Compute actual hash for validation
        from src.core.nemesis.foundry_integration.compilation_validator import CompilationValidator
        validator = CompilationValidator()
        actual_hash = validator.compute_data_hash(mock_compilation["compiled_data"])
        mock_compilation["data_hash"] = actual_hash
        
        return mock_compilation
    
    def list_recent_compilations(self, limit: int = 100, classification: Optional[str] = None, since: Optional[datetime] = None) -> list:
        """Return mock compilation list."""
        print(f"🔧 MOCK MODE: Simulating Foundry compilation list (limit={limit})")
        
        return [
            {
                "compilation_id": f"foundry-comp-{datetime.now().strftime('%Y%m%d')}-{i:03d}",
                "timestamp": datetime.now().isoformat() + "Z",
                "classification": classification or "SBU",
                "source_count": 4
            }
            for i in range(min(limit, 5))  # Return up to 5 mock compilations
        ]
    
    def verify_compilation_exists(self, compilation_id: str) -> bool:
        """Mock verification - always returns True for demo."""
        return True
    
    def get_compilation_metadata(self, compilation_id: str) -> dict:
        """Return mock metadata."""
        return {
            "compilation_id": compilation_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "classification": "SBU",
            "source_count": 4
        }


def test_foundry_connection(use_mock: bool = True):
    """
    Test Foundry API connection.
    
    Args:
        use_mock: If True, use mock connector (demo mode). If False, attempt real API connection.
    """
    print("=" * 60)
    print("Foundry API Connection Test")
    print("=" * 60)
    print()
    
    # Check environment variables
    foundry_api_url = os.getenv("FOUNDRY_API_URL")
    foundry_api_key = os.getenv("FOUNDRY_API_KEY")
    
    if use_mock or not foundry_api_url or not foundry_api_key:
        print("🔧 Using MOCK MODE (demo/staging)")
        print("   Set FOUNDRY_API_URL and FOUNDRY_API_KEY for real connection")
        print()
        
        connector = MockFoundryConnector()
    else:
        print("🔗 Attempting REAL Foundry API connection")
        print(f"   API URL: {foundry_api_url}")
        print(f"   API Key: {'*' * 20}...{foundry_api_key[-4:] if len(foundry_api_key) > 4 else '***'}")
        print()
        
        connector = FoundryConnector(
            foundry_api_url=foundry_api_url,
            api_key=foundry_api_key
        )
    
    # Test 1: Verify compilation exists
    print("Test 1: Verify Compilation Exists")
    print("-" * 60)
    test_compilation_id = "foundry-comp-2025-12-12-001"
    
    try:
        exists = connector.verify_compilation_exists(test_compilation_id)
        if exists:
            print(f"✅ Compilation exists: {test_compilation_id}")
        else:
            print(f"❌ Compilation not found: {test_compilation_id}")
    except Exception as e:
        print(f"❌ Error verifying compilation: {e}")
        return False
    
    print()
    
    # Test 2: Get compilation
    print("Test 2: Get Compilation")
    print("-" * 60)
    
    try:
        compilation = connector.get_compilation(test_compilation_id)
        print(f"✅ Retrieved compilation: {compilation.get('compilation_id')}")
        print(f"   Timestamp: {compilation.get('timestamp')}")
        print(f"   Classification: {compilation.get('classification')}")
        print(f"   Sources: {len(compilation.get('sources', []))}")
        print(f"   Data Hash: {compilation.get('data_hash', 'N/A')[:32]}...")
    except Exception as e:
        print(f"❌ Error retrieving compilation: {e}")
        return False
    
    print()
    
    # Test 3: Validate compilation
    print("Test 3: Validate Compilation")
    print("-" * 60)
    
    try:
        validator = CompilationValidator()
        validation = validator.validate_compilation(compilation)
        
        if validation["valid"]:
            print("✅ Compilation validation passed")
            print(f"   Hash matches: {validation['hash_matches']}")
            print(f"   Sources verified: {validation['sources_verified']}")
            print(f"   Classification appropriate: {validation['classification_appropriate']}")
        else:
            print("❌ Compilation validation failed")
            print(f"   Errors: {validation['errors']}")
            if validation['warnings']:
                print(f"   Warnings: {validation['warnings']}")
    except Exception as e:
        print(f"❌ Error validating compilation: {e}")
        return False
    
    print()
    
    # Test 4: List recent compilations
    print("Test 4: List Recent Compilations")
    print("-" * 60)
    
    try:
        compilations = connector.list_recent_compilations(limit=5)
        print(f"✅ Retrieved {len(compilations)} compilations")
        for comp in compilations[:3]:
            print(f"   - {comp.get('compilation_id')} ({comp.get('classification', 'N/A')})")
    except Exception as e:
        print(f"❌ Error listing compilations: {e}")
        return False
    
    print()
    
    # Test 5: Full integration workflow
    print("Test 5: Full Integration Workflow")
    print("-" * 60)
    
    try:
        if use_mock or not foundry_api_url:
            integration = FoundryIntegration()
            # Replace connector with mock
            integration.connector = MockFoundryConnector()
        else:
            integration = FoundryIntegration(
                foundry_api_url=foundry_api_url,
                api_key=foundry_api_key
            )
        
        # Ingest compilation
        compilation = integration.ingest_compilation(
            compilation_id=test_compilation_id,
            classification="SBU"
        )
        print(f"✅ Ingested compilation: {compilation.get('compilation_id')}")
        
        # Prepare for ABC analysis
        abc_data = integration.prepare_for_abc_analysis(compilation)
        print(f"✅ Prepared for ABC analysis:")
        print(f"   Intelligence items: {len(abc_data.get('raw_intelligence', []))}")
        print(f"   Transaction data: {len(abc_data.get('transaction_data', []))}")
        print(f"   Entities: {len(abc_data.get('network_data', {}).get('entities', []))}")
        print(f"   Relationships: {len(abc_data.get('network_data', {}).get('relationships', []))}")
        
    except Exception as e:
        print(f"❌ Error in integration workflow: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 60)
    print("✅ All Tests Passed!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Set FOUNDRY_API_URL and FOUNDRY_API_KEY for real connection")
    print("2. Test with actual Foundry compilation IDs")
    print("3. Integrate with ABC compilation engine")
    print()
    
    return True


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Foundry API connection"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Attempt real API connection (requires FOUNDRY_API_URL and FOUNDRY_API_KEY)"
    )
    
    args = parser.parse_args()
    
    use_mock = not args.real
    
    success = test_foundry_connection(use_mock=use_mock)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

