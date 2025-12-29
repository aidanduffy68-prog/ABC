"""
Generate PNG Visual: Scoring Primitives Examples
Shows actual scoring primitives that become verifiable
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import json

def generate_scoring_primitive_visual(output_path="nemesis/on_chain_receipt/scoring_primitive_example.png"):
    """Generate visual showing example scoring primitives"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    
    # Title
    ax.text(5, 9.2, 'VERIFIABLE SCORING PRIMITIVES', 
            ha='center', va='center', fontsize=32, fontweight='bold', color='#00ff88')
    ax.text(5, 8.5, 'Example: Risk Scores, Behavioral Signatures, Threat Assessments', 
            ha='center', va='center', fontsize=14, color='#ffffff', alpha=0.8)
    
    # Left side - Scoring Primitives (what gets verified) - Using blue color scheme
    left_box = FancyBboxPatch((0.5, 2), 4, 6, 
                              boxstyle="round,pad=0.4",
                              edgecolor='#00aaff', linewidth=3,
                              facecolor='#001a2e', alpha=0.8)
    ax.add_patch(left_box)
    
    ax.text(2.5, 7.5, 'SCORING PRIMITIVES', ha='center', va='center',
            fontsize=18, fontweight='bold', color='#00aaff')
    
    # Example 1: Risk Score
    risk_box = FancyBboxPatch((0.7, 5.8), 3.6, 1,
                              boxstyle="round,pad=0.2",
                              edgecolor='#00aaff', linewidth=2,
                              facecolor='#002d4d', alpha=0.6)
    ax.add_patch(risk_box)
    ax.text(0.9, 6.3, 'Overall Risk Score', ha='left', va='center',
            fontsize=12, color='#ffffff')
    ax.text(4.1, 6.3, '0.94', ha='right', va='center',
            fontsize=20, fontweight='bold', color='#00aaff')
    
    # Example 2: Behavioral Signature
    behavior_box = FancyBboxPatch((0.7, 4.5), 3.6, 1,
                                  boxstyle="round,pad=0.2",
                                  edgecolor='#00aaff', linewidth=2,
                                  facecolor='#002d4d', alpha=0.6)
    ax.add_patch(behavior_box)
    ax.text(0.9, 5.0, 'Risk Tolerance', ha='left', va='center',
            fontsize=12, color='#ffffff')
    ax.text(4.1, 5.0, '0.95', ha='right', va='center',
            fontsize=20, fontweight='bold', color='#00aaff')
    
    # Example 3: Threat Assessment
    threat_box = FancyBboxPatch((0.7, 3.2), 3.6, 1,
                                boxstyle="round,pad=0.2",
                                edgecolor='#00aaff', linewidth=2,
                                facecolor='#002d4d', alpha=0.6)
    ax.add_patch(threat_box)
    ax.text(0.9, 3.7, 'Threat Confidence', ha='left', va='center',
            fontsize=12, color='#ffffff')
    ax.text(4.1, 3.7, '0.89', ha='right', va='center',
            fontsize=20, fontweight='bold', color='#00aaff')
    
    # Arrow
    arrow = FancyArrowPatch((4.5, 5), (5.5, 5),
                            arrowstyle='->', mutation_scale=40,
                            color='#00aaff', linewidth=4,
                            zorder=10)
    ax.add_patch(arrow)
    
    # Right side - Cryptographic Receipt (verifiable proof)
    right_box = FancyBboxPatch((5.5, 2), 4, 6,
                               boxstyle="round,pad=0.4",
                               edgecolor='#00aaff', linewidth=3,
                               facecolor='#001a2e', alpha=0.8)
    ax.add_patch(right_box)
    
    ax.text(7.5, 7.5, 'CRYPTOGRAPHIC RECEIPT', ha='center', va='center',
            fontsize=18, fontweight='bold', color='#00aaff')
    ax.text(7.5, 7, 'On-Chain Proof', ha='center', va='center',
            fontsize=12, color='#ffffff', alpha=0.7)
    
    # Receipt content
    receipt_items = [
        ('Hash:', '9c9832a491bf0edf...'),
        ('Timestamp:', '2025-11-18T17:43:55'),
        ('Signature:', '601da71bd61c1d2...'),
        ('Actor ID:', 'LAZARUS_GROUP'),
        ('Threat Level:', 'critical')
    ]
    
    y_start = 6.2
    for i, (label, value) in enumerate(receipt_items):
        ax.text(7.5, y_start - i*0.5, f'{label} {value}', 
                ha='center', va='center',
                fontsize=10, color='#ffffff', alpha=0.9,
                family='monospace')
    
    # Verification checkmark
    check_circle = plt.Circle((7.5, 3.5), 0.5, 
                             facecolor='#00ff88', edgecolor='#ffffff', 
                             linewidth=2, zorder=11)
    ax.add_patch(check_circle)
    ax.text(7.5, 3.5, '✓', ha='center', va='center',
            fontsize=24, fontweight='bold', color='#0a0a0a')
    ax.text(7.5, 2.8, 'VERIFIABLE', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#00ff88')
    
    # Bottom message
    message_box = FancyBboxPatch((1, 0.8), 8, 0.8,
                                 boxstyle="round,pad=0.3",
                                 edgecolor='#00ff88', linewidth=2,
                                 facecolor='#001a0d', alpha=0.6)
    ax.add_patch(message_box)
    
    ax.text(5, 1.3, 'All scoring primitives are cryptographically verifiable', 
            ha='center', va='center',
            fontsize=16, fontweight='bold', color='#00ff88')
    ax.text(5, 0.9, 'Trust without exposure', 
            ha='center', va='center',
            fontsize=12, color='#ffffff', alpha=0.8)
    
    # Footer
    ax.text(5, 0.3, 'GH SYSTEMS', ha='center', va='center',
            fontsize=10, color='#666666', style='italic')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    print(f"✓ Visual saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    output = generate_scoring_primitive_visual()
    print(f"\n✓ Scoring primitive example visual generated: {output}")

