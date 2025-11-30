"""
On-Chain Cryptographic Receipt System
Generates minimal cryptographic proofs of intelligence outputs without revealing proprietary systems
"""

from .receipt_generator import (
    CryptographicReceiptGenerator,
    IntelligenceReceipt,
    ReceiptStatus
)

from .bitcoin_integration import (
    BitcoinOnChainIntegration,
    submit_receipt_to_bitcoin
)

from .receipt_verifier import (
    ReceiptVerifier,
    verify_receipt
)

__all__ = [
    "CryptographicReceiptGenerator",
    "IntelligenceReceipt",
    "ReceiptStatus",
    "BitcoinOnChainIntegration",
    "submit_receipt_to_bitcoin",
    "ReceiptVerifier",
    "verify_receipt"
]
