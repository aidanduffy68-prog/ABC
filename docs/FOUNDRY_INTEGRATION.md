# Palantir Foundry Integration Guide

**GH Systems ABC - Foundry Integration Documentation**

This guide explains how to integrate GH Systems ABC with Palantir Foundry for data pipeline integration, analytics, and visualization.

---

## Overview

GH Systems ABC provides multiple integration points for Palantir Foundry:

1. **Real-time Data Feeds** - Continuous intelligence compilation data
2. **Batch Exports** - Historical compilation data in Foundry-compatible formats
3. **API Endpoints** - Foundry-optimized REST APIs
4. **Data Connectors** - Direct Foundry dataset integration

---

## Quick Start

### 1. Configure Foundry Connection

Set environment variables:

```bash
export FOUNDRY_URL="https://your-foundry-instance.palantirfoundry.com"
export FOUNDRY_API_TOKEN="your-api-token"
```

### 2. Export Data for Foundry

```bash
# Export compilation data
python3 scripts/export_to_foundry.py \
  --input compiled_output.json \
  --format all \
  --output-dir foundry_exports \
  --dataset-name intelligence_compilations
```

### 3. Push to Foundry (Optional)

```bash
# Push directly to Foundry
python3 scripts/export_to_foundry.py \
  --input compiled_output.json \
  --push \
  --dataset-name gh_systems/intelligence_compilations
```

---

## Data Formats

### JSON Export (Flattened)

Foundry-compatible flattened JSON structure:

```json
{
  "compilation_id": "abc_actor_001_1234567890",
  "actor_id": "actor_001",
  "actor_name": "Threat Actor",
  "compiled_at": "2025-12-02T01:00:00Z",
  "compilation_time_ms": 342.15,
  "confidence_score": 0.88,
  "behavioral_confidence": 0.85,
  "behavioral_traits": "{\"risk_tolerance\": 0.7, \"flight_risk\": 0.6}",
  "coordination_partners": 3,
  "coordination_facilitators": 2,
  "network_confidence": 0.82,
  "threat_risk_score": 0.88,
  "threat_level": "critical",
  "targeting_instructions_count": 3,
  "sources": "[\"intel_feed_1\", \"blockchain_analysis\"]",
  "drift_alerts_count": 0,
  "engine_version": "1.0.0",
  "exported_at": "2025-12-02T01:00:00Z"
}
```

### CSV Export

Flattened CSV format with all fields as columns.

### Parquet Export

Columnar Parquet format (Foundry's preferred format for large datasets).

---

## API Endpoints

### Get Foundry Schema

```bash
GET /api/v1/foundry/schema
```

Returns dataset schema definition for Foundry.

### Push to Foundry

```bash
POST /api/v1/foundry/push
Content-Type: application/json

{
  "compilation_data": {...},
  "dataset_path": "gh_systems/intelligence_compilations"
}
```

### Batch Push

```bash
POST /api/v1/foundry/push/batch
Content-Type: application/json

{
  "compilations": [...],
  "dataset_path": "gh_systems/intelligence_compilations"
}
```

### Real-time Feed

```bash
GET /api/v1/foundry/feed/intelligence_compilations?limit=100&since=2025-12-01T00:00:00Z
```

Returns real-time compilation data feed.

### Export Endpoints

```bash
# JSON export
GET /api/v1/foundry/export/json?flattened=true

# CSV export
GET /api/v1/foundry/export/csv
```

---

## Foundry Dataset Schema

### Primary Fields

- `compilation_id` (string, primary key) - Unique compilation identifier
- `actor_id` (string, indexed) - Actor identifier
- `actor_name` (string) - Actor name/designation
- `compiled_at` (timestamp) - Compilation timestamp

### Metrics

- `compilation_time_ms` (double) - Compilation duration
- `confidence_score` (double) - Overall confidence (0.0-1.0)
- `behavioral_confidence` (double) - Behavioral signature confidence
- `network_confidence` (double) - Coordination network confidence
- `threat_risk_score` (double) - Threat forecast risk score

### Behavioral Data

- `behavioral_traits` (string, JSON) - Behavioral trait scores
- `coordination_partners` (integer) - Number of coordination partners
- `coordination_facilitators` (integer) - Number of facilitators

### Threat Assessment

- `threat_level` (string) - LOW, MEDIUM, HIGH, CRITICAL
- `targeting_instructions_count` (integer) - Number of targeting instructions

### Metadata

- `sources` (string, JSON array) - Intelligence source identifiers
- `drift_alerts_count` (integer) - Number of drift alerts
- `engine_version` (string) - Compilation engine version
- `exported_at` (timestamp) - Export timestamp

---

## Integration Patterns

### Pattern 1: Real-time Pipeline

1. **Configure Foundry Connector**
   ```python
   from src.integrations.foundry.connector import FoundryConnector
   
   connector = FoundryConnector()
   ```

2. **Push After Each Compilation**
   ```python
   from src.core.nemesis.compilation_engine import ABCCompilationEngine
   
   engine = ABCCompilationEngine()
   compiled = engine.compile_intelligence(...)
   
   # Push to Foundry
   result = connector.push_compilation(
       compilation_data=asdict(compiled),
       dataset_path="gh_systems/intelligence_compilations"
   )
   ```

### Pattern 2: Batch Export

1. **Collect Compilations**
   ```python
   compilations = []
   for actor in actors:
       compiled = engine.compile_intelligence(...)
       compilations.append(asdict(compiled))
   ```

2. **Export for Foundry**
   ```python
   from src.integrations.foundry.export import FoundryDataExporter
   
   export_result = FoundryDataExporter.export_foundry_dataset(
       compilations=compilations,
       dataset_name="intelligence_compilations",
       output_dir="foundry_exports"
   )
   ```

3. **Import into Foundry**
   - Upload exported files to Foundry
   - Create dataset from schema
   - Map fields to Foundry ontology

### Pattern 3: API Integration

1. **Configure Foundry to Consume API**
   - Set up Foundry data connection
   - Point to `/api/v1/foundry/feed/intelligence_compilations`
   - Configure authentication (API token)

2. **Real-time Data Flow**
   - Foundry polls API endpoint
   - New compilations automatically ingested
   - Data available in Foundry datasets

---

## Data Transformation

### Flattening Nested Structures

Foundry prefers flattened data structures. The exporter automatically:

- Flattens nested dictionaries (e.g., `behavioral_signature.traits` → `behavioral_traits`)
- Converts arrays to JSON strings (e.g., `sources` → JSON string)
- Preserves data types (timestamps, numbers, strings)

### Custom Transformations

You can customize transformations by modifying `FoundryConnector._format_for_foundry()`:

```python
def custom_format(compilation_data):
    # Your custom transformation logic
    return formatted_data
```

---

## Authentication

### API Token Authentication

Foundry integration uses API token authentication:

1. Generate API token in Foundry
2. Set `FOUNDRY_API_TOKEN` environment variable
3. Token included in API requests automatically

### Foundry API Authentication

For direct Foundry API calls:

```python
headers = {
    "Authorization": f"Bearer {foundry_api_token}",
    "Content-Type": "application/json"
}
```

---

## Performance Considerations

### Batch Size

- **Recommended**: 100-1000 records per batch
- **Maximum**: 10,000 records (API limit)

### Real-time Feed

- **Rate Limit**: 1000 requests per minute
- **Recommended Polling**: Every 5-10 seconds
- **Max Records per Request**: 1000

### Export Performance

- **JSON**: Fastest, good for small datasets (<10MB)
- **CSV**: Fast, good for medium datasets (<100MB)
- **Parquet**: Slower export, best for large datasets (>100MB)

---

## Foundry Ontology Mapping

### Recommended Ontology Structure

```
gh_systems/
  ├── intelligence_compilations/
  │   ├── compilation_id (primary key)
  │   ├── actor_id (indexed)
  │   ├── metrics/
  │   │   ├── confidence_score
  │   │   ├── compilation_time_ms
  │   │   └── threat_risk_score
  │   ├── behavioral/
  │   │   ├── behavioral_confidence
  │   │   └── behavioral_traits (JSON)
  │   ├── coordination/
  │   │   ├── partners
  │   │   ├── facilitators
  │   │   └── network_confidence
  │   └── threat/
  │       ├── threat_level
  │       └── targeting_instructions_count
```

---

## Troubleshooting

### Connection Issues

```bash
# Check Foundry connector status
curl http://localhost:8000/api/v1/foundry/status
```

### Export Errors

- **Parquet export fails**: Install `pandas` and `pyarrow`: `pip install pandas pyarrow`
- **CSV encoding issues**: Ensure UTF-8 encoding
- **Large file issues**: Use Parquet format for large datasets

### API Authentication

- Verify `FOUNDRY_API_TOKEN` is set
- Check token has appropriate permissions
- Verify `FOUNDRY_URL` is correct

---

## Example Workflows

### Daily Batch Export

```bash
#!/bin/bash
# Daily export script

# Run compilations
python3 scripts/compile_intelligence.py --batch-mode

# Export to Foundry
python3 scripts/export_to_foundry.py \
  --input daily_compilations.json \
  --format parquet \
  --dataset-name daily_intelligence_$(date +%Y%m%d)

# Upload to Foundry (via Foundry CLI or API)
```

### Real-time Integration

```python
# Continuous integration script
from src.core.nemesis.compilation_engine import ABCCompilationEngine
from src.integrations.foundry.connector import FoundryConnector

engine = ABCCompilationEngine()
connector = FoundryConnector()

while True:
    # Compile intelligence
    compiled = engine.compile_intelligence(...)
    
    # Push to Foundry
    connector.push_compilation(asdict(compiled))
    
    # Wait for next compilation
    time.sleep(60)
```

---

## Related Documentation

- [API Documentation](../src/api/README.md)
- [Data Schemas](../src/schemas/README.md)
- [Architecture Specification](ARCHITECTURE_SPEC.md)

---

**Last Updated**: December 2, 2025

