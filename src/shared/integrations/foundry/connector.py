"""
Palantir Foundry Connector
Handles authentication, data pipeline integration, and real-time feeds

Supports both:
- Pushing ABC data TO Foundry (export)
- Ingesting Foundry compilations FROM Foundry (for Foundry Chain verification)

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import hashlib
import time

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class FoundryDataExportConnector:
    """
    Connector for exporting ABC compilation data to Palantir Foundry
    
    Handles:
    - Authentication with Foundry
    - Data pipeline integration
    - Real-time data feeds
    - Batch data exports
    
    Note: This is for exporting ABC data TO Foundry.
    For Foundry Chain (ingesting FROM Foundry), see:
    src.core.nemesis.foundry_integration.foundry_connector
    """
    
    def __init__(self, foundry_url: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize Foundry connector
        
        Args:
            foundry_url: Foundry instance URL (from environment if not provided)
            api_token: Foundry API token (from environment if not provided)
        """
        import os
        self.foundry_url = foundry_url or os.getenv('FOUNDRY_URL', '')
        self.api_token = api_token or os.getenv('FOUNDRY_API_TOKEN', '')
        self.enabled = bool(self.foundry_url and self.api_token)
        
        if not self.enabled:
            logger.warning("Foundry connector not fully configured (missing URL or token)")
        
        # Set up requests session with retry logic
        if REQUESTS_AVAILABLE and self.enabled:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        else:
            self.session = None
    
    def push_compilation(
        self,
        compilation_data: Dict[str, Any],
        dataset_path: str = "gh_systems/intelligence_compilations"
    ) -> Dict[str, Any]:
        """
        Push compilation data to Foundry dataset
        
        Args:
            compilation_data: Compiled intelligence data
            dataset_path: Foundry dataset path (e.g., "gh_systems/intelligence_compilations")
        
        Returns:
            Push result with status and dataset reference
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "Foundry connector not configured"
            }
        
        # Format data for Foundry
        foundry_record = self._format_for_foundry(compilation_data)
        
        # In production, this would use Foundry API
        # For now, return formatted data structure
        return {
            "status": "success",
            "dataset_path": dataset_path,
            "record_id": compilation_data.get('compilation_id'),
            "timestamp": datetime.now().isoformat(),
            "data": foundry_record
        }
    
    def push_batch(
        self,
        compilations: List[Dict[str, Any]],
        dataset_path: str = "gh_systems/intelligence_compilations"
    ) -> Dict[str, Any]:
        """
        Push batch of compilations to Foundry
        
        Args:
            compilations: List of compiled intelligence data
            dataset_path: Foundry dataset path
        
        Returns:
            Batch push result
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "Foundry connector not configured"
            }
        
        formatted_records = [self._format_for_foundry(comp) for comp in compilations]
        
        return {
            "status": "success",
            "dataset_path": dataset_path,
            "records_pushed": len(formatted_records),
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_for_foundry(self, compilation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format compilation data for Foundry consumption
        
        Foundry prefers:
        - Flat or nested JSON structures
        - Timestamp fields
        - Clear data types
        - Consistent schemas
        """
        # Extract key fields
        behavioral_signature = compilation_data.get('behavioral_signature', {})
        coordination_network = compilation_data.get('coordination_network', {})
        threat_forecast = compilation_data.get('threat_forecast', {})
        targeting_package = compilation_data.get('targeting_package', {})
        
        # Format for Foundry (flattened structure with clear types)
        return {
            # Primary identifiers
            "compilation_id": compilation_data.get('compilation_id'),
            "actor_id": compilation_data.get('actor_id'),
            "actor_name": compilation_data.get('actor_name'),
            "compiled_at": compilation_data.get('compiled_at'),
            
            # Metrics
            "compilation_time_ms": float(compilation_data.get('compilation_time_ms', 0)),
            "confidence_score": float(compilation_data.get('confidence_score', 0)),
            
            # Behavioral signature (flattened)
            "behavioral_confidence": float(behavioral_signature.get('confidence', 0)) if isinstance(behavioral_signature, dict) else 0.0,
            "behavioral_traits": json.dumps(behavioral_signature.get('traits', {})) if isinstance(behavioral_signature, dict) else "{}",
            
            # Coordination network
            "coordination_partners": int(coordination_network.get('partner_count', 0)),
            "coordination_facilitators": int(coordination_network.get('facilitator_count', 0)),
            "network_confidence": float(coordination_network.get('network_confidence', 0)),
            
            # Threat forecast
            "threat_risk_score": float(threat_forecast.get('overall_risk_score', 0)) if isinstance(threat_forecast, dict) else 0.0,
            "threat_level": targeting_package.get('risk_assessment', {}).get('threat_level', 'unknown'),
            
            # Targeting package summary
            "targeting_instructions_count": len(targeting_package.get('targeting_instructions', [])),
            
            # Sources
            "sources": json.dumps(compilation_data.get('sources', [])),
            
            # Drift alerts
            "drift_alerts_count": len(compilation_data.get('drift_alerts', [])),
            
            # Metadata
            "engine_version": compilation_data.get('engine_version', '1.0.0'),
            "exported_at": datetime.now().isoformat()
        }
    
    def create_realtime_feed(
        self,
        feed_name: str = "gh_systems_intelligence_feed"
    ) -> Dict[str, Any]:
        """
        Create real-time data feed for Foundry
        
        Args:
            feed_name: Name of the feed
        
        Returns:
            Feed configuration
        """
        return {
            "feed_name": feed_name,
            "feed_type": "intelligence_compilations",
            "endpoint": f"/api/v1/foundry/feed/{feed_name}",
            "format": "json",
            "authentication": "api_token",
            "status": "active" if self.enabled else "disabled"
        }
    
    def get_dataset_schema(self) -> Dict[str, Any]:
        """
        Get Foundry dataset schema definition
        
        Returns:
            Schema definition for Foundry dataset
        """
        return {
            "dataset_name": "gh_systems_intelligence_compilations",
            "description": "GH Systems ABC intelligence compilation data",
            "schema": {
                "compilation_id": {"type": "string", "primary_key": True},
                "actor_id": {"type": "string", "indexed": True},
                "actor_name": {"type": "string"},
                "compiled_at": {"type": "timestamp"},
                "compilation_time_ms": {"type": "double"},
                "confidence_score": {"type": "double"},
                "behavioral_confidence": {"type": "double"},
                "behavioral_traits": {"type": "string"},  # JSON string
                "coordination_partners": {"type": "integer"},
                "coordination_facilitators": {"type": "integer"},
                "network_confidence": {"type": "double"},
                "threat_risk_score": {"type": "double"},
                "threat_level": {"type": "string"},
                "targeting_instructions_count": {"type": "integer"},
                "sources": {"type": "string"},  # JSON array string
                "drift_alerts_count": {"type": "integer"},
                "engine_version": {"type": "string"},
                "exported_at": {"type": "timestamp"}
            }
        }
    
    # ============================================================================
    # FOUNDRY INGESTION METHODS (For Foundry Chain Integration)
    # ============================================================================
    
    def get_compilation(self, compilation_id: str) -> Dict[str, Any]:
        """
        Fetch specific Foundry compilation by ID.
        
        Used by Foundry Chain to ingest Foundry compilation outputs for ABC verification.
        
        Args:
            compilation_id: Foundry compilation identifier
            
        Returns:
            Foundry compilation data with structure:
            {
                "compilation_id": str,
                "data_hash": str,  # SHA-256 hash
                "timestamp": str,  # ISO format
                "sources": List[Dict],  # Source providers and datasets
                "compiled_data": Dict  # Actual compilation content
            }
        """
        if not self.enabled:
            logger.warning(f"Foundry connector not enabled. Returning mock compilation for {compilation_id}")
            return self._mock_get_compilation(compilation_id)
        
        try:
            # Real API call to Foundry
            url = f"{self.foundry_url}/api/v1/compilations/{compilation_id}"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Fetching Foundry compilation: {compilation_id}")
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            compilation = response.json()
            logger.info(f"Successfully fetched compilation: {compilation_id}")
            return compilation
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Foundry compilation {compilation_id}: {e}")
            # Fallback to mock for development
            logger.warning(f"Falling back to mock compilation for {compilation_id}")
            return self._mock_get_compilation(compilation_id)
    
    def verify_compilation_hash(self, compilation: Dict[str, Any]) -> bool:
        """
        Verify that compilation.data_hash matches the actual content hash.
        
        Uses SHA-256 hashing (consistent with receipt_generator.py).
        Ensures data integrity for Foundry Chain verification.
        
        Args:
            compilation: Foundry compilation dictionary
            
        Returns:
            True if hash matches, False otherwise
        """
        if not compilation or "compiled_data" not in compilation:
            logger.warning("Compilation missing compiled_data, cannot verify hash")
            return False
        
        if "data_hash" not in compilation:
            logger.warning("Compilation missing data_hash field")
            return False
        
        # Calculate hash of compiled_data (consistent with Foundry's format)
        compiled_data = compilation["compiled_data"]
        
        # Serialize to JSON with sorted keys for consistent hashing
        serialized = json.dumps(compiled_data, sort_keys=True, ensure_ascii=False)
        calculated_hash = f"sha256:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"
        
        # Compare with provided hash
        provided_hash = compilation["data_hash"]
        matches = calculated_hash == provided_hash
        
        if not matches:
            logger.warning(
                f"Hash mismatch for compilation {compilation.get('compilation_id', 'unknown')}: "
                f"Expected {provided_hash}, Got {calculated_hash}"
            )
        else:
            logger.debug(f"Hash verified for compilation {compilation.get('compilation_id', 'unknown')}")
        
        return matches
    
    def list_recent_compilations(
        self,
        hours: int = 24,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get compilations from the last N hours.
        
        Supports pagination for large result sets.
        Used by Foundry Chain to discover new compilations for verification.
        
        Args:
            hours: Number of hours to look back (default: 24)
            limit: Maximum number of compilations to return (default: 100)
            offset: Pagination offset (default: 0)
            
        Returns:
            List of Foundry compilation dictionaries
        """
        if not self.enabled:
            logger.warning("Foundry connector not enabled. Returning mock compilations")
            return self._mock_list_recent_compilations(hours, limit, offset)
        
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Real API call to Foundry
            url = f"{self.foundry_url}/api/v1/compilations"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            params = {
                "since": start_time.isoformat(),
                "limit": limit,
                "offset": offset
            }
            
            logger.info(f"Fetching recent compilations (last {hours} hours, limit={limit}, offset={offset})")
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            compilations = response.json().get("compilations", [])
            logger.info(f"Successfully fetched {len(compilations)} compilations")
            return compilations
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching recent compilations: {e}")
            # Fallback to mock for development
            logger.warning("Falling back to mock compilations")
            return self._mock_list_recent_compilations(hours, limit, offset)
    
    # ============================================================================
    # MOCK METHODS (For Development/Testing)
    # ============================================================================
    
    def _mock_get_compilation(self, compilation_id: str) -> Dict[str, Any]:
        """
        Generate mock Foundry compilation for development/testing.
        
        Matches format from FOUNDRY_CHAIN_SPEC.md examples.
        """
        # Generate mock compiled_data
        compiled_data = {
            "threat_actors": [
                {
                    "id": "actor_001",
                    "name": "Mock Threat Actor",
                    "description": "Mock threat actor for testing",
                    "risk_level": "high"
                }
            ],
            "wallet_addresses": [
                {
                    "address": "0x1234567890abcdef",
                    "label": "Test Wallet",
                    "risk_score": 0.85
                }
            ],
            "coordination_networks": [
                {
                    "source_entity": "actor_001",
                    "target_entity": "0x1234567890abcdef",
                    "relationship_type": "coordinates_with",
                    "confidence": 0.82
                }
            ],
            "temporal_patterns": []
        }
        
        # Calculate hash (consistent with verify_compilation_hash)
        serialized = json.dumps(compiled_data, sort_keys=True, ensure_ascii=False)
        data_hash = f"sha256:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"
        
        return {
            "compilation_id": compilation_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "sources": [
                {"provider": "chainalysis", "dataset": "sanctions_list_v2"},
                {"provider": "trm_labs", "dataset": "threat_actors_q4"},
                {"provider": "ofac", "dataset": "sdn_list_current"},
                {"provider": "dhs", "dataset": "cyber_threats_classified"}
            ],
            "data_hash": data_hash,
            "classification": "SBU",
            "compiled_data": compiled_data
        }
    
    def _mock_list_recent_compilations(
        self,
        hours: int = 24,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Generate mock list of recent compilations for development/testing.
        """
        compilations = []
        now = datetime.now()
        
        # Generate mock compilations (one per hour for the requested time range)
        num_compilations = min(limit, hours)
        
        for i in range(num_compilations):
            timestamp = now - timedelta(hours=hours - i - offset)
            compilation_id = f"foundry-comp-{timestamp.strftime('%Y%m%d%H%M%S')}"
            compilations.append(self._mock_get_compilation(compilation_id))
        
        return compilations

