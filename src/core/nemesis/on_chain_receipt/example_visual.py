"""
Visual Example: Verifiable Scoring Primitives
Demonstrates how intelligence becomes verifiable objects
"""

import json
import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nemesis.on_chain_receipt.receipt_generator import CryptographicReceiptGenerator

def generate_visual_example():
    """Generate a complete example for visual demonstration"""
    
    print("=" * 80)
    print("GH SYSTEMS — VERIFIABLE SCORING PRIMITIVES EXAMPLE")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = CryptographicReceiptGenerator()
    
    # Example intelligence package (stays off-chain - proprietary)
    intelligence_package = {
        "actor_id": "LAZARUS_GROUP",
        "actor_name": "Lazarus Group (DPRK)",
        "threat_level": "critical",
        
        # Scoring primitives (what gets verified)
        "risk_scores": {
            "overall_risk": 0.94,
            "sanctions_evasion_risk": 0.97,
            "coordination_risk": 0.89,
            "off_ramp_risk": 0.92
        },
        
        "behavioral_signature": {
            "risk_tolerance": 0.95,
            "pattern_repetition": 1.00,
            "flight_risk": 0.96,
            "coordination_likelihood": 0.88
        },
        
        "threat_assessment": {
            "threat_level": "critical",
            "confidence": 0.89,
            "next_action_window": "48-72h",
            "predicted_actions": [
                {"action": "off_ramp_attempt", "confidence": 0.87},
                {"action": "mixer_usage", "confidence": 0.82}
            ]
        },
        
        # Full proprietary intelligence (stays off-chain)
        "full_analysis": {
            "transaction_history": [],  # 1000+ transactions (example: empty for demo)
            "network_analysis": {},  # Full graph data
            "ai_model_outputs": {},  # Proprietary ML results
            "intelligence_sources": []  # Classified sources
        }
    }
    
    print("📦 INTELLIGENCE PACKAGE (Off-Chain - Proprietary)")
    print("-" * 80)
    print(f"Actor: {intelligence_package['actor_name']}")
    print(f"Threat Level: {intelligence_package['threat_level']}")
    print()
    print("Scoring Primitives:")
    print(f"  Overall Risk: {intelligence_package['risk_scores']['overall_risk']:.2f}")
    print(f"  Risk Tolerance: {intelligence_package['behavioral_signature']['risk_tolerance']:.2f}")
    print(f"  Flight Risk: {intelligence_package['behavioral_signature']['flight_risk']:.2f}")
    print(f"  Threat Assessment Confidence: {intelligence_package['threat_assessment']['confidence']:.2f}")
    print()
    print("Full Package Size: ~2.3MB (proprietary data)")
    print()
    
    # Generate cryptographic receipt
    receipt = generator.generate_receipt(
        intelligence_package=intelligence_package,
        actor_id="LAZARUS_GROUP",
        threat_level="critical",
        package_type="threat_assessment"
    )
    
    print("🔐 CRYPTOGRAPHIC RECEIPT (On-Chain - Minimal Proof)")
    print("-" * 80)
    print(f"Receipt ID: {receipt.receipt_id}")
    print(f"Intelligence Hash: {receipt.intelligence_hash[:32]}...")
    print(f"Timestamp: {receipt.timestamp}")
    print(f"Signature: {receipt.gh_systems_signature[:32]}...")
    print()
    print("Minimal Metadata:")
    print(f"  Actor ID: {receipt.actor_id}")
    print(f"  Threat Level: {receipt.threat_level}")
    print(f"  Package Type: {receipt.package_type}")
    print()
    print("Receipt Size: ~500 bytes (minimal proof)")
    print()
    
    # Prepare for on-chain
    on_chain_data = generator.prepare_for_on_chain(receipt)
    
    print("⛓️  ON-CHAIN DATA (What Goes to Blockchain)")
    print("-" * 80)
    print(json.dumps(on_chain_data, indent=2))
    print()
    print("On-Chain Size: ~400 bytes")
    print()
    
    # Verify receipt
    is_valid = generator.verify_receipt(receipt, intelligence_package)
    
    print("✅ VERIFICATION")
    print("-" * 80)
    print(f"Receipt Valid: {is_valid}")
    print(f"Hash Matches: {receipt.intelligence_hash == generator._hash_intelligence_package(intelligence_package)}")
    print()
    print("Anyone can verify:")
    print("  ✓ Intelligence came from GH Systems")
    print("  ✓ Scoring primitives are authentic")
    print("  ✓ No proprietary methods revealed")
    print()
    
    # Show the contrast
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print()
    print("OFF-CHAIN (Proprietary):")
    print("  • Full AI models")
    print("  • Complete intelligence packages")
    print("  • All proprietary systems")
    print("  • Size: ~2.3MB")
    print()
    print("ON-CHAIN (Verifiable Proof):")
    print("  • Cryptographic hash")
    print("  • Timestamp")
    print("  • GH Systems signature")
    print("  • Minimal metadata")
    print("  • Size: ~400 bytes")
    print()
    print("RESULT:")
    print("  ✓ Scoring primitives are verifiable")
    print("  ✓ Intelligence becomes verifiable objects")
    print("  ✓ Trust without exposure")
    print()
    
    # Commit to blockchain (mock)
    tx_hash = generator.commit_to_blockchain(receipt)
    
    print("=" * 80)
    print("BLOCKCHAIN COMMITMENT")
    print("=" * 80)
    print(f"Transaction Hash: {tx_hash}")
    print(f"Status: {receipt.status}")
    print()
    print("Receipt is now:")
    print("  ✓ Immutably recorded on Bitcoin blockchain")
    print("  ✓ Verifiable by anyone")
    print("  ✓ Usable in workflows")
    print("  ✓ Ready for BTC settlement")
    print()
    
    return receipt, on_chain_data, intelligence_package


if __name__ == "__main__":
    receipt, on_chain_data, intelligence_package = generate_visual_example()
    
    print("=" * 80)
    print("EXAMPLE COMPLETE")
    print("=" * 80)
    print()
    print("This demonstrates:")
    print("  1. Intelligence package (off-chain, proprietary)")
    print("  2. Cryptographic receipt (minimal proof)")
    print("  3. On-chain data (what goes to blockchain)")
    print("  4. Verification (anyone can verify)")
    print("  5. Blockchain commitment (immutable record)")
    print()
    print("Scoring primitives are now verifiable without revealing proprietary methods.")

