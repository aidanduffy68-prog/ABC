# API Documentation
**GH Systems ABC AI Ontology REST API**

## Base URL
```
https://api.ghsystems.io/api/v1
```

## Authentication
All endpoints require authentication via API key:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check
**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "GH Systems ABC AI Ontology",
  "version": "2.0.0",
  "timestamp": "2024-11-15T12:00:00Z"
}
```

---

### Process Intelligence Feed
**POST** `/intelligence/process`

Process raw intelligence through AI pipeline.

**Request Body:**
```json
{
  "intelligence": [
    {
      "text": "Lazarus Group activity detected...",
      "source": "twitter",
      "timestamp": "2024-11-15T10:00:00Z"
    }
  ],
  "transaction_data": [
    {
      "tx_hash": "0x...",
      "amount": 1000000,
      "timestamp": "2024-11-15T10:00:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "entities": [...],
    "relationships": [...],
    "behavioral_signatures": {...},
    "threat_forecasts": {...}
  }
}
```

---

### Get Targeting Package
**GET** `/actors/{actor_id}/targeting-package`

Generate targeting package for an actor.

**Query Parameters:**
- `include_dossier` (boolean, default: false) — Include full dossier

**Response:**
```json
{
  "status": "success",
  "package": {
    "package_id": "nemesis_actor_123_20241115",
    "actor_id": "actor_123",
    "confidence": 0.87,
    "predicted_actions": [...],
    "recommended_countermeasures": [...],
    "timing_window": "2024-11-17T00:00:00Z to 2024-11-19T00:00:00Z"
  }
}
```

---

### Natural Language Query
**POST** `/query`

Process natural language query.

**Request Body:**
```json
{
  "query": "Who is coordinating with Lazarus Group?",
  "user": "analyst_123"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "query": "Who is coordinating with Lazarus Group?",
    "response": "Found coordination relationships...",
    "structured_data": {
      "relationships": [...],
      "network_size": 12
    },
    "confidence": 0.85,
    "sources": ["echo_networks", "relationship_inference"]
  }
}
```

---

### Get Threat Dossier
**GET** `/actors/{actor_id}/dossier`

Generate threat dossier for an actor.

**Query Parameters:**
- `format` (string, default: "json") — Response format: "json" or "markdown"

**Response (JSON):**
```json
{
  "status": "success",
  "dossier": {
    "dossier_id": "dossier_actor_123_20241115",
    "actor_id": "actor_123",
    "threat_level": "HIGH",
    "behavioral_signature": {...},
    "threat_forecast": {...}
  }
}
```

**Response (Markdown):**
Returns markdown-formatted dossier (Content-Type: text/markdown)

---

### Record Feedback
**POST** `/feedback`

Record feedback for continuous learning.

**Request Body:**
```json
{
  "feedback_type": "true_positive",
  "entity_id": "actor_123",
  "actual_outcome": {
    "detected": true,
    "action_taken": "freeze"
  },
  "predicted_outcome": {
    "prediction_id": "pred_123",
    "confidence": 0.87
  }
}
```

**Response:**
```json
{
  "status": "success",
  "feedback": {
    "feedback_id": "feedback_20241115T120000",
    "feedback_type": "true_positive",
    "entity_id": "actor_123",
    "confidence_impact": 0.1
  }
}
```

---

### Get Learning Report
**GET** `/learning/report`

Get continuous learning performance report.

**Response:**
```json
{
  "status": "success",
  "report": {
    "total_feedback": 1250,
    "recent_feedback": 150,
    "feedback_by_type": {
      "true_positive": 800,
      "false_positive": 200,
      "false_negative": 50
    },
    "model_performance": {
      "v1.0.0": {
        "accuracy": 0.92,
        "f1_score": 0.89
      }
    },
    "recommendations": [
      "Model performance is stable"
    ]
  }
}
```

---

## Error Responses

All errors return:
```json
{
  "status": "error",
  "message": "Error description"
}
```

**Status Codes:**
- `200` — Success
- `400` — Bad Request (missing/invalid parameters)
- `401` — Unauthorized (invalid API key)
- `404` — Not Found
- `500` — Internal Server Error

---

## Rate Limits

- **Free tier:** 100 requests/hour
- **Pro tier:** 1,000 requests/hour
- **Enterprise:** Custom limits

---

## SDKs

### Python
```python
from gh_systems_sdk import ABCClient

client = ABCClient(api_key="YOUR_API_KEY")
result = client.process_intelligence(intelligence)
```

### JavaScript
```javascript
const { ABCClient } = require('@ghsystems/sdk');

const client = new ABCClient({ apiKey: 'YOUR_API_KEY' });
const result = await client.processIntelligence(intelligence);
```

---

*GH Systems — Compiling behavioral bytecode so lawful actors win the economic battlefield.*

