"""
Foundry Compilation Validator
Validates Foundry compilation data integrity and structure

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CompilationValidator:
    """
    Validates Foundry compilation data for integrity and structure.
    
    Ensures:
    - Data hash matches expected value
    - Sources are verified
    - Classification is appropriate
    - Structure is valid
    """
    
    def __init__(self):
        """Initialize compilation validator."""
        pass
    
    def validate_compilation(
        self,
        compilation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a Foundry compilation.
        
        Args:
            compilation: Foundry compilation data
            
        Returns:
            Validation result with status and details
        """
        result = {
            "valid": True,
            "sources_verified": False,
            "hash_matches": False,
            "classification_appropriate": False,
            "structure_valid": False,
            "errors": [],
            "warnings": []
        }
        
        # Validate structure
        structure_valid = self._validate_structure(compilation)
        result["structure_valid"] = structure_valid
        
        if not structure_valid:
            result["valid"] = False
            result["errors"].append("Invalid compilation structure")
            return result
        
        # Validate hash
        hash_matches = self._validate_hash(compilation)
        result["hash_matches"] = hash_matches
        
        if not hash_matches:
            result["valid"] = False
            result["errors"].append("Data hash does not match")
        
        # Validate sources
        sources_verified = self._validate_sources(compilation)
        result["sources_verified"] = sources_verified
        
        if not sources_verified:
            result["warnings"].append("Some sources could not be verified")
        
        # Validate classification
        classification_appropriate = self._validate_classification(compilation)
        result["classification_appropriate"] = classification_appropriate
        
        if not classification_appropriate:
            result["warnings"].append("Classification may be inappropriate for data content")
        
        # Overall validity
        result["valid"] = (
            structure_valid and
            hash_matches and
            sources_verified
        )
        
        return result
    
    def _validate_structure(
        self,
        compilation: Dict[str, Any]
    ) -> bool:
        """Validate compilation structure."""
        required_fields = [
            "compilation_id",
            "timestamp",
            "sources",
            "data_hash"
        ]
        
        for field in required_fields:
            if field not in compilation:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate sources structure
        if not isinstance(compilation["sources"], list):
            logger.error("Sources must be a list")
            return False
        
        # Validate timestamp format
        try:
            datetime.fromisoformat(compilation["timestamp"].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.error("Invalid timestamp format")
            return False
        
        return True
    
    def _validate_hash(
        self,
        compilation: Dict[str, Any]
    ) -> bool:
        """Validate data hash matches computed hash."""
        expected_hash = compilation.get("data_hash", "")
        
        if not expected_hash:
            return False
        
        # Extract hash algorithm and value
        if ":" in expected_hash:
            algorithm, hash_value = expected_hash.split(":", 1)
        else:
            algorithm = "sha256"
            hash_value = expected_hash
        
        # Compute hash of compiled data
        compiled_data = compilation.get("compiled_data", {})
        data_json = json.dumps(compiled_data, sort_keys=True)
        
        if algorithm.lower() == "sha256":
            computed_hash = hashlib.sha256(data_json.encode()).hexdigest()
        else:
            logger.warning(f"Unsupported hash algorithm: {algorithm}")
            return False
        
        # Compare hashes
        matches = computed_hash == hash_value.lower()
        
        if not matches:
            logger.warning(
                f"Hash mismatch: expected {hash_value[:16]}..., "
                f"computed {computed_hash[:16]}..."
            )
        
        return matches
    
    def _validate_sources(
        self,
        compilation: Dict[str, Any]
    ) -> bool:
        """Validate source data."""
        sources = compilation.get("sources", [])
        
        if not sources:
            logger.warning("No sources specified")
            return False
        
        # Validate each source has required fields
        for source in sources:
            if not isinstance(source, dict):
                return False
            
            if "provider" not in source:
                logger.warning("Source missing provider field")
                return False
        
        return True
    
    def _validate_classification(
        self,
        compilation: Dict[str, Any]
    ) -> bool:
        """Validate classification is appropriate."""
        classification = compilation.get("classification", "").upper()
        
        valid_classifications = [
            "UNCLASSIFIED",
            "SBU",
            "SENSITIVE BUT UNCLASSIFIED",
            "CLASSIFIED",
            "SECRET",
            "TOP SECRET"
        ]
        
        # Check if classification is valid
        is_valid = any(
            valid in classification
            for valid in valid_classifications
        )
        
        if not is_valid:
            logger.warning(f"Unrecognized classification: {classification}")
        
        return is_valid
    
    def compute_data_hash(
        self,
        compiled_data: Dict[str, Any],
        algorithm: str = "sha256"
    ) -> str:
        """
        Compute hash of compiled data.
        
        Args:
            compiled_data: Data to hash
            algorithm: Hash algorithm (default: sha256)
            
        Returns:
            Hash string in format "algorithm:hash"
        """
        data_json = json.dumps(compiled_data, sort_keys=True)
        
        if algorithm.lower() == "sha256":
            hash_value = hashlib.sha256(data_json.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        return f"{algorithm}:{hash_value}"

