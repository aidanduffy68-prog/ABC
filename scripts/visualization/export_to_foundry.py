#!/usr/bin/env python3
"""
GH Systems ABC - Foundry Export Tool
Export intelligence compilations for Palantir Foundry integration

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import sys
import argparse
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.integrations.foundry.export import FoundryDataExporter
from src.integrations.foundry.connector import FoundryConnector


def main():
    parser = argparse.ArgumentParser(
        description='Export intelligence compilations for Palantir Foundry'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input JSON file with compilation data'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'parquet', 'all'],
        default='all',
        help='Export format (default: all)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='foundry_exports',
        help='Output directory (default: foundry_exports)'
    )
    parser.add_argument(
        '--dataset-name',
        type=str,
        default='intelligence_compilations',
        help='Dataset name (default: intelligence_compilations)'
    )
    parser.add_argument(
        '--flattened',
        action='store_true',
        help='Flatten nested JSON structures'
    )
    parser.add_argument(
        '--push',
        action='store_true',
        help='Push directly to Foundry (requires FOUNDRY_URL and FOUNDRY_API_TOKEN)'
    )
    
    args = parser.parse_args()
    
    # Load compilation data
    print(f"Loading compilation data from {args.input}...")
    with open(args.input, 'r') as f:
        compilations = json.load(f)
    
    if not isinstance(compilations, list):
        compilations = [compilations]
    
    print(f"Loaded {len(compilations)} compilation(s)")
    print()
    
    # Export in requested formats
    if args.format in ['json', 'all']:
        print("Exporting JSON...")
        json_data = FoundryDataExporter.export_json(compilations, flattened=args.flattened)
        json_path = Path(args.output_dir) / f"{args.dataset_name}.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w') as f:
            f.write(json_data)
        print(f"✅ JSON exported to: {json_path}")
        print()
    
    if args.format in ['csv', 'all']:
        print("Exporting CSV...")
        csv_path = Path(args.output_dir) / f"{args.dataset_name}.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        FoundryDataExporter.export_csv(compilations, str(csv_path))
        print(f"✅ CSV exported to: {csv_path}")
        print()
    
    if args.format in ['parquet', 'all']:
        print("Exporting Parquet...")
        try:
            parquet_path = Path(args.output_dir) / f"{args.dataset_name}.parquet"
            parquet_path.parent.mkdir(parents=True, exist_ok=True)
            FoundryDataExporter.export_parquet(compilations, str(parquet_path))
            print(f"✅ Parquet exported to: {parquet_path}")
        except ImportError:
            print("⚠️  Parquet export requires pandas and pyarrow: pip install pandas pyarrow")
        print()
    
    # Push to Foundry if requested
    if args.push:
        print("Pushing to Foundry...")
        connector = FoundryConnector()
        if connector.enabled:
            result = connector.push_batch(compilations)
            print(f"✅ Push result: {result['status']}")
            if result['status'] == 'success':
                print(f"   Records pushed: {result['records_pushed']}")
                print(f"   Dataset: {result['dataset_path']}")
        else:
            print("❌ Foundry connector not configured")
            print("   Set FOUNDRY_URL and FOUNDRY_API_TOKEN environment variables")
        print()
    
    print("=" * 60)
    print("Export complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

