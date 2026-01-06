"""
On-Chain Receipt System
Chain-agnostic cryptographic receipt generation and verification

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from .receipt_generator import (
    CryptographicReceiptGenerator,
    IntelligenceReceipt,
    ReceiptStatus,
    ReceiptVerifier
)

from .blockchain_abstraction import (
    BlockchainNetwork,
    ChainConfig,
    OnChainCommitment,
    BlockchainAdapter,
    BlockchainAdapterFactory,
    ChainAgnosticReceiptManager,
    commit_receipt_to_chain
)

from .bitcoin_adapter import BitcoinAdapter
from .ethereum_adapter import EthereumAdapter
from .security_tier import (
    SecurityTier,
    TierConfig,
    TieredSecurityManager,
    tiered_security_manager
)

# Register blockchain adapters
BlockchainAdapterFactory.register_adapter(BlockchainNetwork.BITCOIN, BitcoinAdapter)
BlockchainAdapterFactory.register_adapter(BlockchainNetwork.ETHEREUM, EthereumAdapter)
BlockchainAdapterFactory.register_adapter(BlockchainNetwork.POLYGON, EthereumAdapter)
BlockchainAdapterFactory.register_adapter(BlockchainNetwork.ARBITRUM, EthereumAdapter)
BlockchainAdapterFactory.register_adapter(BlockchainNetwork.BASE, EthereumAdapter)
BlockchainAdapterFactory.register_adapter(BlockchainNetwork.OPTIMISM, EthereumAdapter)

__all__ = [
    "CryptographicReceiptGenerator",
    "IntelligenceReceipt",
    "ReceiptStatus",
    "ReceiptVerifier",
    "BlockchainNetwork",
    "ChainConfig",
    "OnChainCommitment",
    "BlockchainAdapter",
    "BlockchainAdapterFactory",
    "ChainAgnosticReceiptManager",
    "commit_receipt_to_chain",
    "BitcoinAdapter",
    "EthereumAdapter",
    "SecurityTier",
    "TierConfig",
    "TieredSecurityManager",
    "tiered_security_manager",
]
