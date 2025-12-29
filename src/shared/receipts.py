"""
Shared cryptographic receipt generation (adapter for existing receipt generator)

This module provides a unified interface to the existing CryptographicReceiptGenerator
for use by both Intelligence and Oracle layers without duplicating code.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import hashlib

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
    
    This wraps the existing receipt generator to maintain backward compatibility
    while providing a consistent API for oracle layer usage.
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

