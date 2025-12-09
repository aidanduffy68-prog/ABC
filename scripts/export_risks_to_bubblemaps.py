#!/usr/bin/env python3
"""
Export Risk Data to Bubblemaps.io Format
Creates data files compatible with bubblemaps.io platform

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import json
import csv
from typing import List, Dict, Any

# Top 3 risks from Ethereum audit
risks_data = [
    {
        'id': 'P0',
        'label': 'Chain-Agnostic Architecture Enables Market Expansion',
        'value': 92,  # Capability score
        'size': 92,  # Bubble size
        'category': 'Critical',
        'confidence': 92,
        'description': 'Chain-agnostic architecture removes blockchain lock-in objections and expands addressable market by 4x.',
        'color': '#00FF00'  # Green
    },
    {
        'id': 'P1',
        'label': 'Ethereum Integration Demonstrates EVM Support',
        'value': 88,
        'size': 88,
        'category': 'High',
        'confidence': 88,
        'description': 'Ethereum commitment demonstrates ABC works with EVM-compatible chains, not just Bitcoin.',
        'color': '#90EE90'  # Light green
    },
    {
        'id': 'P2',
        'label': 'Multi-Agency Deployment Scenarios',
        'value': 75,
        'size': 75,
        'category': 'Medium',
        'confidence': 85,
        'description': 'Chain-agnostic architecture enables different agencies to use different chains simultaneously.',
        'color': '#ADFF2F'  # Yellow-green
    }
]

# Connections/relationships between risks
connections = [
    {
        'source': 'P0',
        'target': 'P1',
        'value': 0.9,  # Connection strength
        'label': 'EVM Support Enables Market Expansion'
    },
    {
        'source': 'P0',
        'target': 'P2',
        'value': 0.8,
        'label': 'Multi-Agency Enables Market Expansion'
    },
    {
        'source': 'P1',
        'target': 'P2',
        'value': 0.7,
        'label': 'EVM Support Enables Multi-Agency'
    }
]


def export_to_bubblemaps_json():
    """
    Export to JSON format compatible with bubblemaps.io
    
    Bubblemaps typically expects:
    - nodes: array of objects with id, label, value/size
    - links: array of connections with source, target
    """
    output = {
        'nodes': [],
        'links': []
    }
    
    # Add nodes (risks)
    for risk in risks_data:
        node = {
            'id': risk['id'],
            'label': risk['label'],
            'value': risk['value'],
            'size': risk['size'],
            'category': risk['category'],
            'confidence': risk['confidence'],
            'description': risk['description'],
            'color': risk['color']
        }
        output['nodes'].append(node)
    
    # Add links (connections)
    for conn in connections:
        link = {
            'source': conn['source'],
            'target': conn['target'],
            'value': conn['value'],
            'label': conn['label']
        }
        output['links'].append(link)
    
    return output


def export_to_csv():
    """
    Export to CSV format (alternative format for bubblemaps.io)
    """
    # Nodes CSV
    nodes_csv = []
    for risk in risks_data:
        nodes_csv.append({
            'id': risk['id'],
            'label': risk['label'],
            'value': risk['value'],
            'size': risk['size'],
            'category': risk['category'],
            'confidence': risk['confidence'],
            'color': risk['color']
        })
    
    # Links CSV
    links_csv = []
    for conn in connections:
        links_csv.append({
            'source': conn['source'],
            'target': conn['target'],
            'value': conn['value'],
            'label': conn['label']
        })
    
    return nodes_csv, links_csv


def main():
    """Export data for bubblemaps.io"""
    output_dir = 'examples/intelligence_audits'
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Export JSON format
    json_data = export_to_bubblemaps_json()
    json_path = os.path.join(output_dir, 'ethereum_risks_bubblemaps.json')
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"✅ JSON export saved to: {json_path}")
    
    # Export CSV format
    nodes_csv, links_csv = export_to_csv()
    
    nodes_path = os.path.join(output_dir, 'ethereum_risks_nodes.csv')
    with open(nodes_path, 'w', newline='') as f:
        if nodes_csv:
            writer = csv.DictWriter(f, fieldnames=nodes_csv[0].keys())
            writer.writeheader()
            writer.writerows(nodes_csv)
    print(f"✅ Nodes CSV saved to: {nodes_path}")
    
    links_path = os.path.join(output_dir, 'ethereum_risks_links.csv')
    with open(links_path, 'w', newline='') as f:
        if links_csv:
            writer = csv.DictWriter(f, fieldnames=links_csv[0].keys())
            writer.writeheader()
            writer.writerows(links_csv)
    print(f"✅ Links CSV saved to: {links_path}")
    
    # Create instructions file
    instructions = f"""# Using Ethereum Risk Data with Bubblemaps.io

## Quick Start

1. Go to https://v2.bubblemaps.io/
2. Upload the data files:
   - **Nodes:** `ethereum_risks_nodes.csv`
   - **Links:** `ethereum_risks_links.csv`
   - OR use the JSON file: `ethereum_risks_bubblemaps.json`

## Data Structure

### Nodes (Risks)
- **P0:** Chain-Agnostic Architecture (92% - Critical)
- **P1:** Ethereum Integration (88% - High)
- **P2:** Multi-Agency Deployment (75% - Medium)

### Links (Relationships)
- P0 ↔ P1: EVM Support Enables Market Expansion
- P0 ↔ P2: Multi-Agency Enables Market Expansion
- P1 ↔ P2: EVM Support Enables Multi-Agency

## Customization

In bubblemaps.io, you can:
- Adjust bubble sizes based on 'value' or 'size' field
- Color-code by 'category' (Critical/High/Medium)
- Show/hide connection lines
- Add labels and descriptions

## Files Generated

- `ethereum_risks_bubblemaps.json` - Complete data in JSON format
- `ethereum_risks_nodes.csv` - Node data (risks)
- `ethereum_risks_links.csv` - Link data (connections)
"""
    
    instructions_path = os.path.join(output_dir, 'BUBBLEMAPS_INSTRUCTIONS.md')
    with open(instructions_path, 'w') as f:
        f.write(instructions)
    print(f"✅ Instructions saved to: {instructions_path}")
    
    print("\n📊 Data ready for bubblemaps.io!")
    print("   Visit: https://v2.bubblemaps.io/")
    print("   Upload the JSON or CSV files to create interactive visualization")


if __name__ == "__main__":
    main()

