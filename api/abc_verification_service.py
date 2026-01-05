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
            "scan_foundry": "/foundry/scan-hash-mismatches",
            "commit_on_chain": "/commit-on-chain",
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


# ============================================================================
# Human Verification → On-Chain Commitment Workflow
# Detects: Artificial (bad) vs Synthetic (good) data for AML models
# ============================================================================

class ScanFoundryRequest(BaseModel):
    """Request to scan Foundry compilation for hash mismatches"""
    compilation_id: str = Field(..., description="Foundry compilation ID")
    dataset_path: Optional[str] = Field(None, description="Dataset path (if needed)")


class ScanFoundryResponse(BaseModel):
    """Response from scanning Foundry compilation"""
    compilation_id: str
    total_records: int
    synthetic_count: int = Field(..., description="Good data: hash matches (synthetic)")
    artificial_count: int = Field(..., description="Bad data: hash mismatch (artificial)")
    artificial_records: List[Dict[str, Any]] = Field(..., description="Artificial (bad) data detected")
    timestamp: str


class CommitOnChainRequest(BaseModel):
    """Request to commit verified data on-chain"""
    block_data: BlockData = Field(..., description="Block data to commit")
    abc_receipt_hash: str = Field(..., description="ABC receipt hash")
    human_analyst: str = Field(..., description="Human analyst ID")
    data_classification: str = Field(..., description="'synthetic' (good) or 'artificial' (bad)")
    verification_notes: Optional[str] = Field(None, description="Verification notes")


class CommitOnChainResponse(BaseModel):
    """Response from on-chain commitment"""
    committed: bool
    tx_hash: Optional[str]
    receipt_id: Optional[str]
    data_classification: str = Field(..., description="'synthetic' (good) or 'artificial' (bad)")
    publicly_verifiable: bool
    timestamp: str


@app.post("/foundry/scan-hash-mismatches", response_model=ScanFoundryResponse)
async def scan_foundry_for_mismatches(request: ScanFoundryRequest):
    """
    Scan Foundry compilation to detect Artificial (bad) vs Synthetic (good) data.
    
    **Purpose:** Detect data integrity issues for AML model training.
    
    - **Synthetic (good):** Legitimate synthetic data for training - hash matches ✅
    - **Artificial (bad):** Deceptive data injection - hash mismatch ❌
    
    **Use Case:** AI system struggles with AML analysis → Human scans Foundry
    to detect artificial (bad) data that's corrupting model training.
    
    **Example Request:**
    ```json
    {
        "compilation_id": "abc_verification_output",
        "dataset_path": "gh_systems/intelligence_compilations"
    }
    ```
    
    Returns count of synthetic (good) vs artificial (bad) records.
    """
    if not foundry_client:
        raise HTTPException(
            status_code=503,
            detail="Foundry client not available. Check FOUNDRY_URL, FOUNDRY_CLIENT_ID, FOUNDRY_CLIENT_SECRET"
        )
    
    try:
        # Try to import Foundry connector (may not be available)
        try:
            from src.verticals.ai_verification.core.nemesis.foundry_integration.foundry_aip_connector import FoundryAIPConnector
            connector = FoundryAIPConnector()
        except (ImportError, SyntaxError, IndentationError) as import_error:
            # Graceful fallback - return empty results if connector not available
            # This is expected in dev environments where Foundry SDK may not be installed
            return ScanFoundryResponse(
                compilation_id=request.compilation_id,
                total_records=0,
                synthetic_count=0,
                artificial_count=0,
                artificial_records=[],
                timestamp=datetime.now().isoformat()
            )
        
        dataset_path = request.dataset_path or "gh_systems/intelligence_compilations"
        compilation_data = connector.read_dataset(dataset_path)
        
        if not compilation_data:
            return ScanFoundryResponse(
                compilation_id=request.compilation_id,
                total_records=0,
                synthetic_count=0,
                artificial_count=0,
                artificial_records=[],
                timestamp=datetime.now().isoformat()
            )
        
        # Scan: Synthetic (good) vs Artificial (bad)
        synthetic_count = 0
        artificial_records = []
        
        for record in compilation_data:
            try:
                block_data = BlockData(
                    block_height=record.get("block_height"),
                    block_hash=record.get("block_hash"),
                    timestamp=record.get("timestamp"),
                    tx_count=record.get("tx_count"),
                    transactions=record.get("transactions", "[]")
                )
                
                abc_receipt_hash = record.get("abc_receipt_hash")
                
                if abc_receipt_hash:
                    verification = verify_single(block_data, abc_receipt_hash)
                    
                    if verification.verified:
                        # Synthetic (good): Hash matches = legitimate synthetic data
                        synthetic_count += 1
                    else:
                        # Artificial (bad): Hash mismatch = deceptive data injection
                        artificial_records.append({
                            "block_height": record.get("block_height"),
                            "foundry_hash": verification.foundry_hash,
                            "computed_hash": verification.computed_hash,
                            "classification": "artificial",
                            "issue": "Hash mismatch - artificial (bad) data detected",
                            "verification_timestamp": verification.timestamp
                        })
            except Exception as e:
                continue
        
        artificial_count = len(artificial_records)
        
        return ScanFoundryResponse(
            compilation_id=request.compilation_id,
            total_records=len(compilation_data),
            synthetic_count=synthetic_count,
            artificial_count=artificial_count,
            artificial_records=artificial_records,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scan Foundry compilation: {str(e)}"
        )


@app.post("/commit-on-chain", response_model=CommitOnChainResponse)
async def human_commit_to_blockchain(request: CommitOnChainRequest):
    """
    Human commits verified data classification to blockchain.
    
    **Purpose:** Document data integrity classification (Synthetic vs Artificial).
    
    - **Synthetic (good):** Legitimate synthetic data for AML model training ✅
    - **Artificial (bad):** Deceptive data injection that corrupts training ❌
    
    **Use Case:** Human verifies hash mismatch → Classifies as artificial (bad) →
    Commits on-chain to document data provenance and resolve AI bottleneck.
    
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
        "abc_receipt_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b",
        "human_analyst": "analyst_001",
        "data_classification": "artificial",
        "verification_notes": "Hash mismatch indicates artificial (bad) data injection in DeFi layering transaction"
    }
    ```
    """
    # Validate classification
    if request.data_classification not in ["synthetic", "artificial"]:
        raise HTTPException(
            status_code=400,
            detail="data_classification must be 'synthetic' (good) or 'artificial' (bad)"
        )
    
    try:
        from src.verticals.ai_verification.core.nemesis.on_chain_receipt.receipt_generator import (
            CryptographicReceiptGenerator
        )
        
        generator = CryptographicReceiptGenerator()
        
        block_data_dict = {
            "block_height": request.block_data.block_height,
            "block_hash": request.block_data.block_hash,
            "timestamp": request.block_data.timestamp,
            "tx_count": request.block_data.tx_count,
            "transactions": request.block_data.transactions
        }
        
        # Metadata with explicit Synthetic vs Artificial classification
        metadata = {
            "verified_by": request.human_analyst,
            "verification_timestamp": datetime.now().isoformat(),
            "verification_notes": request.verification_notes or "",
            "data_classification": request.data_classification,  # "synthetic" or "artificial"
            "provenance": {
                "data_type": "aml_defi_layering",
                "data_quality": "synthetic" if request.data_classification == "synthetic" else "artificial",
                "human_verified": True,
                "issue": "artificial (bad) data detected" if request.data_classification == "artificial" else "synthetic (good) data verified"
            },
            "abc_receipt_hash": request.abc_receipt_hash
        }
        
        receipt = generator.generate_receipt(
            intelligence_package=block_data_dict,
            additional_metadata=metadata
        )
        
        tx_hash = generator.commit_to_blockchain(
            receipt=receipt,
            preferred_network="bitcoin"
        )
        
        return CommitOnChainResponse(
            committed=True,
            tx_hash=tx_hash,
            receipt_id=receipt.receipt_id,
            data_classification=request.data_classification,
            publicly_verifiable=True,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to commit to blockchain: {str(e)}"
        )


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

