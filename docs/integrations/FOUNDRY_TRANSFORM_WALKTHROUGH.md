# Foundry Transform Walkthrough: Hades/Echo/Nemesis Compilation

**Step-by-step guide to using ABC compilation in Foundry Pipeline Builder**

---

## Overview

This transform processes verified hash data through the ABC compilation engine (Hades/Echo/Nemesis) to generate behavioral signatures, coordination networks, and threat forecasts.

---

## Step 1: Understanding the Code Structure

The transform function takes verified hash data and processes it through three stages:

1. **Input**: Verified ABC receipt hash data (DataFrame)
2. **Processing**: ABC compilation engine (Hades/Echo/Nemesis)
3. **Output**: Compiled intelligence with behavioral signatures, coordination networks, threat forecasts (DataFrame)

---

## Step 2: Code Breakdown

### Line 1-4: Transform Decorator
```python
@transform_df(
    output=compile_intelligence,  # Output dataset name in Foundry
    input=verify_abc_receipt      # Input dataset name in Foundry
)
```
- `@transform_df`: Foundry decorator that defines a DataFrame transform
- `output`: Name of your output dataset (define this in Foundry)
- `input`: Name of your input dataset (should be your verified hash data)

### Line 5: Function Signature
```python
def compile_intelligence(verify_abc_receipt: pd.DataFrame) -> pd.DataFrame:
```
- Function name must match your output dataset name
- `verify_abc_receipt`: Input DataFrame with verified hash data
- Returns: Output DataFrame with compiled intelligence

**Note**: If you get `pd` undefined errors, Foundry provides `pandas as pd` automatically. You can also use string annotation: `"pd.DataFrame"`

### Line 9-10: Imports (Inside Function)
```python
import json
import pandas as pd
```
- Imports are inside the function (Foundry pattern)
- `json`: For serializing nested structures
- `pandas as pd`: For DataFrame operations

### Line 12-14: ABC Import
```python
from src.verticals.ai_verification.core.nemesis.foundry_integration.foundry_compilation_transform import (
    compile_from_verified_hashes
)
```
- Imports the ABC compilation function
- Make sure ABC package is installed in your Foundry environment

### Line 17: Convert DataFrame to List
```python
verified_hashes = verify_abc_receipt.to_dict('records')
```
- Converts Foundry DataFrame to list of dictionaries
- Each row becomes a dict with column names as keys

### Line 20-23: ABC Compilation
```python
result = compile_from_verified_hashes(
    verified_hashes,
    assumed_scenario="aml_investigation"
)
```
- Processes data through Hades/Echo/Nemesis
- Works for any AML investigation pattern
- Returns compiled intelligence dictionary

### Line 26-42: Build Output Row
```python
output_row = {
    "compilation_id": result["compilation_id"],
    "actor_id": result["actor_id"],
    # ... more fields
}
```
- Extracts fields from compilation result
- Serializes nested structures to JSON strings (Foundry works better with strings)
- Creates single row dictionary

### Line 44: Return DataFrame
```python
return pd.DataFrame([output_row])
```
- Converts output row to DataFrame
- Single row DataFrame (compiles all input hashes into one result)

---

## Step 3: Setting Up in Foundry

### Prerequisites

1. **ABC Package**: Must be installed in your Foundry environment
   - Add to your `setup.py` or `requirements.txt`
   - Or install via Foundry's package management

2. **Input Dataset**: You need a dataset with verified hash data
   - Columns: `hash`, `verified`, `transaction_hash` (optional), `from_address` (optional), `to_address` (optional), etc.

### Steps

1. **Create Transform Step**
   - In Foundry Pipeline Builder, click "Add transform"
   - Select "Python transform" or "Custom Python"

2. **Configure Input/Output**
   - **Input dataset**: Select your verified hash dataset (e.g., `verify_abc_receipt`)
   - **Output dataset**: Create new or select existing (e.g., `compile_intelligence`)

3. **Copy Code**
   - Copy entire code from `scripts/foundry_transform_code.py`
   - Paste into Foundry's code editor

4. **Update Names (if needed)**
   - Make sure dataset names in `@transform_df` match your actual dataset names
   - Update function name if output dataset name differs

5. **Test**
   - Click "Preview" to test with sample data
   - Check for errors in console
   - Verify output structure

6. **Deploy**
   - Click "Commit" or "Propose changes"
   - Transform will run in your pipeline

---

## Step 4: Understanding the Output

The output DataFrame has one row with these columns:

- **compilation_id**: Unique ABC compilation ID
- **actor_id**: Threat actor identifier
- **actor_name**: Human-readable actor name
- **behavioral_signature_json**: Behavioral patterns (JSON string)
- **coordination_network_json**: Coordination partners/facilitators (JSON string)
- **threat_forecast_json**: Threat level and risk scores (JSON string)
- **targeting_package_json**: Actionable recommendations (JSON string)
- **confidence_score**: Overall confidence (0.0 to 1.0)
- **compilation_time_ms**: Processing time in milliseconds
- **receipt_id**: ABC receipt ID for verification
- **receipt_hash**: ABC receipt hash
- **compiled_at**: Timestamp
- **assumed_scenario**: Scenario type (default: "aml_investigation")
- **input_hash_count**: Number of input records processed
- **transaction_count**: Number of transactions extracted

---

## Step 5: Using the Output

You can:

1. **Parse JSON fields**: Use Foundry's JSON functions to extract specific fields
2. **Filter by confidence**: Filter results by `confidence_score`
3. **Link to receipts**: Use `receipt_id` to verify results
4. **Export**: Export to other Foundry datasets or external systems

---

## Troubleshooting

### Error: "Undefined name `pd`"
- Foundry provides `pandas as pd` automatically
- If errors persist, use string annotation: `verify_abc_receipt: "pd.DataFrame"`
- Or add `import pandas as pd` at the top of your transform

### Error: "Module not found: src.verticals..."
- ABC package not installed in Foundry environment
- Add ABC to your project dependencies
- Or use absolute import path if package is installed

### Error: "compile_from_verified_hashes not found"
- Check import path is correct
- Verify ABC package structure matches import path

### Output is empty
- Check input dataset has data
- Verify column names match expected format
- Check transform logs for errors

---

## Example: Parsing JSON Output

To extract specific fields from JSON columns:

```python
import json

# In a downstream transform
behavioral_signature = json.loads(row["behavioral_signature_json"])
signatures = behavioral_signature.get("signatures", {})
confidence_scores = behavioral_signature.get("confidence_scores", {})
```

---

## Next Steps

1. Test with sample data
2. Verify output structure
3. Connect to downstream transforms
4. Deploy to production pipeline

---

## See Also

- [Foundry Transform Code](FOUNDRY_TRANSFORM_CODE.md)
- [Foundry Workflow Integration](FOUNDRY_WORKFLOW_INTEGRATION.md)
- [Demo Script](../../scripts/demo_foundry_pipeline_compilation.py)

