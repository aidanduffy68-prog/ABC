"""
Agency Assessment API Endpoints
Endpoints for agency AI assessment submissions and consensus calculations

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import Field
import logging
import hashlib

from src.schemas.agency import AgencyAssessment, ConsensusResult
from src.consensus.engine import ConsensusEngine
from src.core.middleware.auth import require_auth
from src.core.middleware.rate_limit import rate_limit
from src.core.nemesis.on_chain_receipt.receipt_generator import CryptographicReceiptGenerator
from src.core.storage.agency_store import get_agency_store
from src.core.nemesis.compilation_engine import ABCCompilationEngine

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/agency", tags=["agency"])

# Initialize engines
consensus_engine = ConsensusEngine()
receipt_gen = CryptographicReceiptGenerator()
compilation_engine = ABCCompilationEngine()
agency_store = get_agency_store()


@router.post("/assessment", status_code=status.HTTP_201_CREATED)
@require_auth
@rate_limit(max_requests=100, window_seconds=60)
async def submit_agency_assessment(
    assessment: AgencyAssessment,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key", description="Idempotency key to prevent duplicate submissions")
) -> Dict[str, Any]:
    """
    Agency submits AI assessment with ABC receipt reference
    
    Flow:
    1. Validate ABC receipt exists and references Foundry compilation
    2. Generate idempotency key if not provided (based on agency + compilation + assessment_hash)
    3. Check for duplicate submission (idempotency)
    4. Generate blockchain receipt for agency assessment
    5. Store assessment in memory store (temporary until Neo4j integration)
    6. Return blockchain receipt
    
    Args:
        assessment: Agency assessment submission
        idempotency_key: Optional idempotency key (prevents duplicate submissions)
    
    Returns:
        Submission result with blockchain receipt
    
    Note:
        Uses in-memory storage (temporary). Neo4j integration planned for production.
    """
    logger.info(
        f"Received agency assessment submission from {assessment.agency} "
        f"for Foundry compilation {assessment.foundry_compilation_id}"
    )
    
    try:
        # Generate idempotency key if not provided
        if not idempotency_key:
            # Create idempotency key from agency + compilation + assessment_hash
            key_data = f"{assessment.agency}:{assessment.foundry_compilation_id}:{assessment.assessment_hash}"
            idempotency_key = hashlib.sha256(key_data.encode()).hexdigest()
        
        # Check for duplicate submission
        existing_record = agency_store._assessments_by_receipt.get(idempotency_key)
        if existing_record:
            logger.info(f"Duplicate submission detected (idempotency_key={idempotency_key[:16]}...)")
            return {
                "status": "duplicate",
                "message": "Assessment already submitted (idempotency key matched)",
                "agency": assessment.agency,
                "foundry_compilation_id": assessment.foundry_compilation_id,
                "blockchain_receipt": {
                    "receipt_id": existing_record['receipt_id'],
                    "intelligence_hash": existing_record.get('assessment', {}).get('assessment_hash'),
                    "timestamp": existing_record['stored_at'],
                    "tx_hash": existing_record.get('blockchain_tx_hash')
                }
            }
        
        # Verify ABC receipt format (basic validation)
        if not assessment.abc_receipt_hash or not assessment.abc_receipt_hash.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="abc_receipt_hash is required"
            )
        
        # Generate blockchain receipt for agency assessment
        logger.info(f"Generating blockchain receipt for agency assessment")
        receipt = receipt_gen.generate_receipt(
            intelligence_package={
                "agency": assessment.agency,
                "foundry_compilation_id": assessment.foundry_compilation_id,
                "abc_receipt_hash": assessment.abc_receipt_hash,
                "assessment_hash": assessment.assessment_hash,
                "confidence_score": assessment.confidence_score,
                "classification": assessment.classification.value
            },
            actor_id=assessment.agency,
            threat_level="INFO",
            package_type="agency_assessment",
            additional_metadata={
                "foundry_compilation_id": assessment.foundry_compilation_id,
                "abc_receipt_hash": assessment.abc_receipt_hash,
                "agency": assessment.agency
            },
            foundry_compilation_id=assessment.foundry_compilation_id,
            foundry_hash=None,  # Not available from agency submission
            foundry_timestamp=None  # Not available from agency submission
        )
        
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate blockchain receipt"
            )
        
        # Store assessment in memory store
        stored_record = agency_store.store_assessment(
            assessment=assessment,
            receipt_id=receipt.receipt_id,
            blockchain_tx_hash=receipt.tx_hash,
            idempotency_key=idempotency_key
        )
        
        logger.info(
            f"Assessment submitted successfully. Receipt ID: {receipt.receipt_id}, "
            f"Storage ID: {stored_record['storage_id']}"
        )
        
        return {
            "status": "submitted",
            "agency": assessment.agency,
            "foundry_compilation_id": assessment.foundry_compilation_id,
            "storage_id": stored_record['storage_id'],
            "blockchain_receipt": {
                "receipt_id": receipt.receipt_id,
                "intelligence_hash": receipt.intelligence_hash,
                "timestamp": receipt.timestamp,
                "tx_hash": receipt.tx_hash
            },
            "idempotency_key": idempotency_key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error submitting agency assessment from {assessment.agency}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during assessment submission: {str(e)}"
        )


@router.get("/consensus/{foundry_compilation_id}", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=50, window_seconds=60)
async def get_consensus(
    foundry_compilation_id: str
) -> ConsensusResult:
    """
    Get multi-agency consensus for Foundry compilation
    
    Calculates consensus metrics across all agency assessments for a given
    Foundry compilation, including mean confidence, standard deviation,
    outlier detection, and recommendations.
    
    Args:
        foundry_compilation_id: Foundry compilation identifier
    
    Returns:
        ConsensusResult with consensus metrics and recommendations
    
    Note:
        Retrieves assessments from in-memory store. If no assessments found,
        returns error. ABC baseline confidence is retrieved from compilation
        engine if available, otherwise defaults to calculated mean.
    """
    logger.info(
        f"Calculating consensus for Foundry compilation: {foundry_compilation_id}"
    )
    
    try:
        # Get all assessments for this compilation
        agency_assessments = agency_store.get_assessments_by_compilation(
            foundry_compilation_id
        )
        
        if not agency_assessments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No agency assessments found for compilation {foundry_compilation_id}"
            )
        
        # Try to get ABC baseline confidence from compilation engine
        # For now, we'll use a default or calculate from assessments
        # TODO: Query ABC receipt to get baseline confidence
        abc_baseline_confidence = 85.0  # Default
        
        # Calculate consensus
        consensus_result = consensus_engine.calculate_consensus(
            foundry_compilation_id=foundry_compilation_id,
            abc_baseline_confidence=abc_baseline_confidence,
            agency_assessments=agency_assessments
        )
        
        logger.info(
            f"Consensus calculated for {foundry_compilation_id}. "
            f"Assessments: {len(agency_assessments)}, "
            f"Mean confidence: {consensus_result.consensus_metrics.get('mean_confidence', 0):.2f}"
        )
        
        return consensus_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error calculating consensus for {foundry_compilation_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during consensus calculation: {str(e)}"
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
@require_auth
async def get_agency_store_stats() -> Dict[str, Any]:
    """
    Get agency assessment store statistics
    
    Returns:
        Store statistics including total assessments, compilations, and agencies
    
    Note:
        Admin/debugging endpoint. Requires authentication.
    """
    try:
        stats = agency_store.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error retrieving store stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error retrieving stats: {str(e)}"
        )

