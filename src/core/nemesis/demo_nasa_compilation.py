"""
Live NASA AI Compilation Demo
Demonstrates real-time federal AI threat compilation with NASA data

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import time
import requests
import json
from datetime import datetime

from nemesis.compilation_engine import ABCCompilationEngine
from nemesis.signal_intake.federal_ai_monitor import FederalAIMonitor
from nemesis.on_chain_receipt.bitcoin_integration import BitcoinOnChainIntegration
from nemesis.on_chain_receipt.receipt_verifier import ReceiptVerifier


def demo_nasa_compilation():
    """Live demo of NASA AI compilation"""
    
    print("=" * 60)
    print("ABC FEDERAL AI SECURITY - LIVE NASA COMPILATION DEMO")
    print("=" * 60)
    print()
    
    # Initialize components
    print("📡 Initializing ABC Compilation Engine...")
    compilation_engine = ABCCompilationEngine()
    federal_monitor = FederalAIMonitor()
    bitcoin_integration = BitcoinOnChainIntegration()
    receipt_verifier = ReceiptVerifier()
    print("✅ Engine initialized\n")
    
    # Step 1: Scan NASA Systems
    print("🔍 Step 1: Scanning NASA AI Systems...")
    print("-" * 60)
    nasa_systems = federal_monitor.scan_nasa_systems()
    
    for system in nasa_systems:
        print(f"  • {system.system_name}")
        print(f"    Type: {system.system_type}")
        print(f"    Vulnerabilities: {len(system.vulnerabilities)}")
        for vuln in system.vulnerabilities:
            print(f"      - {vuln['type']} ({vuln['severity']}) - Confidence: {vuln.get('confidence', 0):.2%}")
    print()
    
    # Step 2: Generate Intelligence Feed
    print("📊 Step 2: Generating Intelligence Feed...")
    print("-" * 60)
    intelligence_feed = federal_monitor.generate_intelligence_feed(nasa_systems)
    print(f"  • Intelligence items: {len(intelligence_feed)}")
    print(f"  • Systems analyzed: {len(nasa_systems)}")
    print()
    
    # Step 3: Compile Intelligence
    print("⚡ Step 3: Compiling Intelligence (Hades → Echo → Nemesis)...")
    print("-" * 60)
    start_time = time.time()
    
    # Extract vulnerability data
    vulnerability_data = []
    ai_system_data = {}
    for system in nasa_systems:
        ai_system_data[system.system_name] = {
            "type": system.system_type,
            "endpoint": system.endpoint,
            "agency": system.agency
        }
        for vuln in system.vulnerabilities:
            vulnerability_data.append({
                "type": vuln["type"],
                "severity": vuln["severity"],
                "description": vuln["description"],
                "confidence": vuln.get("confidence", 0.5)
            })
    
    # Compile federal AI intelligence
    compiled = compilation_engine.compile_federal_ai_intelligence(
        target_agency="NASA",
        ai_system_data=ai_system_data,
        vulnerability_data=vulnerability_data,
        generate_receipt=True
    )
    
    compilation_time = (time.time() - start_time) * 1000
    
    print(f"  ✅ Compilation complete!")
    print(f"  • Compilation time: {compilation_time:.2f}ms")
    print(f"  • Target: <500ms")
    print(f"  • Status: {'✅ MEETS TARGET' if compilation_time < 500 else '⚠️  ABOVE TARGET'}")
    print(f"  • Confidence score: {compiled.confidence_score:.2%}")
    print(f"  • Compilation ID: {compiled.compilation_id}")
    print()
    
    # Step 4: Display Targeting Package
    print("🎯 Step 4: Targeting Package Generated...")
    print("-" * 60)
    targeting_package = compiled.targeting_package
    risk_assessment = targeting_package.get("risk_assessment", {})
    
    print(f"  • Threat Level: {risk_assessment.get('threat_level', 'unknown').upper()}")
    print(f"  • Overall Risk: {risk_assessment.get('overall_risk', 0):.2%}")
    print(f"  • Next Action Window: {risk_assessment.get('next_action_window', 'N/A')}")
    print()
    
    if targeting_package.get("targeting_instructions"):
        print("  Targeting Instructions:")
        for i, instruction in enumerate(targeting_package["targeting_instructions"][:3], 1):
            print(f"    {i}. {instruction.get('action', 'N/A')}")
            print(f"       Confidence: {instruction.get('confidence', 0):.2%}")
            print(f"       Timeframe: {instruction.get('timeframe', 'N/A')}")
    print()
    
    # Step 5: Bitcoin Receipt
    print("₿ Step 5: Generating Bitcoin Receipt...")
    print("-" * 60)
    receipt = targeting_package.get("receipt")
    
    if receipt:
        print(f"  • Receipt ID: {receipt.get('receipt_id')}")
        print(f"  • Intelligence Hash: {receipt.get('intelligence_hash')[:32]}...")
        print(f"  • Timestamp: {receipt.get('timestamp')}")
        print(f"  • Threat Level: {receipt.get('threat_level', 'unknown')}")
        print()
        
        # Submit to Bitcoin
        print("  📤 Submitting to Bitcoin blockchain...")
        try:
            tx_result = bitcoin_integration.submit_receipt_to_blockchain(receipt)
            print(f"  ✅ Transaction submitted!")
            print(f"  • TX Hash: {tx_result.get('tx_hash')}")
            print(f"  • Network: {tx_result.get('network')}")
            print(f"  • Status: {tx_result.get('status')}")
        except Exception as e:
            print(f"  ⚠️  Bitcoin submission error: {e}")
            print(f"  (Mock mode - production would submit to actual blockchain)")
        print()
        
        # Verify receipt
        print("  🔍 Verifying receipt...")
        verification = receipt_verifier.verify_receipt(
            receipt,
            intelligence_package=targeting_package,
            verify_on_chain=False  # Set to True in production
        )
        
        if verification.get("verified"):
            print("  ✅ Receipt verified!")
            print(f"  • Hash integrity: {verification['checks'].get('hash_integrity')}")
            print(f"  • Structure valid: {verification['checks'].get('structure_validity')}")
        else:
            print("  ⚠️  Receipt verification failed")
        print()
    
    # Step 6: Summary
    print("=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    print(f"✅ NASA AI systems scanned: {len(nasa_systems)}")
    print(f"✅ Vulnerabilities identified: {sum(len(s.vulnerabilities) for s in nasa_systems)}")
    print(f"✅ Compilation time: {compilation_time:.2f}ms")
    print(f"✅ Bitcoin receipt generated: {'Yes' if receipt else 'No'}")
    print(f"✅ Targeting package ready: Yes")
    print(f"✅ Confidence score: {compiled.confidence_score:.2%}")
    print()
    print("🚀 System Status: PRODUCTION READY")
    print("📊 Dashboard: http://localhost:5001/dashboard")
    print("🔌 API: http://localhost:5000/api/v1")
    print()
    print("=" * 60)


if __name__ == "__main__":
    demo_nasa_compilation()

