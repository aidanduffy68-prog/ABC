"""
Multi-source verification for oracle data
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from src.shared.receipts import IntelligenceReceipt
from src.shared.verification import VerificationEngine

logger = logging.getLogger(__name__)


class MultiSourceVerifier:
    """
    Verify multiple sources (Chainalysis, TRM, Foundry) used ABC-verified data.
    
    **ABC verifies inputs, not outputs. For AML compliance, ABC proves Chainalysis, TRM,
    and Foundry ML models all analyzed the same blockchain data. The compliance officer
    makes the final call—but with confidence in data integrity. ABC is infrastructure
    for verification, not decision-making.**
    """
    
    def __init__(self):
        self.verification_engine = VerificationEngine()
        # Simple in-memory receipt storage (can be replaced with database later)
        self._receipt_store: Dict[str, IntelligenceReceipt] = {}
        logger.debug("MultiSourceVerifier initialized with in-memory receipt storage")
    
    def verify_external_source(
        self,
        receipt_id: str,
        source_name: str,
        source_data_hash: str
    ) -> Dict[str, Any]:
        """
        Verify external source used ABC-verified data.
        
        Args:
            receipt_id: ABC receipt ID
            source_name: Name of external source
            source_data_hash: Hash of data used by source
            
        Returns:
            Verification result
        """
        # TODO: Retrieve receipt from database
        receipt = self._get_receipt(receipt_id)
        
        if not receipt:
            return {
                "verified": False,
                "error": "Receipt not found",
                "receipt_id": receipt_id
            }
        
        match = receipt.intelligence_hash == source_data_hash
        
        return {
            "verified": match,
            "receipt_id": receipt_id,
            "source": source_name,
            "abc_hash": receipt.intelligence_hash,
            "source_hash": source_data_hash,
            "match": match,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    
    def verify_ml_models(
        self,
        receipt_id: str,
        model_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify multiple ML models used ABC-verified data.
        
        Args:
            receipt_id: ABC receipt ID
            model_results: List of model results with data hashes
                [{"model_id": "kyc-risk-v2", "data_hash": "abc123...", "output": {...}}]
            
        Returns:
            Verification result
        """
        receipt = self._get_receipt(receipt_id)
        
        if not receipt:
            return {
                "verified": False,
                "error": "Receipt not found",
                "receipt_id": receipt_id
            }
        
        # Check each model
        all_match = True
        model_verifications = []
        
        for model in model_results:
            model_hash = model.get('data_hash')
            if not model_hash:
                all_match = False
                model_verifications.append({
                    "model_id": model.get('model_id', 'unknown'),
                    "data_hash": None,
                    "match": False,
                    "error": "Missing data_hash"
                })
                continue
            
            match = model_hash == receipt.intelligence_hash
            all_match = all_match and match
            
            model_verifications.append({
                "model_id": model.get('model_id', 'unknown'),
                "data_hash": model_hash,
                "match": match
            })
        
        return {
            "verified": all_match,
            "all_models_used_identical_data": all_match,
            "receipt_id": receipt_id,
            "source_data_hash": receipt.intelligence_hash,
            "models_verified": len(model_results),
            "model_verifications": model_verifications,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    
    def verify_multi_source_consensus(
        self,
        receipt_id: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify multiple sources (Chainalysis, TRM, etc.) agree on data.
        
        Args:
            receipt_id: ABC receipt ID
            sources: List of sources with their data hashes
                     [{"name": "chainalysis", "data_hash": "abc123..."}]
        
        Returns:
            Consensus verification result
        """
        receipt = self._get_receipt(receipt_id)
        
        if not receipt:
            return {
                "verified": False,
                "error": "Receipt not found",
                "receipt_id": receipt_id
            }
        
        return self.verification_engine.verify_multiple_sources(
            receipt=receipt,
            sources=sources
        )
    
    def store_receipt(self, receipt: IntelligenceReceipt) -> bool:
        """
        Store a receipt for later retrieval.
        
        Args:
            receipt: IntelligenceReceipt to store
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not receipt or not receipt.receipt_id:
            logger.warning("Cannot store receipt: missing receipt_id")
            return False
        
        # Store receipt (overwrites if already exists)
        self._receipt_store[receipt.receipt_id] = receipt
        logger.info(f"Stored receipt: {receipt.receipt_id[:16]}... (total: {len(self._receipt_store)})")
        return True
    
    def _get_receipt(self, receipt_id: str) -> Optional[IntelligenceReceipt]:
        """
        Retrieve receipt from storage.
        
        Args:
            receipt_id: Receipt ID to retrieve
            
        Returns:
            IntelligenceReceipt if found, None otherwise
        """
        receipt = self._receipt_store.get(receipt_id)
        if receipt:
            logger.debug(f"Retrieved receipt: {receipt_id[:16]}...")
        else:
            logger.warning(f"Receipt not found: {receipt_id[:16]}...")
        return receipt
    
    def list_receipts(self) -> List[str]:
        """
        List all stored receipt IDs.
        
        Returns:
            List of receipt IDs
        """
        return list(self._receipt_store.keys())
    
    def get_receipt_count(self) -> int:
        """Get count of stored receipts"""
        return len(self._receipt_store)
    
    def has_receipt(self, receipt_id: str) -> bool:
        """
        Check if a receipt exists in storage.
        
        Args:
            receipt_id: Receipt ID to check
            
        Returns:
            True if receipt exists, False otherwise
        """
        return receipt_id in self._receipt_store
    
    def clear_receipts(self) -> int:
        """
        Clear all stored receipts (useful for testing/reset).
        
        Returns:
            Number of receipts that were cleared
        """
        count = len(self._receipt_store)
        self._receipt_store.clear()
        logger.info(f"Cleared {count} stored receipts")
        return count

