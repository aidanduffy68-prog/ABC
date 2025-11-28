#!/usr/bin/env python3
"""
Generate Treasury Risk Score Breakdown Visual
Creates a horizontal bar chart showing risk scores by category
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np

# Data
categories = [
    "Financial Intelligence Integration",
    "Sanctions Enforcement Automation",
    "Crypto Compliance Dependencies",
    "Cross-Bureau Coordination Gap"
]

scores = [89, 87, 85, 82]
# Grey and green color scheme - darker grey for higher risk
colors = ['#4A4A4A', '#5A5A5A', '#6A6A6A', '#7A7A7A']  # Dark grey to lighter grey

# Create figure with transparent background
fig, ax = plt.subplots(figsize=(12, 6), facecolor='none')
ax.set_facecolor('none')

# Create horizontal bar chart
y_pos = np.arange(len(categories))
bars = ax.barh(y_pos, scores, color=colors, edgecolor='#00FF00', linewidth=2.5, height=0.6)

# Add percentage labels on bars
for i, (bar, score) in enumerate(zip(bars, scores)):
    width = bar.get_width()
    ax.text(width - 2, bar.get_y() + bar.get_height()/2, 
            f'{score}%', 
            ha='right', va='center', 
            fontsize=14, fontweight='bold', color='#00FF00')

# Set y-axis labels
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=12, color='#333333', fontweight='bold')

# Set x-axis (0-100%)
ax.set_xlim(0, 100)
ax.set_xlabel('Risk Score (%)', fontsize=14, color='#00FF00', fontweight='bold')
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'], color='#333333')

# Critical threshold line removed to avoid warping chart perspective

# Title
ax.set_title('Treasury AI Infrastructure Risk Scores\nOverall Risk Score: 85% (Critical)', 
             fontsize=16, fontweight='bold', color='#00FF00', pad=20)

# Remove top and right spines, color others green
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#00FF00')
ax.spines['left'].set_color('#00FF00')
ax.tick_params(colors='#333333', which='both')

# Add legend with grey and green scheme
critical_patch = mpatches.Patch(facecolor='#4A4A4A', edgecolor='#00FF00', linewidth=2, label='Critical (≥85%)')
high_patch = mpatches.Patch(facecolor='#7A7A7A', edgecolor='#00FF00', linewidth=2, label='High (70-84%)')
legend = ax.legend(handles=[critical_patch, high_patch], loc='lower right', 
          facecolor='white', edgecolor='#00FF00', labelcolor='#333333', fontsize=11)
legend.get_frame().set_alpha(0.9)

# Add grid for readability
ax.grid(True, axis='x', alpha=0.2, color='#00FF00', linestyle=':')
ax.set_axisbelow(True)

# Tight layout
plt.tight_layout()

# Save as PNG with transparent background
output_path = 'Deal Room/Assets/treasury_risk_score_breakdown.png'
plt.savefig(output_path, dpi=300, facecolor='none', transparent=True, bbox_inches='tight')
print(f"Visual saved to: {output_path}")

# Also show it
plt.show()

