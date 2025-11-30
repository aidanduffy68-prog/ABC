"""
Bitcoin On-Chain Integration
Submits cryptographic receipts to Bitcoin blockchain

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict

# Note: In production, use a proper Bitcoin library like python-bitcoinlib or bitcoinrpc
# This is a simplified implementation for demonstration


class BitcoinOnChainIntegration:
    """
    Integrates cryptographic receipts with Bitcoin blockchain
    
    Submits minimal on-chain proofs (OP_RETURN transactions)
    """
    
    def __init__(self, rpc_url: Optional[str] = None, rpc_user: Optional[str] = None, rpc_password: Optional[str] = None):
        """
        Initialize Bitcoin integration
        
        Args:
            rpc_url: Bitcoin RPC URL (e.g., 'http://localhost:8332')
            rpc_user: RPC username
            rpc_password: RPC password
        """
        self.rpc_url = rpc_url or "http://localhost:8332"
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.network = "mainnet"  # or "testnet"
    
    def submit_receipt_to_blockchain(
        self,
        receipt: Dict[str, Any],
        fee_rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Submit cryptographic receipt to Bitcoin blockchain via OP_RETURN
        
        Args:
            receipt: IntelligenceReceipt dictionary
            fee_rate: Satoshis per byte (if None, uses network fee)
            
        Returns:
            Transaction result with tx_hash
        """
        # Prepare OP_RETURN data
        # OP_RETURN allows up to 80 bytes of data
        receipt_data = self._prepare_op_return_data(receipt)
        
        # Create transaction
        tx_result = self._create_op_return_transaction(receipt_data, fee_rate)
        
        return {
            "status": "submitted",
            "tx_hash": tx_result.get("tx_hash"),
            "receipt_id": receipt.get("receipt_id"),
            "timestamp": datetime.now().isoformat(),
            "network": self.network,
            "block_height": tx_result.get("block_height"),
            "confirmation_count": 0
        }
    
    def _prepare_op_return_data(self, receipt: Dict[str, Any]) -> bytes:
        """
        Prepare receipt data for OP_RETURN (max 80 bytes)
        
        Format:
        - receipt_id (32 bytes)
        - intelligence_hash (32 bytes)
        - timestamp (8 bytes)
        - metadata (8 bytes)
        """
        # Extract key fields
        receipt_id = receipt.get("receipt_id", "")[:32].encode('utf-8').ljust(32, b'\x00')
        intelligence_hash = receipt.get("intelligence_hash", "")[:32].encode('utf-8').ljust(32, b'\x00')
        
        # Timestamp (Unix timestamp as 8 bytes)
        timestamp_str = receipt.get("timestamp", datetime.now().isoformat())
        timestamp = int(datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).timestamp())
        timestamp_bytes = timestamp.to_bytes(8, byteorder='big')
        
        # Metadata (8 bytes: threat_level + package_type encoding)
        metadata = self._encode_metadata(receipt)
        
        # Combine (80 bytes total)
        op_return_data = receipt_id + intelligence_hash + timestamp_bytes + metadata
        
        return op_return_data[:80]  # Ensure max 80 bytes
    
    def _encode_metadata(self, receipt: Dict[str, Any]) -> bytes:
        """Encode metadata into 8 bytes"""
        threat_level = receipt.get("threat_level", "low")
        package_type = receipt.get("package_type", "targeting_package")
        
        # Simple encoding (in production, use more sophisticated encoding)
        threat_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        type_map = {"targeting_package": 0, "dossier": 1, "forecast": 2}
        
        threat_code = threat_map.get(threat_level, 0)
        type_code = type_map.get(package_type, 0)
        
        # 8 bytes: threat_level (1) + type (1) + reserved (6)
        metadata = bytes([threat_code, type_code]) + b'\x00' * 6
        
        return metadata
    
    def _create_op_return_transaction(self, op_return_data: bytes, fee_rate: Optional[float] = None) -> Dict[str, Any]:
        """
        Create Bitcoin transaction with OP_RETURN output
        
        In production, this would use bitcoinrpc or similar library
        """
        # Mock implementation - in production, use actual Bitcoin RPC
        # This demonstrates the structure
        
        # Generate mock transaction hash
        tx_hash = hashlib.sha256(op_return_data + datetime.now().isoformat().encode()).hexdigest()
        
        return {
            "tx_hash": tx_hash,
            "block_height": None,  # Will be set when confirmed
            "fee": fee_rate or 1000,  # Satoshis
            "status": "pending"
        }
    
    def verify_receipt_on_chain(self, receipt_id: str, tx_hash: str) -> Dict[str, Any]:
        """
        Verify receipt exists on blockchain
        
        Args:
            receipt_id: Receipt ID to verify
            tx_hash: Transaction hash
            
        Returns:
            Verification result
        """
        # In production, query Bitcoin blockchain for transaction
        # This is a mock implementation
        
        return {
            "receipt_id": receipt_id,
            "tx_hash": tx_hash,
            "verified": True,
            "block_height": 850000,  # Mock
            "confirmation_count": 6,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_receipt_from_chain(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve receipt data from blockchain transaction
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Receipt data if found
        """
        # In production, decode OP_RETURN data from transaction
        # This is a mock implementation
        
        return {
            "receipt_id": "abc_receipt_123",
            "intelligence_hash": "sha256:abc123...",
            "timestamp": datetime.now().isoformat(),
            "tx_hash": tx_hash
        }


# Integration with receipt generator
def submit_receipt_to_bitcoin(receipt: Dict[str, Any], rpc_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to submit receipt to Bitcoin
    
    Usage:
        result = submit_receipt_to_bitcoin(receipt_dict)
    """
    bitcoin = BitcoinOnChainIntegration(rpc_url=rpc_url)
    return bitcoin.submit_receipt_to_blockchain(receipt)

