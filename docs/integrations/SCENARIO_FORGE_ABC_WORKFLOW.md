# scenario_forge → ABC Verification → Hades/Echo/Nemesis Workflow

**Complete workflow for processing scenario_forge artificial data through ABC verification to Hades/Echo/Nemesis analysis pipeline.**

---

## Overview

This workflow ensures **all scenario_forge artificial data is ABC-verified before entering the Hades/Echo/Nemesis processing pipeline**. ABC acts as the cryptographic verification gatekeeper, ensuring data integrity, proper labeling, and compliance before processing.

### Workflow Flow

```
scenario_forge → ABC Verification → Hades/Echo/Nemesis Processing
     ↓                ↓                        ↓
 Generate          Verify                   Process
 artificial       labeling,                behavioral
 AML scenario     intent,                  profiling,
                 provenance               coordination
                                        detection,
                                        targeting
```

---

## Why This Workflow?

### Problem
- scenario_forge generates **artificial** AML scenarios for testing/demos
- This data must be **properly labeled** as artificial before processing
- Need **cryptographic proof** that artificial data was used as intended
- Regulatory compliance requires **complete audit trail**

### Solution
1. **scenario_forge** generates properly labeled artificial data
2. **ABC verifies** data integrity, labeling, intent, and provenance
3. **Hades/Echo/Nemesis** processes only ABC-verified data
4. **Complete audit trail** with cryptographic receipts

---

## Architecture

### Components

1. **scenario_forge** - Generates artificial AML scenarios
   - Creates graph-based transaction data
   - Includes intent labels, provenance metadata, hashes
   - Explicitly labeled as "ARTIFICIAL_DATA"

2. **ABC Verification** (`ScenarioForgeVerifier`)
   - Verifies artificial data labeling
   - Checks intent matches declared use case
   - Validates provenance metadata
   - Generates cryptographic receipt

3. **Hades/Echo/Nemesis Pipeline** (`ABCCompilationEngine`)
   - **Hades**: Behavioral profiling (actor signatures & risk posture)
   - **Echo**: Relationship inference (coordination networks)
   - **Nemesis**: Targeting packages (<500ms pipeline)

4. **Workflow Orchestrator** (`ScenarioForgeWorkflow`)
   - Coordinates the complete workflow
   - Handles data transformation between stages
   - Returns compiled intelligence with receipt

---

## Usage

### Basic Usage

```python
from src.verticals.ai_verification.core.nemesis.scenario_forge_workflow import ScenarioForgeWorkflow
from scenario_forge import cross_chain_laundering

# Step 1: Generate scenario
scenario = cross_chain_laundering()
scenario_dict = {
    "scenario_id": scenario.scenario_id,
    "intent": scenario.intent.value,
    "metadata": {"artificial_data": True, "ARTIFICIAL_DATA": True},
    "provenance": {...},
    "transaction_graph": scenario.transaction_graph,
    # ... other scenario data
}

# Step 2: Process through workflow
workflow = ScenarioForgeWorkflow()
verified, compiled_intelligence, verification_details = workflow.process_scenario(
    scenario_data=scenario_dict,
    declared_intent="model_evaluation",
    generate_receipt=True
)

if verified:
    print(f"✅ Verified and processed: {compiled_intelligence.compilation_id}")
    print(f"   Receipt ID: {verification_details['receipt_id']}")
else:
    print(f"❌ Verification failed: {verification_details['errors']}")
```

### Demo Script

Run the complete workflow demo:

```bash
python scripts/demo_scenario_forge_abc_workflow.py
```

This demonstrates:
- scenario_forge scenario generation
- ABC verification (labeling, intent, provenance)
- Hades/Echo/Nemesis processing
- Cryptographic receipt generation

---

## ABC Verification Checks

ABC verifies the following before allowing data into Hades/Echo/Nemesis:

### 1. Artificial Data Labeling ✅
- Checks for explicit "ARTIFICIAL_DATA" markers
- Verifies data is properly labeled as artificial
- Ensures compliance with governance requirements

### 2. Intent Verification ✅
- Validates scenario intent (SANCTIONS_EVASION, LAUNDERING, etc.)
- Checks intent matches declared use case
- Ensures data is used as intended

### 3. Provenance Validation ✅
- Verifies provenance metadata exists
- Checks scenario_id, timestamps, source information
- Ensures complete traceability

### 4. Hash Integrity ✅
- Validates scenario hash exists
- Ensures data integrity
- Detects tampering or corruption

---

## Workflow Output

### Verification Details

```json
{
  "scenario_id": "uuid-here",
  "verified": true,
  "receipt_id": "abc-receipt-id",
  "intelligence_hash": "sha256-hash",
  "checks_passed": {
    "artificial_label": true,
    "intent_verification": true,
    "provenance": true,
    "hash_integrity": true
  },
  "timestamp": "2026-01-08T00:00:00Z"
}
```

### Compiled Intelligence

The workflow returns a `CompiledIntelligence` object containing:

- **Hades Output**: Behavioral signature, actor profile
- **Echo Output**: Coordination network, relationships
- **Nemesis Output**: Targeting package, threat forecast
- **Metadata**: Compilation ID, timing, confidence scores
- **Receipt**: Cryptographic proof of data integrity

---

## Benefits

### 1. Compliance & Auditability
- **Complete audit trail**: scenario_forge → ABC → Hades/Echo/Nemesis
- **Cryptographic proof**: Every processed scenario has a receipt
- **Regulatory compliance**: Proof that artificial data was properly labeled

### 2. Data Integrity
- **ABC prevents ungoverned data** from entering the pipeline
- **Hash verification** ensures data hasn't been tampered
- **Intent verification** ensures data is used as declared

### 3. Trust & Safety
- **Hades/Echo/Nemesis only processes ABC-verified data**
- **Analysts can trust outputs** knowing inputs were verified
- **Complete traceability** from generation to analysis

### 4. Separation of Concerns
- **ABC = Verification layer** (checks data integrity)
- **Hades/Echo/Nemesis = Processing layer** (analyzes data)
- **Clear responsibility boundaries**

---

## Integration with Existing Systems

### Foundry Integration

This workflow integrates with Palantir Foundry:

1. scenario_forge generates artificial scenarios
2. ABC verifies and generates receipt
3. Foundry ingests ABC-verified data
4. Hades/Echo/Nemesis processes Foundry compilations
5. Complete audit trail from generation to analysis

### API Integration

The workflow can be exposed via API:

```python
from api.abc_verification_service import router

@router.post("/process-scenario-forge")
async def process_scenario_forge(scenario_data: dict):
    workflow = ScenarioForgeWorkflow()
    verified, compiled, details = workflow.process_scenario(scenario_data)
    return {
        "verified": verified,
        "compilation_id": compiled.compilation_id if compiled else None,
        "receipt_id": details.get("receipt_id"),
        "verification_details": details
    }
```

---

## Error Handling

### Verification Failures

If ABC verification fails, the workflow returns:

```python
verified = False
compiled_intelligence = None
verification_details = {
    "verified": False,
    "errors": [
        "Missing required artificial data label",
        "Intent verification failed",
        # ... other errors
    ],
    "warnings": [...]
}
```

Common failure reasons:
- Missing "ARTIFICIAL_DATA" label
- Invalid scenario intent
- Missing provenance metadata
- Hash mismatch (data corruption/tampering)

### Processing Failures

If Hades/Echo/Nemesis processing fails after verification:

- Verification details still returned
- Error logged with full traceback
- Receipt still generated (if verification passed)
- Partial results may be available

---

## Best Practices

### 1. Always Use ABC Verification
- **Never bypass ABC verification**
- Always verify scenario_forge data before processing
- Use `ScenarioForgeWorkflow` for complete workflow

### 2. Proper Labeling
- Ensure scenario_forge data is properly labeled
- Include "ARTIFICIAL_DATA" markers in metadata
- Include provenance information

### 3. Declare Intent
- Always declare use case (e.g., "model_evaluation", "demo", "testing")
- Use consistent intent labels
- Document declared intent in metadata

### 4. Audit Trail
- Always generate receipts (`generate_receipt=True`)
- Store verification details
- Track workflow execution

---

## Examples

### Example 1: Model Evaluation

```python
from scenario_forge import cross_chain_laundering
from src.verticals.ai_verification.core.nemesis.scenario_forge_workflow import ScenarioForgeWorkflow

# Generate scenario
scenario = cross_chain_laundering()
scenario_dict = convert_scenario_to_dict(scenario)

# Process through workflow
workflow = ScenarioForgeWorkflow()
verified, compiled, details = workflow.process_scenario(
    scenario_data=scenario_dict,
    declared_intent="model_evaluation",
    generate_receipt=True
)

if verified:
    # Use compiled intelligence for model evaluation
    use_for_evaluation(compiled)
```

### Example 2: Demo/Testing

```python
# Process multiple scenarios
scenarios = [
    cross_chain_laundering(),
    mixer_ransomware_liquidation(),
    sanctions_evasion_jurisdiction_hopping()
]

workflow = ScenarioForgeWorkflow()
for scenario in scenarios:
    scenario_dict = convert_scenario_to_dict(scenario)
    verified, compiled, details = workflow.process_scenario(
        scenario_data=scenario_dict,
        declared_intent="demo",
        generate_receipt=True
    )
    
    if verified:
        print(f"✅ Processed: {scenario.scenario_id}")
    else:
        print(f"❌ Failed: {details['errors']}")
```

---

## Related Documentation

- [scenario_forge README](../../scenario_forge/README.md) - scenario_forge library documentation
- [ABC Architecture](../../architecture/ARCHITECTURE_SPEC.md) - ABC architecture specification
- [Hades/Echo/Nemesis Pipeline](../../architecture/ARCHITECTURE_SPEC.md#the-abc-intelligence-pipeline) - Processing pipeline details
- [Foundry Integration](FOUNDRY_INTEGRATION_QUICKSTART.md) - Foundry integration guide

---

**GH Systems** - Compiling behavioral bytecode so lawful actors win the economic battlefield.

