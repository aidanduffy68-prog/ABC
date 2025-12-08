#!/usr/bin/env python3
"""
GH Systems ABC - Intelligence Compilation CLI
Quick command-line tool to compile threat intelligence

Usage:
    python scripts/compile_intelligence.py --actor-id "lazarus_001" --actor-name "Lazarus Group" --intel-file data.json
    python scripts/compile_intelligence.py --federal-ai --agency "DoD" --vuln-file vulns.json

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.nemesis.compilation_engine import ABCCompilationEngine, compile_intelligence


def load_json_file(file_path: str) -> dict:
    """Load JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def format_output(compiled):
    """Format compiled intelligence for display"""
    print("\n" + "=" * 60)
    print("GH Systems ABC - Intelligence Compilation")
    print("=" * 60)
    print(f"\n📋 Compilation ID: {compiled.compilation_id}")
    print(f"🎯 Actor: {compiled.actor_name} ({compiled.actor_id})")
    print(f"⏱️  Compilation Time: {compiled.compilation_time_ms:.2f}ms")
    print(f"📊 Confidence Score: {compiled.confidence_score:.2%}")
    print(f"🕐 Compiled At: {compiled.compiled_at.isoformat()}")
    
    # Behavioral signature
    if compiled.behavioral_signature:
        print(f"\n🔍 Behavioral Signature:")
        print(f"   Confidence: {compiled.behavioral_signature.confidence:.2%}")
        if compiled.behavioral_signature.traits:
            print(f"   Traits: {len(compiled.behavioral_signature.traits)} identified")
    
    # Coordination network
    if compiled.coordination_network:
        partners = compiled.coordination_network.get('partners', [])
        facilitators = compiled.coordination_network.get('facilitators', [])
        if partners or facilitators:
            print(f"\n🌐 Coordination Network:")
            if partners:
                print(f"   Partners: {len(partners)}")
            if facilitators:
                print(f"   Facilitators: {len(facilitators)}")
    
    # Threat forecast
    if compiled.threat_forecast:
        print(f"\n⚠️  Threat Forecast:")
        print(f"   Overall Risk: {compiled.threat_forecast.overall_risk_score:.2%}")
        if compiled.threat_forecast.predictions:
            print(f"   Predictions: {len(compiled.threat_forecast.predictions)}")
            top_pred = max(compiled.threat_forecast.predictions, key=lambda p: p.confidence)
            print(f"   Top Prediction: {top_pred.action_type.value} ({top_pred.confidence:.2%} confidence)")
    
    # Targeting package
    if compiled.targeting_package:
        risk = compiled.targeting_package.get('risk_assessment', {})
        threat_level = risk.get('threat_level', 'unknown')
        print(f"\n🎯 Targeting Package:")
        print(f"   Threat Level: {threat_level.upper()}")
        if 'targeting_instructions' in compiled.targeting_package:
            print(f"   Instructions: {len(compiled.targeting_package['targeting_instructions'])}")
    
    # Receipt
    if compiled.targeting_package.get('receipt'):
        receipt = compiled.targeting_package['receipt']
        print(f"\n🔐 Cryptographic Receipt:")
        print(f"   Hash: {receipt.get('intelligence_hash', receipt.get('hash', 'N/A'))[:16]}...")
        print(f"   Timestamp: {receipt.get('timestamp', 'N/A')}")
        if receipt.get('blockchain_network'):
            print(f"   Blockchain: {receipt.get('blockchain_network')}")
        if receipt.get('tx_hash'):
            print(f"   TX Hash: {receipt.get('tx_hash')[:16]}...")
    
    # Check if this is a Magic Moment (first successful compilation)
    is_magic_moment = compiled.compilation_time_ms < 500 and compiled.confidence_score > 0
    
    print("\n" + "=" * 60)
    if is_magic_moment:
        print("🎉 MAGIC MOMENT ACHIEVED! 🎉")
        print("=" * 60)
        print("")
        print("You've successfully verified truth in post-AGI intelligence!")
        print("")
        print("This is what government agencies need when AGI generates")
        print("conflicting threat assessments. You've just experienced")
        print("the solution: cryptographically verifiable intelligence")
        print("in <500ms with mathematical proof.")
        print("")
        print("=" * 60)
        print("What's Next?")
        print("=" * 60)
        print("")
        print("1. Try with your own data")
        print("2. Explore the API: src/core/nemesis/ai_ontology/api_documentation.md")
        print("3. Review examples: examples/intelligence_audits/")
        print("4. Read the architecture: docs/ARCHITECTURE_SPEC.md")
        print("")
    else:
        print("✅ Compilation complete!")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='GH Systems ABC - Intelligence Compilation CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compile intelligence for an actor (default: Bitcoin)
  python scripts/compile_intelligence.py \\
    --actor-id "lazarus_001" \\
    --actor-name "Lazarus Group" \\
    --intel-file intelligence.json

  # Compile with Ethereum blockchain
  python scripts/compile_intelligence.py \\
    --actor-id "lazarus_001" \\
    --actor-name "Lazarus Group" \\
    --intel-file intelligence.json \\
    --blockchain ethereum

  # Compile federal AI intelligence with Polygon (lower fees)
  python scripts/compile_intelligence.py \\
    --federal-ai \\
    --agency "DoD" \\
    --vuln-file vulnerabilities.json \\
    --blockchain polygon
        """
    )
    
    # Mode selection
    parser.add_argument('--federal-ai', action='store_true',
                       help='Compile federal AI intelligence')
    
    # Actor mode arguments
    parser.add_argument('--actor-id', type=str,
                       help='Actor identifier')
    parser.add_argument('--actor-name', type=str,
                       help='Actor name/designation')
    parser.add_argument('--intel-file', type=str,
                       help='Path to intelligence data JSON file')
    parser.add_argument('--transaction-file', type=str,
                       help='Path to transaction data JSON file (optional)')
    parser.add_argument('--network-file', type=str,
                       help='Path to network data JSON file (optional)')
    
    # Federal AI mode arguments
    parser.add_argument('--agency', type=str,
                       help='Agency name (DoD, DHS, NASA, etc.)')
    parser.add_argument('--vuln-file', type=str,
                       help='Path to vulnerability data JSON file')
    parser.add_argument('--ai-system-file', type=str,
                       help='Path to AI system data JSON file')
    
    # Output options
    parser.add_argument('--output', type=str,
                       help='Output file path (JSON format)')
    parser.add_argument('--no-receipt', action='store_true',
                       help='Skip cryptographic receipt generation')
    
    # Blockchain options
    parser.add_argument('--blockchain', type=str,
                       choices=['bitcoin', 'ethereum', 'polygon', 'arbitrum', 'base', 'optimism'],
                       default='bitcoin',
                       help='Preferred blockchain network for receipt commitment (default: bitcoin)')
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = ABCCompilationEngine()
    
    try:
        if args.federal_ai:
            # Federal AI compilation mode
            if not args.agency:
                print("❌ Error: --agency required for federal AI compilation")
                sys.exit(1)
            
            ai_system_data = {}
            if args.ai_system_file:
                ai_system_data = load_json_file(args.ai_system_file)
            
            vulnerability_data = []
            if args.vuln_file:
                vuln_data = load_json_file(args.vuln_file)
                if isinstance(vuln_data, list):
                    vulnerability_data = vuln_data
                elif isinstance(vuln_data, dict):
                    vulnerability_data = [vuln_data]
            
            print(f"🔍 Compiling federal AI intelligence for {args.agency}...")
            print(f"⛓️  Blockchain: {args.blockchain}")
            compiled = engine.compile_federal_ai_intelligence(
                target_agency=args.agency,
                ai_system_data=ai_system_data,
                vulnerability_data=vulnerability_data,
                generate_receipt=not args.no_receipt,
                preferred_blockchain=args.blockchain
            )
        else:
            # Standard actor compilation mode
            if not args.actor_id or not args.actor_name:
                print("❌ Error: --actor-id and --actor-name required")
                sys.exit(1)
            
            if not args.intel_file:
                print("❌ Error: --intel-file required")
                sys.exit(1)
            
            # Load intelligence data
            intel_data = load_json_file(args.intel_file)
            if isinstance(intel_data, list):
                raw_intelligence = intel_data
            elif isinstance(intel_data, dict):
                raw_intelligence = [intel_data]
            else:
                print("❌ Error: Intelligence data must be JSON array or object")
                sys.exit(1)
            
            # Load optional data
            transaction_data = None
            if args.transaction_file:
                transaction_data = load_json_file(args.transaction_file)
                if not isinstance(transaction_data, list):
                    transaction_data = [transaction_data]
            
            network_data = None
            if args.network_file:
                network_data = load_json_file(args.network_file)
            
            print(f"🔍 Compiling intelligence for {args.actor_name}...")
            print(f"⛓️  Blockchain: {args.blockchain}")
            compiled = engine.compile_intelligence(
                actor_id=args.actor_id,
                actor_name=args.actor_name,
                raw_intelligence=raw_intelligence,
                transaction_data=transaction_data,
                network_data=network_data,
                generate_receipt=not args.no_receipt,
                preferred_blockchain=args.blockchain
            )
        
        # Display results
        format_output(compiled)
        
        # Save to file if requested
        if args.output:
            output_data = {
                'compilation_id': compiled.compilation_id,
                'actor_id': compiled.actor_id,
                'actor_name': compiled.actor_name,
                'compiled_at': compiled.compiled_at.isoformat(),
                'compilation_time_ms': compiled.compilation_time_ms,
                'confidence_score': compiled.confidence_score,
                'targeting_package': compiled.targeting_package,
                'sources': compiled.sources
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"💾 Output saved to: {args.output}")
        
    except Exception as e:
        print(f"\n❌ Error during compilation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

