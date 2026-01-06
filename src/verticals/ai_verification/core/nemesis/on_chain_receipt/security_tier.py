"""
ABC Tiered Security Model
Three-tier security classification for blockchain commitments

Tier 1 (Unclassified): Public blockchains, anyone can verify
Tier 2 (SBU): Permissioned chains, controlled access
Tier 3 (Classified): Hash-only commitments, zero data exposure

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


class SecurityTier(Enum):
    """
    Security classification tiers for intelligence compilations
    
    TIER_1_UNCLASSIFIED: Public blockchains, full data visibility
    TIER_2_SBU: Permissioned chains, controlled access (Sensitive But Unclassified)
    TIER_3_CLASSIFIED: Hash-only commitments, zero data exposure
    """
    TIER_1_UNCLASSIFIED = "unclassified"
    TIER_2_SBU = "sbu"  # Sensitive But Unclassified
    TIER_3_CLASSIFIED = "classified"


@dataclass
class TierConfig:
    """Configuration for a security tier"""
    tier: SecurityTier
    name: str
    description: str
    blockchain_type: str  # "public", "permissioned", "hash_only"
    data_exposure: str  # "full", "controlled", "zero"
    verification_access: str  # "public", "permissioned", "hash_only"
    allowed_blockchains: List[str]
    requires_authentication: bool
    requires_authorization: bool
    hash_only: bool  # If True, only commit hash, no data


# Tier configurations
TIER_CONFIGS: Dict[SecurityTier, TierConfig] = {
    SecurityTier.TIER_1_UNCLASSIFIED: TierConfig(
        tier=SecurityTier.TIER_1_UNCLASSIFIED,
        name="Unclassified",
        description="Public blockchains, anyone can verify",
        blockchain_type="public",
        data_exposure="full",
        verification_access="public",
        allowed_blockchains=["bitcoin", "ethereum", "polygon", "arbitrum", "base", "optimism"],
        requires_authentication=False,
        requires_authorization=False,
        hash_only=False
    ),
    SecurityTier.TIER_2_SBU: TierConfig(
        tier=SecurityTier.TIER_2_SBU,
        name="Sensitive But Unclassified (SBU)",
        description="Permissioned chains, controlled access",
        blockchain_type="permissioned",
        data_exposure="controlled",
        verification_access="permissioned",
        allowed_blockchains=["hyperledger", "corda", "quorum", "besu"],  # Permissioned chains
        requires_authentication=True,
        requires_authorization=True,
        hash_only=False
    ),
    SecurityTier.TIER_3_CLASSIFIED: TierConfig(
        tier=SecurityTier.TIER_3_CLASSIFIED,
        name="Classified",
        description="Hash-only commitments, zero data exposure",
        blockchain_type="hash_only",
        data_exposure="zero",
        verification_access="hash_only",
        allowed_blockchains=["bitcoin", "ethereum"],  # Can use public chains for hash-only
        requires_authentication=True,
        requires_authorization=True,
        hash_only=True
    )
}


class TieredSecurityManager:
    """
    Manages security tier selection and enforcement for blockchain commitments
    
    Ensures that:
    - Tier 1: Full data on public blockchains
    - Tier 2: Controlled data on permissioned chains
    - Tier 3: Hash-only on any chain (zero data exposure)
    """
    
    def __init__(self):
        self.tier_configs = TIER_CONFIGS
    
    def get_tier_config(self, tier: SecurityTier) -> TierConfig:
        """Get configuration for a security tier"""
        return self.tier_configs[tier]
    
    def validate_blockchain_for_tier(
        self,
        tier: SecurityTier,
        blockchain: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that a blockchain is allowed for a given tier
        
        Args:
            tier: Security tier
            blockchain: Blockchain name
            
        Returns:
            (is_valid, error_message)
        """
        config = self.get_tier_config(tier)
        
        if blockchain.lower() not in [b.lower() for b in config.allowed_blockchains]:
            return False, f"Blockchain '{blockchain}' not allowed for {config.name} tier. Allowed: {config.allowed_blockchains}"
        
        return True, None
    
    def should_commit_data(self, tier: SecurityTier) -> bool:
        """
        Determine if full data should be committed (vs hash-only)
        
        Args:
            tier: Security tier
            
        Returns:
            True if data should be committed, False for hash-only
        """
        config = self.get_tier_config(tier)
        return not config.hash_only
    
    def get_commitment_strategy(
        self,
        tier: SecurityTier,
        blockchain: str
    ) -> Dict[str, Any]:
        """
        Get commitment strategy for tier and blockchain
        
        Args:
            tier: Security tier
            blockchain: Blockchain name
            
        Returns:
            Strategy configuration
        """
        config = self.get_tier_config(tier)
        
        strategy = {
            "tier": tier.value,
            "tier_name": config.name,
            "blockchain": blockchain,
            "commit_data": not config.hash_only,
            "commit_hash": True,  # Always commit hash
            "requires_auth": config.requires_authentication,
            "requires_authorization": config.requires_authorization,
            "data_exposure": config.data_exposure,
            "verification_access": config.verification_access
        }
        
        return strategy
    
    def determine_tier_from_classification(
        self,
        classification: str
    ) -> SecurityTier:
        """
        Determine security tier from classification string
        
        Args:
            classification: Classification string (e.g., "UNCLASSIFIED", "SBU", "CLASSIFIED")
            
        Returns:
            SecurityTier
        """
        classification_upper = classification.upper()
        
        if "CLASSIFIED" in classification_upper or "SECRET" in classification_upper or "TOP SECRET" in classification_upper:
            return SecurityTier.TIER_3_CLASSIFIED
        elif "SBU" in classification_upper or "SENSITIVE" in classification_upper:
            return SecurityTier.TIER_2_SBU
        else:
            return SecurityTier.TIER_1_UNCLASSIFIED
    
    def get_tier_summary(self) -> Dict[str, Any]:
        """Get summary of all tiers"""
        return {
            tier.value: {
                "name": config.name,
                "description": config.description,
                "blockchain_type": config.blockchain_type,
                "data_exposure": config.data_exposure,
                "verification_access": config.verification_access,
                "allowed_blockchains": config.allowed_blockchains,
                "hash_only": config.hash_only
            }
            for tier, config in self.tier_configs.items()
        }


# Global instance
tiered_security_manager = TieredSecurityManager()

