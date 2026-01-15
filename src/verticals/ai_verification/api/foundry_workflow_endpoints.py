"""
Foundry Workflow API Endpoints
API endpoints for scenario_forge → ABC → Hades/Echo/Nemesis workflow

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime
import logging

from src.shared.middleware.auth import require_auth
from src.shared.middleware.rate_limit import rate_limit

# Import workflow (if available)
try:
    from src.verticals.ai_verification.core.nemesis.foundry_integration.foundry_workflow import (
        FoundryWorkflow
    )
    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False
    FoundryWorkflow = None

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/foundry/workflow", tags=["foundry-workflow"])


class ProcessDataRequest(BaseModel):
    """Request to process data through workflow"""
    data: Dict[str, Any]
    data_type: str = "auto"  # "foundry", "scenario_forge", or "auto"
    declared_intent: Optional[str] = None
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    generate_receipt: bool = True


class ProcessDataResponse(BaseModel):
    """Response from workflow processing"""
    success: bool
    compilation_id: Optional[str] = None
    receipt_id: Optional[str] = None
    compilation_time_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    details: Dict[str, Any]
    timestamp: str


@router.post("/process", status_code=status.HTTP_200_OK, response_model=ProcessDataResponse)
@require_auth
@rate_limit(max_requests=50, window_seconds=60)
async def process_data_workflow(
    request: ProcessDataRequest
) -> ProcessDataResponse:
    """
    Process data through scenario_forge → ABC Verification → Hades/Echo/Nemesis workflow.
    
    **ABC verifies inputs, not outputs.** This endpoint processes data through:
    1. ABC verification (for scenario_forge: checks labeling, intent, provenance)
    2. Hades/Echo/Nemesis compilation pipeline
    3. Returns compiled intelligence with cryptographic receipt
    
    Supports:
    - Foundry compilations (existing workflow)
    - scenario_forge artificial data (new workflow with ABC verification)
    
    **Example Request (scenario_forge):**
    ```json
    {
        "data": {
            "scenario_id": "uuid-here",
            "intent": "LAUNDERING",
            "metadata": {"artificial_data": true, "ARTIFICIAL_DATA": true},
            "provenance": {...},
            "transaction_graph": {...}
        },
        "data_type": "scenario_forge",
        "declared_intent": "model_evaluation"
    }
    ```
    
    **Example Request (Foundry):**
    ```json
    {
        "data": {
            "compilation_id": "foundry-comp-2025-12-15-001"
        },
        "data_type": "foundry"
    }
    ```
    """
    if not WORKFLOW_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Foundry workflow not available. Ensure ABC compilation engine is installed."
        )
    
    try:
        workflow = FoundryWorkflow()
        
        success, compiled_intelligence, details = workflow.process_data(
            data=request.data,
            data_type=request.data_type,
            declared_intent=request.declared_intent,
            actor_id=request.actor_id,
            actor_name=request.actor_name,
            generate_receipt=request.generate_receipt
        )
        
        if not success:
            return ProcessDataResponse(
                success=False,
                details=details,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
        
        return ProcessDataResponse(
            success=True,
            compilation_id=compiled_intelligence.compilation_id if compiled_intelligence else None,
            receipt_id=details.get("receipt_id") or (compiled_intelligence.receipt.receipt_id if compiled_intelligence and compiled_intelligence.receipt else None),
            compilation_time_ms=compiled_intelligence.compilation_time_ms if compiled_intelligence else None,
            confidence_score=compiled_intelligence.confidence_score if compiled_intelligence else None,
            details=details,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    except Exception as e:
        logger.error(f"Error processing data through workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow processing failed: {str(e)}"
        )


@router.post("/process/foundry", status_code=status.HTTP_200_OK, response_model=ProcessDataResponse)
@require_auth
@rate_limit(max_requests=50, window_seconds=60)
async def process_foundry_compilation(
    compilation_id: str = Query(..., description="Foundry compilation ID"),
    actor_id: Optional[str] = Query(None, description="Optional actor ID"),
    actor_name: Optional[str] = Query(None, description="Optional actor name"),
    generate_receipt: bool = Query(True, description="Generate ABC receipt")
) -> ProcessDataResponse:
    """
    Process Foundry compilation through ABC → Hades/Echo/Nemesis workflow.
    
    Simplified endpoint for Foundry compilations only.
    """
    if not WORKFLOW_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Foundry workflow not available"
        )
    
    try:
        workflow = FoundryWorkflow()
        
        success, compiled_intelligence, details = workflow.process_foundry_compilation(
            compilation_id=compilation_id,
            actor_id=actor_id,
            actor_name=actor_name,
            generate_receipt=generate_receipt
        )
        
        if not success:
            return ProcessDataResponse(
                success=False,
                details=details,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
        
        return ProcessDataResponse(
            success=True,
            compilation_id=compiled_intelligence.compilation_id if compiled_intelligence else None,
            receipt_id=details.get("receipt_id") or (compiled_intelligence.receipt.receipt_id if compiled_intelligence and compiled_intelligence.receipt else None),
            compilation_time_ms=compiled_intelligence.compilation_time_ms if compiled_intelligence else None,
            confidence_score=compiled_intelligence.confidence_score if compiled_intelligence else None,
            details=details,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    except Exception as e:
        logger.error(f"Error processing Foundry compilation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Foundry compilation processing failed: {str(e)}"
        )


@router.post("/process/scenario-forge", status_code=status.HTTP_200_OK, response_model=ProcessDataResponse)
@require_auth
@rate_limit(max_requests=100, window_seconds=60)
async def process_scenario_forge(
    scenario_data: Dict[str, Any],
    declared_intent: str = Query("model_evaluation", description="Declared use case"),
    actor_id: Optional[str] = Query(None, description="Optional actor ID"),
    actor_name: Optional[str] = Query(None, description="Optional actor name"),
    generate_receipt: bool = Query(True, description="Generate ABC receipt")
) -> ProcessDataResponse:
    """
    Process scenario_forge data through ABC Verification → Hades/Echo/Nemesis workflow.
    
    **ABC verifies inputs, not outputs.** This endpoint:
    1. Verifies scenario_forge artificial data with ABC (checks labeling, intent, provenance)
    2. If verified, processes through Hades/Echo/Nemesis pipeline
    3. Returns compiled intelligence with cryptographic receipt
    
    **Example Request:**
    ```json
    {
        "scenario_id": "uuid-here",
        "intent": "LAUNDERING",
        "metadata": {"artificial_data": true, "ARTIFICIAL_DATA": true},
        "provenance": {...},
        "transaction_graph": {...}
    }
    ```
    """
    if not WORKFLOW_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Foundry workflow not available"
        )
    
    try:
        workflow = FoundryWorkflow()
        
        success, compiled_intelligence, details = workflow.process_scenario_forge_data(
            scenario_data=scenario_data,
            declared_intent=declared_intent,
            actor_id=actor_id,
            actor_name=actor_name,
            generate_receipt=generate_receipt
        )
        
        if not success:
            return ProcessDataResponse(
                success=False,
                details=details,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
        
        return ProcessDataResponse(
            success=True,
            compilation_id=compiled_intelligence.compilation_id if compiled_intelligence else None,
            receipt_id=details.get("receipt_id") or (compiled_intelligence.receipt.receipt_id if compiled_intelligence and compiled_intelligence.receipt else None),
            compilation_time_ms=compiled_intelligence.compilation_time_ms if compiled_intelligence else None,
            confidence_score=compiled_intelligence.confidence_score if compiled_intelligence else None,
            details=details,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    except Exception as e:
        logger.error(f"Error processing scenario_forge data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"scenario_forge processing failed: {str(e)}"
        )

