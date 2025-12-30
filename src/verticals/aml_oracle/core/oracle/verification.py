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
        # TODO: Add receipt storage/retrieval in Phase 5
    
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
    
    def _get_receipt(self, receipt_id: str) -> Optional[IntelligenceReceipt]:
        """Retrieve receipt from database"""
        # TODO: Implement database retrieval in Phase 5
        logger.warning(f"Receipt retrieval not yet implemented: {receipt_id}")
        return None

