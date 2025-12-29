#!/usr/bin/env python3
"""
GH Systems ABC - MITRE ATLAS Threat Analysis
Analyzes system for AI-specific threats using MITRE ATLAS framework

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.shared.security.mitre_atlas import get_atlas_analyzer


def main():
    """Run ATLAS threat analysis"""
    print("=" * 60)
    print("GH Systems ABC - MITRE ATLAS Threat Analysis")
    print("=" * 60)
    print()
    
    analyzer = get_atlas_analyzer()
    
    # Example system state (in production, this would come from monitoring)
    system_state = {
        'model_files': [
            'src/core/nemesis/compilation_engine.py',
            'src/core/hades/',
            'src/core/echo/',
        ],
        'access_logs': [],
        'performance_metrics': {
            'confidence_drop': 0.0,
            'performance_degradation': False,
            'error_rate': 0.0
        },
        'input_patterns': [],
        'security_alerts': []
    }
    
    print("Analyzing system for AI-specific threats...")
    print()
    
    # Analyze system
    threats = analyzer.analyze_system(system_state)
    
    # Generate report
    report = analyzer.get_threat_report()
    
    # Display results
    print(f"Threats Detected: {report['total_threats_detected']}")
    print(f"  Critical: {report['threats_by_severity']['critical']}")
    print(f"  High: {report['threats_by_severity']['high']}")
    print(f"  Medium: {report['threats_by_severity']['medium']}")
    print(f"  Low: {report['threats_by_severity']['low']}")
    print()
    
    if threats:
        print("Detected Threats:")
        print("-" * 60)
        for threat in threats:
            print(f"  [{threat.severity.upper()}] {threat.technique.value}")
            print(f"    Tactic: {threat.tactic.value}")
            print(f"    Description: {threat.description}")
            print()
    else:
        print("✅ No threats detected")
        print()
    
    print("Recommendations:")
    print("-" * 60)
    for rec in report['recommendations']:
        print(f"  • {rec}")
    print()
    
    # Save report
    output_file = 'atlas_threat_report.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Threat report saved to: {output_file}")
    print("=" * 60)


if __name__ == '__main__':
    main()

