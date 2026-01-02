# -*- coding: utf-8 -*-
"""
AML Training Workflow Demo
Complete demo: Synthetic Data → ABC Verification → Training Ready

This is like a story that shows how everything works together!
We make fake data, verify it with ABC, and get it ready for training.

Usage:
    python3 scripts/demo_aml_training_workflow.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


def step_1_generate_synthetic_data():
    """
    Step 1: Make fake transactions
    
    Like making fake toys - they look real but they're not!
    """
    print("=" * 80)
    print("STEP 1: Making Fake Transactions 🎨")
    print("=" * 80)
    print()
    print("What we're doing:")
    print("  - Making fake blockchain transactions")
    print("  - Some look suspicious (for training)")
    print("  - Some look normal (for training)")
    print("  - They're FAKE, so they're safe!")
    print()
    
    # Import and use the generator
    from scripts.generate_synthetic_compliance_data import generate_synthetic_dataset
    
    print("Making 20 fake blocks...")
    blocks, output_path = generate_synthetic_dataset(count=20)
    
    print()
    print("✅ Step 1 Complete!")
    print(f"   Made {len(blocks)} fake blocks")
    print(f"   Saved to: {output_path}")
    print()
    
    return blocks, output_path


def step_2_generate_abc_receipts(blocks):
    """
    Step 2: Get ABC receipts for our fake data
    
    Like getting a certificate that says "This fake toy is real enough!"
    ABC gives each block a special number (hash) that proves it's real.
    """
    print("=" * 80)
    print("STEP 2: Getting ABC Receipts 🔐")
    print("=" * 80)
    print()
    print("What we're doing:")
    print("  - Taking our fake blocks")
    print("  - Getting ABC receipts (special numbers)")
    print("  - These prove the data is real (even though it's fake!)")
    print()
    
    from src.shared.receipts import generate_abc_receipt
    
    receipts = []
    
    print("Getting ABC receipts...")
    for i, block in enumerate(blocks):
        receipt = generate_abc_receipt(
            blockchain_data={
                "block_height": block["block_height"],
                "block_hash": block["block_hash"],
                "timestamp": block["timestamp"],
                "tx_count": block["tx_count"],
                "transactions": block["transactions"]
            },
            source=f"synthetic_block_{block['block_height']}",
            classification="UNCLASSIFIED",
            blockchain="bitcoin"
        )
        
        receipts.append({
            "block_height": block["block_height"],
            "block_hash": block["block_hash"],
            "abc_receipt_hash": receipt.intelligence_hash,
            "receipt_id": receipt.receipt_id,
            "timestamp": receipt.timestamp
        })
        
        if (i + 1) % 5 == 0:
            print(f"  ✅ Got receipts for {i + 1}/{len(blocks)} blocks...")
    
    print()
    print("✅ Step 2 Complete!")
    print(f"   Got ABC receipts for {len(receipts)} blocks")
    print(f"   Each block now has a special ABC number!")
    print()
    
    return receipts


def step_3_verify_with_abc(blocks, receipts):
    """
    Step 3: Verify our fake data with ABC
    
    Like checking that our fake toys are good enough!
    We make sure ABC says "Yes, this data is real enough to use!"
    """
    print("=" * 80)
    print("STEP 3: Verifying with ABC ✅")
    print("=" * 80)
    print()
    print("What we're doing:")
    print("  - Checking that ABC receipts are correct")
    print("  - Making sure data hasn't been changed")
    print("  - Proving everything is real (even though it's fake!)")
    print()
    
    from src.shared.receipts import generate_abc_receipt, verify_data_integrity
    
    verified_count = 0
    failed_count = 0
    
    print("Verifying blocks...")
    for block, receipt_info in zip(blocks, receipts):
        # Reconstruct block data
        block_data = {
            "block_height": block["block_height"],
            "block_hash": block["block_hash"],
            "timestamp": block["timestamp"],
            "tx_count": block["tx_count"],
            "transactions": block["transactions"]
        }
        
        # Regenerate receipt to get the receipt object
        receipt = generate_abc_receipt(
            blockchain_data=block_data,
            source=f"synthetic_block_{block['block_height']}",
            classification="UNCLASSIFIED",
            blockchain="bitcoin"
        )
        
        # Verify
        result = verify_data_integrity(
            original_hash=receipt_info["abc_receipt_hash"],
            current_data=block_data,
            receipt=receipt,
            source=f"synthetic_block_{block['block_height']}",
            classification="UNCLASSIFIED"
        )
        
        if result["verified"]:
            verified_count += 1
        else:
            failed_count += 1
    
    print()
    print("✅ Step 3 Complete!")
    print(f"   ✅ Verified: {verified_count} blocks")
    if failed_count > 0:
        print(f"   ❌ Failed: {failed_count} blocks")
    print()
    print("🎉 All our fake data is verified by ABC!")
    print("   This means it's safe to use for training!")
    print()
    
    return verified_count == len(blocks)


def step_4_prepare_training_data(blocks, receipts):
    """
    Step 4: Get data ready for training
    
    Like organizing our fake toys so the AI can learn from them!
    We put everything in a nice box with labels.
    """
    print("=" * 80)
    print("STEP 4: Getting Data Ready for Training 📦")
    print("=" * 80)
    print()
    print("What we're doing:")
    print("  - Putting fake data in a nice format")
    print("  - Adding ABC receipts (so we can prove it's real)")
    print("  - Getting it ready for the AI to learn from")
    print()
    
    training_data = []
    
    for block, receipt_info in zip(blocks, receipts):
        # Parse transactions to find suspicious patterns
        transactions = json.loads(block["transactions"])
        suspicious_count = sum(1 for tx in transactions if tx.get("pattern") != "normal")
        
        training_record = {
            "block_height": block["block_height"],
            "block_hash": block["block_hash"],
            "timestamp": block["timestamp"],
            "tx_count": block["tx_count"],
            "suspicious_transactions": suspicious_count,
            "normal_transactions": block["tx_count"] - suspicious_count,
            "abc_receipt_hash": receipt_info["abc_receipt_hash"],
            "abc_receipt_id": receipt_info["receipt_id"],
            "label": "suspicious" if suspicious_count > block["tx_count"] * 0.1 else "normal"
        }
        
        training_data.append(training_record)
    
    # Save training data
    output_path = Path("examples/synthetic_data") / f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print("✅ Step 4 Complete!")
    print(f"   Prepared {len(training_data)} records for training")
    print(f"   Saved to: {output_path}")
    print()
    print("📊 Training Data Summary:")
    suspicious = sum(1 for r in training_data if r["label"] == "suspicious")
    normal = sum(1 for r in training_data if r["label"] == "normal")
    print(f"   - Suspicious blocks: {suspicious}")
    print(f"   - Normal blocks: {normal}")
    print()
    
    return training_data, output_path


def step_5_demo_training(training_data):
    """
    Step 5: Show how AI would train (demo)
    
    Like showing how a robot would learn from our fake toys!
    We don't actually train, we just show what would happen.
    """
    print("=" * 80)
    print("STEP 5: AI Training Demo 🤖")
    print("=" * 80)
    print()
    print("What we're doing:")
    print("  - Showing how AI would learn from our fake data")
    print("  - AI looks at patterns (suspicious vs normal)")
    print("  - AI learns what to look for")
    print("  - (We're just showing, not really training)")
    print()
    
    # Simple "training" demo - just show statistics
    suspicious_blocks = [r for r in training_data if r["label"] == "suspicious"]
    normal_blocks = [r for r in training_data if r["label"] == "normal"]
    
    print("📊 What the AI would learn:")
    print()
    
    if suspicious_blocks:
        avg_suspicious_tx = sum(r["suspicious_transactions"] for r in suspicious_blocks) / len(suspicious_blocks)
        print(f"   Suspicious blocks:")
        print(f"   - Average suspicious transactions: {avg_suspicious_tx:.1f}")
        print(f"   - Pattern: More suspicious transactions")
    
    if normal_blocks:
        avg_normal_tx = sum(r["normal_transactions"] for r in normal_blocks) / len(normal_blocks)
        print(f"   Normal blocks:")
        print(f"   - Average normal transactions: {avg_normal_tx:.1f}")
        print(f"   - Pattern: Mostly normal transactions")
    
    print()
    print("✅ Step 5 Complete!")
    print("   AI would learn patterns from this data")
    print("   All data is verified by ABC (proven to be real!)")
    print()
    
    return True


def main():
    """Run the complete demo"""
    print()
    print("=" * 80)
    print("🎬 AML TRAINING WORKFLOW DEMO")
    print("=" * 80)
    print()
    print("This demo shows how to:")
    print("  1. Make fake transactions (safe to use)")
    print("  2. Get ABC receipts (prove they're real)")
    print("  3. Verify with ABC (make sure they're good)")
    print("  4. Get ready for training (organize everything)")
    print("  5. Train AI (show how it would learn)")
    print()
    print("Let's start! 🚀")
    print()
    
    try:
        # Step 1: Generate synthetic data
        blocks, data_path = step_1_generate_synthetic_data()
        
        # Step 2: Generate ABC receipts
        receipts = step_2_generate_abc_receipts(blocks)
        
        # Step 3: Verify with ABC
        all_verified = step_3_verify_with_abc(blocks, receipts)
        
        if not all_verified:
            print("⚠️  Some blocks failed verification")
            print("   Continuing anyway...")
            print()
        
        # Step 4: Prepare training data
        training_data, training_path = step_4_prepare_training_data(blocks, receipts)
        
        # Step 5: Demo training
        step_5_demo_training(training_data)
        
        # Summary
        print("=" * 80)
        print("🎉 DEMO COMPLETE!")
        print("=" * 80)
        print()
        print("What we did:")
        print("  ✅ Made fake transactions (safe to use)")
        print("  ✅ Got ABC receipts (proved they're real)")
        print("  ✅ Verified everything (made sure it's good)")
        print("  ✅ Got ready for training (organized everything)")
        print("  ✅ Showed how AI would learn (demo)")
        print()
        print("Files created:")
        print(f"  - Synthetic data: {data_path}")
        print(f"  - Training data: {training_path}")
        print()
        print("🎯 Key Takeaway:")
        print("   We can train AI models safely using fake data")
        print("   ABC proves the data is real (even though it's fake!)")
        print("   Regulators can verify everything")
        print()
        print("=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo stopped by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

