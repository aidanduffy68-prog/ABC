"""
Validation Agent Hub
Central controller for validation agents (inspired by Chaos Agents Hub)

Routes intelligence updates to appropriate validation agents and manages
common validation logic like access control, circuit breakers, and generic checks.

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass

from src.core.validation.base_agent import (
    BaseValidationAgent,
    ValidationResult,
    RangeValidationAgent,
    ExpirationWindowAgent,
    CircuitBreakerAgent,
    MinimumDelayAgent
)


@dataclass
class AgentConfig:
    """Configuration for an agent"""
    agent_id: str
    update_types: List[str]  # Which update types this agent handles
    enabled: bool = True
    priority: int = 0  # Lower = higher priority


class ValidationAgentHub:
    """
    Central hub for managing validation agents
    
    Similar to Chaos Agents Hub:
    - Routes updates to appropriate agents
    - Manages common validation logic
    - Handles access control
    - Manages circuit breakers
    - Validates expiration windows
    - Enforces minimum delays
    """
    
    def __init__(self):
        """Initialize agent hub"""
        self.agents: Dict[str, BaseValidationAgent] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
        self.update_type_routing: Dict[str, List[str]] = {}  # update_type -> [agent_ids]
        self.hub_enabled = True
        
        # Common validation settings
        self.require_timestamp = True
        self.require_actor_id = True
        self.max_update_size_bytes = 10 * 1024 * 1024  # 10MB default
    
    def register_agent(
        self,
        agent: BaseValidationAgent,
        update_types: List[str],
        priority: int = 0
    ):
        """
        Register a validation agent
        
        Args:
            agent: The validation agent to register
            update_types: List of update types this agent handles
            priority: Priority level (lower = higher priority)
        """
        if agent.agent_id in self.agents:
            raise ValueError(f"Agent {agent.agent_id} already registered")
        
        self.agents[agent.agent_id] = agent
        self.agent_configs[agent.agent_id] = AgentConfig(
            agent_id=agent.agent_id,
            update_types=update_types,
            enabled=agent.enabled,
            priority=priority
        )
        
        # Update routing
        for update_type in update_types:
            if update_type not in self.update_type_routing:
                self.update_type_routing[update_type] = []
            self.update_type_routing[update_type].append(agent.agent_id)
        
        # Sort by priority
        for update_type in self.update_type_routing:
            self.update_type_routing[update_type].sort(
                key=lambda aid: self.agent_configs[aid].priority
            )
    
    def validate_update(
        self,
        intelligence_data: Dict[str, Any],
        update_type: str,
        current_state: Optional[Dict[str, Any]] = None,
        allowed_agents: Optional[Set[str]] = None
    ) -> ValidationResult:
        """
        Validate intelligence update through agent hub
        
        Similar to Chaos Agents Hub validation flow:
        1. Generic validations (expiration, size, format)
        2. Route to appropriate agents
        3. Agent-specific validation
        4. Aggregate results
        
        Args:
            intelligence_data: Intelligence update to validate
            update_type: Type of update (e.g., 'risk_score', 'threat_assessment')
            current_state: Current system state (for comparison)
            allowed_agents: Optional set of agent IDs to use (for testing)
        
        Returns:
            ValidationResult with aggregated validation status
        """
        if not self.hub_enabled:
            return ValidationResult(is_valid=True, reason="Hub disabled")
        
        # Step 1: Generic validations (similar to Chaos Agents Hub)
        generic_result = self._validate_generic(intelligence_data, update_type)
        if not generic_result.is_valid:
            return generic_result
        
        # Step 2: Route to appropriate agents
        agent_ids = self._get_agents_for_update_type(update_type, allowed_agents)
        if not agent_ids:
            # No agents registered for this update type - allow by default
            return ValidationResult(
                is_valid=True,
                reason=f"No agents registered for update type: {update_type}"
            )
        
        # Step 3: Run agents in priority order
        all_results = []
        warnings = []
        
        for agent_id in agent_ids:
            agent = self.agents[agent_id]
            config = self.agent_configs[agent_id]
            
            if not config.enabled:
                continue
            
            result = agent.validate(intelligence_data, update_type, current_state)
            all_results.append(result)
            
            if result.warnings:
                warnings.extend(result.warnings)
            
            # If any agent rejects, fail immediately (fail-fast)
            if not result.is_valid:
                return ValidationResult(
                    is_valid=False,
                    reason=f"Agent {agent_id} rejected: {result.reason}",
                    warnings=warnings
                )
        
        # Step 4: Aggregate results (all passed)
        return ValidationResult(
            is_valid=True,
            reason="All validations passed",
            warnings=warnings,
            metadata={
                "agents_checked": len(all_results),
                "update_type": update_type
            }
        )
    
    def _validate_generic(
        self,
        intelligence_data: Dict[str, Any],
        update_type: str
    ) -> ValidationResult:
        """Generic validations (similar to Chaos Agents Hub common logic)"""
        
        # Check required fields
        if self.require_timestamp and "timestamp" not in intelligence_data:
            return ValidationResult(
                is_valid=False,
                reason="Missing required field: timestamp"
            )
        
        if self.require_actor_id and "actor_id" not in intelligence_data:
            return ValidationResult(
                is_valid=False,
                reason="Missing required field: actor_id"
            )
        
        # Check update size
        import json
        try:
            size_bytes = len(json.dumps(intelligence_data).encode('utf-8'))
            if size_bytes > self.max_update_size_bytes:
                return ValidationResult(
                    is_valid=False,
                    reason=(
                        f"Update too large: {size_bytes} bytes "
                        f"(max {self.max_update_size_bytes} bytes)"
                    )
                )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                reason=f"Error calculating update size: {e}"
            )
        
        # Check for duplicate execution (basic check)
        # In production, this would check against a database of executed updates
        # For now, we'll rely on timestamp + actor_id uniqueness
        
        return ValidationResult(is_valid=True)
    
    def _get_agents_for_update_type(
        self,
        update_type: str,
        allowed_agents: Optional[Set[str]] = None
    ) -> List[str]:
        """Get agents that handle this update type"""
        agent_ids = self.update_type_routing.get(update_type, [])
        
        if allowed_agents is not None:
            agent_ids = [aid for aid in agent_ids if aid in allowed_agents]
        
        return agent_ids
    
    def get_hub_status(self) -> Dict[str, Any]:
        """Get hub status and agent statistics"""
        agent_stats = {}
        for agent_id, agent in self.agents.items():
            agent_stats[agent_id] = agent.get_metadata()
        
        return {
            "hub_enabled": self.hub_enabled,
            "total_agents": len(self.agents),
            "enabled_agents": sum(1 for a in self.agents.values() if a.enabled),
            "update_types": list(self.update_type_routing.keys()),
            "agents": agent_stats
        }


def create_default_agent_hub() -> ValidationAgentHub:
    """
    Create default agent hub with standard validation agents
    
    Similar to Chaos Agents factory pattern
    """
    hub = ValidationAgentHub()
    
    # Risk score range validation (0-100)
    risk_range_agent = RangeValidationAgent(
        agent_id="risk_score_range",
        field_name="risk_score",
        min_value=0.0,
        max_value=100.0
    )
    hub.register_agent(risk_range_agent, update_types=["risk_score", "threat_assessment"], priority=1)
    
    # Expiration window (1 hour default)
    expiration_agent = ExpirationWindowAgent(
        agent_id="expiration_window",
        max_age_seconds=3600
    )
    hub.register_agent(expiration_agent, update_types=["risk_score", "threat_assessment"], priority=2)
    
    # Circuit breaker (max 50% change)
    circuit_breaker_agent = CircuitBreakerAgent(
        agent_id="circuit_breaker",
        max_change_percent=50.0
    )
    hub.register_agent(circuit_breaker_agent, update_types=["risk_score"], priority=3)
    
    # Minimum delay (1 minute between updates)
    min_delay_agent = MinimumDelayAgent(
        agent_id="minimum_delay",
        min_delay_seconds=60
    )
    hub.register_agent(min_delay_agent, update_types=["risk_score", "threat_assessment"], priority=4)
    
    return hub

