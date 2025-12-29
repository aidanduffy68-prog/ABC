"""
Unit tests for oracle layer
"""
import pytest
from src.core.shared.receipts import CryptographicReceiptGenerator
from src.core.shared.verification import VerificationEngine


class TestReceiptGeneration:
    """Test receipt generation and verification"""
    
    def test_receipt_generation(self):
        """Test cryptographic receipt generation"""
        generator = CryptographicReceiptGenerator()
        
        data = {"test": "data", "value": 123}
        receipt = generator.generate_receipt(
            data=data,
            source="test_source",
            classification="UNCLASSIFIED"
        )
        
        assert receipt.receipt_id is not None
        assert receipt.intelligence_hash is not None
        assert len(receipt.intelligence_hash) == 64  # SHA-256 hex length
        assert receipt.source == "test_source"
    
    def test_receipt_verification(self):
        """Test receipt verification"""
        generator = CryptographicReceiptGenerator()
        
        data = {"test": "data"}
        receipt = generator.generate_receipt(data, "test", "UNCLASSIFIED")
        
        # Should verify with same data
        assert generator.verify_receipt(receipt, data) == True
        
        # Should fail with different data
        assert generator.verify_receipt(receipt, {"different": "data"}) == False


class TestBitcoinOracle:
    """Test Bitcoin oracle functionality"""
    
    @pytest.mark.skipif(
        True,
        reason="Bitcoin node not available in test environment"
    )
    def test_bitcoin_block_ingestion(self):
        """Test Bitcoin block ingestion"""
        from src.core.oracle.bitcoin_ingestion import BitcoinOracle
        
        oracle = BitcoinOracle()
        
        # Ingest a known block
        result = oracle.ingest_block(block_height=825000)
        
        assert result['block_height'] == 825000
        assert 'receipt' in result
        assert result['receipt']['receipt_id'] is not None


class TestMultiSourceVerifier:
    """Test multi-source verification"""
    
    def test_verification_engine_multiple_sources(self):
        """Test verification of multiple sources"""
        from src.core.shared.receipts import IntelligenceReceipt
        
        engine = VerificationEngine()
        
        # Create mock receipt
        receipt = IntelligenceReceipt(
            receipt_id="test_receipt_123",
            intelligence_hash="a3f5b8c2d9e1f4a7b6c8d2e5f1a9b3c7",
            timestamp="2025-01-15T10:00:00Z"
        )
        
        # Test with matching sources
        sources = [
            {"name": "chainalysis", "data_hash": "a3f5b8c2d9e1f4a7b6c8d2e5f1a9b3c7"},
            {"name": "trm", "data_hash": "a3f5b8c2d9e1f4a7b6c8d2e5f1a9b3c7"}
        ]
        
        result = engine.verify_multiple_sources(receipt, sources)
        assert result['verified'] == True
        assert result['all_sources_match'] == True
        
        # Test with mismatched source
        sources_mismatch = [
            {"name": "chainalysis", "data_hash": "a3f5b8c2d9e1f4a7b6c8d2e5f1a9b3c7"},
            {"name": "trm", "data_hash": "different_hash_here"}
        ]
        
        result_mismatch = engine.verify_multiple_sources(receipt, sources_mismatch)
        assert result_mismatch['verified'] == False
        assert result_mismatch['all_sources_match'] == False

