"""
Generate PNG Visual: Verifiable Scoring Primitives
Creates a visual diagram showing off-chain vs on-chain comparison
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import json

def generate_visual_png(output_path="nemesis/on_chain_receipt/verifiable_scoring_visual.png"):
    """Generate PNG visual diagram - Simple and eye-catching"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    
    # Title - Large and bold
    ax.text(5, 9, 'VERIFIABLE SCORING PRIMITIVES', 
            ha='center', va='center', fontsize=32, fontweight='bold', color='#00ff88')
    ax.text(5, 8.3, 'Intelligence Becomes Verifiable Objects', 
            ha='center', va='center', fontsize=16, color='#ffffff', alpha=0.8)
    
    # Off-Chain Box (Left) - Large, bold
    off_chain_box = FancyBboxPatch((0.3, 3), 3.5, 4.5, 
                                    boxstyle="round,pad=0.4",
                                    edgecolor='#00ff88', linewidth=3,
                                    facecolor='#001a0d', alpha=0.8)
    ax.add_patch(off_chain_box)
    
    ax.text(2.05, 7, 'OFF-CHAIN', ha='center', va='center', 
            fontsize=20, fontweight='bold', color='#00ff88')
    ax.text(2.05, 6.5, 'Proprietary', ha='center', va='center', 
            fontsize=12, color='#ffffff', alpha=0.7)
    
    # Large size badge
    size_box1 = FancyBboxPatch((0.5, 3.2), 3.1, 0.8,
                               boxstyle="round,pad=0.2",
                               edgecolor='#00ff88', linewidth=2,
                               facecolor='#003d1a', alpha=0.9)
    ax.add_patch(size_box1)
    ax.text(2.05, 3.6, '2.3 MB', ha='center', va='center',
            fontsize=24, fontweight='bold', color='#00ff88')
    
    # Arrow - Bold and colorful
    arrow = FancyArrowPatch((3.8, 5.5), (6.2, 5.5),
                            arrowstyle='->', mutation_scale=40,
                            color='#00ff88', linewidth=4,
                            zorder=10)
    ax.add_patch(arrow)
    
    # Reduction badge on arrow - make it more visible and clear
    reduction_circle = plt.Circle((5, 5.5), 0.7, facecolor='#ff0066', edgecolor='#ffffff', linewidth=2, zorder=11)
    ax.add_patch(reduction_circle)
    ax.text(5, 5.4, '99.98%', ha='center', va='center',
            fontsize=16, fontweight='bold', color='#ffffff')
    ax.text(5, 5.7, 'REDUCTION', ha='center', va='center',
            fontsize=10, fontweight='bold', color='#ffffff')
    
    # On-Chain Box (Right) - Large, bold
    on_chain_box = FancyBboxPatch((6.2, 3), 3.5, 4.5,
                                   boxstyle="round,pad=0.4",
                                   edgecolor='#00aaff', linewidth=3,
                                   facecolor='#001a2e', alpha=0.8)
    ax.add_patch(on_chain_box)
    
    ax.text(7.95, 7, 'ON-CHAIN', ha='center', va='center',
            fontsize=20, fontweight='bold', color='#00aaff')
    ax.text(7.95, 6.5, 'Verifiable Proof', ha='center', va='center',
            fontsize=12, color='#ffffff', alpha=0.7)
    
    # Small size badge
    size_box2 = FancyBboxPatch((6.4, 3.2), 3.1, 0.8,
                               boxstyle="round,pad=0.2",
                               edgecolor='#00aaff', linewidth=2,
                               facecolor='#002d4d', alpha=0.9)
    ax.add_patch(size_box2)
    ax.text(7.95, 3.6, '400 bytes', ha='center', va='center',
            fontsize=24, fontweight='bold', color='#00aaff')
    
    # Key message - Large and centered
    message_box = FancyBboxPatch((1, 1.5), 8, 1.2,
                                 boxstyle="round,pad=0.3",
                                 edgecolor='#00ff88', linewidth=2,
                                 facecolor='#001a0d', alpha=0.6)
    ax.add_patch(message_box)
    
    ax.text(5, 2.2, 'Scoring Primitives Are Verifiable', ha='center', va='center',
            fontsize=18, fontweight='bold', color='#00ff88')
    ax.text(5, 1.7, 'Trust Without Exposure', ha='center', va='center',
            fontsize=14, color='#ffffff', alpha=0.8)
    
    # Footer
    ax.text(5, 0.5, 'GH SYSTEMS', ha='center', va='center',
            fontsize=12, color='#666666', style='italic')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    print(f"✓ Visual saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    output = generate_visual_png()
    print(f"\n✓ PNG visual generated: {output}")

