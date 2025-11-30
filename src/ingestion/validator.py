"""
Ingestion Validator
Validates vendor feeds before compilation
Compiler fails if syntax is wrong (like a real compiler)

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from src.schemas.actor_schema import Actor, Event, Pattern, TargetingPackage


@dataclass
class ValidationError:
    """Validation error with context"""
    field: str
    error_type: str
    message: str
    value: Any = None


class IngestionValidator:
    """
    Validates vendor feed data before compilation
    Throws clear errors if data is invalid (compiler behavior)
    """
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
    
    def validate_vendor_feed(
        self,
        feed_data: Dict[str, Any],
        vendor_name: str
    ) -> tuple[bool, List[ValidationError], List[str]]:
        """
        Validate vendor feed data
        
        Args:
            feed_data: Vendor feed data (JSON-like structure)
            vendor_name: Name of vendor (Chainalysis, TRM, Chaos, etc.)
        
        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Basic structure validation
        if not isinstance(feed_data, dict):
            self.errors.append(ValidationError(
                field="root",
                error_type="type_error",
                message="Feed data must be a dictionary/object",
                value=type(feed_data).__name__
            ))
            return False, self.errors, self.warnings
        
        # Check for required top-level fields
        required_fields = ["vendor", "timestamp", "data"]
        for field in required_fields:
            if field not in feed_data:
                self.errors.append(ValidationError(
                    field=field,
                    error_type="missing_field",
                    message=f"Required field '{field}' is missing",
                    value=None
                ))
        
        # Validate vendor name matches
        if "vendor" in feed_data and feed_data["vendor"] != vendor_name:
            self.warnings.append(f"Vendor name mismatch: expected '{vendor_name}', got '{feed_data['vendor']}'")
        
        # Validate timestamp
        if "timestamp" in feed_data:
            self._validate_timestamp(feed_data["timestamp"])
        
        # Validate data array
        if "data" in feed_data:
            self._validate_data_array(feed_data["data"], vendor_name)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def validate_actor(self, actor_data: Dict[str, Any]) -> tuple[bool, List[ValidationError]]:
        """
        Validate actor entity using Pydantic schema
        
        Args:
            actor_data: Actor data dictionary
        
        Returns:
            (is_valid, errors)
        """
        try:
            Actor(**actor_data)
            return True, []
        except Exception as e:
            error = ValidationError(
                field="actor",
                error_type="schema_validation_error",
                message=str(e),
                value=actor_data
            )
            return False, [error]
    
    def validate_event(self, event_data: Dict[str, Any]) -> tuple[bool, List[ValidationError]]:
        """Validate event entity using Pydantic schema"""
        try:
            Event(**event_data)
            return True, []
        except Exception as e:
            error = ValidationError(
                field="event",
                error_type="schema_validation_error",
                message=str(e),
                value=event_data
            )
            return False, [error]
    
    def validate_pattern(self, pattern_data: Dict[str, Any]) -> tuple[bool, List[ValidationError]]:
        """Validate pattern entity using Pydantic schema"""
        try:
            Pattern(**pattern_data)
            return True, []
        except Exception as e:
            error = ValidationError(
                field="pattern",
                error_type="schema_validation_error",
                message=str(e),
                value=pattern_data
            )
            return False, [error]
    
    def _validate_timestamp(self, timestamp: Any):
        """Validate timestamp format"""
        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            if timestamp < 0 or timestamp > 2147483647:  # Reasonable range
                self.errors.append(ValidationError(
                    field="timestamp",
                    error_type="invalid_timestamp",
                    message="Timestamp out of valid range",
                    value=timestamp
                ))
        elif isinstance(timestamp, str):
            # ISO format
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                self.errors.append(ValidationError(
                    field="timestamp",
                    error_type="invalid_timestamp_format",
                    message="Timestamp must be ISO format or Unix timestamp",
                    value=timestamp
                ))
        else:
            self.errors.append(ValidationError(
                field="timestamp",
                error_type="invalid_timestamp_type",
                message="Timestamp must be string (ISO) or number (Unix)",
                value=type(timestamp).__name__
            ))
    
    def _validate_data_array(self, data: Any, vendor_name: str):
        """Validate data array structure"""
        if not isinstance(data, list):
            self.errors.append(ValidationError(
                field="data",
                error_type="type_error",
                message="Data field must be an array",
                value=type(data).__name__
            ))
            return
        
        if len(data) == 0:
            self.warnings.append("Data array is empty")
            return
        
        # Validate each item in array
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                self.errors.append(ValidationError(
                    field=f"data[{i}]",
                    error_type="type_error",
                    message="Data array items must be objects",
                    value=type(item).__name__
                ))
                continue
            
            # Check for entity type
            if "entity_type" not in item:
                self.errors.append(ValidationError(
                    field=f"data[{i}].entity_type",
                    error_type="missing_field",
                    message="Entity type is required",
                    value=None
                ))
    
    def format_errors(self) -> str:
        """Format errors as human-readable string"""
        if not self.errors:
            return "No errors"
        
        lines = ["Validation Errors:"]
        for error in self.errors:
            lines.append(f"  - {error.field}: {error.message}")
            if error.value is not None:
                lines.append(f"    Value: {error.value}")
        
        return "\n".join(lines)


def validate_vendor_feed(feed_data: Dict[str, Any], vendor_name: str) -> tuple[bool, List[ValidationError], List[str]]:
    """
    Convenience function to validate vendor feed
    
    Usage:
        is_valid, errors, warnings = validate_vendor_feed(feed_data, "Chainalysis")
        if not is_valid:
            print(validator.format_errors())
    """
    validator = IngestionValidator()
    return validator.validate_vendor_feed(feed_data, vendor_name)

