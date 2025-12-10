# Scripts Directory

This directory contains utility scripts for GH Systems ABC.

## Structure

### Core Scripts
- **compile_intelligence.py** - Main intelligence compilation script
- **instant_demo.sh** - One-command demo script
- **generate_sbom.py** - Generate Software Bill of Materials
- **analyze_atlas_threats.py** - MITRE ATLAS threat analysis
- **export_to_foundry.py** - Export data to Palantir Foundry

### Tests (`scripts/tests/`)
- **test_intelligence_verification.py** - Cryptographic receipt verification tests
- **test_validation_agents.py** - Validation agents test suite
- **test_vector_integration.py** - Vector database integration tests

### Visualization (`scripts/visualization/`)
- **generate_ethereum_risk_bubblemap.py** - Ethereum risk bubble map generator
- **export_risks_to_bubblemaps.py** - Export risks to bubblemaps.io format
- **create_interactive_bubblemap.html** - Interactive bubble map HTML

### Deployment (`scripts/deployment/`)
- **run_api_server.py** - Run FastAPI server locally

## Usage

### Quick Demo
```bash
bash scripts/instant_demo.sh
```

### Compile Intelligence
```bash
python3 scripts/compile_intelligence.py --target "Department of War" --blockchain ethereum
```

### Run Tests
```bash
python3 scripts/tests/test_validation_agents.py
python3 scripts/tests/test_vector_integration.py
python3 scripts/tests/test_intelligence_verification.py
```

### Generate Visualizations
```bash
python3 scripts/visualization/generate_ethereum_risk_bubblemap.py
```

### Run API Server
```bash
python3 scripts/deployment/run_api_server.py
```
