"""
Validation Agent System
Inspired by Chaos Labs' Chaos Agents architecture

Provides modular validation agents for intelligence updates:
- Base validation agent interface
- Range validation
- Expiration window validation
- Circuit breaker validation
- Minimum delay validation
- Agent hub for routing and coordination

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from src.core.validation.base_agent import (
    BaseValidationAgent,
    ValidationResult,
    RangeValidationAgent,
    ExpirationWindowAgent,
    CircuitBreakerAgent,
    MinimumDelayAgent
)

from src.core.validation.agent_hub import (
    ValidationAgentHub,
    AgentConfig,
    create_default_agent_hub
)

__all__ = [
    "BaseValidationAgent",
    "ValidationResult",
    "RangeValidationAgent",
    "ExpirationWindowAgent",
    "CircuitBreakerAgent",
    "MinimumDelayAgent",
    "ValidationAgentHub",
    "AgentConfig",
    "create_default_agent_hub"
]

