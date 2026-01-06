"""
Foundry Data Mapper
Maps Foundry compilation data to ABC format

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class FoundryDataMapper:
    """
    Maps Foundry compilation data to ABC intelligence format.
    
    Converts Foundry's unified data model into ABC's expected structure
    for Hades/Echo/Nemesis processing.
    """
    
    def __init__(self):
        """Initialize data mapper."""
        pass
    
    def map_to_abc_format(
        self,
        foundry_compilation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map Foundry compilation to ABC intelligence format.
        
        Args:
            foundry_compilation: Foundry compilation data
            
        Returns:
            ABC-formatted intelligence data
        """
        compiled_data = foundry_compilation.get("compiled_data", {})
        
        # Map threat actors
        raw_intelligence = []
        
        # Add threat actors as intelligence reports
        threat_actors = compiled_data.get("threat_actors", [])
        for actor in threat_actors:
            raw_intelligence.append({
                "text": self._format_threat_actor(actor),
                "source": "foundry",
                "type": "threat_actor",
                "foundry_source": actor.get("source_provider", "unknown")
            })
        
        # Add wallet addresses as transaction data
        transaction_data = []
        wallet_addresses = compiled_data.get("wallet_addresses", [])
        for wallet in wallet_addresses:
            transaction_data.append({
                "address": wallet.get("address"),
                "label": wallet.get("label"),
                "risk_score": wallet.get("risk_score"),
                "source": wallet.get("source_provider", "foundry")
            })
        
        # Add coordination networks as network data
        network_data = {
            "coordination_networks": compiled_data.get("coordination_networks", []),
            "temporal_patterns": compiled_data.get("temporal_patterns", []),
            "foundry_compilation_id": foundry_compilation.get("compilation_id"),
            "foundry_data_hash": foundry_compilation.get("data_hash"),
            "foundry_timestamp": foundry_compilation.get("timestamp"),
            "foundry_sources": foundry_compilation.get("sources", []),
            "classification": foundry_compilation.get("classification", "UNCLASSIFIED")
        }
        
        return {
            "raw_intelligence": raw_intelligence,
            "transaction_data": transaction_data,
            "network_data": network_data,
            "metadata": {
                "foundry_compilation_id": foundry_compilation.get("compilation_id"),
                "foundry_data_hash": foundry_compilation.get("data_hash"),
                "foundry_timestamp": foundry_compilation.get("timestamp"),
                "foundry_sources": foundry_compilation.get("sources", []),
                "classification": foundry_compilation.get("classification", "UNCLASSIFIED")
            }
        }
    
    def _format_threat_actor(
        self,
        actor: Dict[str, Any]
    ) -> str:
        """Format threat actor data as intelligence text."""
        name = actor.get("name", "Unknown Actor")
        description = actor.get("description", "")
        risk_level = actor.get("risk_level", "unknown")
        
        text = f"Threat Actor: {name}"
        
        if description:
            text += f". {description}"
        
        text += f". Risk Level: {risk_level}"
        
        # Add additional attributes
        if actor.get("aliases"):
            text += f". Aliases: {', '.join(actor.get('aliases', []))}"
        
        if actor.get("associated_wallets"):
            wallet_count = len(actor.get("associated_wallets", []))
            text += f". Associated Wallets: {wallet_count}"
        
        return text
    
    def extract_entities(
        self,
        foundry_compilation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract entities from Foundry compilation for graph analysis.
        
        Args:
            foundry_compilation: Foundry compilation data
            
        Returns:
            List of extracted entities
        """
        entities = []
        compiled_data = foundry_compilation.get("compiled_data", {})
        
        # Extract threat actors as entities
        for actor in compiled_data.get("threat_actors", []):
            entities.append({
                "entity_id": actor.get("id", f"actor_{len(entities)}"),
                "entity_type": "threat_actor",
                "name": actor.get("name"),
                "attributes": actor
            })
        
        # Extract wallet addresses as entities
        for wallet in compiled_data.get("wallet_addresses", []):
            entities.append({
                "entity_id": wallet.get("address"),
                "entity_type": "wallet",
                "name": wallet.get("label", wallet.get("address")),
                "attributes": wallet
            })
        
        return entities
    
    def extract_relationships(
        self,
        foundry_compilation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract relationships from Foundry coordination networks.
        
        Args:
            foundry_compilation: Foundry compilation data
            
        Returns:
            List of extracted relationships
        """
        relationships = []
        compiled_data = foundry_compilation.get("compiled_data", {})
        
        # Extract coordination networks as relationships
        for network in compiled_data.get("coordination_networks", []):
            source_entity = network.get("source_entity")
            target_entity = network.get("target_entity")
            relationship_type = network.get("relationship_type", "coordinates_with")
            confidence = network.get("confidence", 0.5)
            
            relationships.append({
                "source_entity_id": source_entity,
                "target_entity_id": target_entity,
                "relationship_type": relationship_type,
                "confidence": confidence,
                "attributes": network
            })
        
        return relationships

