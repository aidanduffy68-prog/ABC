"""
Real-time data feed for oracle streams
"""
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class StreamSubscription:
    """WebSocket subscription for data streams"""
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.active = True
    
    async def send(self, data: Dict[str, Any]):
        """Send data to subscriber"""
        if self.active:
            try:
                await self.websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to subscriber: {e}")
                self.active = False
    
    async def close(self):
        """Close subscription"""
        self.active = False
        try:
            await self.websocket.close()
        except Exception:
            pass


class OracleDataFeed:
    """
    Real-time data feed for blockchain oracles.
    
    Monitors blockchain for new blocks and streams verified data
    to subscribers.
    """
    
    def __init__(self, blockchain: str, oracle: Any):
        """
        Initialize data feed.
        
        Args:
            blockchain: Blockchain to monitor ("bitcoin", "ethereum")
            oracle: Oracle instance (BitcoinOracle, EthereumOracle)
        """
        self.blockchain = blockchain
        self.oracle = oracle
        self.last_block = None
        self.poll_interval = 10  # seconds
    
    async def stream_blocks(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream new blocks as they arrive.
        
        Yields:
            Block data dictionaries
        """
        # Get current block height
        if self.last_block is None:
            try:
                self.last_block = self.oracle.get_latest_block_height()
            except Exception as e:
                logger.error(f"Failed to get latest block height: {e}")
                self.last_block = 0
        
        while True:
            try:
                # Check for new blocks
                current_block = self.oracle.get_latest_block_height()
                
                if current_block > self.last_block:
                    # New block(s) available
                    for height in range(self.last_block + 1, current_block + 1):
                        try:
                            block = self.oracle.get_block(height)
                            yield {
                                "height": height,
                                "hash": block.get('hash', f"mock_{height}"),
                                "time": block.get('time', 0),
                                "tx_count": len(block.get('tx', []))
                            }
                        except Exception as e:
                            logger.error(f"Failed to get block {height}: {e}")
                            # Skip this block and continue
                            continue
                    
                    self.last_block = current_block
                
                # Wait before checking again
                await asyncio.sleep(self.poll_interval)
            
            except Exception as e:
                logger.error(f"Error in block stream: {e}")
                await asyncio.sleep(self.poll_interval)
    
    async def stream_transactions(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream individual transactions as they are confirmed.
        
        Yields:
            Transaction data dictionaries
        """
        async for block_data in self.stream_blocks():
            try:
                block = self.oracle.get_block(block_data['height'])
                transactions = self.oracle.parse_block_transactions(block)
                
                for tx in transactions:
                    yield {
                        "txid": tx.get('txid'),
                        "block_height": block_data['height'],
                        "block_hash": block_data['hash'],
                        "timestamp": block_data['time'],
                        "transaction": tx
                    }
            except Exception as e:
                logger.error(f"Error streaming transactions for block {block_data.get('height')}: {e}")

