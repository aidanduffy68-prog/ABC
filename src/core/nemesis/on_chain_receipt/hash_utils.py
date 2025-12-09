"""
Hash Utility Functions
Provides both SHA-256 and BLAKE2b hashing options

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import hashlib
from typing import Union


def hash_data(data: Union[str, bytes], algorithm: str = "sha256", digest_size: int = 32) -> str:
    """
    Hash data using specified algorithm
    
    Args:
        data: Data to hash (string or bytes)
        algorithm: Hash algorithm ("sha256" or "blake2b")
        digest_size: Digest size in bytes (for BLAKE2b, default 32)
        
    Returns:
        Hexadecimal hash string
        
    Example:
        >>> hash_data("test", "sha256")
        '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'
        >>> hash_data("test", "blake2b")
        '...'
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if algorithm.lower() == "blake2b":
        return hashlib.blake2b(data, digest_size=digest_size).hexdigest()
    elif algorithm.lower() == "sha256":
        return hashlib.sha256(data).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Use 'sha256' or 'blake2b'")


def hash_canonical_json(data: dict, algorithm: str = "sha256") -> str:
    """
    Hash dictionary using canonical JSON representation
    
    Args:
        data: Dictionary to hash
        algorithm: Hash algorithm ("sha256" or "blake2b")
        
    Returns:
        Hexadecimal hash string
    """
    import json
    from datetime import datetime
    from enum import Enum
    from dataclasses import asdict
    
    def json_serializer(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value if hasattr(obj, 'value') else str(obj)
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def make_serializable(obj):
        """Recursively convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {str(k): make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value if hasattr(obj, 'value') else str(obj)
        elif hasattr(obj, '__dataclass_fields__'):
            return make_serializable(asdict(obj))
        elif hasattr(obj, '__dict__'):
            try:
                return make_serializable(obj.__dict__)
            except:
                return str(obj)
        else:
            return obj
    
    serializable_data = make_serializable(data)
    canonical_json = json.dumps(
        serializable_data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(',', ':'),
        default=json_serializer
    )
    
    return hash_data(canonical_json, algorithm=algorithm)


def compare_hashes_constant_time(hash1: Union[str, bytes], hash2: Union[str, bytes]) -> bool:
    """
    Compare two hashes using constant-time comparison
    
    Prevents timing attacks by using secrets.compare_digest()
    
    Args:
        hash1: First hash (string or bytes)
        hash2: Second hash (string or bytes)
        
    Returns:
        True if hashes match, False otherwise
    """
    import secrets
    
    # Convert to bytes if strings
    if isinstance(hash1, str):
        hash1 = hash1.encode('utf-8')
    if isinstance(hash2, str):
        hash2 = hash2.encode('utf-8')
    
    return secrets.compare_digest(hash1, hash2)

