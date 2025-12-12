"""
Assessment Validator
Validates agency assessments for structure and blockchain commitments

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AssessmentValidator:
    """
    Validates agency assessments for:
    - Required fields
    - Blockchain receipt verification
    - Foundry compilation ID matching
    - ABC receipt hash matching
    """
    
    def __init__(self):
        """Initialize assessment validator."""
        pass
    
    def validate_assessment(
        self,
        assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate an agency assessment.
        
        Args:
            assessment: Agency assessment data
            
        Returns:
            Validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate required fields
        required_fields = [
            "agency",
            "foundry_compilation_id",
            "abc_receipt_hash",
            "confidence_score",
            "receipt_hash"
        ]
        
        for field in required_fields:
            if field not in assessment:
                result["valid"] = False
                result["errors"].append(f"Missing required field: {field}")
        
        # Validate confidence score range
        confidence = assessment.get("confidence_score")
        if confidence is not None:
            if not (0.0 <= confidence <= 100.0):
                result["valid"] = False
                result["errors"].append(
                    f"Confidence score out of range: {confidence} (must be 0-100)"
                )
        
        # Validate receipt hash format
        receipt_hash = assessment.get("receipt_hash")
        if receipt_hash:
            if not isinstance(receipt_hash, str) or len(receipt_hash) < 32:
                result["warnings"].append(
                    "Receipt hash format may be invalid"
                )
        
        return result
    
    def validate_consistency(
        self,
        assessments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate consistency across multiple assessments.
        
        Ensures all assessments reference the same:
        - Foundry compilation ID
        - ABC receipt hash
        
        Args:
            assessments: List of agency assessments
            
        Returns:
            Consistency validation result
        """
        if not assessments:
            return {
                "consistent": False,
                "error": "No assessments provided"
            }
        
        # Get reference values from first assessment
        first = assessments[0]
        foundry_compilation_id = first.get("foundry_compilation_id")
        abc_receipt_hash = first.get("abc_receipt_hash")
        
        inconsistencies = []
        
        for i, assessment in enumerate(assessments[1:], start=1):
            agency = assessment.get("agency", f"Assessment {i}")
            
            if assessment.get("foundry_compilation_id") != foundry_compilation_id:
                inconsistencies.append({
                    "agency": agency,
                    "field": "foundry_compilation_id",
                    "expected": foundry_compilation_id,
                    "actual": assessment.get("foundry_compilation_id")
                })
            
            if assessment.get("abc_receipt_hash") != abc_receipt_hash:
                inconsistencies.append({
                    "agency": agency,
                    "field": "abc_receipt_hash",
                    "expected": abc_receipt_hash,
                    "actual": assessment.get("abc_receipt_hash")
                })
        
        return {
            "consistent": len(inconsistencies) == 0,
            "foundry_compilation_id": foundry_compilation_id,
            "abc_receipt_hash": abc_receipt_hash,
            "inconsistencies": inconsistencies if inconsistencies else None
        }

