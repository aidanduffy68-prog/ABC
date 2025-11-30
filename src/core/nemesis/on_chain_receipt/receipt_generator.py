"""
On-Chain Cryptographic Receipt System
Generates minimal cryptographic proofs of intelligence outputs without revealing proprietary systems
"""

import hashlib
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ReceiptStatus(Enum):
    """Receipt status"""
    PENDING = "pending"
    COMMITTED = "committed"
    VERIFIED = "verified"
    INVALID = "invalid"


@dataclass
class IntelligenceReceipt:
    """
    Minimal cryptographic receipt of intelligence output
    Contains only proof of authenticity, not proprietary data
    """
    receipt_id: str
    intelligence_hash: str  # Hash of full intelligence package
    timestamp: str  # ISO format timestamp
    actor_id: Optional[str] = None  # Target actor ID (if applicable)
    threat_level: Optional[str] = None  # Threat level (low/medium/high/critical)
    package_type: Optional[str] = None  # Type: targeting_package, dossier, forecast
    gh_systems_signature: Optional[str] = None  # GH Systems cryptographic signature
    tx_hash: Optional[str] = None  # Bitcoin transaction hash (when committed)
    status: str = ReceiptStatus.PENDING.value
    metadata: Dict[str, Any] = None  # Minimal metadata (no proprietary info)
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CryptographicReceiptGenerator:
    """
    Generates cryptographic receipts for intelligence outputs
    Keeps all proprietary systems off-chain, only puts proof on-chain
    
    Enables licensees to contribute intelligence via BTC without revealing proprietary information.
    Licensees can submit intelligence packages and receive cryptographic receipts, just like they
    receive intelligence from GH Systems—creating a bidirectional intelligence flow.
    """
    
    def __init__(self, private_key: Optional[str] = None, licensee_id: Optional[str] = None):
        """
        Initialize receipt generator
        
        Args:
            private_key: Private key for signing receipts (if None, uses mock signing)
            licensee_id: Licensee identifier (if generating receipts for licensee contributions)
        """
        self.private_key = private_key
        self.licensee_id = licensee_id
        self.receipt_version = "1.0.0"
    
    def generate_receipt(
        self,
        intelligence_package: Dict[str, Any],
        actor_id: Optional[str] = None,
        threat_level: Optional[str] = None,
        package_type: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> IntelligenceReceipt:
        """
        Generate cryptographic receipt for intelligence package
        
        Args:
            intelligence_package: Full intelligence package (stays off-chain)
            actor_id: Target actor ID
            threat_level: Threat level classification
            package_type: Type of package (targeting_package, dossier, forecast)
            additional_metadata: Additional minimal metadata
            
        Returns:
            IntelligenceReceipt with cryptographic proof
        """
        # Generate hash of full intelligence package
        intelligence_hash = self._hash_intelligence_package(intelligence_package)
        
        # Generate receipt ID
        receipt_id = self._generate_receipt_id(intelligence_hash)
        
        # Create minimal metadata (no proprietary info)
        metadata = {
            "version": self.receipt_version,
            "package_size": len(json.dumps(intelligence_package)),
            "generated_at": datetime.now().isoformat()
        }
        
        # Add licensee ID if this is a licensee contribution
        if self.licensee_id:
            metadata["contributor"] = self.licensee_id
            metadata["contribution_type"] = "licensee_intelligence"
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Generate GH Systems signature
        signature = self._sign_receipt(receipt_id, intelligence_hash, metadata)
        
        # Create receipt
        receipt = IntelligenceReceipt(
            receipt_id=receipt_id,
            intelligence_hash=intelligence_hash,
            timestamp=datetime.now().isoformat(),
            actor_id=actor_id,
            threat_level=threat_level,
            package_type=package_type,
            gh_systems_signature=signature,
            status=ReceiptStatus.PENDING.value,
            metadata=metadata
        )
        
        return receipt
    
    def _hash_intelligence_package(self, package: Dict[str, Any]) -> str:
        """
        Generate SHA-256 hash of intelligence package using canonical JSON
        
        CRITICAL: Uses canonical JSON representation to ensure hash consistency
        - sort_keys=True: Deterministic key ordering
        - ensure_ascii=False: Preserve Unicode
        - separators=(',', ':'): No extra whitespace
        - No formatting changes (whitespace) should affect hash
        """
        # Canonical JSON: sort keys, no extra whitespace, consistent encoding
        package_json = json.dumps(
            package,
            sort_keys=True,
            ensure_ascii=False,
            separators=(',', ':')  # No extra whitespace
        )
        return hashlib.sha256(package_json.encode('utf-8')).hexdigest()
    
    def _generate_receipt_id(self, intelligence_hash: str) -> str:
        """Generate unique receipt ID from intelligence hash"""
        # Use first 16 chars of hash + timestamp for uniqueness
        timestamp = datetime.now().isoformat()
        combined = f"{intelligence_hash[:16]}{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def _sign_receipt(
        self,
        receipt_id: str,
        intelligence_hash: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Generate cryptographic signature for receipt
        
        In production, this would use actual cryptographic signing.
        For now, generates a deterministic signature.
        """
        if self.private_key:
            # TODO: Implement actual cryptographic signing with private key
            # For now, generate deterministic signature
            sign_data = f"{receipt_id}{intelligence_hash}{json.dumps(metadata, sort_keys=True)}"
            return hashlib.sha256(f"{self.private_key}{sign_data}".encode()).hexdigest()
        else:
            # Mock signature for development
            sign_data = f"{receipt_id}{intelligence_hash}{json.dumps(metadata, sort_keys=True)}"
            return hashlib.sha256(sign_data.encode()).hexdigest()
    
    def verify_receipt(self, receipt: IntelligenceReceipt, intelligence_package: Dict[str, Any]) -> bool:
        """
        Verify that receipt matches intelligence package
        
        Args:
            receipt: IntelligenceReceipt to verify
            intelligence_package: Full intelligence package to verify against
            
        Returns:
            True if receipt is valid, False otherwise
        """
        # Verify hash matches
        package_hash = self._hash_intelligence_package(intelligence_package)
        if package_hash != receipt.intelligence_hash:
            return False
        
        # Verify signature (if private key available)
        if receipt.gh_systems_signature:
            expected_signature = self._sign_receipt(
                receipt.receipt_id,
                receipt.intelligence_hash,
                receipt.metadata
            )
            if expected_signature != receipt.gh_systems_signature:
                return False
        
        return True
    
    def prepare_for_on_chain(self, receipt: IntelligenceReceipt) -> Dict[str, Any]:
        """
        Prepare receipt for on-chain commitment
        Returns minimal data structure for blockchain transaction
        
        Args:
            receipt: IntelligenceReceipt to prepare
            
        Returns:
            Dict with minimal on-chain data
        """
        return {
            "receipt_id": receipt.receipt_id,
            "intelligence_hash": receipt.intelligence_hash,
            "timestamp": receipt.timestamp,
            "actor_id": receipt.actor_id,
            "threat_level": receipt.threat_level,
            "package_type": receipt.package_type,
            "signature": receipt.gh_systems_signature,
            "version": receipt.metadata.get("version", self.receipt_version)
        }
    
    def commit_to_blockchain(
        self,
        receipt: IntelligenceReceipt,
        btc_address: Optional[str] = None
    ) -> str:
        """
        Commit receipt to Bitcoin blockchain
        
        Args:
            receipt: IntelligenceReceipt to commit
            btc_address: Bitcoin address to use (optional)
            
        Returns:
            Bitcoin transaction hash
        """
        # Prepare minimal on-chain data
        on_chain_data = self.prepare_for_on_chain(receipt)
        
        # TODO: Implement actual Bitcoin transaction
        # For now, return mock transaction hash
        # In production, this would:
        # 1. Create OP_RETURN transaction with receipt data
        # 2. Or use a Bitcoin-based timestamping service
        # 3. Return actual transaction hash
        
        mock_tx_hash = hashlib.sha256(
            json.dumps(on_chain_data, sort_keys=True).encode()
        ).hexdigest()
        
        receipt.tx_hash = mock_tx_hash
        receipt.status = ReceiptStatus.COMMITTED.value
        
        return mock_tx_hash
    
    def export_receipt_json(self, receipt: IntelligenceReceipt) -> str:
        """Export receipt as JSON string"""
        return json.dumps(asdict(receipt), indent=2)
    
    def import_receipt_json(self, receipt_json: str) -> IntelligenceReceipt:
        """Import receipt from JSON string"""
        data = json.loads(receipt_json)
        return IntelligenceReceipt(**data)
    
    def generate_licensee_contribution_receipt(
        self,
        intelligence_package: Dict[str, Any],
        licensee_id: str,
        actor_id: Optional[str] = None,
        threat_level: Optional[str] = None,
        package_type: Optional[str] = None
    ) -> IntelligenceReceipt:
        """
        Generate receipt for licensee intelligence contribution
        
        Enables licensees to contribute intelligence via BTC without revealing proprietary information.
        Licensees submit intelligence packages and receive cryptographic receipts, just like they
        receive intelligence from GH Systems—creating a bidirectional intelligence flow.
        
        Args:
            intelligence_package: Full intelligence package from licensee (stays off-chain)
            licensee_id: Licensee identifier
            actor_id: Target actor ID
            threat_level: Threat level classification
            package_type: Type of package
            
        Returns:
            IntelligenceReceipt with cryptographic proof (can be committed to blockchain for BTC settlement)
        """
        # Temporarily set licensee_id for this receipt
        original_licensee_id = self.licensee_id
        self.licensee_id = licensee_id
        
        try:
            receipt = self.generate_receipt(
                intelligence_package=intelligence_package,
                actor_id=actor_id,
                threat_level=threat_level,
                package_type=package_type,
                additional_metadata={
                    "licensee_contribution": True,
                    "contribution_timestamp": datetime.now().isoformat()
                }
            )
            return receipt
        finally:
            # Restore original licensee_id
            self.licensee_id = original_licensee_id


class ReceiptVerifier:
    """
    Verifies cryptographic receipts without requiring full intelligence package
    Can verify receipt authenticity from on-chain data alone
    """
    
    @staticmethod
    def verify_from_on_chain(
        on_chain_data: Dict[str, Any],
        expected_signature: Optional[str] = None
    ) -> bool:
        """
        Verify receipt from on-chain data
        
        Args:
            on_chain_data: Data retrieved from blockchain
            expected_signature: Expected GH Systems signature (if available)
            
        Returns:
            True if receipt appears valid
        """
        # Check required fields
        required_fields = ["receipt_id", "intelligence_hash", "timestamp", "signature"]
        if not all(field in on_chain_data for field in required_fields):
            return False
        
        # Verify signature if provided
        if expected_signature and on_chain_data.get("signature") != expected_signature:
            return False
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(on_chain_data["timestamp"])
        except (ValueError, TypeError):
            return False
        
        return True
    
    @staticmethod
    def verify_receipt_integrity(receipt: IntelligenceReceipt) -> bool:
        """
        Verify receipt internal integrity
        
        Args:
            receipt: IntelligenceReceipt to verify
            
        Returns:
            True if receipt structure is valid
        """
        # Check required fields
        if not receipt.receipt_id or not receipt.intelligence_hash:
            return False
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(receipt.timestamp)
        except (ValueError, TypeError):
            return False
        
        # Verify status is valid
        try:
            ReceiptStatus(receipt.status)
        except ValueError:
            return False
        
        return True
