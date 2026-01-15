# Foundry Transform Code: ABC Compilation (Hades/Echo/Nemesis)

**Copy this code into Foundry Pipeline Builder**

This is the exact code to use in Foundry Pipeline Builder for processing verified hash data through Hades/Echo/Nemesis compilation.

---

## Setup

1. In Foundry Pipeline Builder, create a new Python transform step
2. Set input dataset: `verify_abc_receipt` (or your verified hash dataset name)
3. Set output dataset: `compile_intelligence` (or your output dataset name)
4. Copy the code below into the transform

---

## Transform Code

```python
@transform_df(
    output=compile_intelligence,
    input=verify_abc_receipt
)
def compile_intelligence(verify_abc_receipt: pd.DataFrame) -> pd.DataFrame:
    """
    Process verified hash data through Hades/Echo/Nemesis compilation.

    Takes verified ABC receipt hash data and processes it through the ABC
    compilation engine to generate behavioral signatures, coordination networks,
    and threat forecasts.

    Args:
        verify_abc_receipt: DataFrame with verified hash data
            Expected columns:
            - hash (or abc_receipt_hash)
            - verified (or is_verified)
            - transaction_hash (optional)
            - from_address (optional)
            - to_address (optional)
            - value (optional)
            - timestamp (optional)

    Returns:
        DataFrame with compiled intelligence (single row)
    """
    import json
    import pandas as pd

    from src.verticals.ai_verification.core.nemesis.foundry_integration.foundry_compilation_transform import (
        compile_from_verified_hashes
    )

    # Convert DataFrame to list of dicts
    verified_hashes = verify_abc_receipt.to_dict('records')

    # Compile through Hades/Echo/Nemesis
    result = compile_from_verified_hashes(
        verified_hashes,
        assumed_scenario="5_hop_laundering"
    )

    # Flatten nested structures for Foundry DataFrame
    # Foundry works better with JSON strings for complex nested data
    output_row = {
        "compilation_id": result["compilation_id"],
        "actor_id": result["actor_id"],
        "actor_name": result["actor_name"],
        "behavioral_signature_json": json.dumps(result["behavioral_signature"]),
        "coordination_network_json": json.dumps(result["coordination_network"]),
        "threat_forecast_json": json.dumps(result["threat_forecast"]),
        "targeting_package_json": json.dumps(result["targeting_package"]),
        "confidence_score": result["confidence_score"],
        "compilation_time_ms": result["compilation_time_ms"],
        "receipt_id": result["receipt_id"],
        "receipt_hash": result["receipt_hash"],
        "compiled_at": result["compiled_at"],
        "assumed_scenario": result["assumed_scenario"],
        "input_hash_count": result["input_hash_count"],
        "transaction_count": result["transaction_count"]
    }

    # Return as single-row DataFrame
    return pd.DataFrame([output_row])
```

---

## Output Schema

The transform returns a single-row DataFrame with the following columns:

- `compilation_id`: ABC compilation ID
- `actor_id`: Threat actor ID
- `actor_name`: Threat actor name
- `behavioral_signature_json`: Behavioral signature (JSON string)
- `coordination_network_json`: Coordination network (JSON string)
- `threat_forecast_json`: Threat forecast (JSON string)
- `targeting_package_json`: Targeting package (JSON string)
- `confidence_score`: Overall confidence score (float)
- `compilation_time_ms`: Compilation time in milliseconds (float)
- `receipt_id`: ABC receipt ID
- `receipt_hash`: ABC receipt hash
- `compiled_at`: Compilation timestamp (ISO format)
- `assumed_scenario`: Assumed scenario type (e.g., "5_hop_laundering")
- `input_hash_count`: Number of input hashes processed
- `transaction_count`: Number of transactions extracted

---

## Prerequisites

1. ABC package must be installed in your Foundry environment
2. Input dataset must have verified hash data with expected columns
3. Transform must have access to the ABC compilation engine

---

## See Also

- [Foundry Workflow Integration](FOUNDRY_WORKFLOW_INTEGRATION.md)
- [Demo Script](../../scripts/demo_foundry_pipeline_compilation.py)

