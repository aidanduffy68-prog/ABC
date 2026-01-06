#!/usr/bin/env python3
"""
GH Systems ABC - Software Bill of Materials (SBOM) Generator
Generates SBOM in SPDX format for AI system components

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_python_packages() -> List[Dict[str, Any]]:
    """Get installed Python packages and versions"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        return [
            {
                'name': pkg['name'],
                'version': pkg['version'],
                'type': 'python-package'
            }
            for pkg in packages
        ]
    except Exception as e:
        print(f"Warning: Could not get Python packages: {e}", file=sys.stderr)
        return []


def get_ai_components() -> List[Dict[str, Any]]:
    """Get AI-specific components"""
    return [
        {
            'name': 'ABC Compilation Engine',
            'version': '1.0.0',
            'type': 'ai-component',
            'description': 'HADES → ECHO → NEMESIS pipeline for threat intelligence compilation',
            'location': 'src/core/nemesis/compilation_engine.py',
            'ai_techniques': ['machine_learning', 'behavioral_profiling', 'network_analysis', 'predictive_modeling']
        },
        {
            'name': 'HADES Behavioral Profiler',
            'version': '1.0.0',
            'type': 'ai-component',
            'description': 'Behavioral risk scoring and profiling engine',
            'location': 'src/core/hades/',
            'ai_techniques': ['machine_learning', 'behavioral_analysis']
        },
        {
            'name': 'ECHO Coordination Detector',
            'version': '1.0.0',
            'type': 'ai-component',
            'description': 'Network coordination and relationship detection',
            'location': 'src/core/echo/',
            'ai_techniques': ['graph_analysis', 'network_analysis']
        },
        {
            'name': 'NEMESIS Predictive Model',
            'version': '1.0.0',
            'type': 'ai-component',
            'description': 'Predictive threat forecasting and targeting',
            'location': 'src/core/nemesis/',
            'ai_techniques': ['predictive_modeling', 'threat_forecasting']
        },
        {
            'name': 'AI Ontology System',
            'version': '1.0.0',
            'type': 'ai-component',
            'description': 'Semantic understanding and entity extraction',
            'location': 'src/core/nemesis/ai_ontology/',
            'ai_techniques': ['natural_language_processing', 'entity_extraction']
        }
    ]


def generate_spdx_sbom(packages: List[Dict], ai_components: List[Dict]) -> Dict[str, Any]:
    """Generate SPDX format SBOM"""
    spdx_id = f"SPDXRef-DOCUMENT-{datetime.now().strftime('%Y%m%d')}"
    
    sbom = {
        'spdxVersion': 'SPDX-2.3',
        'dataLicense': 'CC0-1.0',
        'SPDXID': spdx_id,
        'name': 'GH Systems ABC - Software Bill of Materials',
        'documentNamespace': f'https://github.com/aidanduffy68-prog/ABC/sbom/{datetime.now().isoformat()}',
        'creationInfo': {
            'created': datetime.now().isoformat() + 'Z',
            'creators': [
                'Tool: GH Systems ABC SBOM Generator',
                'Organization: GH Systems'
            ]
        },
        'packages': [],
        'relationships': []
    }
    
    # Add Python packages
    for i, pkg in enumerate(packages):
        pkg_id = f"SPDXRef-Package-{i+1}"
        sbom['packages'].append({
            'SPDXID': pkg_id,
            'name': pkg['name'],
            'versionInfo': pkg['version'],
            'downloadLocation': 'NOASSERTION',
            'filesAnalyzed': False,
            'packageVerificationCode': {
                'packageVerificationCodeValue': 'NOASSERTION'
            }
        })
        sbom['relationships'].append({
            'spdxElementId': spdx_id,
            'relationshipType': 'DESCRIBES',
            'relatedSpdxElement': pkg_id
        })
    
    # Add AI components
    for i, component in enumerate(ai_components):
        comp_id = f"SPDXRef-AIComponent-{i+1}"
        sbom['packages'].append({
            'SPDXID': comp_id,
            'name': component['name'],
            'versionInfo': component['version'],
            'description': component['description'],
            'downloadLocation': 'NOASSERTION',
            'filesAnalyzed': False,
            'externalRefs': [
                {
                    'referenceCategory': 'OTHER',
                    'referenceType': 'AI_TECHNIQUES',
                    'referenceLocator': ','.join(component.get('ai_techniques', []))
                }
            ]
        })
        sbom['relationships'].append({
            'spdxElementId': spdx_id,
            'relationshipType': 'DESCRIBES',
            'relatedSpdxElement': comp_id
        })
    
    return sbom


def generate_cyclonedx_sbom(packages: List[Dict], ai_components: List[Dict]) -> Dict[str, Any]:
    """Generate CycloneDX format SBOM"""
    return {
        'bomFormat': 'CycloneDX',
        'specVersion': '1.5',
        'version': 1,
        'metadata': {
            'timestamp': datetime.now().isoformat() + 'Z',
            'tools': [
                {
                    'vendor': 'GH Systems',
                    'name': 'ABC SBOM Generator',
                    'version': '1.0.0'
                }
            ],
            'component': {
                'type': 'application',
                'name': 'GH Systems ABC',
                'version': '1.0.0',
                'description': 'Truth verification for post-AGI intelligence'
            }
        },
        'components': [
            {
                'type': 'library',
                'name': pkg['name'],
                'version': pkg['version']
            }
            for pkg in packages
        ] + [
            {
                'type': 'application',
                'name': comp['name'],
                'version': comp['version'],
                'description': comp['description'],
                'properties': [
                    {
                        'name': 'ai_techniques',
                        'value': ','.join(comp.get('ai_techniques', []))
                    },
                    {
                        'name': 'location',
                        'value': comp.get('location', '')
                    }
                ]
            }
            for comp in ai_components
        ]
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Software Bill of Materials (SBOM) for GH Systems ABC'
    )
    parser.add_argument(
        '--format',
        choices=['spdx', 'cyclonedx', 'json', 'all'],
        default='all',
        help='SBOM format (default: all)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: sbom.{format}.json)'
    )
    
    args = parser.parse_args()
    
    print("Generating SBOM for GH Systems ABC...")
    print("=" * 60)
    
    # Collect components
    packages = get_python_packages()
    ai_components = get_ai_components()
    
    print(f"Found {len(packages)} Python packages")
    print(f"Found {len(ai_components)} AI components")
    print("=" * 60)
    
    # Generate SBOMs
    formats_to_generate = ['spdx', 'cyclonedx', 'json'] if args.format == 'all' else [args.format]
    
    for fmt in formats_to_generate:
        if fmt == 'spdx':
            sbom = generate_spdx_sbom(packages, ai_components)
            output_file = args.output or 'sbom.spdx.json'
        elif fmt == 'cyclonedx':
            sbom = generate_cyclonedx_sbom(packages, ai_components)
            output_file = args.output or 'sbom.cyclonedx.json'
        else:  # json (simple format)
            sbom = {
                'generated': datetime.now().isoformat() + 'Z',
                'tool': 'GH Systems ABC SBOM Generator v1.0.0',
                'packages': packages,
                'ai_components': ai_components
            }
            output_file = args.output or 'sbom.json'
        
        # Write output
        with open(output_file, 'w') as f:
            json.dump(sbom, f, indent=2)
        
        print(f"✅ Generated {fmt.upper()} SBOM: {output_file}")
    
    print("=" * 60)
    print("SBOM generation complete!")
    print("\nFor AI-specific components, see 'ai_components' section.")
    print("This SBOM includes all AI models, techniques, and dependencies.")


if __name__ == '__main__':
    main()

