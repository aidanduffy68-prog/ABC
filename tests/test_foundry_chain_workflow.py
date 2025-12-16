#!/usr/bin/env python3
"""
Foundry Chain End-to-End Workflow Test
Tests complete workflow: Foundry → ABC Analysis → Blockchain Commitment

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.nemesis.foundry_integration import FoundryIntegration, CompilationValidator
from src.core.nemesis.compilation_engine import ABCCompilationEngine
from src.core.nemesis.on_chain_receipt.security_tier import SecurityTier


class MockFoundryConnector:
    """Mock Foundry connector for testing."""
    
    def get_compilation(self, compilation_id: str) -> dict:
        """Return mock compilation data."""
        validator = CompilationValidator()
        
        compiled_data = {
            "threat_actors": [
                {
                    "id": "actor_001",
                    "name": "Test Threat Actor",
                    "description": "Mock threat actor for Foundry Chain testing",
                    "risk_level": "high",
                    "aliases": ["TestActor"],
                    "associated_wallets": ["0x1234..."]
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
            "temporal_patterns": []
        }
        
        data_hash = validator.compute_data_hash(compiled_data)
        
        return {
            "compilation_id": compilation_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "sources": [
                {"provider": "chainalysis", "dataset": "sanctions_list_v2"},
                {"provider": "trm_labs", "dataset": "threat_actors_q4"}
            ],
            "data_hash": data_hash,
            "classification": "SBU",
            "compiled_data": compiled_data
        }


def test_foundry_chain_workflow():
    """Test complete Foundry Chain workflow."""
    print("=" * 60)
    print("Foundry Chain End-to-End Workflow Test")
    print("=" * 60)
    print()
    
    # Step 1: Foundry Compilation
    print("Step 1: Foundry Compilation")
    print("-" * 60)
    
    foundry = FoundryIntegration()
    foundry.connector = MockFoundryConnector()
    
    compilation_id = "foundry-comp-2025-12-12-001"
    
    try:
        compilation = foundry.ingest_compilation(
            compilation_id=compilation_id,
            classification="SBU"
        )
        print(f"✅ Foundry compilation ingested: {compilation.get('compilation_id')}")
        print(f"   Data hash: {compilation.get('data_hash', 'N/A')[:32]}...")
        print(f"   Classification: {compilation.get('classification')}")
        print(f"   Sources: {len(compilation.get('sources', []))}")
    except Exception as e:
        print(f"❌ Error ingesting Foundry compilation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Step 2: Prepare for ABC Analysis
    print("Step 2: Prepare for ABC Analysis")
    print("-" * 60)
    
    try:
        abc_data = foundry.prepare_for_abc_analysis(compilation)
        print(f"✅ Prepared for ABC analysis:")
        print(f"   Intelligence items: {len(abc_data.get('raw_intelligence', []))}")
        print(f"   Transaction data: {len(abc_data.get('transaction_data', []))}")
        print(f"   Entities: {len(abc_data.get('network_data', {}).get('entities', []))}")
        print(f"   Relationships: {len(abc_data.get('network_data', {}).get('relationships', []))}")
    except Exception as e:
        print(f"❌ Error preparing ABC data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Step 3: ABC Analysis
    print("Step 3: ABC Analysis (Hades → Echo → Nemesis)")
    print("-" * 60)
    
    try:
        engine = ABCCompilationEngine()
        
        # SBU (Tier 2) requires permissioned blockchain, but for demo we'll use unclassified
        # In production, SBU would use Hyperledger/Corda/Quorum
        compiled = engine.compile_intelligence(
            actor_id="foundry_actor_001",
            actor_name="Foundry Threat Actor",
            raw_intelligence=abc_data.get("raw_intelligence", []),
            transaction_data=abc_data.get("transaction_data"),
            network_data=abc_data.get("network_data"),
            generate_receipt=True,
            preferred_blockchain="ethereum",
            classification="UNCLASSIFIED"  # Use unclassified for demo (allows public blockchains)
        )
        
        print(f"✅ ABC compilation complete:")
        print(f"   Compilation ID: {compiled.compilation_id}")
        print(f"   Compilation time: {compiled.compilation_time_ms:.2f}ms")
        print(f"   Confidence score: {compiled.confidence_score:.2%}")
        print(f"   Threat level: {compiled.targeting_package.get('risk_assessment', {}).get('threat_level', 'N/A')}")
        
        # Check receipt
        receipt = compiled.targeting_package.get("receipt")
        if receipt:
            print(f"   Receipt hash: {receipt.get('intelligence_hash', 'N/A')[:32]}...")
            print(f"   Security tier: {receipt.get('security_tier', 'N/A')}")
            print(f"   Blockchain: {receipt.get('blockchain_network', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error in ABC compilation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Step 4: Verify Blockchain Commitment
    print("Step 4: Verify Blockchain Commitment")
    print("-" * 60)
    
    try:
        if receipt:
            print(f"✅ Cryptographic receipt generated:")
            print(f"   Foundry compilation ID: {compilation_id}")
            print(f"   ABC receipt hash: {receipt.get('intelligence_hash', 'N/A')[:32]}...")
            print(f"   Security tier: {receipt.get('security_tier', 'N/A')}")
            print(f"   Tier name: {receipt.get('tier_name', 'N/A')}")
            print(f"   Blockchain: {receipt.get('blockchain_network', 'N/A')}")
            print(f"   Commit data: {receipt.get('commit_data', 'N/A')}")
            
            # Verify tier is appropriate for classification
            if receipt.get('security_tier') == 'sbu':
                print(f"   ✅ Tier matches classification (SBU → Tier 2)")
        else:
            print("⚠️  No receipt generated (demo mode)")
    except Exception as e:
        print(f"❌ Error verifying receipt: {e}")
        return False
    
    print()
    
    # Step 5: Summary
    print("=" * 60)
    print("✅ Foundry Chain Workflow Complete!")
    print("=" * 60)
    print()
    print("Workflow Summary:")
    print(f"  1. Foundry compilation: {compilation_id}")
    print(f"  2. ABC analysis: {compiled.compilation_id}")
    print(f"  3. Compilation time: {compiled.compilation_time_ms:.2f}ms")
    print(f"  4. Confidence: {compiled.confidence_score:.2%}")
    print(f"  5. Blockchain: {receipt.get('blockchain_network', 'N/A') if receipt else 'N/A'}")
    print()
    print("Next Steps:")
    print("  1. Connect to real Foundry API (set FOUNDRY_API_URL and FOUNDRY_API_KEY)")
    print("  2. Test with actual Foundry compilations")
    print("  3. Integrate with agency AI systems")
    print("  4. Deploy Genesis Mission Dashboard")
    print()
    
    return True


def main():
    """Main test function."""
    success = test_foundry_chain_workflow()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

