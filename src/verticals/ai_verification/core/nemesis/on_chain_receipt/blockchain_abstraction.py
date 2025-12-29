"""
Blockchain Abstraction Layer
Chain-agnostic interface for blockchain operations (Bitcoin, Ethereum, etc.)

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    BASE = "base"
    OPTIMISM = "optimism"
    # Add more as needed


@dataclass
class ChainConfig:
    """Configuration for a specific blockchain network"""
    network: BlockchainNetwork
    rpc_url: Optional[str] = None
    rpc_user: Optional[str] = None
    rpc_password: Optional[str] = None
    network_type: str = "mainnet"  # mainnet, testnet, etc.
    gas_price: Optional[int] = None  # For EVM chains
    fee_rate: Optional[float] = None  # For Bitcoin (sat/vB)
    max_data_size: int = 80  # Max bytes for on-chain data (varies by chain)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Validate RPC URL if provided
        if self.rpc_url:
            from src.shared.security.rpc_validation import validate_rpc_url
            import os
            # Allow localhost in development, not in production
            allow_local = os.getenv("ENVIRONMENT", "development") == "development"
            if not validate_rpc_url(self.rpc_url, allow_local=allow_local):
                raise ValueError(
                    f"RPC URL not in whitelist: {self.rpc_url}. "
                    "Only whitelisted RPC endpoints are allowed for security."
                )
        
        # Validate gas price (prevent excessive fees)
        if self.gas_price is not None:
            MAX_GAS_PRICE_GWEI = 1000  # 1000 gwei maximum
            MAX_GAS_PRICE_WEI = MAX_GAS_PRICE_GWEI * 1_000_000_000  # Convert to wei
            if self.gas_price > MAX_GAS_PRICE_WEI:
                raise ValueError(
                    f"Gas price ({self.gas_price} wei) exceeds maximum allowed "
                    f"({MAX_GAS_PRICE_WEI} wei = {MAX_GAS_PRICE_GWEI} gwei)"
                )


@dataclass
class OnChainCommitment:
    """Result of committing data to blockchain"""
    tx_hash: str
    network: BlockchainNetwork
    block_height: Optional[int] = None
    confirmation_count: int = 0
    timestamp: Optional[str] = None
    fee_paid: Optional[float] = None
    status: str = "pending"  # pending, confirmed, failed


class BlockchainAdapter(ABC):
    """
    Abstract base class for blockchain adapters
    Each blockchain (Bitcoin, Ethereum, etc.) implements this interface
    """
    
    @abstractmethod
    def commit_data(
        self,
        data: bytes,
        config: ChainConfig
    ) -> OnChainCommitment:
        """
        Commit data to blockchain
        
        Args:
            data: Data to commit (max size defined by config.max_data_size)
            config: Chain configuration
            
        Returns:
            OnChainCommitment with transaction details
        """
        pass
    
    @abstractmethod
    def verify_commitment(
        self,
        tx_hash: str,
        config: ChainConfig
    ) -> Dict[str, Any]:
        """
        Verify commitment exists on blockchain
        
        Args:
            tx_hash: Transaction hash
            config: Chain configuration
            
        Returns:
            Verification result with confirmation details
        """
        pass
    
    @abstractmethod
    def retrieve_data(
        self,
        tx_hash: str,
        config: ChainConfig
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve committed data from blockchain
        
        Args:
            tx_hash: Transaction hash
            config: Chain configuration
            
        Returns:
            Retrieved data if found
        """
        pass
    
    @abstractmethod
    def estimate_fee(
        self,
        data_size: int,
        config: ChainConfig
    ) -> float:
        """
        Estimate transaction fee for committing data
        
        Args:
            data_size: Size of data to commit (bytes)
            config: Chain configuration
            
        Returns:
            Estimated fee (in native currency)
        """
        pass


class BlockchainAdapterFactory:
    """
    Factory for creating blockchain adapters
    Chain-agnostic interface for vendors and agencies
    """
    
    _adapters: Dict[BlockchainNetwork, type] = {}
    
    @classmethod
    def register_adapter(cls, network: BlockchainNetwork, adapter_class: type):
        """Register a blockchain adapter implementation"""
        if not issubclass(adapter_class, BlockchainAdapter):
            raise ValueError(f"Adapter must implement BlockchainAdapter interface")
        cls._adapters[network] = adapter_class
    
    @classmethod
    def create_adapter(cls, network: BlockchainNetwork) -> BlockchainAdapter:
        """
        Create blockchain adapter for specified network
        
        Args:
            network: Blockchain network to use
            
        Returns:
            BlockchainAdapter instance
            
        Raises:
            ValueError: If network not supported
        """
        if network not in cls._adapters:
            raise ValueError(
                f"Network {network.value} not supported. "
                f"Available: {list(cls._adapters.keys())}"
            )
        
        adapter_class = cls._adapters[network]
        return adapter_class()
    
    @classmethod
    def get_supported_networks(cls) -> List[BlockchainNetwork]:
        """Get list of supported blockchain networks"""
        return list(cls._adapters.keys())


class ChainAgnosticReceiptManager:
    """
    Chain-agnostic receipt manager
    Allows vendors and agencies to choose their preferred blockchain
    """
    
    def __init__(self, default_network: BlockchainNetwork = BlockchainNetwork.BITCOIN):
        """
        Initialize receipt manager
        
        Args:
            default_network: Default blockchain network if not specified
        """
        self.default_network = default_network
        self.factory = BlockchainAdapterFactory()
    
    def commit_receipt(
        self,
        receipt_data: Dict[str, Any],
        preferred_network: Optional[BlockchainNetwork] = None,
        chain_config: Optional[ChainConfig] = None
    ) -> OnChainCommitment:
        """
        Commit receipt to blockchain (chain-agnostic)
        
        Args:
            receipt_data: Receipt data to commit
            preferred_network: Preferred blockchain network (uses default if None)
            chain_config: Chain-specific configuration (uses defaults if None)
            
        Returns:
            OnChainCommitment with transaction details
        """
        # Use preferred network or default
        network = preferred_network or self.default_network
        
        # Create or use provided config
        if chain_config is None:
            chain_config = ChainConfig(network=network)
        elif chain_config.network != network:
            raise ValueError(f"Chain config network mismatch: {chain_config.network} != {network}")
        
        # Create adapter for network
        adapter = self.factory.create_adapter(network)
        
        # Prepare data for on-chain commitment
        data_bytes = self._prepare_receipt_data(receipt_data, chain_config)
        
        # Commit to blockchain
        commitment = adapter.commit_data(data_bytes, chain_config)
        
        return commitment
    
    def verify_receipt(
        self,
        tx_hash: str,
        network: BlockchainNetwork,
        chain_config: Optional[ChainConfig] = None
    ) -> Dict[str, Any]:
        """
        Verify receipt on blockchain
        
        Args:
            tx_hash: Transaction hash
            network: Blockchain network
            chain_config: Chain-specific configuration
            
        Returns:
            Verification result
        """
        if chain_config is None:
            chain_config = ChainConfig(network=network)
        
        adapter = self.factory.create_adapter(network)
        return adapter.verify_commitment(tx_hash, chain_config)
    
    def retrieve_receipt(
        self,
        tx_hash: str,
        network: BlockchainNetwork,
        chain_config: Optional[ChainConfig] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve receipt from blockchain
        
        Args:
            tx_hash: Transaction hash
            network: Blockchain network
            chain_config: Chain-specific configuration
            
        Returns:
            Receipt data if found
        """
        if chain_config is None:
            chain_config = ChainConfig(network=network)
        
        adapter = self.factory.create_adapter(network)
        return adapter.retrieve_data(tx_hash, chain_config)
    
    def _prepare_receipt_data(
        self,
        receipt_data: Dict[str, Any],
        config: ChainConfig
    ) -> bytes:
        """
        Prepare receipt data for on-chain commitment
        Formats data according to chain-specific requirements
        
        Args:
            receipt_data: Receipt data dictionary
            config: Chain configuration
            
        Returns:
            Formatted bytes for on-chain commitment
        """
        # Sanitize receipt data before processing
        from src.shared.security.input_sanitization import sanitize_receipt_data, validate_json_depth
        try:
            validate_json_depth(receipt_data, max_depth=10)
            receipt_data = sanitize_receipt_data(receipt_data)
        except ValueError as e:
            raise ValueError(f"Receipt data validation failed: {e}")
        
        # Extract key fields
        receipt_id = receipt_data.get("receipt_id", "")[:32]
        intelligence_hash = receipt_data.get("intelligence_hash", "")[:32]
        timestamp = receipt_data.get("timestamp", "")
        
        # Format based on chain
        if config.network == BlockchainNetwork.BITCOIN:
            # Bitcoin OP_RETURN format (80 bytes max)
            return self._format_bitcoin_op_return(receipt_id, intelligence_hash, timestamp)
        elif config.network in [BlockchainNetwork.ETHEREUM, BlockchainNetwork.POLYGON,
                                BlockchainNetwork.ARBITRUM, BlockchainNetwork.BASE,
                                BlockchainNetwork.OPTIMISM]:
            # EVM chain format (event log or contract storage)
            return self._format_evm_data(receipt_id, intelligence_hash, timestamp)
        else:
            # Generic format
            data_str = f"{receipt_id}:{intelligence_hash}:{timestamp}"
            return data_str.encode('utf-8')[:config.max_data_size]
    
    def _format_bitcoin_op_return(
        self,
        receipt_id: str,
        intelligence_hash: str,
        timestamp: str
    ) -> bytes:
        """Format data for Bitcoin OP_RETURN (80 bytes max)"""
        receipt_id_bytes = receipt_id.encode('utf-8')[:32].ljust(32, b'\x00')
        hash_bytes = intelligence_hash.encode('utf-8')[:32].ljust(32, b'\x00')
        
        # Timestamp as 8 bytes (Unix timestamp)
        from datetime import datetime
        try:
            ts = int(datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp())
        except:
            ts = 0
        timestamp_bytes = ts.to_bytes(8, byteorder='big')
        
        # Metadata (8 bytes)
        metadata = b'\x00' * 8
        
        return (receipt_id_bytes + hash_bytes + timestamp_bytes + metadata)[:80]
    
    def _format_evm_data(
        self,
        receipt_id: str,
        intelligence_hash: str,
        timestamp: str
    ) -> bytes:
        """Format data for EVM chains (event log or contract call)"""
        # For EVM, we can use event logs or contract storage
        # This is a simplified format - in production, use proper ABI encoding
        data = {
            "receipt_id": receipt_id,
            "intelligence_hash": intelligence_hash,
            "timestamp": timestamp
        }
        import json
        return json.dumps(data).encode('utf-8')


# Convenience function for chain-agnostic receipt commitment
def commit_receipt_to_chain(
    receipt_data: Dict[str, Any],
    network: BlockchainNetwork = BlockchainNetwork.BITCOIN,
    chain_config: Optional[ChainConfig] = None
) -> OnChainCommitment:
    """
    Convenience function to commit receipt to any supported blockchain
    
    Usage:
        commitment = commit_receipt_to_chain(
            receipt_dict,
            network=BlockchainNetwork.ETHEREUM
        )
    """
    manager = ChainAgnosticReceiptManager()
    return manager.commit_receipt(receipt_data, preferred_network=network, chain_config=chain_config)

