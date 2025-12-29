#!/usr/bin/env python3
"""
Test Bitcoin oracle functionality
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.oracle.bitcoin_ingestion import BitcoinOracle

def main():
    print("\n🔗 ABC Bitcoin Oracle Test\n")
    
    try:
        # Initialize oracle
        print("Connecting to Bitcoin node...")
        bitcoin_oracle = BitcoinOracle()
        
        # Get latest block
        latest_block = bitcoin_oracle.get_latest_block_height()
        print(f"✅ Connected! Latest block: {latest_block}\n")
        
        # Ingest a block
        print(f"Ingesting block {latest_block}...")
        result = bitcoin_oracle.ingest_block(latest_block)
        
        # Display results
        print("\n" + "="*60)
        print("Ingestion Result")
        print("="*60)
        print(f"Block Height: {result['block_height']}")
        print(f"Block Hash: {result['block_hash'][:32]}...")
        print(f"TX Count: {result['tx_count']}")
        
        if result.get('receipt'):
            print(f"Receipt ID: {result['receipt']['receipt_id']}")
            print(f"Data Hash: {result['receipt']['intelligence_hash'][:32]}...")
        
        print("="*60)
        print("\n✅ Oracle test complete!\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

