# -*- coding: utf-8 -*-
"""
ABC Verification API Service
REST API for verifying ABC receipt hashes from Foundry pipeline

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import hashlib
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ABC Verification API",
    description="API for verifying ABC receipt hashes from Foundry pipeline",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to initialize Foundry client (optional - for future use)
foundry_client = None
try:
    from abc_integration_sdk import FoundryClient, ConfidentialClientAuth
    
    auth = ConfidentialClientAuth(
        client_id=os.getenv("FOUNDRY_CLIENT_ID"),
        client_secret=os.getenv("FOUNDRY_CLIENT_SECRET"),
        hostname=os.getenv("FOUNDRY_URL"),
        should_refresh=True
    )
    
    foundry_client = FoundryClient(auth=auth, hostname=os.getenv("FOUNDRY_URL"))
    print("✅ Foundry client initialized")
except Exception as e:
    print(f"⚠️  Foundry client not available: {e}")
    print("   API will work without Foundry integration")


# Request/Response Models
class BlockData(BaseModel):
    """Blockchain block data"""
    block_height: int = Field(..., description="Bitcoin block height")
    block_hash: str = Field(..., description="Block hash")
    timestamp: int = Field(..., description="Block timestamp (Unix)")
    tx_count: int = Field(..., description="Number of transactions")
    transactions: str = Field(..., description="JSON string of transactions")


class VerificationRequest(BaseModel):
    """Request to verify ABC receipt hash"""
    block_data: BlockData = Field(..., description="Block data to verify")
    abc_receipt_hash: str = Field(..., description="ABC receipt hash from Foundry")


class VerificationResult(BaseModel):
    """Verification result"""
    verified: bool = Field(..., description="Whether hash matches")
    block_height: int = Field(..., description="Block height")
    foundry_hash: str = Field(..., description="Hash from Foundry")
    computed_hash: str = Field(..., description="Hash computed by ABC")
    timestamp: str = Field(..., description="Verification timestamp")


class VerificationResponse(BaseModel):
    """API response for verification"""
    success: bool = Field(..., description="Request success")
    result: VerificationResult = Field(..., description="Verification result")
    message: str = Field(..., description="Status message")


class BatchVerificationRequest(BaseModel):
    """Batch verification request"""
    requests: List[VerificationRequest] = Field(..., description="List of verification requests")


class BatchVerificationResult(BaseModel):
    """Batch verification result"""
    total: int = Field(..., description="Total records")
    verified: int = Field(..., description="Number verified")
    failed: int = Field(..., description="Number failed")
    results: List[Dict[str, Any]] = Field(..., description="Individual results")


# Helper Functions
def generate_abc_hash(block_data: Dict[str, Any]) -> str:
    """
    Generate ABC hash using same method as Foundry transform.
    
    This matches your Foundry function exactly:
    - json.dumps with sort_keys=True, separators=(',', ':')
    - SHA-256 hash
    
    Args:
        block_data: Block data dictionary
        
    Returns:
        SHA-256 hash as hex string
    """
    normalized = json.dumps(block_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def verify_single(block_data: BlockData, abc_receipt_hash: str) -> VerificationResult:
    """
    Verify a single ABC receipt hash.
    
    Args:
        block_data: Block data
        abc_receipt_hash: Hash from Foundry
        
    Returns:
        Verification result
    """
    # Reconstruct block data dict
    block_data_dict = {
        "block_height": block_data.block_height,
        "block_hash": block_data.block_hash,
        "timestamp": block_data.timestamp,
        "tx_count": block_data.tx_count,
        "transactions": block_data.transactions
    }
    
    # Generate hash
    computed_hash = generate_abc_hash(block_data_dict)
    
    # Compare
    verified = computed_hash == abc_receipt_hash
    
    return VerificationResult(
        verified=verified,
        block_height=block_data.block_height,
        foundry_hash=abc_receipt_hash,
        computed_hash=computed_hash,
        timestamp=datetime.now().isoformat()
    )


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ABC Verification API",
        "version": "1.0.0",
        "status": "operational",
        "foundry_connected": foundry_client is not None,
        "endpoints": {
            "verify": "/verify",
            "verify_batch": "/verify/batch",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.post("/verify", response_model=VerificationResponse)
async def verify_abc_receipt(request: VerificationRequest):
    """
    Verify ABC receipt hash matches recomputed hash.
    
    This endpoint verifies that a Foundry-generated ABC receipt hash
    matches what ABC would generate for the same data.
    
    **Example Request:**
    ```json
    {
        "block_data": {
            "block_height": 825000,
            "block_hash": "94f84c7be087799b54c3e4adce1f9012a7e3c8d4b6f5a2e1c9d8b7a6f5e4d3c2",
            "timestamp": 1735689600,
            "tx_count": 2453,
            "transactions": "[{\"txid\":\"abc123\",\"value\":0.5}]"
        },
        "abc_receipt_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b"
    }
    ```
    """
    try:
        result = verify_single(request.block_data, request.abc_receipt_hash)
        
        return VerificationResponse(
            success=True,
            result=result,
            message="Verification complete" if result.verified else "Hash mismatch detected"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.post("/verify/batch", response_model=BatchVerificationResult)
async def verify_batch(request: BatchVerificationRequest):
    """
    Verify multiple ABC receipts in batch.
    
    Processes multiple verification requests in a single call.
    Useful for verifying entire datasets.
    
    **Example Request:**
    ```json
    {
        "requests": [
            {
                "block_data": {...},
                "abc_receipt_hash": "..."
            },
            {
                "block_data": {...},
                "abc_receipt_hash": "..."
            }
        ]
    }
    ```
    """
    results = []
    
    for req in request.requests:
        try:
            result = verify_single(req.block_data, req.abc_receipt_hash)
            
            results.append({
                "block_height": result.block_height,
                "verified": result.verified,
                "foundry_hash": result.foundry_hash,
                "computed_hash": result.computed_hash,
                "timestamp": result.timestamp
            })
        except Exception as e:
            results.append({
                "block_height": req.block_data.block_height,
                "verified": False,
                "error": str(e)
            })
    
    verified_count = sum(1 for r in results if r.get("verified", False))
    
    return BatchVerificationResult(
        total=len(results),
        verified=verified_count,
        failed=len(results) - verified_count,
        results=results
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and Foundry connection status.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "foundry_connected": foundry_client is not None
    }
    
    if foundry_client:
        try:
            # Could add a simple Foundry API call here to test connection
            health_status["foundry_status"] = "connected"
        except Exception as e:
            health_status["foundry_status"] = "error"
            health_status["foundry_error"] = str(e)
    
    return health_status


@app.get("/stats")
async def get_stats():
    """
    Get API statistics (placeholder for future use).
    """
    return {
        "service": "ABC Verification API",
        "version": "1.0.0",
        "uptime": "N/A",
        "total_verifications": "N/A",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print("=" * 80)
    print("ABC Verification API Service")
    print("=" * 80)
    print(f"Starting server on http://{host}:{port}")
    print(f"API docs available at http://{host}:{port}/docs")
    print("=" * 80)
    
    uvicorn.run(app, host=host, port=port, reload=True)

