# Foundry API Connection Guide

**How to connect ABC to Palantir Foundry API (demo/staging/production)**

Copyright (c) 2026 GH Systems. All rights reserved.

---

## Quick Start

### Demo Mode (No API Required)

Test the Foundry Chain integration without a real Foundry API connection:

```bash
# Run connection test in mock mode
python3 scripts/tests/test_foundry_connection.py

# Run full workflow test
python3 scripts/tests/test_foundry_chain_workflow.py
```

### Staging/Production Mode

Connect to real Palantir Foundry API:

```bash
# Set environment variables
export FOUNDRY_API_URL="https://your-foundry-instance.palantir.com/api/v1"
export FOUNDRY_API_KEY="your-api-key-here"

# Test connection
python3 scripts/tests/test_foundry_connection.py --real
```

---

## Environment Variables

### Required for Real Connection

- **`FOUNDRY_API_URL`** — Foundry API base URL
  - Example: `https://foundry.palantir.com/api/v1`
  - Staging: `https://foundry-staging.palantir.com/api/v1`

- **`FOUNDRY_API_KEY`** — Foundry API authentication key
  - Obtain from Palantir Foundry admin
  - Store securely (use `.env` file or secrets manager)

### Optional

- **`FOUNDRY_TIMEOUT`** — Request timeout in seconds (default: 30)

---

## Connection Test

The test script validates:

1. ✅ **Compilation Retrieval** — Can fetch Foundry compilations
2. ✅ **Data Validation** — Validates hash, sources, structure
3. ✅ **Compilation Listing** — Lists recent compilations
4. ✅ **Integration Workflow** — Full Foundry → ABC pipeline

### Run Tests

```bash
# Mock mode (no API required)
python3 scripts/tests/test_foundry_connection.py

# Real API connection
python3 scripts/tests/test_foundry_connection.py --real
```

---

## Usage in Code

### Basic Connection

```python
from src.core.nemesis.foundry_integration import FoundryIntegration

# Initialize (uses environment variables)
foundry = FoundryIntegration()

# Or specify explicitly
foundry = FoundryIntegration(
    foundry_api_url="https://foundry.palantir.com/api/v1",
    api_key="your-api-key"
)
```

### Ingest Compilation

```python
# Ingest Foundry compilation
compilation = foundry.ingest_compilation(
    compilation_id="foundry-comp-2025-12-12-001",
    classification="SBU"
)

# Validate
validation = foundry.validate_compilation(compilation)
if not validation["valid"]:
    raise ValueError(f"Validation failed: {validation['errors']}")
```

### Prepare for ABC Analysis

```python
# Map Foundry data to ABC format
abc_data = foundry.prepare_for_abc_analysis(compilation)

# Use with ABC compilation engine
from src.core.nemesis.compilation_engine import ABCCompilationEngine

engine = ABCCompilationEngine()
compiled = engine.compile_intelligence(
    actor_id="foundry_actor_001",
    actor_name="Foundry Threat Actor",
    raw_intelligence=abc_data["raw_intelligence"],
    transaction_data=abc_data["transaction_data"],
    network_data=abc_data["network_data"],
    generate_receipt=True,
    preferred_blockchain="ethereum",
    classification="SBU"
)
```

---

## Mock Mode for Development

The test suite includes a `MockFoundryConnector` that simulates Foundry API responses without requiring a real connection. This is useful for:

- Development and testing
- CI/CD pipelines
- Demonstrations
- Training

Mock mode is automatically enabled when:
- `FOUNDRY_API_URL` is not set
- `FOUNDRY_API_KEY` is not set
- `--real` flag is not used

---

## Troubleshooting

### Connection Errors

**Error: "Foundry API key not provided"**
- Set `FOUNDRY_API_KEY` environment variable
- Or pass `api_key` parameter to `FoundryIntegration()`

**Error: "Connection timeout"**
- Check `FOUNDRY_API_URL` is correct
- Verify network connectivity
- Increase timeout: `FOUNDRY_TIMEOUT=60`

**Error: "401 Unauthorized"**
- Verify API key is valid
- Check API key hasn't expired
- Ensure API key has required permissions

### Validation Errors

**Error: "Hash mismatch"**
- Foundry data may have changed
- Re-fetch compilation from Foundry
- Check data integrity

**Error: "Invalid compilation structure"**
- Foundry output format may have changed
- Update `CompilationValidator` if needed
- Check Foundry API version compatibility

---

## Next Steps

1. **Test Connection** — Run `test_foundry_connection.py`
2. **Test Workflow** — Run `test_foundry_chain_workflow.py`
3. **Integrate with ABC** — Use `FoundryIntegration` in your code
4. **Deploy** — Set environment variables in production

---

**See [Foundry Chain Specification](FOUNDRY_CHAIN_SPEC.md) for complete architecture.**

