# ABC Compilation Engine

**Core compilation engine that orchestrates Hades → Echo → Nemesis pipeline**

Compiles intelligence in <500ms from raw telemetry to executable targeting packages.

---

## Quick Start

### Basic Compilation

```python
from nemesis.compilation_engine import compile_intelligence

# Compile intelligence
compiled = compile_intelligence(
    actor_id="lazarus_001",
    actor_name="Lazarus Group",
    raw_intelligence=[
        {"text": "Lazarus Group activity detected", "source": "intel_feed"}
    ],
    transaction_data=[
        {"wallet": "0x123...", "amount": 1000000, "timestamp": "2025-11-21"}
    ]
)

# Access compiled intelligence
print(f"Compilation time: {compiled.compilation_time_ms}ms")
print(f"Confidence: {compiled.confidence_score}")
print(f"Targeting package: {compiled.targeting_package}")
```

### Federal AI Security Compilation

```python
from nemesis.compilation_engine import ABCCompilationEngine
from nemesis.signal_intake import monitor_federal_ai_systems

# Monitor federal AI systems
intelligence_feed = monitor_federal_ai_systems()

# Compile federal AI intelligence
engine = ABCCompilationEngine()
compiled = engine.compile_federal_ai_intelligence(
    target_agency="NASA",
    ai_system_data={
        "name": "Prithvi Foundation Model",
        "type": "foundation_model"
    },
    vulnerability_data=[
        {
            "type": "model_inference_manipulation",
            "severity": "high",
            "description": "Potential for adversarial input manipulation"
        }
    ]
)
```

---

## Architecture

```
Raw Intelligence → Hades (Behavioral Profiling) → Echo (Coordination Detection) → Nemesis (Targeting Packages)
                                                                                        ↓
                                                                          Cryptographic Receipts
```

### Components

1. **Hades** - Behavioral profiling engine
   - Generates behavioral signatures from transaction history
   - Identifies risk patterns and traits
   - Calculates confidence scores

2. **Echo** - Coordination detection engine
   - Infers relationships between entities
   - Maps coordination networks
   - Identifies facilitators and partners

3. **Nemesis** - Targeting package generator
   - Generates executable targeting packages
   - Creates threat forecasts
   - Provides recommended countermeasures

4. **Cryptographic Receipts** - Proof of intelligence
   - Generates minimal on-chain proofs
   - Verifiable without revealing methods
   - Bitcoin settlement ready

---

## API Usage

### REST API

**Compile Intelligence:**
```bash
curl -X POST http://localhost:5000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{
    "actor_id": "lazarus_001",
    "actor_name": "Lazarus Group",
    "raw_intelligence": [{"text": "..."}]
  }'
```

**Scan Federal AI Systems:**
```bash
curl -X POST http://localhost:5000/api/v1/federal-ai/scan \
  -H "Content-Type: application/json" \
  -d '{"agencies": ["NASA", "DoD", "DHS"]}'
```

### WebSocket API

**Connect and Subscribe:**
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  socket.emit('subscribe', {type: 'all'});
});

socket.on('intelligence_compiled', (data) => {
  console.log('New intelligence compiled:', data);
});
```

---

## Performance

- **Compilation Time:** <500ms (target)
- **Throughput:** 100+ compilations/second
- **Confidence Scores:** 0.0-1.0 (weighted average)
- **Real-Time Updates:** WebSocket delivery

---

## Integration

The compilation engine integrates with:
- AI ontology layer (semantic understanding, classification)
- Cryptographic receipt system (on-chain proofs)
- Signal intake (federal AI monitoring)
- Real-time platform (WebSocket delivery)

---

**GH Systems: Compiling behavioral bytecode so lawful actors win the economic battlefield.**

