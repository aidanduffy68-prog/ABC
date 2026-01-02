# -*- coding: utf-8 -*-
"""
Generate Synthetic Compliance Data
Creates fake blockchain transactions for training AI models

Think of this like a toy factory that makes fake toys that look real!
We make fake transactions so we can practice without using real money.

Usage:
    python3 scripts/generate_synthetic_compliance_data.py --count 100
"""

import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def generate_block_hash():
    """Generate a fake block hash (like a fake ID number)"""
    return hashlib.sha256(str(random.random()).encode()).hexdigest()


def generate_transaction(suspicious: bool = False):
    """
    Generate a fake transaction.
    
    Like making a fake toy - it looks real but it's not!
    
    Args:
        suspicious: If True, make it look suspicious (for training)
    """
    if suspicious:
        # Suspicious patterns: rapid transfers, round numbers, etc.
        patterns = [
            {"txid": f"suspicious_{random.randint(1000, 9999)}", "value": round(random.uniform(0.1, 10.0), 1), "pattern": "rapid_transfers"},
            {"txid": f"suspicious_{random.randint(1000, 9999)}", "value": round(random.uniform(100, 1000), 0), "pattern": "round_amounts"},
            {"txid": f"suspicious_{random.randint(1000, 9999)}", "value": random.uniform(0.001, 0.01), "pattern": "micro_transactions"},
        ]
        return random.choice(patterns)
    else:
        # Normal transaction
        return {
            "txid": f"normal_{random.randint(1000, 9999)}",
            "value": random.uniform(0.1, 100.0),
            "pattern": "normal"
        }


def generate_synthetic_block(block_height: int, suspicious_ratio: float = 0.1):
    """
    Generate a fake blockchain block.
    
    Like making a fake page in a book - it has fake transactions on it!
    
    Args:
        block_height: Block number (like page number)
        suspicious_ratio: How many suspicious transactions (10% = 0.1)
    """
    # Generate timestamp (fake time)
    base_time = int(datetime.now().timestamp())
    timestamp = base_time + (block_height * 600)  # 10 minutes per block
    
    # Generate transactions
    tx_count = random.randint(2000, 3000)
    suspicious_count = int(tx_count * suspicious_ratio)
    normal_count = tx_count - suspicious_count
    
    transactions = []
    
    # Add suspicious transactions
    for _ in range(suspicious_count):
        transactions.append(generate_transaction(suspicious=True))
    
    # Add normal transactions
    for _ in range(normal_count):
        transactions.append(generate_transaction(suspicious=False))
    
    # Shuffle them (mix them up)
    random.shuffle(transactions)
    
    # Create the block
    block = {
        "block_height": block_height,
        "block_hash": generate_block_hash(),
        "timestamp": timestamp,
        "tx_count": tx_count,
        "transactions": json.dumps(transactions)
    }
    
    return block


def generate_synthetic_dataset(count: int = 100, output_file: str = None):
    """
    Generate a bunch of fake blocks.
    
    Like making a whole box of fake toys - lots of them!
    
    Args:
        count: How many fake blocks to make
        output_file: Where to save them
    """
    print("=" * 80)
    print("🎨 Making Fake Transactions (Like Making Fake Toys!)")
    print("=" * 80)
    print()
    print(f"Making {count} fake blocks...")
    print("(These are fake, so they're safe to use!)")
    print()
    
    blocks = []
    
    # Start from a random block height
    start_height = random.randint(800000, 900000)
    
    for i in range(count):
        block_height = start_height + i
        block = generate_synthetic_block(block_height)
        blocks.append(block)
        
        if (i + 1) % 10 == 0:
            print(f"✅ Made {i + 1}/{count} fake blocks...")
    
    print()
    print(f"✅ Done! Made {count} fake blocks")
    print()
    
    # Save to file
    if output_file is None:
        output_file = f"synthetic_compliance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_path = Path("examples/synthetic_data") / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(blocks, f, indent=2)
    
    print(f"💾 Saved to: {output_path}")
    print()
    
    # Show summary
    print("=" * 80)
    print("📊 Summary")
    print("=" * 80)
    print(f"Total blocks: {len(blocks)}")
    print(f"Total transactions: {sum(b['tx_count'] for b in blocks):,}")
    print(f"File: {output_path}")
    print()
    print("🎉 Ready to use for training AI models!")
    print("   (Remember: These are fake, so they're safe!)")
    print()
    
    return blocks, output_path


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate synthetic compliance data for AI training'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=100,
        help='Number of blocks to generate (default: 100)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file name (default: auto-generated)'
    )
    
    args = parser.parse_args()
    
    try:
        blocks, output_path = generate_synthetic_dataset(
            count=args.count,
            output_file=args.output
        )
        
        print("=" * 80)
        print("✅ All done!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Send this data to Foundry pipeline")
        print("2. Generate ABC receipts")
        print("3. Use for training AI models")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

