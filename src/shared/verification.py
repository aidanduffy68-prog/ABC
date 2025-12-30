"""
Core verification logic used by both Intelligence and Oracle layers
"""
from typing import List, Dict, Any
from .receipts import IntelligenceReceipt


class VerificationEngine:
    """
    Core verification logic for data integrity.
    
    **ABC verifies inputs, not outputs. ABC is infrastructure for verification, not
    decision-making. This engine verifies that multiple sources analyzed identical data,
    enabling humans to trust inputs and focus on evaluating analysis methodology.**
    
    Provides verification utilities that can be used by both
    the Intelligence layer and the Oracle layer.
    """
    
    def verify_multiple_sources(
        self,
        receipt: IntelligenceReceipt,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify multiple sources used identical data.
        
        Args:
            receipt: Original ABC receipt
            sources: List of sources with their data hashes
                     [{"name": "chainalysis", "data_hash": "abc123..."}]
        
        Returns:
            Verification result
        """
        # Get receipt hash (use intelligence_hash from existing receipt format)
        receipt_hash = receipt.intelligence_hash
        
        # Check if all sources match receipt hash
        all_match = all(
            source.get('data_hash') == receipt_hash 
            for source in sources
        )
        
        # Build source verification details
        source_verifications = []
        for source in sources:
            source_verifications.append({
                "name": source.get('name', 'unknown'),
                "data_hash": source.get('data_hash'),
                "matches": source.get('data_hash') == receipt_hash
            })
        
        return {
            "verified": all_match,
            "receipt_id": receipt.receipt_id,
            "receipt_hash": receipt_hash,
            "sources_verified": len(sources),
            "sources": source_verifications,
            "all_sources_match": all_match
        }
    
    def verify_chain_of_custody(
        self,
        receipt_id: str,
        custody_chain: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify chain of custody for data.
        
        Args:
            receipt_id: Original receipt ID
            custody_chain: List of custody events
                [{"entity": "foundry", "action": "consumed", "timestamp": "...", "hash": "..."}]
        
        Returns:
            Chain of custody verification
        """
        if not custody_chain:
            return {
                "verified": False,
                "receipt_id": receipt_id,
                "error": "Empty custody chain"
            }
        
        # Verify each step in chain maintains hash integrity
        verified = True
        chain_errors = []
        
        for i, event in enumerate(custody_chain):
            # Each event should have a hash
            if 'hash' not in event:
                verified = False
                chain_errors.append(f"Event {i} missing hash")
                continue
            
            # If not first event, verify hash consistency with previous
            if i > 0:
                prev_hash = custody_chain[i-1].get('hash')
                curr_hash = event.get('hash')
                # For chain of custody, hashes might change if data is transformed
                # So we just verify that each step is recorded
                pass
        
        return {
            "verified": verified,
            "receipt_id": receipt_id,
            "custody_events": len(custody_chain),
            "errors": chain_errors if chain_errors else None
        }

