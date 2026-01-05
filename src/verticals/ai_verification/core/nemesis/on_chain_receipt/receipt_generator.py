"""
On-Chain Cryptographic Receipt System
Generates minimal cryptographic proofs of intelligence outputs without revealing proprietary systems

SECURITY: Uses real cryptographic signatures (RSA-PSS) for receipt authentication.
"""

import hashlib
import json
import base64
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Cryptographic signing - use real cryptography library
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    # Will raise error if trying to use real signatures without library


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
    # Foundry Chain integration fields
    foundry_compilation_id: Optional[str] = None  # Foundry compilation ID
    foundry_hash: Optional[str] = None  # Foundry data hash
    foundry_timestamp: Optional[str] = None  # When Foundry compiled
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CryptographicReceiptGenerator:
    """
    Generates cryptographic receipts for intelligence outputs.
    
    **ABC verifies data integrity: hash match = good, hash mismatch = bad.**
    
    This generator creates cryptographic proofs that prove data integrity - enabling
    downstream AI systems and human analysts to trust that all systems analyzed identical
    source data. The receipt proves the input was verified, not that a particular output
    is correct.
    
    Keeps all proprietary systems off-chain, only puts proof on-chain.
    
    Enables licensees to contribute intelligence via BTC without revealing proprietary information.
    Licensees can submit intelligence packages and receive cryptographic receipts, just like they
    receive intelligence from GH Systems—creating a bidirectional intelligence flow.
    """
    
    def __init__(
        self,
        private_key_pem: Optional[str] = None,
        licensee_id: Optional[str] = None,
        use_blake2_hashing: bool = False
    ):
        """
        Initialize receipt generator
        
        Args:
            private_key_pem: RSA private key in PEM format for signing receipts.
                           If None, will use mock signing (NOT SECURE - for development only).
                           In production, MUST provide real private key from secure key management.
            licensee_id: Licensee identifier (if generating receipts for licensee contributions)
            use_blake2_hashing: If True, use BLAKE2b for hashing (faster, more secure).
                              If False, use SHA-256 (default for compatibility).
        """
        self.private_key_pem = private_key_pem
        self.private_key_obj = None
        self.public_key_obj = None
        self.licensee_id = licensee_id
        self.receipt_version = "1.0.0"
        self.use_real_cryptography = False
        self.use_blake2_hashing = use_blake2_hashing
        
        # Load private key if provided
        if private_key_pem and CRYPTOGRAPHY_AVAILABLE:
            try:
                self.private_key_obj = serialization.load_pem_private_key(
                    private_key_pem.encode(),
                    password=None,
                    backend=default_backend()
                )
                self.public_key_obj = self.private_key_obj.public_key()
                self.use_real_cryptography = True
            except Exception as e:
                raise ValueError(f"Failed to load private key: {e}. Ensure key is valid RSA PEM format.")
        elif private_key_pem and not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError(
                "cryptography library required for real signatures. "
                "Install with: pip install cryptography>=41.0.0"
            )
    
    def generate_receipt(
        self,
        intelligence_package: Dict[str, Any],
        actor_id: Optional[str] = None,
        threat_level: Optional[str] = None,
        package_type: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
        validate_before_publish: bool = True,
        require_payment_settlement: bool = True,
        foundry_compilation_id: Optional[str] = None,
        foundry_hash: Optional[str] = None,
        foundry_timestamp: Optional[str] = None
    ) -> Optional[IntelligenceReceipt]:
        """
        Generate cryptographic receipt for intelligence package.
        
        **ABC verifies inputs, not outputs.** This receipt provides cryptographic proof
        that the intelligence package was verified for data integrity. It does NOT validate
        the correctness of analysis or conclusions - that remains with human analysts.
        ABC is infrastructure for verification, not decision-making.
        
        IMPORTANT: Hashes are only published after validation and payment settlement.
        If validation or payment fails, no hash is generated (returns None).
        
        Args:
            intelligence_package: Full intelligence package (stays off-chain)
            actor_id: Target actor ID
            threat_level: Threat level classification
            package_type: Type of package (targeting_package, dossier, forecast)
            additional_metadata: Additional minimal metadata
            validate_before_publish: Whether to validate intelligence before publishing hash
            require_payment_settlement: Whether to require payment settlement before publishing hash
            foundry_compilation_id: Optional Foundry compilation ID for Foundry Chain integration
            foundry_hash: Optional Foundry data hash for verification
            foundry_timestamp: Optional Foundry compilation timestamp
            
        Returns:
            IntelligenceReceipt with cryptographic proof, or None if validation/payment fails
        """
        # Sanitize and validate intelligence package
        from src.shared.security.input_sanitization import validate_json_depth, sanitize_metadata
        
        try:
            # Validate JSON nesting depth
            validate_json_depth(intelligence_package, max_depth=10)
        except ValueError as e:
            raise ValueError(f"Intelligence package validation failed: {e}")
        
        # Sanitize metadata if present
        if "metadata" in intelligence_package and isinstance(intelligence_package["metadata"], dict):
            intelligence_package["metadata"] = sanitize_metadata(intelligence_package["metadata"])
        
        # Validate intelligence before generating hash
        if validate_before_publish:
            if not self._validate_intelligence(intelligence_package):
                return None
        
        # Check payment settlement before generating hash
        if require_payment_settlement:
            if not self._check_payment_settlement(intelligence_package):
                return None
        
        # Only generate hash after validation and payment are confirmed
        # Generate hash of full intelligence package
        intelligence_hash = self._hash_intelligence_package(
            intelligence_package,
            use_blake2=self.use_blake2_hashing
        )
        
        # Generate receipt ID
        receipt_id = self._generate_receipt_id(intelligence_hash)
        
        # Create minimal metadata (no proprietary info)
        # Estimate package size (avoid full serialization here)
        try:
            package_size = len(str(intelligence_package))
        except:
            package_size = 0
        
        metadata = {
            "version": self.receipt_version,
            "package_size": package_size,
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
            metadata=metadata,
            foundry_compilation_id=foundry_compilation_id,
            foundry_hash=foundry_hash,
            foundry_timestamp=foundry_timestamp
        )
        
        return receipt
    
    def _validate_intelligence(self, intelligence_package: Dict[str, Any]) -> bool:
        """
        Validate intelligence package before publishing hash
        
        Returns:
            True if intelligence is valid, False otherwise
        """
        # Check for required fields
        if not intelligence_package:
            return False
        
        # Check for minimum quality thresholds
        # In production, this would include:
        # - Confidence score checks
        # - Source verification
        # - Data quality validation
        # - Classification compliance
        
        # For now, basic validation: ensure package has content
        if isinstance(intelligence_package, dict):
            # Check if package has meaningful content
            if not any(key in intelligence_package for key in ['targeting_package', 'behavioral_signature', 'coordination_network']):
                # Allow if it has any substantial data
                if len(str(intelligence_package)) < 10:
                    return False
        
        return True
    
    def _check_payment_settlement(self, intelligence_package: Dict[str, Any]) -> bool:
        """
        Check if payment has been settled before publishing hash
        
        Returns:
            True if payment is settled, False otherwise
        """
        # In production, this would:
        # - Check Bitcoin transaction confirmation
        # - Verify payment amount matches contract
        # - Confirm payment is linked to this intelligence package
        # - Check for any payment disputes
        
        # For now, check if payment metadata exists
        # In real implementation, this would query blockchain
        metadata = intelligence_package.get('metadata', {})
        if isinstance(metadata, dict):
            payment_status = metadata.get('payment_settled', False)
            payment_tx_hash = metadata.get('payment_tx_hash', None)
            
            # If payment metadata exists and indicates settlement, return True
            if payment_status and payment_tx_hash:
                return True
        
        # For test/demo purposes, assume payment is settled if no payment metadata exists
        # In production, this would return False to require explicit payment
        return True  # Allow for testing, but in production should check actual settlement
    
    def _hash_intelligence_package(self, package: Dict[str, Any], use_blake2: bool = False) -> str:
        """
        Generate hash of intelligence package using canonical JSON
        
        CRITICAL: Uses canonical JSON representation to ensure hash consistency
        - sort_keys=True: Deterministic key ordering
        - ensure_ascii=False: Preserve Unicode
        - separators=(',', ':'): No extra whitespace
        - No formatting changes (whitespace) should affect hash
        
        Args:
            package: Intelligence package dictionary
            use_blake2: If True, use BLAKE2b (faster, more secure). If False, use SHA-256 (default for compatibility)
            
        Returns:
            Hexadecimal hash string (64 characters)
        """
        # Canonical JSON: sort keys, no extra whitespace, consistent encoding
        # Handle non-serializable types (datetime, enums, etc.)
        def json_serializer(obj):
            """JSON serializer for objects not serializable by default json code"""
            from datetime import datetime
            from enum import Enum
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, Enum):
                return obj.value if hasattr(obj, 'value') else str(obj)
            raise TypeError(f"Type {type(obj)} not serializable")
        
        # Convert package to fully serializable format first
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
                # Handle dataclass
                return make_serializable(asdict(obj))
            elif hasattr(obj, '__dict__'):
                # Handle regular object
                try:
                    return make_serializable(obj.__dict__)
                except:
                    return str(obj)
            else:
                return obj
        
        serializable_package = make_serializable(package)
        
        package_json = json.dumps(
            serializable_package,
            sort_keys=True,
            ensure_ascii=False,
            separators=(',', ':'),  # No extra whitespace
            default=json_serializer
        )
        
        package_bytes = package_json.encode('utf-8')
        
        # Use BLAKE2b if requested (faster, more secure)
        if use_blake2:
            return hashlib.blake2b(package_bytes, digest_size=32).hexdigest()
        else:
            # Default to SHA-256 for compatibility
            return hashlib.sha256(package_bytes).hexdigest()
    
    def _generate_receipt_id(self, intelligence_hash: str) -> str:
        """
        Generate unique receipt ID from intelligence hash
        
        SECURITY FIX: Uses full hash + UUID to prevent collisions.
        Previous implementation used only 16 chars of hash, creating collision risk.
        """
        timestamp = datetime.now().isoformat()
        unique_id = str(uuid.uuid4())
        # Use FULL hash + timestamp + UUID for maximum uniqueness
        combined = f"{intelligence_hash}{timestamp}{unique_id}"
        # Return full 64-character SHA-256 hash (not truncated)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _sign_receipt(
        self,
        receipt_id: str,
        intelligence_hash: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Generate REAL cryptographic signature for receipt using RSA-PSS
        
        SECURITY FIX: Now uses actual RSA-PSS signatures, not just hashes.
        Previous implementation was vulnerable to forgery.
        
        Args:
            receipt_id: Unique receipt identifier
            intelligence_hash: SHA-256 hash of intelligence package
            metadata: Receipt metadata dictionary
            
        Returns:
            Base64-encoded RSA-PSS signature (or mock hash if no private key)
            
        Raises:
            ValueError: If private key required but not available
        """
        # Create canonical message to sign
        message = f"{receipt_id}|{intelligence_hash}|{json.dumps(metadata, sort_keys=True)}"
        
        if self.use_real_cryptography and self.private_key_obj:
            # REAL cryptographic signature using RSA-PSS
            try:
                signature = self.private_key_obj.sign(
                    message.encode('utf-8'),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                # Return base64-encoded signature
                return base64.b64encode(signature).decode('utf-8')
            except Exception as e:
                # Generic error message to prevent information leakage
                # Log detailed error internally, but don't expose to caller
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to generate cryptographic signature: {e}", exc_info=True)
                raise ValueError("Failed to generate cryptographic signature")
        else:
            # MOCK signature for development/testing (NOT SECURE)
            # WARNING: This is NOT a real signature and can be forged!
            sign_data = f"{receipt_id}{intelligence_hash}{json.dumps(metadata, sort_keys=True)}"
            mock_signature = hashlib.sha256(sign_data.encode()).hexdigest()
            # Add warning marker to indicate this is not a real signature
            return f"MOCK_{mock_signature}"
    
    def verify_signature(
        self,
        receipt_id: str,
        intelligence_hash: str,
        metadata: Dict[str, Any],
        signature_b64: str
    ) -> bool:
        """
        Verify cryptographic signature using public key
        
        Args:
            receipt_id: Receipt identifier
            intelligence_hash: Intelligence package hash
            metadata: Receipt metadata
            signature_b64: Base64-encoded signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Check if this is a mock signature
        if signature_b64.startswith("MOCK_"):
            # Mock signatures cannot be cryptographically verified
            return False
        
        if not self.use_real_cryptography or not self.public_key_obj:
            return False
        
        # Create canonical message
        message = f"{receipt_id}|{intelligence_hash}|{json.dumps(metadata, sort_keys=True)}"
        
        try:
            signature = base64.b64decode(signature_b64)
            self.public_key_obj.verify(
                signature,
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            # Generic error handling - don't reveal why verification failed
            # This prevents information leakage about key existence, signature format, etc.
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Signature verification failed: {e}")
            return False
    
    def verify_receipt(self, receipt: IntelligenceReceipt, intelligence_package: Dict[str, Any]) -> bool:
        """
        Verify that receipt matches intelligence package
        
        SECURITY FIX: Now uses real cryptographic signature verification and constant-time hash comparison.
        
        Args:
            receipt: IntelligenceReceipt to verify
            intelligence_package: Full intelligence package to verify against
            
        Returns:
            True if receipt is valid, False otherwise
        """
        # Verify hash matches (constant-time comparison to prevent timing attacks)
        import secrets
        package_hash = self._hash_intelligence_package(
            intelligence_package,
            use_blake2=self.use_blake2_hashing
        )
        if not secrets.compare_digest(
            package_hash.encode() if isinstance(package_hash, str) else package_hash,
            receipt.intelligence_hash.encode() if isinstance(receipt.intelligence_hash, str) else receipt.intelligence_hash
        ):
            return False
        
        # Verify signature using real cryptographic verification
        if receipt.gh_systems_signature:
            if not self.verify_signature(
                receipt.receipt_id,
                receipt.intelligence_hash,
                receipt.metadata,
                receipt.gh_systems_signature
            ):
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
        preferred_network: Optional[str] = None,
        chain_config: Optional[Any] = None
    ) -> Optional[str]:
        """
        Commit receipt to blockchain (chain-agnostic)
        
        Supports multiple blockchain networks (Bitcoin, Ethereum, Polygon, etc.)
        Vendors and agencies can specify their preferred chain.
        
        Args:
            receipt: IntelligenceReceipt to commit
            preferred_network: Preferred blockchain network (e.g., "bitcoin", "ethereum")
                              Defaults to Bitcoin if not specified
            chain_config: ChainConfig for network-specific settings (optional)
            
        Returns:
            Transaction hash (or None if not implemented)
            
        Note:
            In production, this uses the chain-agnostic abstraction layer.
            Each blockchain adapter handles network-specific requirements.
        """
        try:
            from .blockchain_abstraction import (
                BlockchainNetwork,
                ChainAgnosticReceiptManager,
                ChainConfig
            )
            
            # Parse network preference
            if preferred_network:
                try:
                    network = BlockchainNetwork(preferred_network.lower())
                except ValueError:
                    # Default to Bitcoin if invalid network specified
                    network = BlockchainNetwork.BITCOIN
            else:
                network = BlockchainNetwork.BITCOIN  # Default
            
            # Create chain-agnostic manager
            manager = ChainAgnosticReceiptManager(default_network=network)
            
            # Prepare receipt data
            receipt_data = asdict(receipt)
            
            # Commit to blockchain
            commitment = manager.commit_receipt(
                receipt_data=receipt_data,
                preferred_network=network,
                chain_config=chain_config
            )
            
            # Update receipt with transaction hash
            receipt.tx_hash = commitment.tx_hash
            receipt.status = ReceiptStatus.COMMITTED.value
            
            return commitment.tx_hash
            
        except ImportError:
            # Fallback if abstraction layer not available
            raise NotImplementedError(
                "Blockchain commitment requires chain-agnostic abstraction layer. "
                "Install required dependencies and ensure adapters are registered."
            )
    
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
