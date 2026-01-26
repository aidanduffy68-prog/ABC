# Scripts Directory

This directory contains utility scripts for GH Systems ABC.

## Core Scripts

### Setup & Configuration
- **setup_foundry_aip.py** - Setup and verify Foundry AIP configuration
- **start_api.sh** - Start the ABC API server

### Data Generation & Verification
- **generate_synthetic_compliance_data.py** - Generate synthetic compliance data for training
- **verify_foundry_hashes.py** - Verify Foundry pipeline hashes match ABC-generated hashes

### Foundry Integration
- **foundry_transform_code.py** - Foundry transform code template
- **foundry_transform_template.py** - Foundry transform template
- **foundry_hades_echo_nemesis_transform.py** - Hades/Echo/Nemesis compilation transform

### Quick Demo
- **instant_demo.sh** - One-command demo script

### Visualization (`scripts/visualization/`)
- **generate_sbom.py** - Generate Software Bill of Materials
- **export_to_foundry.py** - Export data to Palantir Foundry
- **create_foundry_chain_diagram.py** - Create Foundry chain diagram
- **generate_ethereum_risk_bubblemap.py** - Ethereum risk bubble map generator
- **export_risks_to_bubblemaps.py** - Export risks to bubblemaps.io format
- **create_interactive_bubblemap.html** - Interactive bubble map HTML

## Usage

### Setup Foundry AIP
```bash
python scripts/setup_foundry_aip.py
```

### Generate Synthetic Data
```bash
python scripts/generate_synthetic_compliance_data.py --count 100
```

### Verify Foundry Hashes
```bash
python scripts/verify_foundry_hashes.py
```

### Quick Demo
```bash
bash scripts/instant_demo.sh
```

### Start API Server
```bash
bash scripts/start_api.sh
```
