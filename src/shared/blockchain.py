"""
Shared blockchain anchoring utilities (wrapper for existing blockchain abstraction)

This module provides a simplified interface to blockchain anchoring for use
by both Intelligence and Oracle layers.
"""
from typing import Dict, Any, Optional
from src.verticals.ai_verification.core.nemesis.on_chain_receipt.blockchain_abstraction import (
    ChainAgnosticReceiptManager,
    BlockchainNetwork,
    ChainConfig
)


class BlockchainAnchor:
    """
    Simplified blockchain anchoring interface.
    
    Wraps the existing BlockchainManager to provide a simpler API
    for anchoring receipts to blockchain.
    """
    
    def __init__(self, network: str = "bitcoin"):
        """
        Initialize blockchain anchor.
        
        Args:
            network: Blockchain network name ("bitcoin", "ethereum", etc.)
        """
        self.network_name = network.lower()
        try:
            self.network = BlockchainNetwork(self.network_name)
        except ValueError:
            # Default to Bitcoin if network not recognized
            self.network = BlockchainNetwork.BITCOIN
        
        self.manager = ChainAgnosticReceiptManager(default_network=self.network)
    
    def anchor_receipt(self, receipt_hash: str) -> Dict[str, Any]:
        """
        Anchor receipt hash to blockchain.
        
        Args:
            receipt_hash: SHA-256 hash of receipt
            
        Returns:
            Blockchain transaction details
        """
        try:
            # Prepare receipt data for anchoring
            receipt_data = {
                "receipt_hash": receipt_hash,
                "data_type": "receipt"
            }
            
            # Create chain config
            chain_config = ChainConfig(network=self.network)
            
            # Commit to blockchain using existing manager
            commitment = self.manager.commit_receipt(
                receipt_data=receipt_data,
                preferred_network=self.network,
                chain_config=chain_config
            )
            
            return {
                "network": self.network_name,
                "tx_hash": commitment.tx_hash,
                "status": "pending_confirmation",
                "network_enum": self.network.value
            }
        
        except Exception as e:
            # Return pending status if anchoring fails
            return {
                "network": self.network_name,
                "tx_hash": None,
                "status": "failed",
                "error": str(e)
            }
    
    def verify_anchor(self, tx_hash: str) -> Dict[str, Any]:
        """
        Verify blockchain anchor exists and is confirmed.
        
        Args:
            tx_hash: Transaction hash to verify
            
        Returns:
            Verification result with confirmation details
        """
        try:
            chain_config = ChainConfig(network=self.network)
            result = self.manager.verify_receipt(
                tx_hash=tx_hash,
                network=self.network,
                chain_config=chain_config
            )
            
            # Convert result to dict format
            if isinstance(result, dict):
                return result
            else:
                return {
                    "verified": True,
                    "tx_hash": tx_hash,
                    "network": self.network_name,
                    "confirmations": result.get("confirmations", 0) if isinstance(result, dict) else 0
                }
        
        except Exception as e:
            return {
                "verified": False,
                "tx_hash": tx_hash,
                "network": self.network_name,
                "error": str(e)
            }

