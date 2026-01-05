# ABC + Foundry Integration Quick Start

**Get ABC working with Palantir Foundry in 3 steps**

---

## Overview

This guide shows you how to integrate ABC with Palantir Foundry for cryptographic verification of intelligence compilations. From Foundry compilation to ABC verification in <60 seconds.

---

## Integration Proof

**Time-to-Value:** 2-4 hours (API alignment only)  
**Foundry Changes Required:** Zero (API-based integration)  
**Downtime:** None (verification layer operates independently)  
**Compatibility:** All Foundry versions (API-based)

[Full integration guide below ↓]

---

## Prerequisites

- Palantir Foundry instance (or demo mode)
- ABC installed and running
- Foundry API credentials (for production)

---

## Integration in 3 Steps

### Step 1: Configure Foundry Connection

Set environment variables:

```bash
# For production Foundry instance
export FOUNDRY_URL="https://your-foundry-instance.palantirfoundry.com"
export FOUNDRY_API_TOKEN="your-api-token"

# Or use .env file
cat > .env << EOF
FOUNDRY_URL=https://your-foundry-instance.palantirfoundry.com
FOUNDRY_API_TOKEN=your-api-token
EOF
```

**Demo mode:** If you don't have Foundry credentials, ABC will use mock data for testing.

### Step 2: Verify Foundry Compilation

Use the ABC API to verify a Foundry compilation:

```bash
# Via API endpoint
curl -X POST "http://localhost:8000/api/v1/foundry/verify" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "foundry_compilation_id": "foundry-comp-2025-12-15-001",
    "blockchain": "bitcoin"
  }'
```

**Python example:**

```python
import requests

# Verify Foundry compilation
response = requests.post(
    "http://localhost:8000/api/v1/foundry/verify",
    headers={
        "Authorization": "Bearer your-token",
        "Content-Type": "application/json"
    },
    json={
        "foundry_compilation_id": "foundry-comp-2025-12-15-001",
        "blockchain": "bitcoin"  # or "ethereum", "polygon", etc.
    }
)

result = response.json()
print(f"ABC Confidence: {result['abc_analysis']['confidence']}%")
print(f"Blockchain TX: {result['blockchain_receipt']['tx_hash']}")
print(f"Verification URL: {result['blockchain_receipt']['verification_url']}")
```

### Step 3: Verify Receipt Chain

Verify the complete chain (Foundry → ABC → Agency assessments):

```bash
# Public endpoint - no auth required
curl "http://localhost:8000/api/v1/foundry/verify/sha256:abc123..."
```

**Response shows:**
- Foundry compilation verification status
- ABC analysis results
- All agency assessments referencing this compilation
- Complete hash chain verification

---

## Foundry Data Format

ABC expects Foundry compilations in this format:

```json
{
  "compilation_id": "foundry-comp-2025-12-15-001",
  "data_hash": "sha256:abc1234567890123456789012345678901234567890123456789012345678901",
  "timestamp": "2025-12-15T17:00:00Z",
  "sources": [
    {"provider": "chainalysis", "dataset": "sanctions_list_v2"},
    {"provider": "trm_labs", "dataset": "threat_actors_q4"},
    {"provider": "ofac", "dataset": "sdn_list_current"}
  ],
  "classification": "SBU",
  "compiled_data": {
    "threat_actors": [
      {
        "id": "threat_actor_001",
        "name": "APT41",
        "risk_score": 0.88
      }
    ],
    "wallet_addresses": ["0x1234..."],
    "coordination_networks": []
  }
}
```

ABC automatically maps Foundry data to ABC format. See [Data Mapper](../../src/core/nemesis/foundry_integration/data_mapper.py) for details.

---

## API Integration Examples

### Example 1: Verify Foundry Compilation and Get Receipt

```python
from src.integrations.foundry.connector import FoundryDataExportConnector
from src.core.nemesis.compilation_engine import ABCCompilationEngine

# Initialize connectors
foundry = FoundryDataExportConnector()
compilation_engine = ABCCompilationEngine()

# Get Foundry compilation
compilation = foundry.get_compilation("foundry-comp-2025-12-15-001")

# Verify hash
if foundry.verify_compilation_hash(compilation):
    print("✓ Foundry compilation hash verified")
    
    # ABC will automatically verify and generate receipt via API
    # Or use compilation engine directly:
    abc_result = compilation_engine.compile_intelligence(
        actor_id="threat_actor_001",
        raw_intelligence=compilation.get("compiled_data", {}),
        preferred_blockchain="bitcoin"
    )
    print(f"ABC Confidence: {abc_result.confidence_score * 100}%")
```

### Example 2: List Recent Foundry Compilations

```python
# Get recent compilations from Foundry
recent = foundry.list_recent_compilations(hours=24, limit=10)

for comp in recent:
    print(f"{comp['compilation_id']}: {comp['timestamp']}")
    # Verify each compilation
    if foundry.verify_compilation_hash(comp):
        print("  ✓ Hash verified")
```

### Example 3: Verify Receipt Chain (Public)

```python
import requests

# Verify complete chain (no auth required for this endpoint)
receipt_hash = "sha256:abc1234567890123456789012345678901234567890123456789012345678901"

response = requests.get(
    f"http://localhost:8000/api/v1/foundry/verify/{receipt_hash}"
)

verification = response.json()

if verification['chain_verified']:
    print("✓ Complete chain verified")
    print(f"Foundry: {verification['foundry_compilation']['verified']}")
    print(f"ABC: {verification['abc_analysis']['verified']}")
    print(f"Agencies: {len(verification['agency_assessments'])}")
```

---

## From Foundry Compilation to ABC Verification in <60 Seconds

**Complete workflow:**

1. **Foundry compiles intelligence** → `foundry-comp-2025-12-15-001`
2. **ABC verifies compilation** → `POST /api/v1/foundry/verify`
3. **Get blockchain receipt** → Receipt hash returned
4. **Verify chain publicly** → `GET /api/v1/foundry/verify/{receipt_hash}`

**Time:** <60 seconds from Foundry compilation to verified ABC receipt on blockchain.

---

## Integration Templates

### Template 1: Webhook Integration

Set up Foundry webhook to automatically trigger ABC verification:

```python
from fastapi import FastAPI, Request
from src.api.routes.foundry import verify_foundry_compilation

app = FastAPI()

@app.post("/webhook/foundry/compilation-complete")
async def foundry_webhook(request: Request):
    """Webhook handler for Foundry compilation completion"""
    data = await request.json()
    compilation_id = data['compilation_id']
    
    # Automatically verify via ABC
    result = await verify_foundry_compilation(
        foundry_compilation_id=compilation_id,
        blockchain="bitcoin"
    )
    
    return {
        "status": "verified",
        "abc_receipt": result['blockchain_receipt']
    }
```

### Template 2: Batch Verification

Verify multiple Foundry compilations:

```python
compilation_ids = [
    "foundry-comp-2025-12-15-001",
    "foundry-comp-2025-12-15-002",
    "foundry-comp-2025-12-15-003"
]

results = []
for comp_id in compilation_ids:
    try:
        result = await verify_foundry_compilation(
            foundry_compilation_id=comp_id,
            blockchain="ethereum"
        )
        results.append({
            "compilation_id": comp_id,
            "status": "verified",
            "receipt_hash": result['blockchain_receipt']['receipt_id']
        })
    except Exception as e:
        results.append({
            "compilation_id": comp_id,
            "status": "error",
            "error": str(e)
        })
```

---

## Troubleshooting

**Connection issues:**
- Check `FOUNDRY_URL` and `FOUNDRY_API_TOKEN` environment variables
- Verify Foundry API endpoint is accessible
- Use demo mode if credentials unavailable

**Hash verification fails:**
- Ensure Foundry compilation includes `data_hash` field
- Verify hash matches actual compilation content
- Check ABC hash verification logic

**Blockchain commit fails:**
- Verify blockchain network is accessible
- Check blockchain credentials (if required)
- Use testnet for development

**For detailed troubleshooting, see [Foundry Connection Guide](FOUNDRY_CONNECTION_GUIDE.md)**

---

## Next Steps

1. **Production deployment** — See [Foundry Chain Specification](FOUNDRY_CHAIN_SPEC.md)
2. **API documentation** — Visit `http://localhost:8000/docs` when API server is running
3. **Use cases** — See [Use Cases Guide](../USE_CASES.md) for specific scenarios
4. **Security** — Review [Security Documentation](../security/README.md) for classification handling

---

**Questions?** See [Foundry Chain Specification](FOUNDRY_CHAIN_SPEC.md) or [Architecture Documentation](../architecture/ARCHITECTURE_SPEC.md) for complete details.

