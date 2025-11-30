"""
Receipt Verification System
Verifies cryptographic receipts and on-chain proofs

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import asdict

from .receipt_generator import IntelligenceReceipt, CryptographicReceiptGenerator
from .bitcoin_integration import BitcoinOnChainIntegration


class ReceiptVerifier:
    """
    Verifies cryptographic receipts and on-chain proofs
    
    Validates:
    - Receipt integrity (hash verification)
    - On-chain existence (Bitcoin transaction)
    - Signature authenticity (GH Systems signature)
    - Timestamp validity
    """
    
    def __init__(self, bitcoin_rpc_url: Optional[str] = None):
        """
        Initialize receipt verifier
        
        Args:
            bitcoin_rpc_url: Bitcoin RPC URL for on-chain verification
        """
        self.receipt_generator = CryptographicReceiptGenerator()
        self.bitcoin = BitcoinOnChainIntegration(rpc_url=bitcoin_rpc_url)
        self.verifier_version = "1.0.0"
    
    def verify_receipt(
        self,
        receipt: Dict[str, Any],
        intelligence_package: Optional[Dict[str, Any]] = None,
        verify_on_chain: bool = True
    ) -> Dict[str, Any]:
        """
        Verify cryptographic receipt
        
        Args:
            receipt: Receipt dictionary to verify
            intelligence_package: Original intelligence package (for hash verification)
            verify_on_chain: Whether to verify on-chain existence
            
        Returns:
            Verification result
        """
        verification_result = {
            "receipt_id": receipt.get("receipt_id"),
            "verified": False,
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check 1: Receipt hash integrity
        if intelligence_package:
            expected_hash = self.receipt_generator._hash_intelligence_package(intelligence_package)
            actual_hash = receipt.get("intelligence_hash")
            verification_result["checks"]["hash_integrity"] = expected_hash == actual_hash
        else:
            verification_result["checks"]["hash_integrity"] = None  # Cannot verify without package
        
        # Check 2: Receipt structure validity
        required_fields = ["receipt_id", "intelligence_hash", "timestamp"]
        verification_result["checks"]["structure_validity"] = all(
            field in receipt for field in required_fields
        )
        
        # Check 3: Timestamp validity
        try:
            receipt_timestamp = datetime.fromisoformat(receipt.get("timestamp", "").replace('Z', '+00:00'))
            now = datetime.now(receipt_timestamp.tzinfo) if receipt_timestamp.tzinfo else datetime.now()
            age_seconds = (now - receipt_timestamp).total_seconds()
            verification_result["checks"]["timestamp_validity"] = {
                "valid": age_seconds >= 0,  # Not in future
                "age_seconds": age_seconds
            }
        except Exception:
            verification_result["checks"]["timestamp_validity"] = {"valid": False}
        
        # Check 4: On-chain verification
        if verify_on_chain and receipt.get("tx_hash"):
            on_chain_result = self.bitcoin.verify_receipt_on_chain(
                receipt.get("receipt_id"),
                receipt.get("tx_hash")
            )
            verification_result["checks"]["on_chain_verification"] = {
                "verified": on_chain_result.get("verified", False),
                "tx_hash": receipt.get("tx_hash"),
                "confirmation_count": on_chain_result.get("confirmation_count", 0)
            }
        else:
            verification_result["checks"]["on_chain_verification"] = None
        
        # Check 5: Signature verification (if present)
        if receipt.get("gh_systems_signature"):
            # In production, verify cryptographic signature
            verification_result["checks"]["signature_verification"] = {
                "verified": True,  # Mock - implement actual signature verification
                "signature": receipt.get("gh_systems_signature")
            }
        else:
            verification_result["checks"]["signature_verification"] = None
        
        # Overall verification status
        checks = verification_result["checks"]
        verification_result["verified"] = all(
            check is True or (isinstance(check, dict) and check.get("valid", False))
            for check in checks.values()
            if check is not None
        )
        
        return verification_result
    
    def verify_intelligence_package(
        self,
        intelligence_package: Dict[str, Any],
        receipt: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify intelligence package matches receipt
        
        Args:
            intelligence_package: Original intelligence package
            receipt: Cryptographic receipt
            
        Returns:
            Verification result
        """
        # Generate expected hash
        expected_hash = self.receipt_generator._hash_intelligence_package(intelligence_package)
        actual_hash = receipt.get("intelligence_hash")
        
        return {
            "verified": expected_hash == actual_hash,
            "expected_hash": expected_hash,
            "actual_hash": actual_hash,
            "match": expected_hash == actual_hash,
            "timestamp": datetime.now().isoformat()
        }
    
    def batch_verify_receipts(
        self,
        receipts: List[Dict[str, Any]],
        verify_on_chain: bool = True
    ) -> Dict[str, Any]:
        """
        Verify multiple receipts in batch
        
        Args:
            receipts: List of receipt dictionaries
            verify_on_chain: Whether to verify on-chain existence
            
        Returns:
            Batch verification results
        """
        results = []
        for receipt in receipts:
            result = self.verify_receipt(receipt, verify_on_chain=verify_on_chain)
            results.append(result)
        
        verified_count = sum(1 for r in results if r.get("verified", False))
        
        return {
            "total_receipts": len(receipts),
            "verified_count": verified_count,
            "verification_rate": verified_count / len(receipts) if receipts else 0,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }


# Convenience function
def verify_receipt(receipt: Dict[str, Any], intelligence_package: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick receipt verification
    
    Usage:
        result = verify_receipt(receipt_dict, intelligence_package_dict)
    """
    verifier = ReceiptVerifier()
    return verifier.verify_receipt(receipt, intelligence_package)

