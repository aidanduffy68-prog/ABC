"""
Palantir Foundry Data Export
Formats and exports data in Foundry-compatible formats

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import json
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import StringIO
from pathlib import Path


class FoundryDataExporter:
    """
    Exports data in formats compatible with Palantir Foundry
    
    Supports:
    - JSON (nested and flattened)
    - CSV
    - Parquet (via pandas)
    - Foundry-specific formats
    """
    
    @staticmethod
    def export_json(
        compilations: List[Dict[str, Any]],
        flattened: bool = False
    ) -> str:
        """
        Export compilations as JSON
        
        Args:
            compilations: List of compilation data
            flattened: Whether to flatten nested structures
        
        Returns:
            JSON string
        """
        if flattened:
            # Flatten for Foundry
            flattened_data = [
                FoundryDataExporter._flatten_dict(comp)
                for comp in compilations
            ]
            return json.dumps(flattened_data, indent=2, default=str)
        else:
            return json.dumps(compilations, indent=2, default=str)
    
    @staticmethod
    def export_csv(
        compilations: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """
        Export compilations as CSV
        
        Args:
            compilations: List of compilation data
            output_path: Optional file path to write to
        
        Returns:
            CSV string
        """
        if not compilations:
            return ""
        
        # Flatten data
        flattened = [FoundryDataExporter._flatten_dict(comp) for comp in compilations]
        
        # Get all keys (union of all keys)
        all_keys = set()
        for record in flattened:
            all_keys.update(record.keys())
        
        # Sort keys for consistent output
        fieldnames = sorted(all_keys)
        
        # Write CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in flattened:
            # Fill missing keys with empty strings
            row = {key: record.get(key, '') for key in fieldnames}
            writer.writerow(row)
        
        csv_string = output.getvalue()
        
        # Write to file if path provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(csv_string)
        
        return csv_string
    
    @staticmethod
    def export_parquet(
        compilations: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        Export compilations as Parquet (Foundry's preferred format)
        
        Args:
            compilations: List of compilation data
            output_path: File path to write Parquet file
        
        Returns:
            Path to written file
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas and pyarrow required for Parquet export. Install with: pip install pandas pyarrow")
        
        # Flatten data
        flattened = [FoundryDataExporter._flatten_dict(comp) for comp in compilations]
        
        # Create DataFrame
        df = pd.DataFrame(flattened)
        
        # Write Parquet
        df.to_parquet(output_path, index=False, engine='pyarrow')
        
        return output_path
    
    @staticmethod
    def _flatten_dict(
        d: Dict[str, Any],
        parent_key: str = '',
        sep: str = '_'
    ) -> Dict[str, Any]:
        """
        Flatten nested dictionary for Foundry compatibility
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for nested keys
        
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(FoundryDataExporter._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to JSON strings for Foundry
                items.append((new_key, json.dumps(v) if v else ''))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    @staticmethod
    def export_foundry_dataset(
        compilations: List[Dict[str, Any]],
        dataset_name: str,
        output_dir: str = "foundry_exports"
    ) -> Dict[str, Any]:
        """
        Export complete Foundry dataset with multiple formats
        
        Args:
            compilations: List of compilation data
            dataset_name: Name for the dataset
            output_dir: Output directory
        
        Returns:
            Export summary
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export in multiple formats
        json_path = output_path / f"{dataset_name}_{timestamp}.json"
        csv_path = output_path / f"{dataset_name}_{timestamp}.csv"
        parquet_path = output_path / f"{dataset_name}_{timestamp}.parquet"
        
        # JSON export
        json_data = FoundryDataExporter.export_json(compilations, flattened=True)
        with open(json_path, 'w') as f:
            f.write(json_data)
        
        # CSV export
        FoundryDataExporter.export_csv(compilations, str(csv_path))
        
        # Parquet export (if available)
        parquet_exported = False
        try:
            FoundryDataExporter.export_parquet(compilations, str(parquet_path))
            parquet_exported = True
        except ImportError:
            pass
        
        return {
            "dataset_name": dataset_name,
            "records_exported": len(compilations),
            "formats": {
                "json": str(json_path),
                "csv": str(csv_path),
                "parquet": str(parquet_path) if parquet_exported else None
            },
            "timestamp": datetime.now().isoformat()
        }

