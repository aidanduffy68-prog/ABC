# Monitoring Setup
**Prometheus + Grafana for ABC AI Ontology**

## Quick Start

1. **Start Prometheus:**
```bash
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

2. **Start Grafana:**
```bash
docker run -d -p 3000:3000 grafana/grafana
```

3. **Import Dashboard:**
   - Open Grafana at http://localhost:3000
   - Import `grafana_dashboard.json`
   - Configure Prometheus data source

## Metrics Exposed

### API Metrics
- `http_requests_total` — Total API requests
- `http_request_duration_seconds` — Request latency
- `http_requests_active` — Active requests

### Model Metrics
- `model_inference_duration_seconds` — Model inference time
- `model_inference_total` — Total inferences
- `model_cache_hits_total` — Model cache hits

### Business Metrics
- `intelligence_items_processed_total` — Intelligence items processed
- `entities_extracted_total` — Entities extracted
- `predictions_generated_total` — Predictions generated
- `feedback_recorded_total` — Feedback entries

## Alerts

Configure alerts for:
- High error rate (> 1%)
- High latency (P95 > 1s)
- Low cache hit rate (< 70%)
- Model inference failures

---
*GH Systems — Compiling behavioral bytecode so lawful actors win the economic battlefield.*

