"""
Input Sanitization Utilities
Security utilities for sanitizing user inputs and preventing injection attacks

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import html
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize metadata to prevent XSS attacks
    
    Escapes HTML special characters in string values to prevent XSS
    when metadata is displayed in web interfaces.
    
    Args:
        metadata: Metadata dictionary to sanitize
        
    Returns:
        Sanitized metadata dictionary
        
    Example:
        >>> metadata = {"description": "<script>alert('XSS')</script>"}
        >>> sanitized = sanitize_metadata(metadata)
        >>> sanitized["description"]
        "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;"
    """
    if not isinstance(metadata, dict):
        return metadata
    
    sanitized = {}
    for key, value in metadata.items():
        if isinstance(value, str):
            # Escape HTML special characters
            sanitized[key] = html.escape(value)
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_metadata(value)
        elif isinstance(value, list):
            # Sanitize list items
            sanitized[key] = [
                sanitize_metadata(item) if isinstance(item, dict) else html.escape(str(item)) if isinstance(item, str) else item
                for item in value
            ]
        else:
            # Non-string values pass through (numbers, booleans, etc.)
            sanitized[key] = value
    
    return sanitized


def validate_json_depth(
    obj: Any,
    max_depth: int = 10,
    current_depth: int = 0
) -> bool:
    """
    Validate JSON nesting depth to prevent stack overflow
    
    Recursively checks the depth of nested JSON structures and raises
    an error if the maximum depth is exceeded.
    
    Args:
        obj: Object to validate (dict, list, or primitive)
        max_depth: Maximum allowed nesting depth (default: 10)
        current_depth: Current nesting depth (internal use)
        
    Returns:
        True if depth is within limits
        
    Raises:
        ValueError: If nesting depth exceeds maximum
        
    Example:
        >>> deep_dict = {"level": 1}
        >>> for i in range(100):
        ...     deep_dict = {"level": i, "nested": deep_dict}
        >>> validate_json_depth(deep_dict)  # Raises ValueError
    """
    if current_depth > max_depth:
        raise ValueError(
            f"JSON nesting depth ({current_depth}) exceeds maximum allowed depth ({max_depth}). "
            "This may indicate a malicious payload attempting to cause a stack overflow."
        )
    
    if isinstance(obj, dict):
        return all(
            validate_json_depth(value, max_depth, current_depth + 1)
            for value in obj.values()
        )
    elif isinstance(obj, list):
        return all(
            validate_json_depth(item, max_depth, current_depth + 1)
            for item in obj
        )
    
    # Primitive types (str, int, float, bool, None) don't add depth
    return True


def sanitize_receipt_data(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize receipt data for safe processing
    
    Applies multiple sanitization steps:
    1. Validates JSON nesting depth
    2. Sanitizes metadata fields
    3. Validates string lengths
    
    Args:
        receipt_data: Receipt data dictionary
        
    Returns:
        Sanitized receipt data
        
    Raises:
        ValueError: If data fails validation
    """
    # Validate nesting depth
    validate_json_depth(receipt_data, max_depth=10)
    
    # Sanitize metadata if present
    if "metadata" in receipt_data and isinstance(receipt_data["metadata"], dict):
        receipt_data["metadata"] = sanitize_metadata(receipt_data["metadata"])
    
    # Validate and truncate string fields
    string_fields = ["receipt_id", "intelligence_hash", "timestamp"]
    for field in string_fields:
        if field in receipt_data and isinstance(receipt_data[field], str):
            # Limit string length to prevent DoS
            max_length = 1024  # 1KB per field
            if len(receipt_data[field]) > max_length:
                receipt_data[field] = receipt_data[field][:max_length]
    
    return receipt_data


def sanitize_actor_data(actor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize threat actor data
    
    Args:
        actor_data: Threat actor data dictionary
        
    Returns:
        Sanitized actor data
    """
    # Validate nesting depth
    validate_json_depth(actor_data, max_depth=10)
    
    # Sanitize metadata
    if "metadata" in actor_data and isinstance(actor_data["metadata"], dict):
        actor_data["metadata"] = sanitize_metadata(actor_data["metadata"])
    
    return actor_data

