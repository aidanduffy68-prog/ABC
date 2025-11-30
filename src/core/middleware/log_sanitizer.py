"""
Log Sanitization Utility
Removes sensitive data from logs before writing

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import re
import json
from typing import Any, Dict, List


# Patterns for sensitive data
SENSITIVE_PATTERNS = [
    (r'api_key["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'api_key="***REDACTED***"'),
    (r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'password="***REDACTED***"'),
    (r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'secret="***REDACTED***"'),
    (r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'token="***REDACTED***"'),
    (r'credential["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'credential="***REDACTED***"'),
    (r'private_key["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'private_key="***REDACTED***"'),
    (r'authorization["\']?\s*[:=]\s*["\']?([^"\'\s]+)', r'authorization="***REDACTED***"'),
    (r'Bearer\s+([A-Za-z0-9\-_\.]+)', r'Bearer ***REDACTED***'),
    # Credit card patterns
    (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', r'****-****-****-****'),
    # SSN patterns
    (r'\b\d{3}-\d{2}-\d{4}\b', r'***-**-****'),
]


def sanitize_string(text: str) -> str:
    """
    Sanitize a string by removing sensitive patterns
    
    Args:
        text: String to sanitize
        
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        return text
    
    sanitized = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize a dictionary
    
    Args:
        data: Dictionary to sanitize
        
    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    sensitive_keys = ['api_key', 'password', 'secret', 'token', 'credential', 
                     'private_key', 'authorization', 'auth', 'key']
    
    for key, value in data.items():
        # Check if key is sensitive
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = '***REDACTED***'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_dict(item) if isinstance(item, dict) else sanitize_string(str(item)) for item in value]
        elif isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        else:
            sanitized[key] = value
    
    return sanitized


def sanitize_json(data: Any) -> str:
    """
    Sanitize data and convert to JSON string
    
    Args:
        data: Data to sanitize (dict, list, etc.)
        
    Returns:
        Sanitized JSON string
    """
    if isinstance(data, dict):
        sanitized = sanitize_dict(data)
    elif isinstance(data, list):
        sanitized = [sanitize_dict(item) if isinstance(item, dict) else sanitize_string(str(item)) for item in data]
    else:
        sanitized = sanitize_string(str(data))
    
    try:
        return json.dumps(sanitized, default=str)
    except (TypeError, ValueError):
        return str(sanitized)


# Example usage in logging
def safe_log(logger, level: str, message: str, *args, **kwargs):
    """
    Safe logging function that sanitizes data
    
    Usage:
        safe_log(logger, 'info', 'Processing request: %s', request_data)
    """
    # Sanitize message
    sanitized_message = sanitize_string(message)
    
    # Sanitize args
    sanitized_args = [sanitize_string(str(arg)) if isinstance(arg, str) else arg for arg in args]
    
    # Sanitize kwargs
    sanitized_kwargs = {k: sanitize_dict(v) if isinstance(v, dict) else sanitize_string(str(v)) 
                       for k, v in kwargs.items()}
    
    # Log with sanitized data
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(sanitized_message, *sanitized_args, **sanitized_kwargs)

