# Repository Structure

This document describes the organized structure of the GH Systems ABC repository.

## Directory Structure

```
USD_FRY/
├── assets/                    # Static assets
│   ├── images/                # Images, diagrams, logos
│   └── visualizations/        # Visualization generation scripts
│
├── docs/                      # Documentation
│   ├── architecture/          # Architecture specifications
│   ├── security/              # Security documentation
│   ├── sales/                 # Sales and strategy docs
│   ├── deployment/            # Deployment guides
│   └── README.md              # Documentation index
│
├── examples/                  # Examples and demos
│   ├── intelligence_audits/   # Threat intelligence compilations
│   ├── QUICK_DEMO.md          # Quick demo guide
│   └── ECONOMIC_SECURITY_USE_CASES.md
│
├── kubernetes/                 # Kubernetes manifests
│   ├── api-deployment.yaml
│   ├── postgres-deployment.yaml
│   ├── neo4j-deployment.yaml
│   ├── redis-deployment.yaml
│   ├── ingress.yaml
│   └── README.md
│
├── scripts/                   # Utility scripts
│   ├── tests/                 # Test scripts
│   ├── visualization/         # Visualization scripts
│   ├── deployment/            # Deployment scripts
│   ├── compile_intelligence.py
│   ├── instant_demo.sh
│   └── README.md
│
├── security/                  # Security documentation and tests
│   ├── RED_TEAM_TEST_SUITE.py
│   ├── SECURITY_AUDIT_REPORT.md
│   └── README.md
│
├── src/                       # Source code
│   ├── api/                   # FastAPI application
│   ├── core/                  # Core systems
│   │   ├── hades/             # Risk profiling
│   │   ├── echo/              # Network analysis
│   │   ├── hypnos/            # Long-term memory
│   │   ├── nemesis/           # Compilation engine
│   │   ├── middleware/        # API middleware
│   │   ├── security/          # Security utilities
│   │   └── validation/       # Validation agents
│   ├── graph/                 # Graph processing
│   ├── ingestion/             # Data ingestion
│   ├── integrations/          # External integrations
│   ├── schemas/               # Pydantic schemas
│   └── settlements/           # Settlement layer
│
├── tests/                     # Test suite
│   └── test_cryptographic_receipts.py
│
├── Dockerfile                 # Main API container
├── docker-compose.yml         # Local development
├── requirements.txt           # Python dependencies
├── requirements-vector.txt   # Vector DB dependencies
├── README.md                  # Main README
├── GETTING_STARTED.md         # Quick start guide
└── GLOSSARY.md                # Terminology
```

## Key Changes from Reorganization

### 1. Assets Organization
- **Before:** `Deal Room/Assets/` scattered files
- **After:** `assets/images/` and `assets/visualizations/`
- All images and visualization scripts now in dedicated folders

### 2. Documentation Organization
- **Before:** All docs in `docs/` root
- **After:** Organized into subdirectories:
  - `docs/architecture/` - System architecture specs
  - `docs/security/` - Security and cryptography docs
  - `docs/sales/` - Sales strategy and positioning
  - `docs/deployment/` - Deployment and integration guides

### 3. Scripts Organization
- **Before:** All scripts in `scripts/` root
- **After:** Organized into subdirectories:
  - `scripts/tests/` - Test scripts
  - `scripts/visualization/` - Chart/graph generators
  - `scripts/deployment/` - Deployment utilities

### 4. Source Code Cleanup
- Removed scattered README files from `src/core/nemesis/`
- Consolidated into `docs/architecture/`
- Maintained component-specific READMEs where needed

### 5. Test Organization
- Moved `test_verification_results.json` to `tests/`
- All test files now in `tests/` or `scripts/tests/`

## File Path Updates

If you have scripts or documentation that reference old paths, update them:

### Documentation References
- `docs/ARCHITECTURE_SPEC.md` → `docs/architecture/ARCHITECTURE_SPEC.md`
- `docs/CRYPTOGRAPHY_AUDIT_INSIGHTS.md` → `docs/security/CRYPTOGRAPHY_AUDIT_INSIGHTS.md`
- `docs/GOVERNMENT_SALES_STRATEGY.md` → `docs/sales/GOVERNMENT_SALES_STRATEGY.md`
- `docs/FOUNDRY_INTEGRATION.md` → `docs/deployment/FOUNDRY_INTEGRATION.md`

### Script References
- `scripts/test_*.py` → `scripts/tests/test_*.py`
- `scripts/generate_*.py` → `scripts/visualization/generate_*.py`
- `scripts/export_*.py` → `scripts/visualization/export_*.py`
- `scripts/run_api_server.py` → `scripts/deployment/run_api_server.py`

### Asset References
- `Deal Room/Assets/*.png` → `assets/images/*.png`
- `Deal Room/*.py` → `assets/visualizations/*.py`

## Benefits

1. **Clearer Organization** - Related files grouped together
2. **Easier Navigation** - Logical directory structure
3. **Better Scalability** - Easy to add new files in right places
4. **Investor-Friendly** - Professional structure for due diligence
5. **Maintainability** - Easier to find and update files

## Next Steps

1. Update any hardcoded paths in scripts
2. Update documentation links
3. Update CI/CD paths if needed
4. Verify all imports still work

