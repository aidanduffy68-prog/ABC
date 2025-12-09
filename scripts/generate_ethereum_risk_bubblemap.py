#!/usr/bin/env python3
"""
Generate Bubble Map/Web Visualization for Top 3 Capabilities
Ethereum Chain-Agnostic Architecture Demonstration

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import os

# Set style
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_facecolor('#000000')
fig.patch.set_facecolor('#000000')

# Capability data - Top 3 capabilities from Ethereum audit
# IMPORTANT: These are ABC's capabilities/opportunities, NOT risks of blockchain implementations
# We are demonstrating what ABC CAN DO, not assessing risks of Ethereum/Bitcoin/etc.
capabilities = [
    {
        'id': 'P0',
        'title': 'Chain-Agnostic Architecture\nEnables Market Expansion',
        'capability': 92,
        'confidence': 92,
        'priority': 'Critical',
        'color': '#00FF00',  # Green
        'position': (0, 0),  # Center
        'size': 92
    },
    {
        'id': 'P1',
        'title': 'Ethereum Integration\nDemonstrates EVM Support',
        'capability': 88,
        'confidence': 88,
        'priority': 'High',
        'color': '#90EE90',  # Light green
        'position': (-2, 1.5),  # Top left
        'size': 88
    },
    {
        'id': 'P2',
        'title': 'Multi-Agency Deployment\nScenarios',
        'capability': 75,
        'confidence': 85,
        'priority': 'Medium',
        'color': '#ADFF2F',  # Yellow-green
        'position': (2, 1.5),  # Top right
        'size': 75
    }
]

# Create connections between capabilities (showing relationships)
connections = [
    ('P0', 'P1', 0.9),  # Strong connection
    ('P0', 'P2', 0.8),  # Strong connection
    ('P1', 'P2', 0.7),  # Medium connection
]

# Draw connections first (behind bubbles)
for conn in connections:
    cap1_id, cap2_id, strength = conn
    cap1 = next(c for c in capabilities if c['id'] == cap1_id)
    cap2 = next(c for c in capabilities if c['id'] == cap2_id)
    
    x1, y1 = cap1['position']
    x2, y2 = cap2['position']
    
    # Connection line with alpha based on strength
    line = ConnectionPatch(
        (x1, y1), (x2, y2),
        "data", "data",
        arrowstyle="-",
        shrinkA=cap1['size']/100,
        shrinkB=cap2['size']/100,
        mutation_scale=20,
        fc=cap1['color'],
        ec=cap1['color'],
        alpha=strength * 0.6,
        linewidth=2 * strength,
        zorder=1
    )
    ax.add_patch(line)

# Draw bubbles (capabilities)
for cap in capabilities:
    x, y = cap['position']
    size = cap['size'] * 8  # Scale for visibility
    color = cap['color']
    
    # Main bubble
    circle = plt.Circle(
        (x, y),
        size/100,
        color=color,
        alpha=0.3,
        zorder=2
    )
    ax.add_patch(circle)
    
    # Border
    border = plt.Circle(
        (x, y),
        size/100,
        fill=False,
        edgecolor=color,
        linewidth=3,
        zorder=3
    )
    ax.add_patch(border)
    
    # Text labels
    # Title
    ax.text(
        x, y + size/100 + 0.15,
        cap['title'],
        ha='center',
        va='bottom',
        fontsize=11,
        fontweight='bold',
        color='white',
        zorder=4
    )
    
    # Capability score
    ax.text(
        x, y,
        f"{cap['capability']}%",
        ha='center',
        va='center',
        fontsize=24,
        fontweight='bold',
        color=color,
        zorder=4
    )
    
    # Priority label
    ax.text(
        x, y - size/100 - 0.15,
        f"{cap['priority']} | {cap['confidence']}% Confidence",
        ha='center',
        va='top',
        fontsize=9,
        color='#CCCCCC',
        zorder=4
    )

# Title
ax.text(
    0, 2.5,
    'Top 3 Capabilities\nEthereum Chain-Agnostic Architecture',
    ha='center',
    va='top',
    fontsize=16,
    fontweight='bold',
    color='#00FF00',
    zorder=5
)

# Legend
legend_elements = [
    mpatches.Patch(color='#00FF00', alpha=0.3, label='Critical (P0)'),
    mpatches.Patch(color='#90EE90', alpha=0.3, label='High (P1)'),
    mpatches.Patch(color='#ADFF2F', alpha=0.3, label='Medium (P2)'),
]
ax.legend(handles=legend_elements, loc='lower left', framealpha=0.3, facecolor='black', edgecolor='#00FF00')

# Remove axes
ax.set_xlim(-3.5, 3.5)
ax.set_ylim(-1, 3)
ax.axis('off')

# Save
output_dir = 'examples/intelligence_audits'
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'ethereum_risk_bubblemap.png')
plt.tight_layout()
plt.savefig(output_path, dpi=300, facecolor='black', bbox_inches='tight')
print(f"✅ Bubble map saved to: {output_path}")

plt.close()

