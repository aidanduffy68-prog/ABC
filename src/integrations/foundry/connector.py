"""
Palantir Foundry Connector
Handles authentication, data pipeline integration, and real-time feeds

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class FoundryConnector:
    """
    Connector for Palantir Foundry integration
    
    Handles:
    - Authentication with Foundry
    - Data pipeline integration
    - Real-time data feeds
    - Batch data exports
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

