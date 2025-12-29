# AI-Powered Threat Ontology
**Making ABC Undeniable Through AI**

## Overview

This module transforms the Adversarial Behavior Compiler from a rule-based system into an **AI-powered threat ontology** that learns, evolves, and provides deeper intelligence than any manual approach.

## Components

### Core AI Systems
- **`semantic_understanding.py`** — LLM-based entity extraction from unstructured intelligence
- **`auto_classification.py`** — ML models for threat actor and TTP classification
- **`relationship_inference.py`** — Graph neural networks for relationship discovery
- **`behavioral_signature.py`** — AI-powered Hades behavioral profiling
- **`predictive_modeling.py`** — Next-move forecasting and threat prediction
- **`continuous_learning.py`** — Feedback loops and model evolution
- **`natural_language_interface.py`** — Plain English query interface
- **`threat_dossier_generator.py`** — Auto-generated threat dossiers
- **`integration_layer.py`** — Integration with Hades/Echo/Nemesis
- **`api_endpoints.py`** — RESTful API for AI-powered queries

## Quick Start

```python
from nemesis.ai_ontology import ABCIntegrationLayer

# Initialize integration layer
abc = ABCIntegrationLayer()

# Process intelligence feed
intelligence = [
    {"text": "Lazarus Group activity detected...", "source": "twitter"}
]
result = abc.process_intelligence_feed(intelligence)

# Generate targeting package
package = abc.generate_targeting_package("actor_123", result)

# Natural language query
response = abc.query_natural_language("Who is coordinating with Lazarus?")
```

## API Server

Run the API server:

```bash
python -m nemesis.ai_ontology.api_endpoints
```

Endpoints:
- `GET /api/v1/health` — Health check
- `POST /api/v1/intelligence/process` — Process intelligence feed
- `GET /api/v1/actors/<id>/targeting-package` — Get targeting package
- `POST /api/v1/query` — Natural language query
- `GET /api/v1/actors/<id>/dossier` — Get threat dossier
- `POST /api/v1/feedback` — Record feedback
- `GET /api/v1/learning/report` — Learning performance report

## Installation

```bash
pip install -r nemesis/ai_ontology/requirements.txt
```

## Documentation

- **`nemesis/AI_THREAT_ONTOLOGY_SPEC.md`** — Complete AI ontology specification
- **`nemesis/AI_ONTOLOGY_INTEGRATION.md`** — Integration roadmap and checklist
- **`Deal Room/GH_ONTOLOGY_SPEC.md`** — Core Behavioral Intelligence Graph spec

---
*GH Systems — Compiling behavioral bytecode so lawful actors win the economic battlefield.*

