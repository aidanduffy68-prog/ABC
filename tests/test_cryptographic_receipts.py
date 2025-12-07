"""
Test Suite for Cryptographic Receipt System

Tests RSA-PSS signatures, receipt generation, and verification

Run with: pytest tests/test_cryptographic_receipts.py -v
"""

import pytest
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

from src.core.nemesis.on_chain_receipt.receipt_generator import (
    CryptographicReceiptGenerator,
    IntelligenceReceipt,
    ReceiptStatus
)


class TestCryptographicSignatures:
    """Test real RSA-PSS cryptographic signatures"""
    
    @pytest.fixture
    def rsa_keys(self):
        """Generate RSA-4096 key pair for testing"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return {
            'private_pem': private_pem,
            'public_pem': public_pem,
            'private_key': private_key,
            'public_key': public_key
        }
    
    def test_signature_generation_with_real_key(self, rsa_keys):
        """Test that real RSA-PSS signatures are generated correctly"""
        generator = CryptographicReceiptGenerator(
            private_key_pem=rsa_keys['private_pem']
        )
        
        # Generate receipt
        intelligence_package = {
            "actor_id": "test_actor_001",
            "threat_level": "high",
            "behavioral_signature": {"pattern": "test"}
        }
        
        receipt = generator.generate_receipt(
            intelligence_package=intelligence_package,
            actor_id="test_actor_001",
            threat_level="high"
        )
        
        # Verify signature exists and is not mock
        assert receipt.gh_systems_signature is not None
        assert not receipt.gh_systems_signature.startswith("MOCK_")
        
        # Verify it's base64 encoded
        try:
            signature_bytes = base64.b64decode(receipt.gh_systems_signature)
            assert len(signature_bytes) > 0
        except Exception as e:
            pytest.fail(f"Signature is not valid base64: {e}")
    
    def test_signature_verification_success(self, rsa_keys):
        """Test that valid signatures verify successfully"""
        generator = CryptographicReceiptGenerator(
            private_key_pem=rsa_keys['private_pem']
        )
        
        intelligence_package = {
            "actor_id": "test_actor_002",
            "data": "test data"
        }
        
        receipt = generator.generate_receipt(
            intelligence_package=intelligence_package
        )
        
        # Verify signature
        is_valid = generator.verify_signature(
            receipt.receipt_id,
            receipt.intelligence_hash,
            receipt.metadata,
            receipt.gh_systems_signature
        )
        
        assert is_valid is True
    
    def test_signature_verification_failure_tampered_data(self, rsa_keys):
        """Test that tampered data fails verification"""
        generator = CryptographicReceiptGenerator(
            private_key_pem=rsa_keys['private_pem']
        )
        
        intelligence_package = {
            "actor_id": "test_actor_003",
            "data": "original data"
        }
        
        receipt = generator.generate_receipt(
            intelligence_package=intelligence_package
        )
        
        # Tamper with receipt ID
        tampered_receipt_id = receipt.receipt_id + "tampered"
        
        # Verification should fail
        is_valid = generator.verify_signature(
            tampered_receipt_id,  # Tampered!
            receipt.intelligence_hash,
            receipt.metadata,
            receipt.gh_systems_signature
        )
        
        assert is_valid is False
    
    def test_mock_signature_when_no_key(self):
        """Test that mock signatures are generated when no key provided"""
        generator = CryptographicReceiptGenerator()  # No key
        
        intelligence_package = {"data": "test"}
        receipt = generator.generate_receipt(intelligence_package)
        
        # Should be mock signature
        assert receipt.gh_systems_signature.startswith("MOCK_")
    
    def test_mock_signature_cannot_be_verified(self):
        """Test that mock signatures fail verification"""
        generator = CryptographicReceiptGenerator()  # No key
        
        intelligence_package = {"data": "test"}
        receipt = generator.generate_receipt(intelligence_package)
        
        # Mock signatures should fail verification
        is_valid = generator.verify_signature(
            receipt.receipt_id,
            receipt.intelligence_hash,
            receipt.metadata,
            receipt.gh_systems_signature
        )
        
        assert is_valid is False


class TestReceiptGeneration:
    """Test receipt generation and integrity"""
    
    @pytest.fixture
    def generator(self):
        """Create generator without keys for basic tests"""
        return CryptographicReceiptGenerator()
    
    def test_receipt_generation_basic(self, generator):
        """Test basic receipt generation"""
        intelligence_package = {
            "actor_id": "actor_001",
            "threat_level": "critical",
            "behavioral_signature": {"pattern": "ransomware"}
        }
        
        receipt = generator.generate_receipt(
            intelligence_package=intelligence_package,
            actor_id="actor_001",
            threat_level="critical"
        )
        
        assert receipt.receipt_id is not None
        assert receipt.intelligence_hash is not None
        assert receipt.actor_id == "actor_001"
        assert receipt.threat_level == "critical"
        assert receipt.status == ReceiptStatus.PENDING.value
    
    def test_receipt_hash_consistency(self, generator):
        """Test that same package produces same hash"""
        intelligence_package = {
            "actor_id": "actor_002",
            "data": "consistent data"
        }
        
        receipt1 = generator.generate_receipt(intelligence_package)
        receipt2 = generator.generate_receipt(intelligence_package)
        
        # Same package should produce same hash
        assert receipt1.intelligence_hash == receipt2.intelligence_hash
    
    def test_receipt_hash_changes_with_data(self, generator):
        """Test that different packages produce different hashes"""
        package1 = {"data": "package 1"}
        package2 = {"data": "package 2"}
        
        receipt1 = generator.generate_receipt(package1)
        receipt2 = generator.generate_receipt(package2)
        
        # Different packages should produce different hashes
        assert receipt1.intelligence_hash != receipt2.intelligence_hash
    
    def test_receipt_id_uniqueness(self, generator):
        """Test that receipt IDs are unique even for same package"""
        intelligence_package = {"data": "same data"}
        
        receipt1 = generator.generate_receipt(intelligence_package)
        receipt2 = generator.generate_receipt(intelligence_package)
        
        # Receipt IDs should be unique (due to UUID)
        assert receipt1.receipt_id != receipt2.receipt_id
    
    def test_receipt_verification_against_package(self, generator):
        """Test that receipt can be verified against original package"""
        intelligence_package = {
            "actor_id": "actor_003",
            "threat_level": "high"
        }
        
        receipt = generator.generate_receipt(intelligence_package)
        
        # Verify receipt matches package
        is_valid = generator.verify_receipt(receipt, intelligence_package)
        assert is_valid is True
    
    def test_receipt_verification_fails_wrong_package(self, generator):
        """Test that verification fails with wrong package"""
        original_package = {"data": "original"}
        wrong_package = {"data": "wrong"}
        
        receipt = generator.generate_receipt(original_package)
        
        # Verification should fail with wrong package
        is_valid = generator.verify_receipt(receipt, wrong_package)
        assert is_valid is False


class TestBlockchainCommitment:
    """Test blockchain commitment behavior"""
    
    def test_blockchain_commitment_raises_not_implemented(self):
        """Test that blockchain commitment raises NotImplementedError"""
        generator = CryptographicReceiptGenerator()
        
        intelligence_package = {"data": "test"}
        receipt = generator.generate_receipt(intelligence_package)
        
        # Should raise NotImplementedError
        with pytest.raises(NotImplementedError) as exc_info:
            generator.commit_to_blockchain(receipt)
        
        assert "not yet implemented" in str(exc_info.value).lower()


class TestReceiptExportImport:
    """Test receipt serialization"""
    
    @pytest.fixture
    def generator(self):
        return CryptographicReceiptGenerator()
    
    def test_receipt_export_to_json(self, generator):
        """Test exporting receipt to JSON"""
        intelligence_package = {"data": "test"}
        receipt = generator.generate_receipt(intelligence_package)
        
        json_str = generator.export_receipt_json(receipt)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed['receipt_id'] == receipt.receipt_id
        assert parsed['intelligence_hash'] == receipt.intelligence_hash
    
    def test_receipt_import_from_json(self, generator):
        """Test importing receipt from JSON"""
        intelligence_package = {"data": "test"}
        original_receipt = generator.generate_receipt(intelligence_package)
        
        # Export and import
        json_str = generator.export_receipt_json(original_receipt)
        imported_receipt = generator.import_receipt_json(json_str)
        
        # Should match
        assert imported_receipt.receipt_id == original_receipt.receipt_id
        assert imported_receipt.intelligence_hash == original_receipt.intelligence_hash
        assert imported_receipt.actor_id == original_receipt.actor_id


class TestLicenseeContributions:
    """Test licensee contribution receipts"""
    
    def test_licensee_contribution_receipt(self):
        """Test generating receipt for licensee contribution"""
        generator = CryptographicReceiptGenerator()
        
        intelligence_package = {
            "actor_id": "licensee_actor_001",
            "data": "licensee intelligence"
        }
        
        receipt = generator.generate_licensee_contribution_receipt(
            intelligence_package=intelligence_package,
            licensee_id="LICENSEE_001",
            actor_id="licensee_actor_001",
            threat_level="medium"
        )
        
        # Check licensee metadata
        assert receipt.metadata.get("contributor") == "LICENSEE_001"
        assert receipt.metadata.get("contribution_type") == "licensee_intelligence"
        assert receipt.metadata.get("licensee_contribution") is True


class TestSecurityProperties:
    """Test security properties and edge cases"""
    
    @pytest.fixture
    def rsa_keys(self):
        """Generate RSA-4096 key pair for testing"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        return {
            'private_pem': private_pem,
            'private_key': private_key,
        }
    
    def test_signature_cannot_be_reused(self, rsa_keys):
        """Test that signatures are unique and cannot be reused"""
        generator = CryptographicReceiptGenerator(
            private_key_pem=rsa_keys['private_pem']
        )
        
        package1 = {"data": "package 1"}
        package2 = {"data": "package 2"}
        
        receipt1 = generator.generate_receipt(package1)
        receipt2 = generator.generate_receipt(package2)
        
        # Signature from receipt1 should not verify receipt2
        is_valid = generator.verify_signature(
            receipt2.receipt_id,
            receipt2.intelligence_hash,
            receipt2.metadata,
            receipt1.gh_systems_signature  # Wrong signature!
        )
        
        assert is_valid is False
    
    def test_hash_collision_resistance(self):
        """Test that similar packages produce different hashes"""
        generator = CryptographicReceiptGenerator()
        
        # Very similar packages
        package1 = {"data": "test data 1"}
        package2 = {"data": "test data 2"}
        
        receipt1 = generator.generate_receipt(package1)
        receipt2 = generator.generate_receipt(package2)
        
        # Hashes should be completely different
        assert receipt1.intelligence_hash != receipt2.intelligence_hash
        
        # Check Hamming distance (should be ~50% different bits)
        hash1_int = int(receipt1.intelligence_hash, 16)
        hash2_int = int(receipt2.intelligence_hash, 16)
        xor = hash1_int ^ hash2_int
        different_bits = bin(xor).count('1')
        
        # SHA-256 should produce ~128 different bits for similar inputs
        assert different_bits > 100  # At least 100 bits different


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

