"""
Palantir Foundry Integration API Endpoints
Provides Foundry-compatible data feeds and exports

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from datetime import datetime, timedelta
import json

from src.integrations.foundry.connector import FoundryConnector
from src.integrations.foundry.export import FoundryDataExporter
from src.core.middleware.auth import require_auth
from src.core.middleware.rate_limit import rate_limit

# Create router
router = APIRouter(prefix="/api/v1/foundry", tags=["foundry"])

# Initialize connector
foundry_connector = FoundryConnector()


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

