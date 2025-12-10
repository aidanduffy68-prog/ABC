"""
Base Validation Agent
Inspired by Chaos Labs' Agent pattern for modular validation

Each agent validates one specific type of intelligence update before compilation.
Agents are lightweight, single-purpose, and follow a standard interface.

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of agent validation"""
    is_valid: bool
    reason: Optional[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


class BaseValidationAgent(ABC):
    """
    Base class for validation agents
    
    Each agent validates one specific aspect of intelligence updates:
    - Risk score validation
    - Expiration window validation
    - Circuit breaker validation
    - Range validation
    - Timing validation
    
    Inspired by Chaos Labs' agent pattern:
    - One agent = one validation type
    - Lightweight and single-purpose
    - Standard interface: validate(), get_metadata()
    """
    
    def __init__(self, agent_id: str, enabled: bool = True):
        """
        Initialize validation agent
        
        Args:
            agent_id: Unique identifier for this agent
            enabled: Whether agent is active
        """
        self.agent_id = agent_id
        self.enabled = enabled
        self.validation_count = 0
        self.rejection_count = 0
    
    @abstractmethod
    def validate(
        self,
        intelligence_data: Dict[str, Any],
        update_type: str,
        current_state: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate intelligence update
        
        Args:
            intelligence_data: The intelligence update to validate
            update_type: Type of update (e.g., 'risk_score', 'threat_assessment')
            current_state: Current state of the system (for comparison)
        
        Returns:
            ValidationResult indicating if update is valid
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get agent metadata (similar to Chaos Agents' getMarkets())
        
        Returns:
            Dictionary with agent configuration and stats
        """
        return {
            "agent_id": self.agent_id,
            "enabled": self.enabled,
            "validation_count": self.validation_count,
            "rejection_count": self.rejection_count,
            "rejection_rate": (
                self.rejection_count / self.validation_count
                if self.validation_count > 0
                else 0.0
            )
        }
    
    def _record_validation(self, result: ValidationResult):
        """Record validation attempt"""
        self.validation_count += 1
        if not result.is_valid:
            self.rejection_count += 1


class RangeValidationAgent(BaseValidationAgent):
    """
    Validates that values are within acceptable ranges
    
    Similar to Chaos Labs' RangeValidationModule
    """
    
    def __init__(
        self,
        agent_id: str,
        field_name: str,
        min_value: float,
        max_value: float,
        enabled: bool = True
    ):
        super().__init__(agent_id, enabled)
        self.field_name = field_name
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(
        self,
        intelligence_data: Dict[str, Any],
        update_type: str,
        current_state: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate that field is within range"""
        if not self.enabled:
            return ValidationResult(is_valid=True, reason="Agent disabled")
        
        value = intelligence_data.get(self.field_name)
        if value is None:
            result = ValidationResult(
                is_valid=False,
                reason=f"Missing required field: {self.field_name}"
            )
            self._record_validation(result)
            return result
        
        try:
            value_float = float(value)
        except (ValueError, TypeError):
            result = ValidationResult(
                is_valid=False,
                reason=f"Invalid value type for {self.field_name}: {type(value)}"
            )
            self._record_validation(result)
            return result
        
        if value_float < self.min_value or value_float > self.max_value:
            result = ValidationResult(
                is_valid=False,
                reason=(
                    f"{self.field_name} ({value_float}) outside valid range "
                    f"[{self.min_value}, {self.max_value}]"
                )
            )
            self._record_validation(result)
            return result
        
        result = ValidationResult(is_valid=True)
        self._record_validation(result)
        return result


class ExpirationWindowAgent(BaseValidationAgent):
    """
    Validates that intelligence updates are within expiration window
    
    Similar to Chaos Agents' expiration window validation
    """
    
    def __init__(
        self,
        agent_id: str,
        max_age_seconds: int = 3600,  # 1 hour default
        enabled: bool = True
    ):
        super().__init__(agent_id, enabled)
        self.max_age_seconds = max_age_seconds
    
    def validate(
        self,
        intelligence_data: Dict[str, Any],
        update_type: str,
        current_state: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate expiration window"""
        if not self.enabled:
            return ValidationResult(is_valid=True, reason="Agent disabled")
        
        timestamp_str = intelligence_data.get("timestamp")
        if timestamp_str is None:
            result = ValidationResult(
                is_valid=False,
                reason="Missing timestamp in intelligence data"
            )
            self._record_validation(result)
            return result
        
        try:
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            elif isinstance(timestamp_str, datetime):
                timestamp = timestamp_str
            else:
                result = ValidationResult(
                    is_valid=False,
                    reason=f"Invalid timestamp type: {type(timestamp_str)}"
                )
                self._record_validation(result)
                return result
        except (ValueError, AttributeError) as e:
            result = ValidationResult(
                is_valid=False,
                reason=f"Invalid timestamp format: {e}"
            )
            self._record_validation(result)
            return result
        
        now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
        age = (now - timestamp).total_seconds()
        
        if age > self.max_age_seconds:
            result = ValidationResult(
                is_valid=False,
                reason=(
                    f"Intelligence expired: {age:.0f}s old "
                    f"(max {self.max_age_seconds}s)"
                )
            )
            self._record_validation(result)
            return result
        
        if age < 0:
            result = ValidationResult(
                is_valid=False,
                reason="Intelligence timestamp is in the future"
            )
            self._record_validation(result)
            return result
        
        result = ValidationResult(
            is_valid=True,
            metadata={"age_seconds": age}
        )
        self._record_validation(result)
        return result


class CircuitBreakerAgent(BaseValidationAgent):
    """
    Circuit breaker to prevent extreme risk score changes
    
    Similar to Chaos Agents' circuit breaker management
    """
    
    def __init__(
        self,
        agent_id: str,
        max_change_percent: float = 50.0,  # Max 50% change
        enabled: bool = True
    ):
        super().__init__(agent_id, enabled)
        self.max_change_percent = max_change_percent
    
    def validate(
        self,
        intelligence_data: Dict[str, Any],
        update_type: str,
        current_state: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate that risk score change is within limits"""
        if not self.enabled:
            return ValidationResult(is_valid=True, reason="Agent disabled")
        
        new_risk_score = intelligence_data.get("risk_score")
        if new_risk_score is None:
            result = ValidationResult(
                is_valid=False,
                reason="Missing risk_score in intelligence data"
            )
            self._record_validation(result)
            return result
        
        try:
            new_score = float(new_risk_score)
        except (ValueError, TypeError):
            result = ValidationResult(
                is_valid=False,
                reason=f"Invalid risk_score type: {type(new_risk_score)}"
            )
            self._record_validation(result)
            return result
        
        # If no current state, allow first update
        if current_state is None:
            result = ValidationResult(is_valid=True, reason="First update (no current state)")
            self._record_validation(result)
            return result
        
        current_risk_score = current_state.get("risk_score")
        if current_risk_score is None:
            result = ValidationResult(is_valid=True, reason="No current risk score to compare")
            self._record_validation(result)
            return result
        
        try:
            current_score = float(current_risk_score)
        except (ValueError, TypeError):
            result = ValidationResult(is_valid=True, reason="Invalid current risk score format")
            self._record_validation(result)
            return result
        
        # Calculate percent change
        if current_score == 0:
            change_percent = 100.0 if new_score > 0 else 0.0
        else:
            change_percent = abs((new_score - current_score) / current_score) * 100
        
        if change_percent > self.max_change_percent:
            result = ValidationResult(
                is_valid=False,
                reason=(
                    f"Risk score change too large: {change_percent:.1f}% "
                    f"(max {self.max_change_percent}%). "
                    f"Current: {current_score:.2f}, New: {new_score:.2f}"
                ),
                warnings=[f"Large change detected: {change_percent:.1f}%"]
            )
            self._record_validation(result)
            return result
        
        result = ValidationResult(
            is_valid=True,
            metadata={"change_percent": change_percent}
        )
        self._record_validation(result)
        return result


class MinimumDelayAgent(BaseValidationAgent):
    """
    Enforces minimum delay between updates
    
    Similar to Chaos Agents' minimumDelay validation
    """
    
    def __init__(
        self,
        agent_id: str,
        min_delay_seconds: int = 60,  # 1 minute default
        enabled: bool = True
    ):
        super().__init__(agent_id, enabled)
        self.min_delay_seconds = min_delay_seconds
        self.last_update_time: Dict[str, datetime] = {}
    
    def validate(
        self,
        intelligence_data: Dict[str, Any],
        update_type: str,
        current_state: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate minimum delay between updates"""
        if not self.enabled:
            return ValidationResult(is_valid=True, reason="Agent disabled")
        
        actor_id = intelligence_data.get("actor_id")
        if actor_id is None:
            result = ValidationResult(
                is_valid=False,
                reason="Missing actor_id for minimum delay validation"
            )
            self._record_validation(result)
            return result
        
        now = datetime.now()
        last_update = self.last_update_time.get(actor_id)
        
        if last_update is not None:
            delay = (now - last_update).total_seconds()
            if delay < self.min_delay_seconds:
                result = ValidationResult(
                    is_valid=False,
                    reason=(
                        f"Update too soon: {delay:.0f}s since last update "
                        f"(min {self.min_delay_seconds}s required)"
                    )
                )
                self._record_validation(result)
                return result
        
        # Update last update time
        self.last_update_time[actor_id] = now
        
        result = ValidationResult(
            is_valid=True,
            metadata={"delay_seconds": (now - last_update).total_seconds() if last_update else None}
        )
        self._record_validation(result)
        return result

