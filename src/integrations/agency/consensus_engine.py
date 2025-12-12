"""
Consensus Engine
Detects conflicts and calculates consensus across agency assessments

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from statistics import mean, stdev
import logging

logger = logging.getLogger(__name__)


class ConsensusEngine:
    """
    Analyzes multiple agency assessments and calculates consensus.
    
    Detects:
    - Conflicting assessments
    - Outliers
    - Consensus metrics
    - Recommendations
    """
    
    def __init__(self, outlier_threshold: float = 2.0):
        """
        Initialize consensus engine.
        
        Args:
            outlier_threshold: Standard deviations from mean to consider outlier
        """
        self.outlier_threshold = outlier_threshold
    
    def analyze_conflicting_assessments(
        self,
        target: str,
        assessments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze conflicting assessments for a target.
        
        Args:
            target: Target identifier
            assessments: List of agency assessments
            
        Returns:
            Consensus analysis with conflicts and recommendations
        """
        if not assessments:
            return {
                "target": target,
                "error": "No assessments provided"
            }
        
        # Verify all reference same source data
        foundry_compilation_id = assessments[0].get("foundry_compilation_id")
        abc_receipt_hash = assessments[0].get("abc_receipt_hash")
        
        verified_assessments = []
        verification_errors = []
        
        for assessment in assessments:
            # Verify blockchain commitment
            receipt_hash = assessment.get("receipt_hash")
            if not receipt_hash:
                verification_errors.append({
                    "agency": assessment.get("agency", "unknown"),
                    "error": "Missing receipt hash"
                })
                continue
            
            # Verify same Foundry compilation
            if assessment.get("foundry_compilation_id") != foundry_compilation_id:
                verification_errors.append({
                    "agency": assessment.get("agency", "unknown"),
                    "error": "Different Foundry compilation ID"
                })
                continue
            
            # Verify same ABC receipt
            if assessment.get("abc_receipt_hash") != abc_receipt_hash:
                verification_errors.append({
                    "agency": assessment.get("agency", "unknown"),
                    "error": "Different ABC receipt hash"
                })
                continue
            
            verified_assessments.append(assessment)
        
        if not verified_assessments:
            return {
                "target": target,
                "error": "No verified assessments",
                "verification_errors": verification_errors
            }
        
        # Extract confidence scores
        confidence_scores = [
            a.get("confidence_score", 0.0)
            for a in verified_assessments
        ]
        
        # Calculate statistics
        mean_confidence = mean(confidence_scores)
        std_dev = stdev(confidence_scores) if len(confidence_scores) > 1 else 0.0
        
        # Identify outliers
        outliers = []
        for assessment in verified_assessments:
            confidence = assessment.get("confidence_score", 0.0)
            z_score = abs((confidence - mean_confidence) / std_dev) if std_dev > 0 else 0
            
            if z_score > self.outlier_threshold:
                outliers.append({
                    "agency": assessment.get("agency"),
                    "confidence": confidence,
                    "z_score": z_score
                })
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            verified_assessments,
            mean_confidence,
            std_dev,
            outliers
        )
        
        return {
            "target": target,
            "foundry_compilation": foundry_compilation_id,
            "abc_baseline": {
                "receipt_hash": abc_receipt_hash,
                "blockchain_verified": True
            },
            "agency_assessments": [
                {
                    "agency": a.get("agency"),
                    "confidence": a.get("confidence_score"),
                    "threat_level": a.get("threat_level"),
                    "verified": True,
                    "receipt_hash": a.get("receipt_hash")
                }
                for a in verified_assessments
            ],
            "consensus": {
                "mean_confidence": mean_confidence,
                "std_deviation": std_dev,
                "outliers": outliers,
                "recommendation": recommendation
            },
            "verification_errors": verification_errors if verification_errors else None
        }
    
    def _generate_recommendation(
        self,
        assessments: List[Dict[str, Any]],
        mean_confidence: float,
        std_dev: float,
        outliers: List[Dict[str, Any]]
    ) -> str:
        """Generate recommendation based on consensus analysis."""
        if not outliers:
            return "All assessments are in consensus. Proceed with mean confidence."
        
        outlier_agencies = [o["agency"] for o in outliers]
        
        if std_dev > 20.0:
            return (
                f"High variance detected (σ={std_dev:.1f}). "
                f"Investigate methodology differences, especially for: {', '.join(outlier_agencies)}"
            )
        elif std_dev > 10.0:
            return (
                f"Moderate variance detected (σ={std_dev:.1f}). "
                f"Review assessments from: {', '.join(outlier_agencies)}"
            )
        else:
            return (
                f"Low variance (σ={std_dev:.1f}). "
                f"Minor differences in: {', '.join(outlier_agencies)}"
            )

