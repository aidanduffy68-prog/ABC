"""
Key Derivation Functions
PBKDF2 and Argon2 key derivation for secure key generation

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import os
import hashlib
from typing import Optional, Union
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def derive_key_pbkdf2(
    master_key: Union[str, bytes],
    salt: Optional[bytes] = None,
    length: int = 32,
    iterations: int = 100000,
    algorithm: hashes.HashAlgorithm = hashes.SHA256()
) -> tuple[bytes, bytes]:
    """
    Derive encryption key from master key using PBKDF2
    
    PBKDF2 (Password-Based Key Derivation Function 2) is a widely-used
    key derivation function that's secure and standardized.
    
    Args:
        master_key: Master key (password or key material) as string or bytes
        salt: Salt for key derivation (random bytes). If None, generates new salt.
        length: Desired key length in bytes (default: 32 bytes = 256 bits)
        iterations: Number of iterations (default: 100,000). Higher = more secure but slower.
        algorithm: Hash algorithm to use (default: SHA256)
        
    Returns:
        Tuple of (derived_key, salt) - both as bytes
        
    Example:
        >>> key, salt = derive_key_pbkdf2("master_password", iterations=100000)
        >>> # Use key for encryption, store salt for later key derivation
    """
    if isinstance(master_key, str):
        master_key = master_key.encode('utf-8')
    
    if salt is None:
        # Generate random salt
        salt = os.urandom(16)  # 128-bit salt
    
    kdf = PBKDF2HMAC(
        algorithm=algorithm,
        length=length,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    
    derived_key = kdf.derive(master_key)
    return derived_key, salt


def derive_key_argon2(
    master_key: Union[str, bytes],
    salt: Optional[bytes] = None,
    length: int = 32,
    time_cost: int = 3,
    memory_cost: int = 65536,  # 64 MB
    parallelism: int = 4
) -> tuple[bytes, bytes]:
    """
    Derive encryption key from master key using Argon2
    
    Argon2 is the winner of the Password Hashing Competition and is
    more secure than PBKDF2, but requires the argon2-cffi library.
    
    Args:
        master_key: Master key (password or key material) as string or bytes
        salt: Salt for key derivation (random bytes). If None, generates new salt.
        length: Desired key length in bytes (default: 32 bytes = 256 bits)
        time_cost: Number of iterations (default: 3)
        memory_cost: Memory cost in KB (default: 65536 = 64 MB)
        parallelism: Number of parallel threads (default: 4)
        
    Returns:
        Tuple of (derived_key, salt) - both as bytes
        
    Raises:
        ImportError: If argon2-cffi is not installed
        
    Example:
        >>> key, salt = derive_key_argon2("master_password")
        >>> # Argon2 is more secure but requires: pip install argon2-cffi
    """
    try:
        import argon2
    except ImportError:
        raise ImportError(
            "argon2-cffi required for Argon2 key derivation. "
            "Install with: pip install argon2-cffi"
        )
    
    if isinstance(master_key, str):
        master_key = master_key.encode('utf-8')
    
    if salt is None:
        salt = os.urandom(16)  # 128-bit salt
    
    # Use Argon2id (hybrid of Argon2i and Argon2d)
    argon2_hasher = argon2.PasswordHasher(
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=length
    )
    
    # Argon2 expects password and salt, returns full hash
    # We'll extract just the key portion
    hash_result = argon2.low_level.hash_secret(
        master_key,
        salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=length,
        type=argon2.low_level.Type.ID
    )
    
    # Extract the actual key from Argon2 hash
    # Argon2 format: $argon2id$v=19$m=...,t=...,p=...$salt$hash
    # We just need the hash portion
    derived_key = hash_result[-length:]  # Last 'length' bytes are the key
    
    return derived_key, salt


def generate_key_from_password(
    password: str,
    salt: Optional[bytes] = None,
    use_argon2: bool = False,
    **kwargs
) -> tuple[bytes, bytes]:
    """
    Generate encryption key from password
    
    Convenience function that chooses PBKDF2 or Argon2 based on preference.
    
    Args:
        password: Password string
        salt: Salt bytes (if None, generates new salt)
        use_argon2: If True, use Argon2 (more secure). If False, use PBKDF2 (default).
        **kwargs: Additional arguments passed to derivation function
        
    Returns:
        Tuple of (derived_key, salt) - both as bytes
        
    Example:
        >>> key, salt = generate_key_from_password("my_password")
        >>> key2, salt2 = generate_key_from_password("my_password", use_argon2=True)
    """
    if use_argon2:
        return derive_key_argon2(password, salt=salt, **kwargs)
    else:
        return derive_key_pbkdf2(password, salt=salt, **kwargs)


def verify_key_derivation(
    master_key: Union[str, bytes],
    derived_key: bytes,
    salt: bytes,
    use_argon2: bool = False,
    **kwargs
) -> bool:
    """
    Verify that derived key matches master key and salt
    
    Args:
        master_key: Original master key
        derived_key: Previously derived key to verify
        salt: Salt used in original derivation
        use_argon2: Whether Argon2 was used (must match original)
        **kwargs: Additional arguments (must match original)
        
    Returns:
        True if key matches, False otherwise
    """
    new_key, _ = generate_key_from_password(
        master_key if isinstance(master_key, str) else master_key.decode('utf-8'),
        salt=salt,
        use_argon2=use_argon2,
        **kwargs
    )
    
    # Constant-time comparison
    import secrets
    return secrets.compare_digest(new_key, derived_key)


def generate_salt(length: int = 16) -> bytes:
    """
    Generate cryptographically secure random salt
    
    Args:
        length: Salt length in bytes (default: 16 = 128 bits)
        
    Returns:
        Random salt bytes
    """
    return os.urandom(length)

