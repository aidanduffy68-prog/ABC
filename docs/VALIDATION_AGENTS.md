# Validation Agents System

**Inspired by Chaos Labs' Chaos Agents Architecture**

## Overview

The Validation Agents system provides modular, agent-based validation for intelligence updates before compilation. Each agent validates one specific aspect of intelligence data, following the Chaos Agents pattern of lightweight, single-purpose validation modules.

## Architecture

### Agent Hub
The `ValidationAgentHub` serves as the central controller, similar to Chaos Agents' Hub:
- Routes updates to appropriate agents based on `update_type`
- Performs generic validations (expiration, size, format)
- Aggregates results from multiple agents
- Provides fail-fast validation (rejects on first failure)

### Base Agents

All agents inherit from `BaseValidationAgent` and implement:
- `validate()`: Validates intelligence update
- `get_metadata()`: Returns agent statistics and configuration

## Available Agents

### 1. RangeValidationAgent
Validates that values are within acceptable ranges.

**Example:**
```python
agent = RangeValidationAgent(
    agent_id="risk_score_range",
    field_name="risk_score",
    min_value=0.0,
    max_value=100.0
)
```

**Use Cases:**
- Risk score bounds (0-100)
- Confidence score bounds (0-1)
- Any numeric field validation

### 2. ExpirationWindowAgent
Validates that intelligence updates are within expiration window.

**Example:**
```python
agent = ExpirationWindowAgent(
    agent_id="expiration_window",
    max_age_seconds=3600  # 1 hour
)
```

**Use Cases:**
- Stale intelligence rejection
- Time-sensitive threat assessments
- Real-time intelligence freshness

### 3. CircuitBreakerAgent
Prevents extreme risk score changes (circuit breaker pattern).

**Example:**
```python
agent = CircuitBreakerAgent(
    agent_id="circuit_breaker",
    max_change_percent=50.0  # Max 50% change
)
```

**Use Cases:**
- Preventing sudden risk score spikes
- Protecting against data corruption
- Gradual risk score transitions

### 4. MinimumDelayAgent
Enforces minimum delay between updates for the same actor.

**Example:**
```python
agent = MinimumDelayAgent(
    agent_id="minimum_delay",
    min_delay_seconds=60  # 1 minute
)
```

**Use Cases:**
- Rate limiting intelligence updates
- Preventing rapid-fire updates
- Reducing system load

## Usage

### Default Agent Hub

The easiest way to use validation is with the default agent hub:

```python
from src.core.validation.agent_hub import create_default_agent_hub

hub = create_default_agent_hub()

# Validate intelligence update
intelligence_data = {
    "actor_id": "threat_001",
    "timestamp": datetime.now().isoformat(),
    "risk_score": 85.0
}

result = hub.validate_update(
    intelligence_data=intelligence_data,
    update_type="risk_score",
    current_state={"risk_score": 80.0}  # Optional: for circuit breaker
)

if result.is_valid:
    print("✅ Validation passed")
else:
    print(f"❌ Validation failed: {result.reason}")
```

### Custom Agent Hub

Create a custom hub with specific agents:

```python
from src.core.validation.agent_hub import ValidationAgentHub
from src.core.validation.base_agent import RangeValidationAgent

hub = ValidationAgentHub()

# Register custom agent
risk_agent = RangeValidationAgent(
    agent_id="custom_risk_range",
    field_name="risk_score",
    min_value=0.0,
    max_value=100.0
)

hub.register_agent(
    agent=risk_agent,
    update_types=["risk_score", "threat_assessment"],
    priority=1  # Lower = higher priority
)
```

### Integration with Compilation Engine

Validation is automatically integrated into the compilation engine:

```python
from src.core.nemesis.compilation_engine import ABCCompilationEngine

engine = ABCCompilationEngine()

# Compile with validation (default: enabled)
compiled = engine.compile_intelligence(
    actor_id="threat_001",
    actor_name="Threat Actor",
    raw_intelligence=[{"text": "..."}],
    validate_before_compile=True,  # Enable validation
    current_state={"risk_score": 80.0}  # For circuit breaker
)
```

## Red Team Testing

The validation agents protect against common attack scenarios:

### Scenario 1: Rapid-Fire Updates
**Attack:** Send multiple updates in quick succession  
**Protection:** `MinimumDelayAgent` blocks updates within delay window

### Scenario 2: Extreme Risk Score Changes
**Attack:** Attempt to change risk score from 10% to 95% instantly  
**Protection:** `CircuitBreakerAgent` blocks changes >50% (configurable)

### Scenario 3: Expired Intelligence
**Attack:** Submit stale intelligence data  
**Protection:** `ExpirationWindowAgent` rejects intelligence older than threshold

### Scenario 4: Out-of-Range Values
**Attack:** Submit invalid risk scores (e.g., 150%)  
**Protection:** `RangeValidationAgent` enforces bounds

## Testing

Run the validation agent test suite:

```bash
python3 scripts/test_validation_agents.py
```

This tests:
- Individual agent validation logic
- Agent hub integration
- Red team attack scenarios
- Edge cases and error handling

## Comparison to Chaos Agents

| Feature | Chaos Agents | GH Systems Validation Agents |
|---------|-------------|------------------------------|
| **Architecture** | Smart contracts (Solidity) | Python classes |
| **Purpose** | Risk parameter updates | Intelligence validation |
| **Hub Pattern** | ✅ Yes | ✅ Yes |
| **Agent Pattern** | ✅ One agent = one updateType | ✅ One agent = one validation type |
| **Standard Interface** | `validate()`, `inject()`, `getMarkets()` | `validate()`, `get_metadata()` |
| **Circuit Breakers** | ✅ Yes | ✅ Yes |
| **Expiration Windows** | ✅ Yes | ✅ Yes |
| **Minimum Delay** | ✅ Yes | ✅ Yes |
| **Range Validation** | ✅ Yes (RangeValidationModule) | ✅ Yes |

## Benefits

1. **Modularity**: Each agent handles one validation concern
2. **Extensibility**: Easy to add new validation agents
3. **Testability**: Agents can be tested independently
4. **Security**: Fail-fast validation prevents invalid data from entering system
5. **Calibration**: Agents can be tuned for specific use cases

## Future Enhancements

- [ ] Custom validation agents for specific intelligence types
- [ ] Agent performance metrics and monitoring
- [ ] Dynamic agent configuration (enable/disable at runtime)
- [ ] Agent priority and dependency management
- [ ] Integration with red team test suite

---

**Inspired by:** [Chaos Labs Chaos Agents Factory](https://github.com/ChaosLabsInc/chaos-agents-factory)

