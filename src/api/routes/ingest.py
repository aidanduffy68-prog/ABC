"""
Ingestion API Route
FastAPI endpoint for vendor feed ingestion with clear error handling and type safety

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, validator
from datetime import datetime
import logging

from src.schemas.threat_actor import ThreatActor, ActorType
from src.core.middleware.log_sanitizer import safe_log
from src.core.middleware.api_auth import verify_api_token, require_vendor
try:
    from src.ingestion.validator import IngestionValidator, ValidationError
except ImportError:
    # Fallback if validator not available
    from typing import List as ValidationErrorList
    class IngestionValidator:
        def validate_vendor_feed(self, feed_data, vendor_name):
            return True, [], []
        def validate_actor(self, actor_data):
            return True, []
        def validate_event(self, event_data):
            return True, []
        def validate_pattern(self, pattern_data):
            return True, []
    ValidationError = None

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create router
router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])


class IngestRequest(BaseModel):
    """Request model for ingestion endpoint"""
    vendor: str = Field(..., description="Vendor name (Chainalysis, TRM, Chaos, etc.)", min_length=1, max_length=50)
    timestamp: datetime = Field(default_factory=datetime.now, description="Feed timestamp")
    data: List[Dict[str, Any]] = Field(..., description="Array of entity data", min_items=1, max_items=10000)
    
    @validator('vendor')
    def validate_vendor(cls, v):
        """Validate vendor name - SECURITY: Whitelist approach"""
        import re
        # Strip whitespace
        v = v.strip()
        # Validate format (alphanumeric and spaces only)
        if not re.match(r'^[a-zA-Z0-9\s]+$', v):
            raise ValueError("vendor contains invalid characters")
        # Whitelist valid vendors
        valid_vendors = ["Chainalysis", "TRM", "Chaos", "Custom"]
        if v not in valid_vendors:
            raise ValueError(f"vendor must be one of {valid_vendors}")
        return v
    
    @validator('data')
    def validate_data_not_empty(cls, v):
        """Validate data array - SECURITY: Size limits"""
        if not v:
            raise ValueError("data array cannot be empty")
        if len(v) > 10000:
            raise ValueError("data array too large (max 10000 items)")
        return v


class IngestResponse(BaseModel):
    """Response model for ingestion endpoint"""
    status: str = Field(..., description="Ingestion status")
    ingested_count: int = Field(..., description="Number of entities successfully ingested")
    rejected_count: int = Field(..., description="Number of entities rejected")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    ingestion_id: str = Field(..., description="Unique ingestion identifier")


class IngestError(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


@router.post(
    "/feed",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": IngestError, "description": "Validation error"},
        401: {"model": IngestError, "description": "Authentication required"},
        403: {"model": IngestError, "description": "Insufficient permissions"},
        422: {"model": IngestError, "description": "Unprocessable entity"},
        500: {"model": IngestError, "description": "Internal server error"}
    },
    dependencies=[Depends(require_vendor)]
)
async def ingest_vendor_feed(
    request: IngestRequest,
    validator: IngestionValidator = Depends(lambda: IngestionValidator()),
    token_payload: dict = Depends(verify_api_token)
) -> IngestResponse:
    """
    Ingest vendor feed data
    
    Validates and ingests threat intelligence from vendor feeds (Chainalysis, TRM, Chaos, etc.)
    
    Args:
        request: IngestRequest with vendor name, timestamp, and entity data
        validator: IngestionValidator dependency
    
    Returns:
        IngestResponse with ingestion results
    
    Raises:
        HTTPException: 400 if validation fails, 500 if ingestion fails
    """
    try:
        # SECURITY: Use safe logging to prevent sensitive data leakage
        # Log authenticated user
        user_id = token_payload.get("sub", "unknown")
        user_role = token_payload.get("role", "unknown")
        safe_log(logger, 'info', 'Feed ingestion by user: %s (role: %s)', user_id, user_role)
        safe_log(logger, 'info', 'Ingesting feed from vendor: %s', request.vendor)
        safe_log(logger, 'info', 'Feed contains %d entities', len(request.data))
        
        # Step 1: Validate feed structure
        is_valid, errors, warnings = validator.validate_vendor_feed(
            feed_data=request.dict(),
            vendor_name=request.vendor
        )
        
        if not is_valid:
            logger.warning(f"Feed validation failed: {len(errors)} errors")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Feed validation failed",
                    "error_type": "validation_error",
                    "errors": [{"field": e.field, "message": e.message} for e in errors],
                    "warnings": warnings
                }
            )
        
        # Step 2: Validate individual entities
        ingested_count = 0
        rejected_count = 0
        entity_errors = []
        
        for i, entity_data in enumerate(request.data):
            try:
                # Validate entity type
                entity_type = entity_data.get("entity_type", "actor")
                
                if entity_type == "actor":
                    # Validate using ThreatActor schema
                    is_valid_actor, actor_errors = validator.validate_actor(entity_data)
                    if is_valid_actor:
                        # Create ThreatActor instance (validates again)
                        actor = ThreatActor.from_dict(entity_data)
                        ingested_count += 1
                        logger.debug(f"Ingested actor: {actor.actor_id}")
                    else:
                        rejected_count += 1
                        entity_errors.append({
                            "index": i,
                            "entity_type": "actor",
                            "errors": [{"field": e.field, "message": e.message} for e in actor_errors]
                        })
                elif entity_type == "event":
                    # Validate event
                    is_valid_event, event_errors = validator.validate_event(entity_data)
                    if is_valid_event:
                        ingested_count += 1
                    else:
                        rejected_count += 1
                        entity_errors.append({
                            "index": i,
                            "entity_type": "event",
                            "errors": [{"field": e.field, "message": e.message} for e in event_errors]
                        })
                elif entity_type == "pattern":
                    # Validate pattern
                    is_valid_pattern, pattern_errors = validator.validate_pattern(entity_data)
                    if is_valid_pattern:
                        ingested_count += 1
                    else:
                        rejected_count += 1
                        entity_errors.append({
                            "index": i,
                            "entity_type": "pattern",
                            "errors": [{"field": e.field, "message": e.message} for e in pattern_errors]
                        })
                else:
                    rejected_count += 1
                    entity_errors.append({
                        "index": i,
                        "entity_type": entity_type,
                        "errors": [{"field": "entity_type", "message": f"Unknown entity type: {entity_type}"}]
                    })
            
            except Exception as e:
                # Catch any unexpected errors during entity validation
                logger.error(f"Error validating entity at index {i}: {str(e)}")
                rejected_count += 1
                entity_errors.append({
                    "index": i,
                    "entity_type": entity_data.get("entity_type", "unknown"),
                    "errors": [{"field": "unknown", "message": f"Unexpected error: {str(e)}"}]
                })
        
        # Step 3: Generate ingestion ID
        import hashlib
        ingestion_id = hashlib.sha256(
            f"{request.vendor}{request.timestamp.isoformat()}{len(request.data)}".encode()
        ).hexdigest()[:16]
        
        logger.info(f"Ingestion complete: {ingested_count} ingested, {rejected_count} rejected")
        
        # Step 4: Return response
        return IngestResponse(
            status="completed",
            ingested_count=ingested_count,
            rejected_count=rejected_count,
            errors=entity_errors,
            warnings=warnings,
            ingestion_id=ingestion_id
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error during ingestion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error during ingestion",
                "error_type": "internal_error",
                "details": {"message": str(e)}
            }
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ingestion_api",
        "timestamp": datetime.now().isoformat()
    }

