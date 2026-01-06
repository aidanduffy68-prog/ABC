#!/usr/bin/env python3
"""
Export Capability Data to Bubblemaps.io Format
Creates data files compatible with bubblemaps.io platform

NOTE: These are ABC's capabilities, NOT risks of blockchain implementations

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import json
import csv
from typing import List, Dict, Any

# Top 3 capabilities from Ethereum audit
# These represent ABC's capabilities, not risks of blockchain implementations
capabilities_data = [
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
    
    # Add nodes (capabilities)
    for cap in capabilities_data:
        node = {
            'id': cap['id'],
            'label': cap['label'],
            'value': cap['value'],
            'size': cap['size'],
            'category': cap['category'],
            'confidence': cap['confidence'],
            'description': cap['description'],
            'color': cap['color']
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
    for cap in capabilities_data:
        nodes_csv.append({
            'id': cap['id'],
            'label': cap['label'],
            'value': cap['value'],
            'size': cap['size'],
            'category': cap['category'],
            'confidence': cap['confidence'],
            'color': cap['color']
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
    json_path = os.path.join(output_dir, 'ethereum_capabilities_bubblemaps.json')
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"✅ JSON export saved to: {json_path}")
    
    # Export CSV format
    nodes_csv, links_csv = export_to_csv()
    
    nodes_path = os.path.join(output_dir, 'ethereum_capabilities_nodes.csv')
    with open(nodes_path, 'w', newline='') as f:
        if nodes_csv:
            writer = csv.DictWriter(f, fieldnames=nodes_csv[0].keys())
            writer.writeheader()
            writer.writerows(nodes_csv)
    print(f"✅ Nodes CSV saved to: {nodes_path}")
    
    links_path = os.path.join(output_dir, 'ethereum_capabilities_links.csv')
    with open(links_path, 'w', newline='') as f:
        if links_csv:
            writer = csv.DictWriter(f, fieldnames=links_csv[0].keys())
            writer.writeheader()
            writer.writerows(links_csv)
    print(f"✅ Links CSV saved to: {links_path}")
    
    print("\n📊 Data ready for bubblemaps.io!")
    print("   Visit: https://v2.bubblemaps.io/")
    print("   Upload the JSON or CSV files to create interactive visualization")
    print("\n⚠️  NOTE: These represent ABC's capabilities, NOT risks of blockchain implementations")


if __name__ == "__main__":
    main()

