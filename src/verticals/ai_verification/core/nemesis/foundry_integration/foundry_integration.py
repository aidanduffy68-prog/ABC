"""
Foundry Integration
Main integration class for ABC-Foundry workflow

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, Optional
import logging

from .foundry_connector import FoundryConnector
from .compilation_validator import CompilationValidator
from .data_mapper import FoundryDataMapper

logger = logging.getLogger(__name__)


class FoundryIntegration:
    """
    Main integration class for ABC-Foundry workflow.
    
    Orchestrates:
    1. Retrieving Foundry compilations
    2. Validating compilation integrity
    3. Mapping to ABC format
    4. Preparing for ABC analysis
    """
    
    def __init__(
        self,
        foundry_api_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Foundry integration.
        
        Args:
            foundry_api_url: Foundry API base URL
            api_key: Foundry API key
        """
        self.connector = FoundryConnector(
            foundry_api_url=foundry_api_url,
            api_key=api_key
        )
        self.validator = CompilationValidator()
        self.mapper = FoundryDataMapper()
    
    def ingest_compilation(
        self,
        compilation_id: str,
        data_hash: Optional[str] = None,
        classification: Optional[str] = None,
        sources: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Ingest a Foundry compilation for ABC analysis.
        
        Args:
            compilation_id: Foundry compilation identifier
            data_hash: Expected data hash (optional, will validate if provided)
            classification: Expected classification (optional)
            sources: Expected sources (optional)
            
        Returns:
            Foundry compilation data ready for ABC analysis
            
        Raises:
            ValueError: If compilation validation fails
        """
        # Retrieve compilation from Foundry
        logger.info(f"Ingesting Foundry compilation: {compilation_id}")
        compilation = self.connector.get_compilation(compilation_id)
        
        # Validate compilation
        validation = self.validator.validate_compilation(compilation)
        
        if not validation["valid"]:
            error_msg = f"Compilation validation failed: {validation['errors']}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Verify optional parameters if provided
        if data_hash and compilation.get("data_hash") != data_hash:
            raise ValueError(f"Data hash mismatch: expected {data_hash}, got {compilation.get('data_hash')}")
        
        if classification and compilation.get("classification", "").upper() != classification.upper():
            logger.warning(
                f"Classification mismatch: expected {classification}, "
                f"got {compilation.get('classification')}"
            )
        
        if sources:
            compilation_sources = [s.get("provider") for s in compilation.get("sources", [])]
            expected_sources = [s if isinstance(s, str) else s.get("provider") for s in sources]
            
            if set(compilation_sources) != set(expected_sources):
                logger.warning(
                    f"Source mismatch: expected {expected_sources}, "
                    f"got {compilation_sources}"
                )
        
        logger.info(f"Successfully ingested Foundry compilation: {compilation_id}")
        
        return compilation
    
    def validate_compilation(
        self,
        compilation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a Foundry compilation.
        
        Args:
            compilation: Foundry compilation data
            
        Returns:
            Validation result
        """
        return self.validator.validate_compilation(compilation)
    
    def prepare_for_abc_analysis(
        self,
        compilation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare Foundry compilation for ABC analysis.
        
        Maps Foundry data to ABC format and extracts entities/relationships.
        
        Args:
            compilation: Foundry compilation data
            
        Returns:
            ABC-formatted data ready for Hades/Echo/Nemesis
        """
        # Map to ABC format
        abc_data = self.mapper.map_to_abc_format(compilation)
        
        # Extract entities and relationships
        entities = self.mapper.extract_entities(compilation)
        relationships = self.mapper.extract_relationships(compilation)
        
        # Add to network data
        abc_data["network_data"]["entities"] = entities
        abc_data["network_data"]["relationships"] = relationships
        
        logger.info(
            f"Prepared Foundry compilation {compilation.get('compilation_id')} "
            f"for ABC analysis: {len(abc_data['raw_intelligence'])} intelligence items, "
            f"{len(entities)} entities, {len(relationships)} relationships"
        )
        
        return abc_data
    
    def get_compilation_metadata(
        self,
        compilation_id: str
    ) -> Dict[str, Any]:
        """
        Get metadata for a compilation without full data.
        
        Args:
            compilation_id: Foundry compilation identifier
            
        Returns:
            Compilation metadata
        """
        return self.connector.get_compilation_metadata(compilation_id)
    
    def list_recent_compilations(
        self,
        limit: int = 100,
        classification: Optional[str] = None
    ) -> list:
        """
        List recent Foundry compilations.
        
        Args:
            limit: Maximum number to return
            classification: Filter by classification
            
        Returns:
            List of compilation summaries
        """
        return self.connector.list_recent_compilations(
            limit=limit,
            classification=classification
        )

