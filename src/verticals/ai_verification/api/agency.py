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

from src.verticals.ai_verification.schemas.agency import AgencyAssessment, ConsensusResult
from src.verticals.ai_verification.consensus.engine import ConsensusEngine
from src.shared.middleware.auth import require_auth
from src.shared.middleware.rate_limit import rate_limit
from src.verticals.ai_verification.core.nemesis.on_chain_receipt.receipt_generator import CryptographicReceiptGenerator
from src.verticals.ai_verification.storage.agency_store import get_agency_store
from src.verticals.ai_verification.core.nemesis.compilation_engine import ABCCompilationEngine
from src.shared.integrations.foundry.connector import FoundryDataExportConnector
from src.verticals.ai_verification.core.nemesis.foundry_integration.data_mapper import FoundryDataMapper

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/agency", tags=["agency"])

# Initialize engines
consensus_engine = ConsensusEngine()
receipt_gen = CryptographicReceiptGenerator()
compilation_engine = ABCCompilationEngine()
agency_store = get_agency_store()
foundry_connector = FoundryDataExportConnector()
data_mapper = FoundryDataMapper()


@router.post("/assessment", status_code=status.HTTP_201_CREATED)
@require_auth
@rate_limit(max_requests=100, window_seconds=60)
async def submit_agency_assessment(
    assessment: AgencyAssessment,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key", description="Idempotency key to prevent duplicate submissions")
) -> Dict[str, Any]:
    """
    Agency submits AI assessment with ABC receipt reference.
    
    **ABC verifies inputs, not outputs. This endpoint proves the agency's AI analyzed
    the same data that ABC verified, enabling humans to trust the inputs and focus
    on evaluating the analysis methodology.**
    
    Flow:
    1. Validate ABC receipt exists and references Foundry compilation
    2. Generate idempotency key if not provided (based on agency + compilation + assessment_hash)
    3. Check for duplicate submission (idempotency)
    4. Generate blockchain receipt for agency assessment
    5. Store assessment in memory store (temporary until Neo4j integration)
    6. Return blockchain receipt
    
    **Note:** ABC provides cryptographic proof that all agencies analyzed identical source data.
    The disagreement is methodology, not data quality. Human analysts make the final decision.
    
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
        
        # Validate ABC receipt hash format
        abc_receipt_hash_clean = assessment.abc_receipt_hash.strip() if assessment.abc_receipt_hash else ""
        if not abc_receipt_hash_clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="abc_receipt_hash is required"
            )
        
        # Remove "sha256:" prefix if present for validation
        abc_hash_value = abc_receipt_hash_clean
        if abc_receipt_hash_clean.startswith("sha256:"):
            abc_hash_value = abc_receipt_hash_clean[7:]
        
        # Validate hex format (SHA256 should be 64 hex characters)
        if len(abc_hash_value) != 64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid abc_receipt_hash format. Expected SHA256 hash (64 hex characters), got {len(abc_hash_value)} characters"
            )
        
        # Validate hex characters only
        try:
            int(abc_hash_value, 16)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid abc_receipt_hash format. Must be hexadecimal (0-9, a-f, A-F)"
            )
        
        # Generate blockchain receipt for agency assessment
        logger.info(f"Generating blockchain receipt for agency assessment")
        receipt = receipt_gen.generate_receipt(
            intelligence_package={
                "agency": assessment.agency,
                "foundry_compilation_id": assessment.foundry_compilation_id,
                "abc_receipt_hash": abc_receipt_hash_clean,  # Use validated hash
                "assessment_hash": assessment.assessment_hash,
                "confidence_score": assessment.confidence_score,
                "classification": assessment.classification.value
            },
            actor_id=assessment.agency,
            threat_level="INFO",
            package_type="agency_assessment",
            additional_metadata={
                "foundry_compilation_id": assessment.foundry_compilation_id,
                "abc_receipt_hash": abc_receipt_hash_clean,  # Use validated hash
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
    
    Raises:
        HTTPException: 400 if foundry_compilation_id is invalid
        HTTPException: 404 if no assessments found
        HTTPException: 500 for internal errors
    
    Note:
        Retrieves assessments from in-memory store. If no assessments found,
        returns error. ABC baseline confidence is retrieved from compilation
        engine if available, otherwise defaults to calculated mean.
    """
    # Validate foundry_compilation_id
    foundry_compilation_id_clean = foundry_compilation_id.strip() if foundry_compilation_id else ""
    if not foundry_compilation_id_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="foundry_compilation_id cannot be empty"
        )
    
    logger.info(
        f"Calculating consensus for Foundry compilation: {foundry_compilation_id_clean}"
    )
    
    try:
        # Get all assessments for this compilation
        agency_assessments = agency_store.get_assessments_by_compilation(
            foundry_compilation_id_clean
        )
        
        if not agency_assessments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No agency assessments found for compilation {foundry_compilation_id_clean}"
            )
        
        # Get ABC baseline confidence from stored data or calculate smart default
        abc_baseline_confidence = None
        
        # Strategy 1: Check if baseline stored in assessment metadata
        for assessment in agency_assessments:
            if assessment.metadata and "abc_baseline_confidence" in assessment.metadata:
                abc_baseline_confidence = float(assessment.metadata["abc_baseline_confidence"])
                logger.debug(f"Found ABC baseline in assessment metadata: {abc_baseline_confidence:.2f}")
                break
        
        # Strategy 2: Query Foundry compilation to get real ABC baseline (if available)
        if abc_baseline_confidence is None:
            try:
                foundry_compilation = foundry_connector.get_compilation(foundry_compilation_id_clean)
                if foundry_compilation and foundry_connector.enabled:
                    logger.debug(f"Querying Foundry compilation for ABC baseline")
                    # Map Foundry data to ABC format
                    abc_data = data_mapper.map_to_abc_format(foundry_compilation)
                    
                    # Extract actor info
                    compiled_data = foundry_compilation.get("compiled_data", {})
                    threat_actors = compiled_data.get("threat_actors", [])
                    if threat_actors:
                        actor_id = threat_actors[0].get("id", foundry_compilation_id_clean)
                        actor_name = threat_actors[0].get("name", f"Foundry {foundry_compilation_id_clean}")
                    else:
                        actor_id = f"foundry_{foundry_compilation_id_clean}"
                        actor_name = f"Foundry Compilation {foundry_compilation_id_clean}"
                    
                    # Run ABC compilation to get baseline confidence
                    compiled_intelligence = compilation_engine.compile_intelligence(
                        actor_id=actor_id,
                        actor_name=actor_name,
                        raw_intelligence=abc_data.get("raw_intelligence", []),
                        transaction_data=abc_data.get("transaction_data"),
                        network_data=abc_data.get("network_data"),
                        generate_receipt=False,
                        classification=foundry_compilation.get("classification")
                    )
                    
                    abc_baseline_confidence = compiled_intelligence.confidence_score * 100
                    logger.info(
                        f"Retrieved ABC baseline from Foundry compilation: {abc_baseline_confidence:.2f}%"
                    )
            except Exception as e:
                logger.debug(f"Could not query ABC baseline from Foundry: {e}")
        
        # Strategy 3: Calculate smart default from assessment scores (median is more robust)
        if abc_baseline_confidence is None:
            import statistics
            confidence_scores = [a.confidence_score for a in agency_assessments]
            if len(confidence_scores) > 0:
                # Use median as baseline estimate (less affected by outliers than mean)
                abc_baseline_confidence = statistics.median(confidence_scores)
                logger.info(
                    f"Calculated ABC baseline from assessment median: {abc_baseline_confidence:.2f}% "
                    f"(fallback - real baseline not available)"
                )
            else:
                # Final fallback
                abc_baseline_confidence = 85.0
                logger.warning("Using default ABC baseline (85.0%) - no assessments or compilation data available")
        
        # Calculate consensus
        consensus_result = consensus_engine.calculate_consensus(
            foundry_compilation_id=foundry_compilation_id_clean,
            abc_baseline_confidence=abc_baseline_confidence,
            agency_assessments=agency_assessments
        )
        
        logger.info(
            f"Consensus calculated for {foundry_compilation_id_clean}. "
            f"Assessments: {len(agency_assessments)}, "
            f"Mean confidence: {consensus_result.consensus_metrics.get('mean_confidence', 0):.2f}"
        )
        
        return consensus_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error calculating consensus for {foundry_compilation_id_clean}: {e}",
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

