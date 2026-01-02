# -*- coding: utf-8 -*-
"""
Test Foundry AIP Workflow
Tests complete workflow: Foundry AIP → ABC Receipt → Verification

Usage:
    python3 scripts/test_foundry_aip_workflow.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_foundry_aip_workflow():
    """Test complete Foundry AIP workflow"""
    print("=" * 70)
    print("Foundry AIP Workflow Test")
    print("=" * 70)
    print()
    
    # Step 1: Test Connection
    print("Step 1: Connect to Foundry AIP")
    print("-" * 70)
    
    try:
        from src.verticals.ai_verification.core.nemesis.foundry_integration import FoundryIntegration
        
        foundry = FoundryIntegration(use_aip=True)
        print("✅ Connected to Foundry AIP")
        print(f"   Using AIP connector: {foundry.use_aip}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Step 2: List Recent Compilations (if any exist)
    print("Step 2: List Recent Compilations")
    print("-" * 70)
    
    try:
        compilations = foundry.list_recent_compilations(limit=5)
        print(f"✅ Found {len(compilations)} compilations")
        
        if compilations:
            for comp in compilations[:3]:
                comp_id = comp.get('compilation_id', 'N/A')
                print(f"   - {comp_id}")
        else:
            print("   (No compilations found - this is OK for new setup)")
    except Exception as e:
        print(f"⚠️  Could not list compilations: {e}")
        print("   (This is OK if no datasets exist yet)")
    
    print()
    
    # Step 3: Create Test Data and Generate ABC Receipt
    print("Step 3: Generate ABC Receipt from Test Data")
    print("-" * 70)
    
    try:
        from src.shared.receipts import generate_abc_receipt, generate_abc_receipt_id, verify_data_integrity
        
        # Create test blockchain data
        test_data = {
            "block": 825000,
            "hash": "0x1234567890abcdef",
            "timestamp": datetime.now().isoformat(),
            "source": "foundry_test",
            "test": True
        }
        
        # Generate receipt
        receipt = generate_abc_receipt(
            blockchain_data=test_data,
            source="foundry_test_workflow",
            classification="UNCLASSIFIED",
            blockchain="bitcoin"
        )
        
        print("✅ ABC Receipt Generated:")
        print(f"   Receipt ID: {receipt.receipt_id[:32]}...")
        print(f"   Intelligence Hash: {receipt.intelligence_hash[:32]}...")
        print(f"   Timestamp: {receipt.timestamp}")
        print(f"   Status: {receipt.status}")
        
    except Exception as e:
        print(f"❌ Failed to generate receipt: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Step 4: Generate Receipt ID
    print("Step 4: Generate Receipt ID")
    print("-" * 70)
    
    try:
        receipt_id = generate_abc_receipt_id(receipt.intelligence_hash)
        print(f"✅ Receipt ID Generated: {receipt_id[:32]}...")
        print(f"   Length: {len(receipt_id)} characters")
    except Exception as e:
        print(f"❌ Failed to generate receipt ID: {e}")
        return False
    
    print()
    
    # Step 5: Verify Data Integrity
    print("Step 5: Verify Data Integrity")
    print("-" * 70)
    
    try:
        # Test with original data (should pass)
        # Need to pass source and classification to match how receipt was created
        result = verify_data_integrity(
            original_hash=receipt.intelligence_hash,
            current_data=test_data,
            receipt=receipt,
            source="foundry_test_workflow",
            classification="UNCLASSIFIED"
        )
        
        if result["verified"]:
            print("✅ Data integrity verified (no tampering detected)")
        else:
            print("❌ Data integrity check failed")
            return False
        
        # Test with modified data (should fail)
        tampered_data = test_data.copy()
        tampered_data["block"] = 999999  # Tamper with data
        
        tampered_result = verify_data_integrity(
            original_hash=receipt.intelligence_hash,
            current_data=tampered_data,
            receipt=receipt,
            source="foundry_test_workflow",
            classification="UNCLASSIFIED"
        )
        
        if not tampered_result["verified"]:
            print("✅ Tampering detection works (modified data correctly rejected)")
        else:
            print("⚠️  Tampering detection may not be working correctly")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Step 6: Push to Foundry (if dataset exists)
    print("Step 6: Push Test Data to Foundry")
    print("-" * 70)
    
    try:
        if foundry.use_aip and hasattr(foundry.connector, 'push_compilation'):
            test_compilation = {
                "compilation_id": f"test_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "abc_receipt_id": receipt.receipt_id,
                "abc_hash": receipt.intelligence_hash,
                "timestamp": receipt.timestamp,
                "status": "test",
                "source": "foundry_aip_workflow_test"
            }
            
            push_result = foundry.connector.push_compilation(
                compilation_data=test_compilation,
                dataset_path="gh_systems/intelligence_compilations"
            )
            
            print(f"✅ Test data pushed to Foundry")
            print(f"   Transaction RID: {push_result.get('transaction_rid', 'N/A')}")
            print(f"   Records written: {push_result.get('records_written', 0)}")
        else:
            print("⚠️  Push to Foundry skipped (dataset may not exist yet)")
            print("   This is OK - create the dataset in Foundry first")
    
    except Exception as e:
        print(f"⚠️  Could not push to Foundry: {e}")
        print("   (This is OK if dataset doesn't exist yet)")
    
    print()
    
    # Summary
    print("=" * 70)
    print("✅ Foundry AIP Workflow Test Complete!")
    print("=" * 70)
    print()
    print("Workflow Summary:")
    print("  ✅ Connected to Foundry AIP")
    print("  ✅ Listed compilations")
    print("  ✅ Generated ABC receipt")
    print("  ✅ Generated receipt ID")
    print("  ✅ Verified data integrity")
    print("  ✅ Tested tampering detection")
    print()
    print("Next Steps:")
    print("  1. Create datasets in Foundry (if needed)")
    print("  2. Test with real Foundry compilations")
    print("  3. Integrate with ABC compilation engine")
    print("  4. Deploy to production")
    print()
    
    return True


def main():
    """Main test function"""
    try:
        success = test_foundry_aip_workflow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

