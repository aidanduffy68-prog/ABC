"""
Palantir Foundry Integration API Endpoints - AML Oracle Vertical
Provides AML-specific Foundry endpoints for blockchain data ingestion and ML model verification

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime
from pydantic import BaseModel
import logging

from src.shared.integrations.foundry.connector import FoundryDataExportConnector
from src.shared.middleware.auth import require_auth
from src.shared.middleware.rate_limit import rate_limit

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/foundry/aml", tags=["foundry-aml"])

# Initialize connector
foundry_connector = FoundryDataExportConnector()


class ModelResult(BaseModel):
    """Model result with data hash"""
    model_id: str
    data_hash: str
    output: Optional[Dict[str, Any]] = None


class MLModelVerificationRequest(BaseModel):
    """Request to verify ML models"""
    receipt_id: str
    model_results: List[ModelResult]


@router.post("/ingest/blockchain", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=50, window_seconds=60)
async def foundry_ingest_blockchain(
    blockchain: str = Query(..., description="Blockchain to ingest (bitcoin, ethereum)"),
    start_height: int = Query(..., description="Starting block height"),
    end_height: int = Query(..., description="Ending block height"),
    generate_receipts: bool = Query(default=True, description="Generate cryptographic receipts")
) -> Dict[str, Any]:
    """
    Ingest blockchain data for Foundry with ABC verification.
    
    **ABC provides cryptographic verification that all ML models analyzed identical customer
    data - critical for regulatory audit and explainability.** ABC is infrastructure for
    verification, not decision-making. Humans (compliance officers) make the final call.
    
    This endpoint allows Foundry to ingest verified blockchain data with cryptographic
    receipts for audit trails. When Foundry runs ML models for AML risk scoring, ABC proves
    all models analyzed the same blockchain data.
    
    Args:
        blockchain: Blockchain to ingest ("bitcoin", "ethereum")
        start_height: Starting block height
        end_height: Ending block height
        generate_receipts: Generate cryptographic receipts
        
    Returns:
        Ingestion results with receipts (proof of data integrity)
    """
    if blockchain.lower() != "bitcoin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blockchain {blockchain} not yet supported. Only 'bitcoin' is currently supported."
        )
    
    try:
        from src.verticals.aml_oracle.core.oracle.bitcoin_ingestion import BitcoinOracle
        import os
        
        bitcoin_oracle = BitcoinOracle(
            rpc_url=os.getenv("BITCOIN_RPC_URL", "http://localhost:8332"),
            rpc_user=os.getenv("BITCOIN_RPC_USER"),
            rpc_password=os.getenv("BITCOIN_RPC_PASSWORD")
        )
        
        try:
            results = bitcoin_oracle.ingest_block_range(
                start_height=start_height,
                end_height=end_height
            )
            
            return {
                "blockchain": blockchain,
                "blocks_ingested": len(results),
                "start_height": start_height,
                "end_height": end_height,
                "receipts": [r['receipt'] for r in results if r.get('receipt')],
                "total_transactions": sum(r.get('tx_count', 0) for r in results)
            }
        
        except Exception as e:
            logger.error(f"Error ingesting blockchain data: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Oracle layer not available. Set ORACLE_ENABLED=true and install oracle dependencies."
        )


@router.post("/verify/ml-models", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=100, window_seconds=60)
async def foundry_verify_ml_models(
    request: MLModelVerificationRequest
) -> Dict[str, Any]:
    """
    Verify Foundry ML models analyzed ABC-verified data.
    
    **ABC verifies inputs, not outputs. For AML compliance, ABC proves Chainalysis, TRM,
    and Foundry all analyzed the same blockchain data. The compliance officer makes the
    final call—but with confidence in data integrity.**
    
    When Foundry runs multiple ML models on blockchain data, this endpoint verifies all
    models used identical ABC-verified inputs. This is critical for regulatory audit and
    explainability - proving that different risk scores stem from model methodology, not
    data inconsistency.
    
    **Example (AML Risk Scoring):**
    - Foundry ML models flag a transaction for review
    - ABC proves Chainalysis, TRM, and Foundry all analyzed the same blockchain data
    - Compliance officer reviews with confidence in data integrity
    - Final decision remains with compliance officer (human in the loop)
    
    Args:
        request: Verification request with receipt_id and model_results
    
    Returns:
        Verification result showing all models used identical ABC-verified inputs
    """
    try:
        from src.verticals.aml_oracle.core.oracle.verification import MultiSourceVerifier
        
        verifier = MultiSourceVerifier()
        result = verifier.verify_ml_models(
            receipt_id=request.receipt_id,
            model_results=[m.dict() for m in request.model_results]
        )
        return result
    
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Oracle verification not available"
        )
    except Exception as e:
        logger.error(f"Error verifying ML models: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/webhook/data-consumed", status_code=status.HTTP_200_OK)
async def foundry_webhook_data_consumed(
    receipt_id: str = Query(..., description="ABC receipt ID"),
    foundry_data_hash: str = Query(..., description="Hash of data Foundry consumed"),
    pipeline_id: str = Query(..., description="Foundry pipeline identifier"),
    consumed_at: str = Query(..., description="Timestamp of consumption")
) -> Dict[str, Any]:
    """
    Webhook for Foundry to report data consumption.
    
    **ABC verifies Foundry used the correct ABC-verified data.** This enables cryptographic
    proof that Foundry's ML models analyzed identical blockchain data, critical for regulatory
    compliance and audit trails. Humans (compliance officers) make final decisions based on
    verified data integrity.
    
    Foundry calls this when it consumes ABC-verified data, allowing ABC to verify Foundry
    used the correct data. This creates a complete audit trail from blockchain → ABC → Foundry
    → ML models → human decision.
    
    Args:
        receipt_id: ABC receipt ID
        foundry_data_hash: Hash of data Foundry consumed
        pipeline_id: Foundry pipeline identifier
        consumed_at: Timestamp of consumption
        
    Returns:
        Verification result proving Foundry consumed correct ABC-verified data
    """
    try:
        from src.verticals.aml_oracle.core.oracle.bitcoin_ingestion import BitcoinOracle
        import os
        
        bitcoin_oracle = BitcoinOracle(
            rpc_url=os.getenv("BITCOIN_RPC_URL", "http://localhost:8332"),
            rpc_user=os.getenv("BITCOIN_RPC_USER"),
            rpc_password=os.getenv("BITCOIN_RPC_PASSWORD")
        )
        
        result = bitcoin_oracle.verify_external_source(
            receipt_id=receipt_id,
            source_name=f"foundry_pipeline_{pipeline_id}",
            source_data_hash=foundry_data_hash
        )
        
        return {
            **result,
            "pipeline_id": pipeline_id,
            "consumed_at": consumed_at
        }
    
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Oracle layer not available"
        )
    except Exception as e:
        logger.error(f"Error verifying Foundry data consumption: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/audit-trail/{receipt_id}", status_code=status.HTTP_200_OK)
@require_auth
async def foundry_audit_trail(
    receipt_id: str
) -> Dict[str, Any]:
    """
    Get complete audit trail for ABC-verified data in Foundry.
    
    Args:
        receipt_id: ABC receipt ID
        
    Returns:
        Complete audit trail
    """
    # TODO: Implement audit trail retrieval (database layer in Phase 5)
    return {
        "receipt_id": receipt_id,
        "audit_trail": [],
        "note": "Audit trail retrieval not yet implemented"
    }

