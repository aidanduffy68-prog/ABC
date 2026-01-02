"""
Shared cryptographic receipt generation (adapter for existing receipt generator)

This module provides a unified interface to the existing CryptographicReceiptGenerator
for use by both Intelligence and Oracle layers without duplicating code.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import hashlib
import secrets
import uuid

# Import existing receipt generator
from src.verticals.ai_verification.core.nemesis.on_chain_receipt.receipt_generator import (
    CryptographicReceiptGenerator as BaseReceiptGenerator,
    IntelligenceReceipt as BaseIntelligenceReceipt
)

# Re-export the existing classes for backward compatibility
IntelligenceReceipt = BaseIntelligenceReceipt


class CryptographicReceiptGenerator:
    """
    Adapter for existing receipt generator that provides unified interface
    for both Intelligence and Oracle layers.
    
    **ABC verifies inputs, not outputs. ABC is infrastructure for verification, not
    decision-making. Humans stay in the loop where it matters.**
    
    This wraps the existing receipt generator to maintain backward compatibility
    while providing a consistent API for oracle layer usage. Receipts prove data
    integrity - they do not validate correctness of analysis or conclusions.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize receipt generator adapter.
        
        Args:
            **kwargs: Arguments passed to base receipt generator
        """
        self._generator = BaseReceiptGenerator(**kwargs)
    
    def generate_data_hash(self, data: Any) -> str:
        """
        Generate SHA-256 hash of data.
        
        Args:
            data: Data to hash (dict, list, or string)
            
        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, (dict, list)):
            # Normalize JSON for deterministic hashing
            normalized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            normalized = str(data)
        
        hash_object = hashlib.sha256(normalized.encode('utf-8'))
        return hash_object.hexdigest()
    
    def generate_receipt(
        self,
        data: Any,
        source: str,
        classification: str = "UNCLASSIFIED",
        blockchain: Optional[str] = None,
        **kwargs
    ) -> BaseIntelligenceReceipt:
        """
        Generate cryptographic receipt for data.
        
        Args:
            data: Data to generate receipt for
            source: Source identifier (e.g., "bitcoin_block_825000")
            classification: Data classification level
            blockchain: Blockchain to anchor to (optional)
            **kwargs: Additional arguments for base generator
            
        Returns:
            IntelligenceReceipt object
        """
        # Generate hash of data
        data_hash = self.generate_data_hash(data)
        
        # Use existing generator to create receipt
        # Map our parameters to the existing generator's expected format
        intelligence_data = {
            "data": data,
            "source": source,
            "classification": classification
        }
        
        # Generate receipt using existing generator
        # Disable validation and payment for oracle receipts
        receipt = self._generator.generate_receipt(
            intelligence_package=intelligence_data,
            package_type="oracle_data" if "oracle" in source.lower() or "bitcoin" in source.lower() else "intelligence",
            threat_level="INFO",
            foundry_compilation_id=None,
            foundry_hash=None,
            foundry_timestamp=None,
            validate_before_publish=False,
            require_payment_settlement=False,
            **kwargs
        )
        
        # If blockchain specified, add blockchain anchor info to metadata
        if blockchain:
            if receipt.metadata is None:
                receipt.metadata = {}
            receipt.metadata['blockchain'] = blockchain
            receipt.metadata['blockchain_anchor'] = {
                "network": blockchain,
                "status": "pending"
            }
        
        return receipt
    
    def verify_receipt(self, receipt: BaseIntelligenceReceipt, data: Any) -> bool:
        """
        Verify receipt matches data.
        
        Args:
            receipt: Receipt to verify
            data: Data to verify against
            
        Returns:
            True if receipt is valid for data
        """
        computed_hash = self.generate_data_hash(data)
        return computed_hash == receipt.intelligence_hash


# Convenience functions for ABC receipt operations
def generate_abc_receipt(blockchain_data: Dict[str, Any], **kwargs) -> BaseIntelligenceReceipt:
    """
    Generate SHA-256 hash of blockchain data and create ABC receipt.
    
    This is a convenience wrapper for generating cryptographic receipts
    for blockchain data verification.
    
    Args:
        blockchain_data: Blockchain data dictionary to hash
        **kwargs: Additional arguments for receipt generation
                 (e.g., source, classification, blockchain)
        
    Returns:
        IntelligenceReceipt with cryptographic proof
        
    Example:
        >>> receipt = generate_abc_receipt(
        ...     {"block": 825000, "hash": "0x123..."},
        ...     source="bitcoin_block_825000",
        ...     blockchain="bitcoin"
        ... )
    """
    # Extract receipt generator kwargs (don't pass source/classification/blockchain to constructor)
    generator_kwargs = {k: v for k, v in kwargs.items() 
                       if k not in ['source', 'classification', 'blockchain']}
    generator = CryptographicReceiptGenerator(**generator_kwargs)
    
    source = kwargs.get("source", "blockchain_data")
    classification = kwargs.get("classification", "UNCLASSIFIED")
    blockchain = kwargs.get("blockchain", None)
    
    return generator.generate_receipt(
        data=blockchain_data,
        source=source,
        classification=classification,
        blockchain=blockchain
    )


def generate_abc_receipt_id(intelligence_hash: str) -> str:
    """
    Create unique receipt ID from intelligence hash.
    
    Generates a unique receipt identifier using the intelligence hash,
    timestamp, and UUID to ensure uniqueness and prevent collisions.
    
    Args:
        intelligence_hash: SHA-256 hash of the intelligence/blockchain data
        
    Returns:
        Unique receipt ID (64-character hexadecimal string)
        
    Example:
        >>> hash_value = "abc123..."
        >>> receipt_id = generate_abc_receipt_id(hash_value)
    """
    timestamp = datetime.now().isoformat()
    unique_id = str(uuid.uuid4())
    # Use FULL hash + timestamp + UUID for maximum uniqueness
    combined = f"{intelligence_hash}{timestamp}{unique_id}"
    # Return full 64-character SHA-256 hash (not truncated)
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_data_integrity(
    original_hash: str,
    current_data: Dict[str, Any],
    receipt: Optional[BaseIntelligenceReceipt] = None,
    source: Optional[str] = None,
    classification: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compare hashes to detect tampering.
    
    Verifies data integrity by comparing the original hash with a newly
    computed hash of the current data. Detects any tampering or modification.
    
    Args:
        original_hash: Original SHA-256 hash to compare against
        current_data: Current data to verify (will be hashed)
        receipt: Optional IntelligenceReceipt object (if provided, uses receipt hash)
        source: Optional source identifier (needed to match receipt hash)
        classification: Optional classification (needed to match receipt hash)
        
    Returns:
        Dictionary with verification results:
        - verified: bool - True if hashes match (no tampering detected)
        - original_hash: str - Original hash value
        - computed_hash: str - Newly computed hash
        - tampered: bool - True if tampering detected
        
    Example:
        >>> result = verify_data_integrity(
        ...     original_hash="abc123...",
        ...     current_data={"block": 825000, "hash": "0x123..."}
        ... )
        >>> if result["verified"]:
        ...     print("Data integrity confirmed")
    """
    generator = CryptographicReceiptGenerator()
    
    # Use receipt hash if provided, otherwise use original_hash
    expected_hash = receipt.intelligence_hash if receipt else original_hash
    
    # If we have a receipt, we need to hash the same structure that was used to create it
    # The receipt was created with intelligence_package = {"data": data, "source": source, "classification": classification}
    if receipt and (source is not None or classification is not None):
        # Reconstruct the intelligence package structure
        intelligence_package = {
            "data": current_data,
            "source": source or "blockchain_data",
            "classification": classification or "UNCLASSIFIED"
        }
        # Use the base generator's hash method to match how the receipt was created
        computed_hash = generator._generator._hash_intelligence_package(intelligence_package)
    else:
        # Simple hash of just the data
        computed_hash = generator.generate_data_hash(current_data)
    
    # Constant-time comparison to prevent timing attacks
    hashes_match = secrets.compare_digest(
        expected_hash.encode() if isinstance(expected_hash, str) else expected_hash,
        computed_hash.encode() if isinstance(computed_hash, str) else computed_hash
    )
    
    return {
        "verified": hashes_match,
        "original_hash": expected_hash,
        "computed_hash": computed_hash,
        "tampered": not hashes_match,
        "timestamp": datetime.now().isoformat()
    }

