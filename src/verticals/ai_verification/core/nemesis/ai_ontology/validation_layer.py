"""
Validation Layer - Sanity checks before graph insertion
Validates wallet existence, schema compliance, confidence thresholds
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class ValidationResult:
    """Result of entity validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    confidence_adjusted: Optional[float] = None


class ValidationLayer:
    """
    Validates entities before graph insertion
    Prevents bad data from entering the graph
    """
    
    def __init__(self):
        self.confidence_threshold_high = 0.95  # Auto-insert threshold
        self.confidence_threshold_medium = 0.80  # Human review threshold
        self.confidence_threshold_low = 0.80  # Reject threshold
    
    def validate_entity(
        self,
        entity_type: str,
        entity_data: Dict[str, Any],
        confidence: float,
        source_id: str
    ) -> ValidationResult:
        """
        Validate an entity before graph insertion
        
        Args:
            entity_type: Type of entity (actor, event, pattern, etc.)
            entity_data: Entity data to validate
            confidence: Confidence score
            source_id: Source document ID
        
        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        warnings = []
        
        # Confidence threshold check
        if confidence < self.confidence_threshold_low:
            errors.append(f"Confidence {confidence:.2f} below minimum threshold {self.confidence_threshold_low}")
        
        # Entity type-specific validation
        if entity_type == "actor":
            result = self._validate_actor(entity_data, errors, warnings)
        elif entity_type == "event":
            result = self._validate_event(entity_data, errors, warnings)
        elif entity_type == "pattern":
            result = self._validate_pattern(entity_data, errors, warnings)
        else:
            errors.append(f"Unknown entity type: {entity_type}")
            result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Schema validation
        schema_errors = self._validate_schema(entity_type, entity_data)
        errors.extend(schema_errors)
        
        # On-chain validation for wallets
        if entity_type == "actor" and entity_data.get("type") == "wallet":
            wallet_errors = self._validate_wallet_exists(entity_data)
            errors.extend(wallet_errors)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            confidence_adjusted=confidence if is_valid else None
        )
    
    def _validate_actor(self, entity_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> ValidationResult:
        """Validate actor entity"""
        # Required fields
        if "actor_id" not in entity_data:
            errors.append("Missing required field: actor_id")
        if "name" not in entity_data:
            errors.append("Missing required field: name")
        if "type" not in entity_data:
            errors.append("Missing required field: type")
        
        # Type validation
        valid_types = ["wallet", "individual", "organization", "nation_state", "service_provider"]
        if "type" in entity_data and entity_data["type"] not in valid_types:
            errors.append(f"Invalid actor type: {entity_data['type']}. Must be one of {valid_types}")
        
        # Wallet address validation
        if entity_data.get("type") == "wallet" and "address" in entity_data:
            address = entity_data["address"]
            if not self._is_valid_wallet_address(address):
                errors.append(f"Invalid wallet address format: {address}")
        
        # Risk score validation
        if "risk_score" in entity_data:
            risk_score = entity_data["risk_score"]
            if not isinstance(risk_score, (int, float)) or not (0 <= risk_score <= 1):
                errors.append(f"Invalid risk_score: {risk_score}. Must be float between 0 and 1")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_event(self, entity_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> ValidationResult:
        """Validate event entity"""
        # Required fields
        if "event_id" not in entity_data:
            errors.append("Missing required field: event_id")
        if "event_type" not in entity_data:
            errors.append("Missing required field: event_type")
        if "timestamp" not in entity_data:
            errors.append("Missing required field: timestamp")
        
        # Timestamp validation
        if "timestamp" in entity_data:
            timestamp = entity_data["timestamp"]
            if not self._is_valid_timestamp(timestamp):
                warnings.append(f"Timestamp format may be invalid: {timestamp}")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_pattern(self, entity_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> ValidationResult:
        """Validate pattern entity"""
        # Required fields
        if "pattern_id" not in entity_data:
            errors.append("Missing required field: pattern_id")
        if "category" not in entity_data:
            errors.append("Missing required field: category")
        if "description" not in entity_data:
            errors.append("Missing required field: description")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_schema(self, entity_type: str, entity_data: Dict[str, Any]) -> List[str]:
        """Validate entity matches schema"""
        errors = []
        
        # Basic schema validation
        if not isinstance(entity_data, dict):
            errors.append("Entity data must be a dictionary")
            return errors
        
        # Type-specific schema checks
        if entity_type == "actor":
            required = ["actor_id", "name", "type"]
        elif entity_type == "event":
            required = ["event_id", "event_type", "timestamp"]
        elif entity_type == "pattern":
            required = ["pattern_id", "category", "description"]
        else:
            return errors
        
        for field in required:
            if field not in entity_data:
                errors.append(f"Missing required schema field: {field}")
        
        return errors
    
    def _validate_wallet_exists(self, entity_data: Dict[str, Any]) -> List[str]:
        """
        Validate wallet exists on-chain
        TODO: Implement actual on-chain check via RPC call
        """
        errors = []
        address = entity_data.get("address")
        
        if not address:
            return errors
        
        # Basic format validation (actual existence check would require RPC)
        if not self._is_valid_wallet_address(address):
            errors.append(f"Invalid wallet address format: {address}")
        
        # TODO: Add actual on-chain existence check
        # Example: Check if address has any transactions or balance > 0
        
        return errors
    
    def _is_valid_wallet_address(self, address: str) -> bool:
        """Check if wallet address has valid format"""
        # Ethereum address format
        if re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return True
        
        # Bitcoin address format (basic check)
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return True
        
        # Add other chain formats as needed
        return False
    
    def _is_valid_timestamp(self, timestamp: Any) -> bool:
        """Check if timestamp is valid format"""
        if isinstance(timestamp, (int, float)):
            return True  # Unix timestamp
        
        if isinstance(timestamp, str):
            # ISO format
            if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', timestamp):
                return True
            # Date format
            if re.match(r'^\d{4}-\d{2}-\d{2}$', timestamp):
                return True
        
        return False
    
    def get_review_status(self, confidence: float) -> str:
        """
        Determine review status based on confidence
        
        Returns:
            "auto" (≥0.95), "pending" (0.80-0.94), "rejected" (<0.80)
        """
        if confidence >= self.confidence_threshold_high:
            return "auto"
        elif confidence >= self.confidence_threshold_medium:
            return "pending"
        else:
            return "rejected"

