"""
Bitcoin blockchain data ingestion and verification
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

# Bitcoin RPC imports
try:
    from bitcoin.rpc import RawProxy
    BITCOIN_AVAILABLE = True
except ImportError:
    BITCOIN_AVAILABLE = False
    RawProxy = None

from src.shared.receipts import CryptographicReceiptGenerator, IntelligenceReceipt
from src.shared.blockchain import BlockchainAnchor
from .parsers.bitcoin_parser import BitcoinTransactionParser

logger = logging.getLogger(__name__)


class BitcoinOracle:
    """
    Bitcoin blockchain oracle for verified data feeds.
    
    Ingests Bitcoin blocks, generates cryptographic receipts,
    and provides verified data to downstream systems.
    """
    
    def __init__(
        self,
        rpc_url: str = "http://localhost:8332",
        rpc_user: Optional[str] = None,
        rpc_password: Optional[str] = None
    ):
        """
        Initialize Bitcoin oracle.
        
        Args:
            rpc_url: Bitcoin RPC endpoint
            rpc_user: RPC username
            rpc_password: RPC password
        """
        if not BITCOIN_AVAILABLE:
            logger.warning("python-bitcoinlib not available. Bitcoin oracle will use mock mode.")
            self.rpc = None
            self.enabled = False
        else:
            try:
                # Initialize RPC connection
                if rpc_user and rpc_password:
                    # Build connection URL with credentials
                    # RawProxy expects service_url format: http://user:pass@host:port
                    if "@" not in rpc_url:
                        # Parse URL and add credentials
                        from urllib.parse import urlparse, urlunparse
                        parsed = urlparse(rpc_url)
                        netloc = f"{rpc_user}:{rpc_password}@{parsed.netloc}"
                        rpc_url = urlunparse(parsed._replace(netloc=netloc))
                    
                    self.rpc = RawProxy(service_url=rpc_url)
                else:
                    self.rpc = RawProxy(service_url=rpc_url)
                
                # Verify connection
                try:
                    self.rpc.getblockcount()
                    self.enabled = True
                    logger.info(f"Bitcoin oracle connected to {rpc_url}")
                except Exception as e:
                    logger.warning(f"Failed to connect to Bitcoin node: {e}")
                    self.rpc = None
                    self.enabled = False
            
            except Exception as e:
                logger.error(f"Failed to initialize Bitcoin oracle: {e}")
                self.rpc = None
                self.enabled = False
        
        self.rpc_url = rpc_url
        self.receipt_generator = CryptographicReceiptGenerator()
        self.blockchain_anchor = BlockchainAnchor(network="bitcoin")
        self.parser = BitcoinTransactionParser()
    
    def get_block(self, block_height: int) -> Dict[str, Any]:
        """
        Fetch Bitcoin block by height.
        
        Args:
            block_height: Block height to fetch
            
        Returns:
            Block data with full transaction details
        """
        if not self.enabled or not self.rpc:
            raise RuntimeError("Bitcoin oracle not enabled or node not connected")
        
        block_hash = self.rpc.getblockhash(block_height)
        # Verbosity 2 = full transaction data
        block = self.rpc.getblock(block_hash, 2)
        return block
    
    def get_latest_block_height(self) -> int:
        """Get current blockchain height"""
        if not self.enabled or not self.rpc:
            # Return mock height if not connected
            return 825000
        
        return self.rpc.getblockcount()
    
    def parse_block_transactions(self, block: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse transactions from block.
        
        Args:
            block: Raw block data from Bitcoin RPC
            
        Returns:
            List of parsed transactions
        """
        return self.parser.parse_transactions(block)
    
    def ingest_block(
        self,
        block_height: int,
        generate_receipt: bool = True,
        anchor_to_blockchain: bool = False
    ) -> Dict[str, Any]:
        """
        Ingest Bitcoin block and generate cryptographic receipt.
        
        Args:
            block_height: Block height to ingest
            generate_receipt: Whether to generate cryptographic receipt
            anchor_to_blockchain: Whether to anchor receipt to blockchain
            
        Returns:
            Ingestion result with receipt
        """
        # Fetch block (will raise if not connected)
        try:
            block = self.get_block(block_height)
        except RuntimeError:
            # Mock mode - return empty block structure
            logger.warning(f"Bitcoin oracle in mock mode, returning mock block {block_height}")
            block = {
                "hash": f"mock_block_{block_height}",
                "height": block_height,
                "time": int(datetime.now().timestamp()),
                "tx": []
            }
        
        # Parse transactions
        transactions = self.parse_block_transactions(block)
        
        # Prepare data package
        data_package = {
            "block_height": block_height,
            "block_hash": block.get('hash', f"mock_{block_height}"),
            "timestamp": block.get('time', int(datetime.now().timestamp())),
            "tx_count": len(transactions),
            "transactions": transactions
        }
        
        # Generate receipt
        receipt = None
        if generate_receipt:
            receipt = self.receipt_generator.generate_receipt(
                data=data_package,
                source=f"bitcoin_block_{block_height}",
                classification="UNCLASSIFIED",
                blockchain="bitcoin" if anchor_to_blockchain else None
            )
        
        # Anchor to blockchain if requested
        blockchain_anchor_result = None
        if anchor_to_blockchain and receipt:
            try:
                blockchain_anchor_result = self.blockchain_anchor.anchor_receipt(receipt.intelligence_hash)
            except Exception as e:
                logger.warning(f"Failed to anchor receipt to blockchain: {e}")
                blockchain_anchor_result = {"status": "failed", "error": str(e)}
        
        return {
            "block_height": block_height,
            "block_hash": block.get('hash', f"mock_{block_height}"),
            "tx_count": len(transactions),
            "data_package": data_package,
            "receipt": receipt.__dict__ if receipt else None,
            "blockchain_anchor": blockchain_anchor_result,
            "ingested_at": datetime.utcnow().isoformat() + 'Z'
        }
    
    def ingest_block_range(
        self,
        start_height: int,
        end_height: int,
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Ingest range of Bitcoin blocks.
        
        Args:
            start_height: Starting block height
            end_height: Ending block height
            batch_size: Number of blocks to process in parallel (future: async)
            
        Returns:
            List of ingestion results
        """
        results = []
        for height in range(start_height, end_height + 1):
            try:
                result = self.ingest_block(height)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to ingest block {height}: {e}")
                results.append({
                    "block_height": height,
                    "error": str(e),
                    "ingested_at": datetime.utcnow().isoformat() + 'Z'
                })
        
        return results
    
    def get_receipt(self, receipt_id: str) -> Optional[IntelligenceReceipt]:
        """
        Retrieve receipt by ID.
        
        Args:
            receipt_id: Receipt ID to retrieve
            
        Returns:
            Receipt object or None (database retrieval to be implemented)
        """
        # TODO: Implement receipt storage/retrieval
        logger.warning(f"Receipt retrieval not yet implemented: {receipt_id}")
        return None
    
    def verify_external_source(
        self,
        receipt_id: str,
        source_name: str,
        source_data_hash: str
    ) -> Dict[str, Any]:
        """
        Verify external source (Chainalysis, TRM, etc.) used ABC-verified data.
        
        Args:
            receipt_id: ABC receipt ID
            source_name: Name of external source
            source_data_hash: Hash of data used by external source
            
        Returns:
            Verification result
        """
        receipt = self.get_receipt(receipt_id)
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

