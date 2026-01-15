"""
Foundry Transformation: ABC Compilation (Hades/Echo/Nemesis)

Processes verified hash data through Hades/Echo/Nemesis compilation pipeline.

This transformation takes verified ABC receipt hash data and processes it through
the ABC compilation engine to generate behavioral signatures, coordination networks,
and threat forecasts.

Usage in Foundry Pipeline:
    1. Input: Verified hash data (from verify_abc_receipt transformation)
    2. This transform: Processes through Hades/Echo/Nemesis
    3. Output: Compiled intelligence with behavioral signatures, coordination, threat forecasts

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json

from src.verticals.ai_verification.core.nemesis.compilation_engine import (
    ABCCompilationEngine,
    CompiledIntelligence
)

logger = logging.getLogger(__name__)


def compile_from_verified_hashes(
    verified_hash_data: List[Dict[str, Any]],
    actor_id: Optional[str] = None,
    actor_name: Optional[str] = None,
    assumed_scenario: str = "aml_investigation"
) -> Dict[str, Any]:
    """
    Process verified hash data through Hades/Echo/Nemesis compilation.
    
    Takes verified ABC receipt hash data and processes it through the ABC compilation
    engine to generate behavioral signatures, coordination networks, and threat forecasts.
    
    Args:
        verified_hash_data: List of verified hash records from Foundry dataset
            Expected columns:
            - hash (or abc_receipt_hash)
            - verified (or is_verified)
            - transaction_hash (optional)
            - from_address (optional)
            - to_address (optional)
            - value (optional)
            - timestamp (optional)
            - source (optional)
        actor_id: Optional actor ID (defaults to derived from data)
        actor_name: Optional actor name (defaults to "AML Investigation")
        assumed_scenario: Scenario type (defaults to "aml_investigation" - works for any AML pattern)
    
    Returns:
        Dictionary with compiled intelligence:
        - compilation_id: ABC compilation ID
        - actor_id: Threat actor ID
        - actor_name: Threat actor name
        - behavioral_signature: Behavioral signature with confidence scores
        - coordination_network: Coordination network with partners/facilitators
        - threat_forecast: Threat forecast with risk scores
        - targeting_package: Targeting package with recommendations
        - confidence_score: Overall confidence score
        - compilation_time_ms: Compilation time in milliseconds
        - receipt_id: ABC receipt ID
        - receipt_hash: ABC receipt hash
        - compiled_at: Compilation timestamp
    """
    try:
        # Initialize compilation engine
        compilation_engine = ABCCompilationEngine()
        
        # Convert verified hash data to transaction format
        transaction_data = _convert_to_transaction_data(verified_hash_data)
        
        # Extract intelligence from verified hashes
        raw_intelligence = _extract_intelligence_from_hashes(verified_hash_data, assumed_scenario)
        
        # Determine actor ID/name
        if not actor_id:
            # Try to extract from data, or use default
            actor_id = _extract_actor_id(verified_hash_data) or f"foundry_{assumed_scenario}_{int(datetime.utcnow().timestamp())}"
        
        if not actor_name:
            actor_name = "AML Investigation" if assumed_scenario == "aml_investigation" else assumed_scenario.replace("_", " ").title()
        
        # Extract network data from transactions
        network_data = _extract_network_data(transaction_data)
        
        # Process through Hades/Echo/Nemesis
        compiled_intelligence = compilation_engine.compile_intelligence(
            actor_id=actor_id,
            actor_name=actor_name,
            raw_intelligence=raw_intelligence,
            transaction_data=transaction_data,
            network_data=network_data,
            generate_receipt=True,
            classification="UNCLASSIFIED"
        )
        
        # Convert CompiledIntelligence to dict for Foundry using asdict
        from dataclasses import asdict
        
        # Convert to dict first
        compiled_dict = asdict(compiled_intelligence)
        
        # Extract receipt info from targeting_package (receipt is stored there)
        receipt_id = None
        receipt_hash = None
        receipt_info = compiled_dict.get("targeting_package", {}).get("receipt", {})
        if receipt_info and isinstance(receipt_info, dict):
            receipt_id = receipt_info.get("receipt_id")
            receipt_hash = receipt_info.get("intelligence_hash")
        
        # Build result dict
        result = {
            "compilation_id": compiled_intelligence.compilation_id,
            "actor_id": compiled_intelligence.actor_id,
            "actor_name": compiled_intelligence.actor_name,
            "behavioral_signature": compiled_dict.get("behavioral_signature", {}),
            "coordination_network": compiled_dict.get("coordination_network", {}),
            "threat_forecast": compiled_dict.get("threat_forecast", {}),
            "targeting_package": compiled_dict.get("targeting_package", {}),
            "confidence_score": compiled_intelligence.confidence_score,
            "compilation_time_ms": compiled_intelligence.compilation_time_ms,
            "receipt_id": receipt_id,
            "receipt_hash": receipt_hash,
            "compiled_at": compiled_intelligence.compiled_at.isoformat() if compiled_intelligence.compiled_at else None,
            "assumed_scenario": assumed_scenario,
            "input_hash_count": len(verified_hash_data),
            "transaction_count": len(transaction_data)
        }
        
        logger.info(
            f"Successfully compiled {len(verified_hash_data)} verified hashes "
            f"through Hades/Echo/Nemesis (compilation_id: {compiled_intelligence.compilation_id})"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error compiling verified hashes: {e}", exc_info=True)
        raise


def _convert_to_transaction_data(verified_hash_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert verified hash data to transaction format"""
    transaction_data = []
    
    for record in verified_hash_data:
        # Extract transaction information
        tx_data = {
            "tx_hash": record.get("transaction_hash") or record.get("tx_hash") or record.get("hash"),
            "from_address": record.get("from_address") or record.get("from"),
            "to_address": record.get("to_address") or record.get("to"),
            "value": record.get("value") or record.get("amount"),
            "timestamp": record.get("timestamp") or record.get("block_timestamp"),
            "verified": record.get("verified") or record.get("is_verified", True),
            "source": record.get("source") or "foundry_verified_hash"
        }
        
        # Only add if we have at least a hash
        if tx_data["tx_hash"]:
            transaction_data.append(tx_data)
    
    return transaction_data


def _extract_intelligence_from_hashes(
    verified_hash_data: List[Dict[str, Any]],
    assumed_scenario: str
) -> List[Dict[str, Any]]:
    """Extract intelligence text from verified hashes (works for any AML investigation)"""
    intelligence = []
    
    # Add intelligence for verified hashes
    verified_count = sum(1 for r in verified_hash_data if r.get("verified") or r.get("is_verified", True))
    intelligence.append({
        "text": f"{verified_count} transactions verified with ABC receipt hashes",
        "source": "foundry_abc_verification",
        "type": "verification_summary"
    })
    
    # Add transaction pattern intelligence
    if len(verified_hash_data) > 1:
        intelligence.append({
            "text": f"Transaction pattern detected: {len(verified_hash_data)} verified transactions",
            "source": "foundry_pattern_detection",
            "type": "pattern_analysis"
        })
    
    return intelligence


def _extract_actor_id(verified_hash_data: List[Dict[str, Any]]) -> Optional[str]:
    """Extract actor ID from verified hash data"""
    # Try to find a common address pattern
    addresses = []
    for record in verified_hash_data:
        if record.get("from_address"):
            addresses.append(record["from_address"])
        if record.get("to_address"):
            addresses.append(record["to_address"])
    
    # Use first address as actor ID if available
    if addresses:
        # Hash the first address to create a stable actor ID
        import hashlib
        actor_id = hashlib.sha256(addresses[0].encode()).hexdigest()[:16]
        return f"foundry_actor_{actor_id}"
    
    return None


def _extract_network_data(transaction_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract network data from transaction data"""
    network_data = {
        "addresses": set(),
        "transactions": len(transaction_data)
    }
    
    for tx in transaction_data:
        if tx.get("from_address"):
            network_data["addresses"].add(tx["from_address"])
        if tx.get("to_address"):
            network_data["addresses"].add(tx["to_address"])
    
    # Convert set to list for JSON serialization
    network_data["addresses"] = list(network_data["addresses"])
    network_data["unique_address_count"] = len(network_data["addresses"])
    
    return network_data




# Foundry transform function (for use in Foundry pipelines)
def foundry_compile_intelligence(verified_hash_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Foundry transform function for ABC compilation.
    
    Processes verified hash data through Hades/Echo/Nemesis and returns
    compiled intelligence as a single-row dataset.
    Works for any AML investigation pattern.
    """
    result = compile_from_verified_hashes(
        verified_hash_data,
        assumed_scenario="aml_investigation"
    )
    
    # Return as list with single dict (can be converted to DataFrame)
    return [result]

