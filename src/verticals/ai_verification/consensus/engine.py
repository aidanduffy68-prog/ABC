"""
Consensus Calculation Engine
Calculate multi-agency consensus on Foundry compilations

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any
import statistics
import logging

from src.verticals.ai_verification.schemas.agency import AgencyAssessment, ConsensusResult

logger = logging.getLogger(__name__)


class ConsensusEngine:
    """
    Calculate multi-agency consensus on Foundry compilations.
    
    **ABC is infrastructure for verification, not decision-making.**
    This engine detects outliers and generates recommendations, but **humans make
    the final decision** based on the verified data integrity proof.
    
    Detects outliers and generates advisory recommendations. When agencies disagree
    (e.g., CIA 85%, DHS 60%, NSA 78%), ABC proves they analyzed the same data.
    The disagreement is methodology, not data quality - humans evaluate analysis approaches.
    """
    
    def __init__(self, outlier_threshold_std_devs: float = 2.0):
        """
        Initialize consensus engine.
        
        Args:
            outlier_threshold_std_devs: Number of std devs to flag outliers
        """
        self.outlier_threshold = outlier_threshold_std_devs
    
    def calculate_consensus(
        self,
        foundry_compilation_id: str,
        abc_baseline_confidence: float,
        agency_assessments: List[AgencyAssessment]
    ) -> ConsensusResult:
        """
        Calculate consensus across agency assessments.
        
        **ABC verifies inputs, not outputs.** This method provides statistical analysis
        and advisory recommendations, but humans (analysts, compliance officers) make
        final decisions. ABC proves all agencies analyzed identical source data.
        
        Args:
            foundry_compilation_id: Foundry compilation identifier
            abc_baseline_confidence: ABC baseline confidence score (0-100)
            agency_assessments: List of agency assessment submissions
        
        Returns:
            ConsensusResult with mean, std dev, outliers, and advisory recommendation.
            Recommendation is advisory only - humans make final decisions.
        """
        if not agency_assessments:
            raise ValueError("agency_assessments cannot be empty")
        
        logger.info(
            f"Calculating consensus for {foundry_compilation_id} "
            f"with {len(agency_assessments)} agency assessments"
        )
        
        # Extract confidence scores
        scores = [a.confidence_score for a in agency_assessments]
        
        # Calculate statistics
        mean = statistics.mean(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
        
        logger.debug(
            f"Consensus statistics - Mean: {mean:.2f}, Std Dev: {std_dev:.2f}"
        )
        
        # Detect outliers (>threshold std devs from mean)
        outliers = []
        for assessment in agency_assessments:
            z_score = abs(assessment.confidence_score - mean) / std_dev if std_dev > 0 else 0
            if z_score > self.outlier_threshold:
                outlier_info = {
                    "agency": assessment.agency,
                    "confidence": assessment.confidence_score,
                    "z_score": round(z_score, 2)
                }
                outliers.append(outlier_info)
                logger.warning(
                    f"Outlier detected: {assessment.agency} "
                    f"(confidence={assessment.confidence_score:.2f}, z_score={z_score:.2f})"
                )
        
        # Generate advisory recommendation (humans make final decision)
        # ABC provides infrastructure for verification - recommendations are advisory only
        if outliers:
            agencies = [o["agency"] for o in outliers]
            recommendation = f"Advisory: Investigate methodology for: {', '.join(agencies)}. These agencies show significant deviation from consensus mean. Human analyst makes final decision."
        else:
            recommendation = "Consensus achieved - no outliers detected. All agencies are within acceptable range. Human analyst reviews for final decision."
        
        # Verify all reference same Foundry compilation
        verified = all(
            a.foundry_compilation_id == foundry_compilation_id 
            for a in agency_assessments
        )
        
        if not verified:
            logger.error(
                f"Verification failed: Not all assessments reference "
                f"the same Foundry compilation {foundry_compilation_id}"
            )
        
        # Build consensus metrics
        consensus_metrics = {
            "mean_confidence": round(mean, 2),
            "std_deviation": round(std_dev, 2),
            "outliers": outliers,
            "num_assessments": len(agency_assessments),
            "abc_baseline_confidence": abc_baseline_confidence,
            "baseline_deviation": round(abs(mean - abc_baseline_confidence), 2)
        }
        
        result = ConsensusResult(
            foundry_compilation_id=foundry_compilation_id,
            abc_baseline_confidence=abc_baseline_confidence,
            agency_assessments=[a.dict() for a in agency_assessments],
            consensus_metrics=consensus_metrics,
            recommendation=recommendation,
            verified=verified
        )
        
        logger.info(
            f"Consensus calculation complete for {foundry_compilation_id}. "
            f"Outliers: {len(outliers)}, Verified: {verified}"
        )
        
        return result

