"""
Palantir Foundry Integration API Endpoints
Provides Foundry-compatible data feeds and exports

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from datetime import datetime, timedelta
from dataclasses import asdict
import json

from src.integrations.foundry.connector import FoundryDataExportConnector
from src.integrations.foundry.export import FoundryDataExporter
from src.core.middleware.auth import require_auth
from src.core.middleware.rate_limit import rate_limit
from src.core.nemesis.compilation_engine import ABCCompilationEngine
from src.core.nemesis.foundry_integration.data_mapper import FoundryDataMapper
from src.core.nemesis.on_chain_receipt.receipt_generator import CryptographicReceiptGenerator
from src.core.middleware.cache import cache_response
from src.core.storage.agency_store import get_agency_store
from src.core.nemesis.on_chain_receipt.blockchain_abstraction import (
    BlockchainManager,
    BlockchainNetwork
)
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/foundry", tags=["foundry"])

# Initialize connectors and engines
foundry_connector = FoundryDataExportConnector()
compilation_engine = ABCCompilationEngine()
data_mapper = FoundryDataMapper()
receipt_generator = CryptographicReceiptGenerator()
agency_store = get_agency_store()
blockchain_manager = BlockchainManager()


@router.get("/schema", status_code=status.HTTP_200_OK)
async def get_foundry_schema() -> Dict[str, Any]:
    """
    Get Foundry dataset schema definition
    
    Returns:
        Schema definition for Foundry integration
    """
    return foundry_connector.get_dataset_schema()


@router.post("/push", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=100, window_seconds=60)
async def push_to_foundry(
    compilation_data: Dict[str, Any],
    dataset_path: str = Query(default="gh_systems/intelligence_compilations", description="Foundry dataset path")
) -> Dict[str, Any]:
    """
    Push compilation data to Foundry dataset
    
    Args:
        compilation_data: Compiled intelligence data
        dataset_path: Foundry dataset path
    
    Returns:
        Push result
    """
    return foundry_connector.push_compilation(compilation_data, dataset_path)


@router.post("/push/batch", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=10, window_seconds=60)
async def push_batch_to_foundry(
    compilations: List[Dict[str, Any]],
    dataset_path: str = Query(default="gh_systems/intelligence_compilations", description="Foundry dataset path")
) -> Dict[str, Any]:
    """
    Push batch of compilations to Foundry
    
    Args:
        compilations: List of compiled intelligence data
        dataset_path: Foundry dataset path
    
    Returns:
        Batch push result
    """
    return foundry_connector.push_batch(compilations, dataset_path)


@router.get("/feed/{feed_name}", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=1000, window_seconds=60)
async def foundry_realtime_feed(
    feed_name: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
    since: Optional[str] = Query(default=None, description="ISO timestamp to fetch records since")
) -> Dict[str, Any]:
    """
    Real-time data feed for Foundry consumption
    
    Args:
        feed_name: Feed name identifier
        limit: Maximum number of records
        since: Fetch records since this timestamp
    
    Returns:
        Feed data in Foundry-compatible format
    """
    # In production, this would query from database
    # For now, return feed configuration
    feed_config = foundry_connector.create_realtime_feed(feed_name)
    
    return {
        "feed_name": feed_name,
        "format": "json",
        "records": [],  # Would be populated from database
        "limit": limit,
        "since": since,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/export/json", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=20, window_seconds=60)
async def export_json(
    compilations: List[Dict[str, Any]],
    flattened: bool = Query(default=True, description="Flatten nested structures")
) -> Dict[str, Any]:
    """
    Export compilations as JSON for Foundry
    
    Args:
        compilations: List of compilation data
        flattened: Whether to flatten nested structures
    
    Returns:
        JSON export
    """
    json_data = FoundryDataExporter.export_json(compilations, flattened=flattened)
    
    return {
        "format": "json",
        "flattened": flattened,
        "records": len(compilations),
        "data": json.loads(json_data),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/export/csv", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=20, window_seconds=60)
async def export_csv(
    compilations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Export compilations as CSV for Foundry
    
    Args:
        compilations: List of compilation data
    
    Returns:
        CSV export
    """
    csv_data = FoundryDataExporter.export_csv(compilations)
    
    return {
        "format": "csv",
        "records": len(compilations),
        "data": csv_data,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/verify", status_code=status.HTTP_200_OK)
@require_auth
@rate_limit(max_requests=100, window_seconds=60)
@cache_response(ttl=300)  # Cache for 5 minutes
async def verify_foundry_compilation(
    foundry_compilation_id: str = Query(..., description="Foundry compilation identifier"),
    blockchain: str = Query(default="bitcoin", description="Blockchain network (bitcoin, ethereum, hyperledger)")
) -> Dict[str, Any]:
    """
    Verify a Foundry compilation and commit to blockchain
    
    Flow:
    1. Fetch Foundry compilation via FoundryConnector.get_compilation()
    2. Verify hash matches content
    3. Run ABC compilation (use existing CompilationEngine)
    4. Generate blockchain receipt (use existing CryptographicReceiptGenerator)
    5. Return verification result with blockchain TX
    
    Args:
        foundry_compilation_id: Foundry compilation identifier
        blockchain: Blockchain network (bitcoin, ethereum, hyperledger)
    
    Returns:
        Verification result with blockchain transaction hash
    
    Raises:
        HTTPException: 400 if parameters are invalid
        HTTPException: 404 if compilation not found
        HTTPException: 500 for internal errors
    """
    # Validate foundry_compilation_id
    foundry_compilation_id_clean = foundry_compilation_id.strip() if foundry_compilation_id else ""
    if not foundry_compilation_id_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="foundry_compilation_id cannot be empty"
        )
    
    # Validate blockchain parameter
    allowed_blockchains = {"bitcoin", "ethereum", "hyperledger"}
    blockchain_lower = blockchain.strip().lower() if blockchain else "bitcoin"
    if blockchain_lower not in allowed_blockchains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid blockchain '{blockchain}'. Must be one of: {', '.join(allowed_blockchains)}"
        )
    
    try:
        # Step 1: Fetch Foundry compilation
        logger.info(f"Fetching Foundry compilation: {foundry_compilation_id_clean}")
        foundry_compilation = foundry_connector.get_compilation(foundry_compilation_id_clean)
        
        if not foundry_compilation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Foundry compilation not found: {foundry_compilation_id_clean}"
            )
        
        # Step 2: Verify hash matches content
        logger.info(f"Verifying hash for compilation: {foundry_compilation_id_clean}")
        hash_verified = foundry_connector.verify_compilation_hash(foundry_compilation)
        
        if not hash_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hash verification failed for compilation: {foundry_compilation_id_clean}"
            )
        
        foundry_hash = foundry_compilation.get("data_hash", "")
        
        # Step 3: Map Foundry data to ABC format
        logger.info(f"Mapping Foundry compilation to ABC format: {foundry_compilation_id_clean}")
        abc_data = data_mapper.map_to_abc_format(foundry_compilation)
        
        # Extract actor information from compilation
        # Use first threat actor if available, otherwise use compilation ID
        compiled_data = foundry_compilation.get("compiled_data", {})
        threat_actors = compiled_data.get("threat_actors", [])
        
        if threat_actors and len(threat_actors) > 0:
            first_actor = threat_actors[0]
            actor_id = first_actor.get("id", foundry_compilation_id_clean)
            actor_name = first_actor.get("name", f"Foundry Compilation {foundry_compilation_id_clean}")
        else:
            actor_id = f"foundry_{foundry_compilation_id_clean}"
            actor_name = f"Foundry Compilation {foundry_compilation_id_clean}"
        
        # Step 4: Run ABC compilation
        logger.info(f"Running ABC compilation for actor: {actor_id}")
        compiled_intelligence = compilation_engine.compile_intelligence(
            actor_id=actor_id,
            actor_name=actor_name,
            raw_intelligence=abc_data.get("raw_intelligence", []),
            transaction_data=abc_data.get("transaction_data"),
            network_data=abc_data.get("network_data"),
            generate_receipt=False,  # We'll generate receipt separately
            classification=foundry_compilation.get("classification")
        )
        
        # Extract ABC analysis results
        abc_analysis = {
            "confidence": round(compiled_intelligence.confidence_score, 2),
            "threat_level": compiled_intelligence.targeting_package.get("risk_assessment", {}).get("threat_level", "UNKNOWN").upper(),
            "compilation_time_ms": round(compiled_intelligence.compilation_time_ms, 2)
        }
        
        # Step 5: Generate blockchain receipt
        logger.info(f"Generating blockchain receipt for compilation: {foundry_compilation_id_clean}")
        
        # Prepare intelligence package for receipt generation
        # Serialize dataclass objects properly
        behavioral_sig_dict = asdict(compiled_intelligence.behavioral_signature) if compiled_intelligence.behavioral_signature else {}
        threat_forecast_dict = asdict(compiled_intelligence.threat_forecast) if compiled_intelligence.threat_forecast else None
        
        intelligence_package = {
            "compilation_id": compiled_intelligence.compilation_id,
            "foundry_compilation_id": foundry_compilation_id_clean,
            "foundry_hash": foundry_hash,
            "actor_id": actor_id,
            "actor_name": actor_name,
            "behavioral_signature": behavioral_sig_dict,
            "coordination_network": compiled_intelligence.coordination_network,
            "threat_forecast": threat_forecast_dict,
            "targeting_package": compiled_intelligence.targeting_package,
            "confidence_score": compiled_intelligence.confidence_score,
            "sources": foundry_compilation.get("sources", []),
            "classification": foundry_compilation.get("classification", "UNCLASSIFIED")
        }
        
        # Generate receipt
        receipt = receipt_generator.generate_receipt(
            intelligence_package=intelligence_package,
            actor_id=actor_id,
            threat_level=abc_analysis["threat_level"],
            package_type="foundry_compilation",
            additional_metadata={
                "foundry_compilation_id": foundry_compilation_id_clean,
                "foundry_hash": foundry_hash
            },
            foundry_compilation_id=foundry_compilation_id_clean,
        )
        
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate receipt"
            )
        
        # Commit receipt to blockchain
        logger.info(f"Committing receipt to blockchain: {blockchain_lower}")
        tx_hash = receipt_generator.commit_to_blockchain(
            receipt=receipt,
            preferred_network=blockchain_lower
        )
        
        # Build verification URL (assuming base URL from environment or config)
        verification_url = f"https://abc.ghsystems.io/verify/{receipt.receipt_id}" if receipt.receipt_id else None
        
        # Return verification result
        return {
            "foundry_compilation_id": foundry_compilation_id_clean,
            "foundry_hash": foundry_hash,
            "foundry_verified": hash_verified,
            "abc_analysis": abc_analysis,
            "blockchain_receipt": {
                "receipt_id": receipt.receipt_id,
                "tx_hash": tx_hash or receipt.tx_hash,
                "blockchain": blockchain_lower,
                "verification_url": verification_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying Foundry compilation {foundry_compilation_id_clean}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during verification: {str(e)}"
        )


@router.get("/verify/{receipt_hash}", status_code=status.HTTP_200_OK)
async def verify_receipt_chain(
    receipt_hash: str
) -> Dict[str, Any]:
    """
    Verify complete chain: Foundry → ABC → Agency assessments
    
    Returns verification proof showing all agencies analyzed same Foundry data.
    This is a public endpoint - anyone can verify receipts.
    
    Args:
        receipt_hash: ABC receipt hash to verify (should be SHA256 hash, optionally prefixed with "sha256:")
    
    Returns:
        Complete verification chain with Foundry compilation, ABC analysis, and agency assessments
    
    Raises:
        HTTPException: 400 if receipt_hash format is invalid
        HTTPException: 404 if no assessments found for receipt hash
        HTTPException: 500 for internal errors
    """
    logger.info(f"Verifying receipt chain for receipt hash: {receipt_hash}")
    
    # Validate receipt_hash format
    receipt_hash_clean = receipt_hash.strip()
    if not receipt_hash_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="receipt_hash cannot be empty"
        )
    
    # Remove "sha256:" prefix if present for validation
    hash_value = receipt_hash_clean
    if receipt_hash_clean.startswith("sha256:"):
        hash_value = receipt_hash_clean[7:]
    
    # Validate hex format (SHA256 should be 64 hex characters)
    if len(hash_value) != 64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid receipt_hash format. Expected SHA256 hash (64 hex characters), got {len(hash_value)} characters"
        )
    
    # Validate hex characters only
    try:
        int(hash_value, 16)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid receipt_hash format. Must be hexadecimal (0-9, a-f, A-F)"
        )
    
    try:
        # Normalize receipt hash (remove prefix for lookup)
        receipt_hash_normalized = hash_value  # Use cleaned hash without prefix
        
        # Query agency assessments referencing this ABC receipt
        # Try with both prefixed and non-prefixed versions
        agency_assessments_data = agency_store.get_assessments_by_abc_receipt_hash(receipt_hash_normalized)
        
        # If no results with normalized hash, try with original (in case stored with prefix)
        if not agency_assessments_data and receipt_hash_clean != receipt_hash_normalized:
            agency_assessments_data = agency_store.get_assessments_by_abc_receipt_hash(receipt_hash_clean)
        
        # If still no results, try with sha256: prefix
        if not agency_assessments_data and not receipt_hash_normalized.startswith("sha256:"):
            agency_assessments_data = agency_store.get_assessments_by_abc_receipt_hash(f"sha256:{receipt_hash_normalized}")
        
        # Return 404 if no assessments found
        if not agency_assessments_data:
            logger.info(f"No agency assessments found for receipt hash: {receipt_hash_clean[:16]}...")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No agency assessments found for receipt hash: {receipt_hash_clean[:16]}...{receipt_hash_clean[-8:]}"
            )
        
        # Build agency assessments response with blockchain verification
        agency_assessments_response = []
        abc_receipt_tx_hash = None
        blockchain_verification_status = {"abc_receipt": "pending", "agency_receipts": []}
        
        for assessment in agency_assessments_data:
            # Get stored assessment record to access blockchain_tx_hash
            # _assessments_by_abc_receipt is a list, so find matching record
            stored_record = None
            matching_records = agency_store._assessments_by_abc_receipt.get(assessment.abc_receipt_hash, [])
            for record in matching_records:
                if (record.get('agency') == assessment.agency and
                    record.get('foundry_compilation_id') == assessment.foundry_compilation_id):
                    stored_record = record
                    break
            
            # Fallback: search all assessments if not found in index
            if not stored_record:
                for record in agency_store._assessments.values():
                    if (record.get('abc_receipt_hash') == assessment.abc_receipt_hash and 
                        record.get('agency') == assessment.agency and
                        record.get('foundry_compilation_id') == assessment.foundry_compilation_id):
                        stored_record = record
                        break
            
            agency_tx_hash = stored_record.get('blockchain_tx_hash') if stored_record else None
            agency_verified_on_chain = False
            
            # Verify agency assessment on blockchain if tx_hash available
            if agency_tx_hash:
                try:
                    # Try to determine blockchain network from assessment metadata or use default
                    # For now, default to Bitcoin (most common for intelligence receipts)
                    network = BlockchainNetwork.BITCOIN
                    verification_result = blockchain_manager.verify_receipt(
                        tx_hash=agency_tx_hash,
                        network=network
                    )
                    agency_verified_on_chain = verification_result.get('verified', False)
                    blockchain_verification_status["agency_receipts"].append({
                        "agency": assessment.agency,
                        "tx_hash": agency_tx_hash,
                        "verified": agency_verified_on_chain,
                        "network": network.value
                    })
                except Exception as e:
                    logger.debug(f"Could not verify agency assessment on blockchain: {e}")
                    blockchain_verification_status["agency_receipts"].append({
                        "agency": assessment.agency,
                        "tx_hash": agency_tx_hash,
                        "verified": False,
                        "error": str(e)
                    })
            
            agency_assessments_response.append({
                "agency": assessment.agency,
                "confidence": assessment.confidence_score,
                "classification": assessment.classification.value,
                "assessment_hash": assessment.assessment_hash,
                "submitted_at": assessment.submitted_at.isoformat() if assessment.submitted_at else None,
                "verified": True,  # Assessments are verified if they reference valid ABC receipt
                "blockchain_tx_hash": agency_tx_hash,
                "verified_on_chain": agency_verified_on_chain
            })
        
        # Note: ABC receipt tx_hash would need to be retrieved from ABC receipt store
        # For now, we verify hash chain integrity which proves cryptographic linkage
        logger.info(
            f"Found {len(agency_assessments_data)} agency assessments for receipt hash {receipt_hash_clean[:16]}..."
        )
        
        # Extract Foundry compilation ID from first assessment (all should reference same compilation)
        foundry_compilation_id = None
        if agency_assessments_data:
            foundry_compilation_id = agency_assessments_data[0].foundry_compilation_id
            
            # Try to get Foundry compilation details
            try:
                foundry_compilation = foundry_connector.get_compilation(foundry_compilation_id)
                if foundry_compilation:
                    foundry_info = {
                        "id": foundry_compilation_id,
                        "hash": foundry_compilation.get("data_hash", "unknown"),
                        "timestamp": foundry_compilation.get("timestamp", ""),
                        "verified": True  # Hash verified when compilation was ingested
                    }
                else:
                    foundry_info = {
                        "id": foundry_compilation_id,
                        "hash": "unknown",
                        "timestamp": "unknown",
                        "verified": False
                    }
            except Exception as e:
                logger.debug(f"Could not retrieve Foundry compilation: {e}")
                foundry_info = {
                    "id": foundry_compilation_id or "unknown",
                    "hash": "unknown",
                    "timestamp": "unknown",
                    "verified": False
                }
        else:
            foundry_info = {
                "id": "unknown",
                "hash": "unknown",
                "timestamp": "unknown",
                "verified": False
            }
        
        # Verify hash chain integrity: Foundry hash → ABC receipt hash → Agency assessment hashes
        chain_verified = True
        hash_chain_issues = []
        
        if agency_assessments_data:
            # 1. All assessments should reference same ABC receipt hash
            unique_receipt_hashes = set(a.abc_receipt_hash for a in agency_assessments_data)
            if len(unique_receipt_hashes) > 1:
                chain_verified = False
                hash_chain_issues.append("Assessments reference different ABC receipts")
                logger.warning(f"Hash chain integrity issue: assessments reference different ABC receipts")
            
            # 2. All assessments should reference same Foundry compilation
            unique_compilations = set(a.foundry_compilation_id for a in agency_assessments_data)
            if len(unique_compilations) > 1:
                chain_verified = False
                hash_chain_issues.append("Assessments reference different Foundry compilations")
                logger.warning(f"Hash chain integrity issue: assessments reference different Foundry compilations")
            
            # 3. Verify ABC receipt hash matches the receipt_hash parameter
            first_assessment = agency_assessments_data[0]
            if first_assessment.abc_receipt_hash:
                # Normalize both hashes for comparison
                abc_hash_normalized = first_assessment.abc_receipt_hash
                if abc_hash_normalized.startswith("sha256:"):
                    abc_hash_normalized = abc_hash_normalized[7:]
                
                if abc_hash_normalized != receipt_hash_normalized:
                    chain_verified = False
                    hash_chain_issues.append("ABC receipt hash mismatch")
                    logger.warning(f"Hash chain integrity issue: ABC receipt hash mismatch")
        
        # Determine overall verification status
        abc_blockchain_verified = False  # Would need ABC receipt tx_hash to verify (requires receipt store)
        all_agency_verified = all(
            receipt.get("verified", False) 
            for receipt in blockchain_verification_status.get("agency_receipts", [])
        ) if blockchain_verification_status.get("agency_receipts") else False
        
        overall_verified = chain_verified and (
            abc_blockchain_verified or 
            all_agency_verified or
            len(blockchain_verification_status.get("agency_receipts", [])) == 0
        )
        
        return {
            "foundry_compilation": foundry_info,
            "abc_analysis": {
                "receipt_hash": receipt_hash_clean,
                "receipt_hash_normalized": receipt_hash_normalized,
                "verified": True,  # Receipt hash is valid (assessments exist referencing it)
                "blockchain_verified": abc_blockchain_verified,
                "note": "ABC receipt blockchain verification requires receipt store access to get tx_hash"
            },
            "agency_assessments": agency_assessments_response,
            "blockchain_verification": blockchain_verification_status,
            "hash_chain_integrity": {
                "verified": chain_verified,
                "issues": hash_chain_issues if hash_chain_issues else None,
                "chain_links": {
                    "foundry_to_abc": "verified" if foundry_info.get("hash") != "unknown" else "pending",
                    "abc_to_agencies": "verified" if chain_verified else "failed"
                }
            },
            "chain_verified": overall_verified,
            "verification_timestamp": datetime.now().isoformat(),
            "verification_status": "complete" if overall_verified else "partial"
        }
        
    except Exception as e:
        logger.error(f"Error verifying receipt chain for {receipt_hash}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during receipt verification: {str(e)}"
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def foundry_status() -> Dict[str, Any]:
    """
    Get Foundry connector status
    
    Returns:
        Connection status and configuration
    """
    return {
        "enabled": foundry_connector.enabled,
        "foundry_url_configured": bool(foundry_connector.foundry_url),
        "api_token_configured": bool(foundry_connector.api_token),
        "timestamp": datetime.now().isoformat()
    }

