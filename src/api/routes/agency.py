"""
Agency Assessment API Endpoints
Endpoints for agency AI assessment submissions and consensus calculations

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
import logging

from src.schemas.agency import AgencyAssessment, ConsensusResult
from src.consensus.engine import ConsensusEngine
from src.core.middleware.auth import require_auth
from src.core.middleware.rate_limit import rate_limit
from src.core.nemesis.on_chain_receipt.receipt_generator import CryptographicReceiptGenerator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/agency", tags=["agency"])

# Initialize engines
consensus_engine = ConsensusEngine()
receipt_gen = CryptographicReceiptGenerator()


@router.post("/assessment", status_code=status.HTTP_201_CREATED)
@require_auth
@rate_limit(max_requests=100, window_seconds=60)
async def submit_agency_assessment(
    assessment: AgencyAssessment
) -> Dict[str, Any]:
    """
    Agency submits AI assessment with ABC receipt reference
    
    Flow:
    1. Validate ABC receipt exists (check receipt_gen)
    2. Verify ABC receipt references same Foundry compilation
    3. Generate blockchain receipt for agency assessment
    4. Store in database (TODO: Neo4j integration)
    5. Return blockchain receipt
    
    Args:
        assessment: Agency assessment submission
    
    Returns:
        Submission result with blockchain receipt
    """
    logger.info(
        f"Received agency assessment submission from {assessment.agency} "
        f"for Foundry compilation {assessment.foundry_compilation_id}"
    )
    
    try:
        # Verify ABC receipt exists
        # TODO: Add receipt verification logic
        # For now, we'll proceed with receipt generation
        
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
            }
        )
        
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate blockchain receipt"
            )
        
        # TODO: Store assessment in database (Neo4j integration)
        logger.info(
            f"Assessment submitted successfully. Receipt ID: {receipt.receipt_id}"
        )
        
        return {
            "status": "submitted",
            "agency": assessment.agency,
            "foundry_compilation_id": assessment.foundry_compilation_id,
            "blockchain_receipt": {
                "receipt_id": receipt.receipt_id,
                "intelligence_hash": receipt.intelligence_hash,
                "timestamp": receipt.timestamp,
                "tx_hash": receipt.tx_hash
            }
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
    
    TODO: Query all assessments from database
    For now, returns mock data for demonstration
    """
    logger.info(
        f"Calculating consensus for Foundry compilation: {foundry_compilation_id}"
    )
    
    try:
        # TODO: Query all assessments from database
        # For now, return mock data for demo
        mock_assessments = [
            AgencyAssessment(
                agency="CIA",
                foundry_compilation_id=foundry_compilation_id,
                abc_receipt_hash="sha256:abc123",
                assessment_hash="sha256:cia456",
                confidence_score=85.2,
                classification="SECRET"
            ),
            AgencyAssessment(
                agency="DHS",
                foundry_compilation_id=foundry_compilation_id,
                abc_receipt_hash="sha256:abc123",
                assessment_hash="sha256:dhs789",
                confidence_score=60.1,
                classification="SBU"
            )
        ]
        
        # Calculate consensus
        consensus_result = consensus_engine.calculate_consensus(
            foundry_compilation_id=foundry_compilation_id,
            abc_baseline_confidence=88.4,
            agency_assessments=mock_assessments
        )
        
        logger.info(
            f"Consensus calculated for {foundry_compilation_id}. "
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

