# -*- coding: utf-8 -*-
"""
Verify Foundry Pipeline Hashes
Verifies that ABC hashes from Foundry pipeline match ABC-generated hashes

Usage:
    python3 scripts/verify_foundry_hashes.py [--output-dir OUTPUT_DIR]
"""

import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def verify_hash(block_height, block_hash, timestamp, tx_count, transactions, expected_hash):
    """Verify hash matches Foundry function"""
    # Reconstruct exactly as your Foundry function does
    block_data = {
        "block_height": block_height,
        "block_hash": block_hash,
        "timestamp": timestamp,
        "tx_count": tx_count,
        "transactions": transactions
    }
    
    # Generate hash (same method as Foundry)
    normalized = json.dumps(block_data, sort_keys=True, separators=(',', ':'))
    computed_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    match = computed_hash == expected_hash
    return match, computed_hash, normalized


def save_results(results: List[Dict[str, Any]], output_dir: Path):
    """Save verification results to files"""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON results
    json_path = output_dir / f"verification_results_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump({
            "verification_timestamp": datetime.now().isoformat(),
            "total_records": len(results),
            "verified_count": sum(1 for r in results if r["verified"]),
            "failed_count": sum(1 for r in results if not r["verified"]),
            "all_verified": all(r["verified"] for r in results),
            "results": results
        }, f, indent=2)
    print(f"✅ JSON results saved to: {json_path}")
    
    # Save CSV results
    csv_path = output_dir / f"verification_results_{timestamp}.csv"
    with open(csv_path, 'w') as f:
        # Header
        f.write("block_height,verified,foundry_hash,computed_hash,match\n")
        # Data
        for r in results:
            f.write(f"{r['block_height']},{r['verified']},{r['foundry_hash']},{r['computed_hash']},{r['verified']}\n")
    print(f"✅ CSV results saved to: {csv_path}")
    
    # Save summary report
    report_path = output_dir / f"verification_report_{timestamp}.txt"
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("FOUNDRY PIPELINE HASH VERIFICATION REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Verification Date: {datetime.now().isoformat()}\n")
        f.write(f"Total Records: {len(results)}\n")
        f.write(f"Verified: {sum(1 for r in results if r['verified'])}\n")
        f.write(f"Failed: {sum(1 for r in results if not r['verified'])}\n")
        f.write(f"Status: {'✅ ALL VERIFIED' if all(r['verified'] for r in results) else '❌ SOME FAILED'}\n")
        f.write("\n" + "=" * 80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        for r in results:
            f.write(f"Block Height: {r['block_height']}\n")
            f.write(f"Status: {'✅ VERIFIED' if r['verified'] else '❌ FAILED'}\n")
            f.write(f"Foundry Hash: {r['foundry_hash']}\n")
            f.write(f"Computed Hash: {r['computed_hash']}\n")
            f.write("\n")
    
    print(f"✅ Summary report saved to: {report_path}")
    
    return json_path, csv_path, report_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify Foundry pipeline hashes')
    parser.add_argument('--output-dir', type=str, default='verification_output',
                       help='Directory to save verification results (default: verification_output)')
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    print("=" * 80)
    print("FOUNDRY PIPELINE HASH VERIFICATION")
    print("Verifying ABC hashes from Foundry pipeline match ABC-generated hashes")
    print("=" * 80)
    print()
    
    # Test data
    test_records = [
        {
            "block_height": 825000,
            "block_hash": "94f84c7be087799b54c3e4adce1f9012a7e3c8d4b6f5a2e1c9d8b7a6f5e4d3c2",
            "timestamp": 1735689600,
            "tx_count": 2453,
            "transactions": '[{"txid":"abc123","value":0.5}]',
            "expected_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b"
        },
        {
            "block_height": 825001,
            "block_hash": "b1789a1a7aca6780a5646decd77c8e67c9d8b7a6f5e4d3c2a1b0c9d8e7f6a5b4",
            "timestamp": 1735690200,
            "tx_count": 2387,
            "transactions": '[{"txid":"def456","value":1.2}]',
            "expected_hash": "98b3e80720281074c8f05ac5cfb2d1cae23ab8eb1adf46fdfa57e39a6a96b6df"
        },
        {
            "block_height": 825002,
            "block_hash": "c2890b2b8bdb7891b6757efde88d9f78d0e9c8b7a6f5e4d3c2b1d0e9f8a7b6c5",
            "timestamp": 1735690800,
            "tx_count": 2541,
            "transactions": '[{"txid":"ghi789","value":0.8}]',
            "expected_hash": "4813c1c4c3bf247f8134288fcc83c17f4895d317067f7f110ec48ef127731b4a"
        },
        {
            "block_height": 825003,
            "block_hash": "d3901c3c9cec8902c7868f0ef99e0a89e1f0d9c8b7a6f5e4d3c2e1f0a9b8c7d6",
            "timestamp": 1735691400,
            "tx_count": 2298,
            "transactions": '[{"txid":"jkl012","value":2.5}]',
            "expected_hash": "4aac03e6e8a652f60889b718bdbe4934870ff6eff364ab700cf1200a77a507e1"
        }
    ]
    
    results = []
    
    # Verify each record
    for i, record in enumerate(test_records, 1):
        print("=" * 80)
        print(f"VERIFYING RECORD {i} (block_height: {record['block_height']})")
        print("=" * 80)
        
        match, computed_hash, json_data = verify_hash(
            record["block_height"],
            record["block_hash"],
            record["timestamp"],
            record["tx_count"],
            record["transactions"],
            record["expected_hash"]
        )
        
        print(f"Expected hash: {record['expected_hash']}")
        print(f"Computed hash: {computed_hash}")
        print(f"Match: {'✅ YES' if match else '❌ NO'}")
        if not match:
            print(f"JSON used: {json_data}")
        print()
        
        results.append({
            "block_height": record["block_height"],
            "block_hash": record["block_hash"],
            "timestamp": record["timestamp"],
            "tx_count": record["tx_count"],
            "transactions": record["transactions"],
            "foundry_hash": record["expected_hash"],
            "computed_hash": computed_hash,
            "verified": match,
            "json_data": json_data
        })
    
    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    for r in results:
        status = "✅ VERIFIED" if r["verified"] else "❌ FAILED"
        print(f"Record {r['block_height']}: {status}")
    print()
    
    all_match = all(r["verified"] for r in results)
    verified_count = sum(1 for r in results if r["verified"])
    
    if all_match:
        print("🎉 SUCCESS: All 4 hashes match!")
        print("   Your Foundry pipeline is generating correct ABC receipts!")
        print("   ABC verification is working correctly!")
        print()
        print("✅ Your Foundry transform:")
        print("   - Uses the same hashing method as ABC")
        print("   - Generates correct cryptographic receipts")
        print("   - Can be used for ABC verification")
    else:
        print(f"⚠️  {verified_count}/4 hashes matched")
        print("   Check the mismatched records above")
        print("   This might indicate a data format difference")
    
    print()
    print("=" * 80)
    
    # Save results to files
    print()
    print("Saving verification results...")
    json_path, csv_path, report_path = save_results(results, output_dir)
    print()
    print(f"✅ All results saved to: {output_dir}")
    print(f"   - JSON: {json_path.name}")
    print(f"   - CSV: {csv_path.name}")
    print(f"   - Report: {report_path.name}")
    
    return all_match


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

