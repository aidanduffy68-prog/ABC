# Foundry Pipeline with scenario_forge → ABC → Hades/Echo/Nemesis Integration

**Enhanced Foundry integration that supports scenario_forge artificial data processing**

Copyright (c) 2026 GH Systems. All rights reserved.

---

## Overview

The Foundry pipeline has been enhanced to support the complete workflow:

1. **Foundry compilations** (existing workflow)
2. **scenario_forge artificial data** (new workflow with ABC verification)
3. **ABC verification** before processing
4. **Hades/Echo/Nemesis compilation pipeline**

**ABC verifies inputs, not outputs.** This workflow ensures all data is properly verified before entering the analysis pipeline.

---

## Architecture

```
┌─────────────────┐
│  Foundry Data   │
│  OR             │
│  scenario_forge │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ABC Verification│  ← Checks labeling, intent, provenance
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Hades/Echo/     │
│ Nemesis Pipeline│  ← Behavioral profiling, coordination, threat forecasting
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Compiled        │
│ Intelligence    │  ← With cryptographic receipt
└─────────────────┘
```

---

## Components

### 1. FoundryWorkflow

**Location:** `src/verticals/ai_verification/core/nemesis/foundry_integration/foundry_workflow.py`

Main workflow orchestrator that:
- Processes Foundry compilations
- Processes scenario_forge artificial data
- Performs ABC verification (for scenario_forge)
- Runs Hades/Echo/Nemesis compilation
- Returns compiled intelligence with cryptographic receipts

**Key Methods:**
- `process_foundry_compilation()` - Process Foundry compilation
- `process_scenario_forge_data()` - Process scenario_forge data with ABC verification
- `process_data()` - Auto-detect data type and process

### 2. API Endpoints

**Location:** `src/verticals/ai_verification/api/foundry_workflow_endpoints.py`

**Endpoints:**
- `POST /api/v1/foundry/workflow/process` - Process any data type (auto-detect)
- `POST /api/v1/foundry/workflow/process/foundry` - Process Foundry compilation
- `POST /api/v1/foundry/workflow/process/scenario-forge` - Process scenario_forge data

### 3. Demo Script

**Location:** `scripts/demo_foundry_scenario_forge_workflow.py`

Demonstrates the complete workflow with both Foundry and scenario_forge data.

---

## Usage

### Python API

```python
from src.verticals.ai_verification.core.nemesis.foundry_integration.foundry_workflow import FoundryWorkflow

# Initialize workflow
workflow = FoundryWorkflow(use_aip=False)  # or True for AIP

# Process scenario_forge data
success, compiled, details = workflow.process_scenario_forge_data(
    scenario_data=scenario_dict,
    declared_intent="model_evaluation",
    generate_receipt=True
)

if success:
    print(f"Compilation ID: {compiled.compilation_id}")
    print(f"Confidence: {compiled.confidence_score:.2%}")
    print(f"Time: {compiled.compilation_time_ms:.2f}ms")
```

### REST API

**Process scenario_forge data:**
```bash
curl -X POST "http://localhost:8000/api/v1/foundry/workflow/process/scenario-forge" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "uuid-here",
    "intent": "LAUNDERING",
    "metadata": {"artificial_data": true, "ARTIFICIAL_DATA": true},
    "provenance": {...},
    "transaction_graph": {...}
  }'
```

**Process Foundry compilation:**
```bash
curl -X POST "http://localhost:8000/api/v1/foundry/workflow/process/foundry?compilation_id=foundry-comp-2025-12-15-001" \
  -H "Authorization: Bearer your-token"
```

---

## ABC Verification for scenario_forge

When processing scenario_forge data, ABC verifies:

1. **Artificial Data Labeling** - Ensures data is properly marked as artificial
2. **Intent Verification** - Validates scenario intent matches declared use case
3. **Provenance Metadata** - Checks provenance information is present
4. **Hash Integrity** - Verifies scenario hash matches data

If verification fails, the workflow stops and returns error details.

---

## Integration Points

### Foundry Integration

The workflow uses the existing `FoundryIntegration` class for:
- Retrieving Foundry compilations
- Validating compilation integrity
- Mapping to ABC format

### Compilation Engine

The workflow uses `ABCCompilationEngine` for:
- Hades: Behavioral profiling
- Echo: Coordination detection
- Nemesis: Threat forecasting

### scenario_forge Verification

The workflow uses `ScenarioForgeVerifier` (if available) for:
- ABC verification of artificial data
- Intent and provenance checks
- Receipt generation

---

## Demo

Run the demo script:

```bash
python3 scripts/demo_foundry_scenario_forge_workflow.py
```

This demonstrates:
1. scenario_forge → ABC → Hades/Echo/Nemesis workflow
2. Auto-detect data type
3. Complete processing with receipts

---

## Benefits

1. **Unified Pipeline** - Single workflow for both Foundry and scenario_forge data
2. **ABC Verification** - Ensures artificial data is properly governed
3. **Complete Processing** - Full Hades/Echo/Nemesis compilation
4. **Cryptographic Proof** - Receipts for audit trail
5. **Auto-Detection** - Automatically detects data type

---

## Next Steps

1. **Production Deployment** - Deploy workflow endpoints to production
2. **Monitoring** - Add metrics for workflow performance
3. **Documentation** - Update API documentation with workflow examples
4. **Testing** - Add integration tests for complete workflow

---

## Related Documentation

- [Foundry Integration Quick Start](FOUNDRY_INTEGRATION_QUICKSTART.md)
- [scenario_forge ABC Workflow](SCENARIO_FORGE_ABC_WORKFLOW.md)
- [Architecture Specification](../architecture/ARCHITECTURE_SPEC.md)

