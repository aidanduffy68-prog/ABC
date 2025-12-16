# Repository Structure

**Clean, organized structure optimized for Foundry Chain integration and production deployment.**

```
ABC/
├── docs/              # 📚 Documentation (architecture, security, sales)
│   ├── assets/        # Static assets (logos, images)
│   ├── architecture/  # Architecture specifications
│   ├── integrations/  # Integration specs (Foundry Chain)
│   ├── security/      # Security documentation and tests
│   └── sales/         # Sales and strategy docs
│
├── examples/          # 🎯 Intelligence audits & demos
│   └── intelligence_audits/  # Threat intelligence compilations
│
├── k8s/               # ☸️ Kubernetes manifests (production)
│   ├── api-deployment.yaml
│   ├── configmap.yaml
│   ├── ingress.yaml
│   ├── namespace.yaml
│   ├── neo4j-deployment.yaml
│   ├── postgres-deployment.yaml
│   ├── redis-deployment.yaml
│   └── secrets.yaml.example
│
├── scripts/           # 🛠️ Dev utilities & demos
│   ├── visualization/ # Visualization generation scripts
│   ├── instant_demo.sh
│   └── README.md
│
├── src/               # 💻 Source code
│   ├── api/           # FastAPI application
│   │   └── routes/    # API endpoints (ingest, foundry, agency, status)
│   ├── cli/           # Production CLI tools
│   │   ├── compile_intelligence.py
│   │   ├── analyze_atlas_threats.py
│   │   └── run_api_server.py
│   ├── core/          # Hades/Echo/Nemesis (your IP)
│   │   ├── hades/     # Risk profiling
│   │   ├── echo/      # Network analysis
│   │   ├── hypnos/    # Long-term memory
│   │   ├── nemesis/   # Compilation engine
│   │   │   └── foundry_integration/  # Foundry Chain integration
│   │   ├── middleware/ # API middleware (auth, rate limiting, caching)
│   │   ├── security/   # Security utilities
│   │   └── validation/ # Validation agents
│   ├── consensus/     # Multi-agency consensus engine
│   ├── graph/         # Graph processing
│   ├── ingestion/     # Data ingestion
│   ├── integrations/  # External integrations
│   │   ├── agency/    # Agency integration framework
│   │   └── foundry/   # Foundry connector
│   ├── schemas/       # Pydantic schemas
│   └── settlements/   # Settlement layer
│
├── tests/             # ✅ Test suite
│   ├── api/           # API endpoint tests
│   ├── integrations/  # Integration tests
│   │   └── foundry/   # Foundry connector tests
│   └── test_cryptographic_receipts.py
│
├── docker-compose.yml # 🐳 Local development
├── Dockerfile         # 📦 Production container
├── requirements.txt   # 📋 All dependencies (consolidated)
└── README.md          # 📖 Start here
```

---

## Core Integration: Foundry Chain

**Primary Integration:** `src/core/nemesis/foundry_integration/`
- Foundry Connector — API integration
- Compilation Validator — Data validation
- Data Mapper — Format conversion
- Foundry Integration — Workflow orchestration

**Agency Framework:** `src/integrations/agency/`
- Agency Connector — Generic framework
- Assessment Validator — Assessment validation
- Consensus Engine — Conflict resolution

**Consensus Engine:** `src/consensus/`
- Multi-agency consensus calculation
- Outlier detection
- Mathematical consensus recommendations

**Documentation:** `docs/integrations/`
- Foundry Chain Specification — Complete architecture
- Foundry Chain Visual — Visual diagrams and workflows
- Foundry Integration Guide — Technical details

---

## Quick Reference

### Getting Started
```bash
# Install dependencies
pip install -r requirements.txt

# Run demo
bash scripts/instant_demo.sh

# Run API server
python -m src.cli.run_api_server

# Compile intelligence
python -m src.cli.compile_intelligence --help
```

### Development
```bash
# Local development with Docker
docker-compose up

# Run tests
pytest tests/

# Kubernetes deployment
kubectl apply -f k8s/
```

### Documentation
- **[Architecture Spec](docs/architecture/ARCHITECTURE_SPEC.md)** — Full technical specification
- **[Foundry Chain Spec](docs/integrations/FOUNDRY_CHAIN_SPEC.md)** — Foundry integration details
- **[Security Docs](docs/security/README.md)** — Security audit and configuration
- **[Getting Started](GETTING_STARTED.md)** — Quick start guide

---

## Key Simplifications

1. **Consolidated Docker** — Single Dockerfile and docker-compose.yml at root
2. **Consolidated Requirements** — Single requirements.txt with optional extras
3. **Organized Assets** — All static assets in docs/assets/
4. **Standard Kubernetes** — k8s/ directory (standard convention)
5. **Separated CLI** — Production CLI tools in src/cli/
6. **Organized Tests** — All tests in tests/ directory
7. **Consolidated Security** — All security docs in docs/security/

---

*GH Systems — Compiling behavioral bytecode so lawful actors win the economic battlefield.*
