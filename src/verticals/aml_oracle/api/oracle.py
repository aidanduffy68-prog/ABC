"""
Oracle API endpoints for blockchain data feeds
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from typing import Optional, List
import asyncio
import logging
import os

# Conditional import - oracle may not be available
try:
    from src.verticals.aml_oracle.core.oracle.bitcoin_ingestion import BitcoinOracle
    from src.verticals.aml_oracle.core.oracle.data_feed import OracleDataFeed, StreamSubscription
    ORACLE_AVAILABLE = True
except ImportError as e:
    ORACLE_AVAILABLE = False
    BitcoinOracle = None
    OracleDataFeed = None
    StreamSubscription = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/oracle", tags=["oracle"])

# Initialize oracles (will be None if not available)
bitcoin_oracle = None

# Check if oracle is enabled
ORACLE_ENABLED = os.getenv("ORACLE_ENABLED", "false").lower() == "true"

if ORACLE_ENABLED and ORACLE_AVAILABLE:
    try:
        bitcoin_oracle = BitcoinOracle(
            rpc_url=os.getenv("BITCOIN_RPC_URL", "http://localhost:8332"),
            rpc_user=os.getenv("BITCOIN_RPC_USER"),
            rpc_password=os.getenv("BITCOIN_RPC_PASSWORD")
        )
    except Exception as e:
        logger.warning(f"Failed to initialize Bitcoin oracle: {e}")
        bitcoin_oracle = None


@router.get("/health")
async def oracle_health():
    """Check oracle service health"""
    if not ORACLE_ENABLED:
        return {
            "status": "disabled",
            "message": "Oracle layer is disabled. Set ORACLE_ENABLED=true to enable."
        }
    
    if not bitcoin_oracle:
        return {
            "status": "unavailable",
            "message": "Bitcoin oracle not initialized"
        }
    
    try:
        latest_block = bitcoin_oracle.get_latest_block_height()
        return {
            "status": "healthy",
            "bitcoin": {
                "connected": bitcoin_oracle.enabled,
                "latest_block": latest_block
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/ingest/bitcoin/block/{block_height}")
async def ingest_bitcoin_block(
    block_height: int,
    generate_receipt: bool = Query(default=True, description="Generate cryptographic receipt"),
    anchor_to_blockchain: bool = Query(default=False, description="Anchor receipt to blockchain")
):
    """
    Ingest Bitcoin block and generate cryptographic receipt.
    
    **ABC provides infrastructure for verification.** This endpoint ingests blockchain data
    and generates cryptographic receipts, enabling downstream systems (Foundry, ML models)
    to prove they analyzed identical data. ABC verifies inputs, not outputs - humans make
    final decisions.
    
    Args:
        block_height: Block height to ingest
        generate_receipt: Generate cryptographic receipt (proof of data integrity)
        anchor_to_blockchain: Anchor receipt to blockchain for immutability
        
    Returns:
        Ingestion result with receipt (cryptographic proof of data integrity)
    """
    if not bitcoin_oracle:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin oracle not available. Check configuration and ORACLE_ENABLED setting."
        )
    
    try:
        result = bitcoin_oracle.ingest_block(
            block_height=block_height,
            generate_receipt=generate_receipt,
            anchor_to_blockchain=anchor_to_blockchain
        )
        return result
    except Exception as e:
        logger.error(f"Error ingesting Bitcoin block {block_height}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/bitcoin/range")
async def ingest_bitcoin_range(
    start_height: int = Query(..., description="Starting block height"),
    end_height: int = Query(..., description="Ending block height"),
    batch_size: int = Query(default=10, description="Batch size for processing")
):
    """
    Ingest range of Bitcoin blocks.
    
    Args:
        start_height: Starting block height
        end_height: Ending block height
        batch_size: Batch size for processing
        
    Returns:
        List of ingestion results
    """
    if not bitcoin_oracle:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin oracle not available"
        )
    
    try:
        results = bitcoin_oracle.ingest_block_range(
            start_height=start_height,
            end_height=end_height,
            batch_size=batch_size
        )
        return {
            "blocks_ingested": len(results),
            "start_height": start_height,
            "end_height": end_height,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error ingesting Bitcoin block range {start_height}-{end_height}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/receipt/{receipt_id}")
async def get_receipt(receipt_id: str):
    """
    Retrieve oracle receipt by ID.
    
    Args:
        receipt_id: Receipt ID
        
    Returns:
        Receipt data
    """
    if not bitcoin_oracle:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin oracle not available"
        )
    
    receipt = bitcoin_oracle.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipt.__dict__


@router.post("/verify/source")
async def verify_external_source(
    receipt_id: str = Query(..., description="ABC receipt ID"),
    source_name: str = Query(..., description="Name of external source"),
    source_data_hash: str = Query(..., description="Hash of data used by source")
):
    """
    Verify external source (Chainalysis, TRM, Foundry) used ABC-verified data.
    
    **ABC proves all sources analyzed the same data.** For AML compliance, this enables
    cryptographic proof that Chainalysis, TRM, and Foundry ML models all analyzed identical
    blockchain data. The compliance officer makes the final call—but with confidence in
    data integrity. ABC verifies inputs, not outputs.
    
    Args:
        receipt_id: ABC receipt ID
        source_name: Name of external source (e.g., "chainalysis", "trm_labs", "foundry")
        source_data_hash: Hash of data used by source
        
    Returns:
        Verification result proving source used ABC-verified data
    """
    if not bitcoin_oracle:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin oracle not available"
        )
    
    result = bitcoin_oracle.verify_external_source(
        receipt_id=receipt_id,
        source_name=source_name,
        source_data_hash=source_data_hash
    )
    return result


@router.websocket("/stream/bitcoin")
async def stream_bitcoin_data(websocket: WebSocket):
    """
    WebSocket endpoint for real-time Bitcoin data stream.
    
    Streams verified Bitcoin blocks as they arrive.
    """
    if not bitcoin_oracle:
        await websocket.close(code=1008, reason="Bitcoin oracle not available")
        return
    
    await websocket.accept()
    
    feed = OracleDataFeed(blockchain="bitcoin", oracle=bitcoin_oracle)
    subscription = StreamSubscription(websocket=websocket)
    
    try:
        async for block_data in feed.stream_blocks():
            # Ingest block and generate receipt
            try:
                result = bitcoin_oracle.ingest_block(block_data['height'])
                
                # Send to subscriber
                await subscription.send({
                    "type": "block",
                    "blockchain": "bitcoin",
                    "block_height": block_data['height'],
                    "block_hash": block_data['hash'],
                    "tx_count": result['tx_count'],
                    "receipt_id": result['receipt']['receipt_id'] if result['receipt'] else None,
                    "data_hash": result['receipt']['intelligence_hash'] if result['receipt'] else None,
                    "timestamp": result['receipt']['timestamp'] if result['receipt'] else result['ingested_at']
                })
            except Exception as e:
                logger.error(f"Error processing block {block_data.get('height')}: {e}")
                # Continue streaming despite errors
    
    except WebSocketDisconnect:
        logger.info("Client disconnected from Bitcoin stream")
    except Exception as e:
        logger.error(f"Error in Bitcoin stream: {e}", exc_info=True)
        try:
            await websocket.close()
        except Exception:
            pass


@router.websocket("/stream/bitcoin/transactions")
async def stream_bitcoin_transactions(websocket: WebSocket):
    """
    WebSocket endpoint for real-time Bitcoin transaction stream.
    
    Streams individual transactions as they are confirmed.
    """
    if not bitcoin_oracle:
        await websocket.close(code=1008, reason="Bitcoin oracle not available")
        return
    
    await websocket.accept()
    
    feed = OracleDataFeed(blockchain="bitcoin", oracle=bitcoin_oracle)
    subscription = StreamSubscription(websocket=websocket)
    
    try:
        async for tx_data in feed.stream_transactions():
            await subscription.send({
                "type": "transaction",
                "blockchain": "bitcoin",
                "txid": tx_data['txid'],
                "block_height": tx_data['block_height'],
                "timestamp": tx_data['timestamp']
            })
    
    except WebSocketDisconnect:
        logger.info("Client disconnected from transaction stream")
    except Exception as e:
        logger.error(f"Error in transaction stream: {e}", exc_info=True)
        try:
            await websocket.close()
        except Exception:
            pass

