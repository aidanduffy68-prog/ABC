# Repository Structure

Simplified structure emphasizing **Foundry Chain** as the core integration.

## Directory Structure

```
USD_FRY/
├── docs/                      # Documentation
│   ├── assets/               # Static assets (logos, images)
│   ├── architecture/         # Architecture specifications
│   ├── integrations/         # Integration specs (Foundry Chain)
│   ├── security/             # Security documentation and tests
│   └── sales/                # Sales and strategy docs
│
├── examples/                  # Examples and demos
│   └── intelligence_audits/  # Threat intelligence compilations
│
├── k8s/                       # Kubernetes manifests (standard convention)
│
├── scripts/                   # Utility scripts (visualization, demos)
│   └── visualization/        # Visualization generation scripts
│
├── src/                       # Source code
│   ├── api/                  # FastAPI application
│   ├── core/                 # Core systems
│   │   ├── hades/            # Risk profiling
│   │   ├── echo/             # Network analysis
│   │   ├── hypnos/           # Long-term memory
│   │   ├── nemesis/          # Compilation engine
│   │   │   └── foundry_integration/  # Foundry Chain integration
│   │   ├── middleware/       # API middleware
│   │   ├── security/         # Security utilities
│   │   └── validation/       # Validation agents
│   ├── graph/                # Graph processing
│   ├── ingestion/            # Data ingestion
│   ├── integrations/         # External integrations
│   │   └── agency/           # Agency integration framework
│   ├── schemas/              # Pydantic schemas
│   └── settlements/          # Settlement layer
│
├── tests/                     # Test suite
│
├── Dockerfile                 # Consolidated Dockerfile
├── docker-compose.yml         # Consolidated docker-compose
├── requirements.txt           # Consolidated requirements (core + optional extras)
├── README.md                  # Main README
└── GETTING_STARTED.md         # Quick start guide
```

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

**Documentation:** `docs/integrations/`
- Foundry Chain Specification — Complete architecture
- Foundry Integration Guide — Technical details

## Key Simplifications

1. **Removed visual assets** — Only logo retained
2. **Removed Deal Room** — No longer needed
3. **Consolidated integrations** — Foundry Chain is primary focus
4. **Simplified docs** — Emphasis on Foundry Chain integration
