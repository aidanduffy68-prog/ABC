#!/usr/bin/env python3
"""
Generate risk score breakdown bar chart for CIA Supply Chain Intelligence Audit
Similar to Treasury and DoW risk visualizations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Risk scores from CIA Supply Chain Intelligence Audit (Critical only: 85%+)
categories = [
    "Critical Minerals",
    "Rare Earth Processing",
    "Semiconductors"
]

risk_scores = [88, 87, 85]  # Percentages (Critical risk surfaces only)

# Create figure with transparent background
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_alpha(0)  # Transparent background
ax.set_facecolor('white')

# Color scheme: grey and green (all critical, so darker green)
colors = ['#2d5016' for score in risk_scores]  # All critical, use darker green

# Create horizontal bar chart
y_pos = np.arange(len(categories))
bars = ax.barh(y_pos, risk_scores, color=colors, height=0.6, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for i, (bar, score) in enumerate(zip(bars, risk_scores)):
    width = bar.get_width()
    ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
            f'{score}%', 
            ha='left', va='center', 
            fontsize=11, fontweight='bold', color='black')

# Customize axes
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=11, fontweight='bold')
ax.set_xlabel('Risk Score (%)', fontsize=12, fontweight='bold', color='black')
ax.set_xlim(0, 100)
ax.set_xticks(range(0, 101, 10))
ax.set_xticklabels([f'{i}%' for i in range(0, 101, 10)], fontsize=10)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('black')
ax.spines['left'].set_color('black')

# Add title
ax.set_title('CIA Supply Chain Intelligence: Critical Risk Surfaces', 
             fontsize=14, fontweight='bold', color='black', pad=20)

# Add grid for readability
ax.grid(axis='x', alpha=0.3, linestyle='--', color='gray')
ax.set_axisbelow(True)

# Invert y-axis so highest risk is at top
ax.invert_yaxis()

# Adjust layout
plt.tight_layout()

# Save with transparent background
output_path = 'Deal Room/Assets/cia_supply_chain_risk_score_breakdown.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', transparent=True, facecolor='white')
print(f"✅ Bar chart saved to: {output_path}")

plt.close()

