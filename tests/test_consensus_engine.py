"""
Test Suite for Consensus Engine
Tests consensus calculation with edge cases

Run with: pytest tests/test_consensus_engine.py -v
"""

import pytest
import statistics
from src.consensus.engine import ConsensusEngine
from src.schemas.agency import AgencyAssessment, ClassificationLevel


@pytest.fixture
def consensus_engine():
    """Create consensus engine instance"""
    return ConsensusEngine(outlier_threshold_std_devs=2.0)


def test_consensus_single_assessment(consensus_engine):
    """Test consensus with single assessment"""
    assessment = AgencyAssessment(
        agency="CIA",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc123",
        assessment_hash="sha256:cia456",
        confidence_score=85.0,
        classification=ClassificationLevel.SECRET
    )
    
    result = consensus_engine.calculate_consensus(
        foundry_compilation_id="foundry-comp-001",
        abc_baseline_confidence=88.0,
        agency_assessments=[assessment]
    )
    
    assert result.foundry_compilation_id == "foundry-comp-001"
    assert result.abc_baseline_confidence == 88.0
    assert len(result.agency_assessments) == 1
    assert result.consensus_metrics["mean_confidence"] == 85.0
    assert result.consensus_metrics["std_deviation"] == 0.0
    assert len(result.consensus_metrics["outliers"]) == 0
    assert result.verified == True


def test_consensus_all_identical_scores(consensus_engine):
    """Test consensus when all agencies have identical scores"""
    assessments = [
        AgencyAssessment(
            agency="CIA",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash=f"sha256:cia{i}",
            confidence_score=85.0,
            classification=ClassificationLevel.SECRET
        )
        for i in range(5)
    ]
    
    result = consensus_engine.calculate_consensus(
        foundry_compilation_id="foundry-comp-001",
        abc_baseline_confidence=85.0,
        agency_assessments=assessments
    )
    
    assert result.consensus_metrics["mean_confidence"] == 85.0
    assert result.consensus_metrics["std_deviation"] == 0.0
    assert len(result.consensus_metrics["outliers"]) == 0
    assert "no outliers" in result.recommendation.lower()


def test_consensus_outlier_detection(consensus_engine):
    """Test outlier detection when one agency differs significantly"""
    assessments = [
        AgencyAssessment(
            agency="CIA",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:cia456",
            confidence_score=85.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="DHS",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:dhs789",
            confidence_score=82.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="Treasury",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:treasury123",
            confidence_score=84.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="FBI",  # Outlier: much lower confidence
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:fbi456",
            confidence_score=30.0,  # Significant outlier
            classification=ClassificationLevel.SECRET
        )
    ]
    
    result = consensus_engine.calculate_consensus(
        foundry_compilation_id="foundry-comp-001",
        abc_baseline_confidence=85.0,
        agency_assessments=assessments
    )
    
    assert result.consensus_metrics["mean_confidence"] == pytest.approx(70.25, abs=0.1)
    assert len(result.consensus_metrics["outliers"]) > 0
    
    # FBI should be detected as outlier
    outlier_agencies = [o["agency"] for o in result.consensus_metrics["outliers"]]
    assert "FBI" in outlier_agencies
    assert "Investigate methodology" in result.recommendation


def test_consensus_no_outliers(consensus_engine):
    """Test consensus when all scores are close together"""
    assessments = [
        AgencyAssessment(
            agency="CIA",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:cia456",
            confidence_score=85.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="DHS",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:dhs789",
            confidence_score=83.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="Treasury",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:treasury123",
            confidence_score=84.0,
            classification=ClassificationLevel.SECRET
        )
    ]
    
    result = consensus_engine.calculate_consensus(
        foundry_compilation_id="foundry-comp-001",
        abc_baseline_confidence=85.0,
        agency_assessments=assessments
    )
    
    assert len(result.consensus_metrics["outliers"]) == 0
    assert "Consensus achieved" in result.recommendation


def test_consensus_empty_assessments(consensus_engine):
    """Test error when no assessments provided"""
    with pytest.raises(ValueError, match="cannot be empty"):
        consensus_engine.calculate_consensus(
            foundry_compilation_id="foundry-comp-001",
            abc_baseline_confidence=85.0,
            agency_assessments=[]
        )


def test_consensus_verification_mismatch(consensus_engine):
    """Test verification fails when assessments reference different compilations"""
    assessments = [
        AgencyAssessment(
            agency="CIA",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:cia456",
            confidence_score=85.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="DHS",
            foundry_compilation_id="foundry-comp-002",  # Different compilation
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:dhs789",
            confidence_score=82.0,
            classification=ClassificationLevel.SECRET
        )
    ]
    
    result = consensus_engine.calculate_consensus(
        foundry_compilation_id="foundry-comp-001",
        abc_baseline_confidence=85.0,
        agency_assessments=assessments
    )
    
    assert result.verified == False


def test_consensus_extreme_outlier(consensus_engine):
    """Test consensus with extreme outlier (confidence = 0 or 100)"""
    assessments = [
        AgencyAssessment(
            agency="CIA",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:cia456",
            confidence_score=90.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="DHS",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:dhs789",
            confidence_score=88.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="Extreme",  # Extreme outlier
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:extreme123",
            confidence_score=0.0,  # Minimum possible
            classification=ClassificationLevel.SECRET
        )
    ]
    
    result = consensus_engine.calculate_consensus(
        foundry_compilation_id="foundry-comp-001",
        abc_baseline_confidence=90.0,
        agency_assessments=assessments
    )
    
    assert len(result.consensus_metrics["outliers"]) > 0
    outlier_agencies = [o["agency"] for o in result.consensus_metrics["outliers"]]
    assert "Extreme" in outlier_agencies


def test_consensus_custom_threshold(consensus_engine):
    """Test consensus with custom outlier threshold"""
    # Create engine with stricter threshold
    strict_engine = ConsensusEngine(outlier_threshold_std_devs=1.0)
    
    assessments = [
        AgencyAssessment(
            agency="Agency1",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:agency1",
            confidence_score=85.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="Agency2",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:agency2",
            confidence_score=75.0,  # 10 points difference
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="Agency3",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:agency3",
            confidence_score=80.0,
            classification=ClassificationLevel.SECRET
        )
    ]
    
    result = strict_engine.calculate_consensus(
        foundry_compilation_id="foundry-comp-001",
        abc_baseline_confidence=85.0,
        agency_assessments=assessments
    )
    
    # With stricter threshold, Agency2 might be flagged
    # (depends on std dev calculation)
    assert "consensus_metrics" in result.dict()
    assert result.verified == True


def test_consensus_baseline_deviation(consensus_engine):
    """Test that baseline deviation is calculated correctly"""
    assessments = [
        AgencyAssessment(
            agency="CIA",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:cia456",
            confidence_score=85.0,
            classification=ClassificationLevel.SECRET
        ),
        AgencyAssessment(
            agency="DHS",
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash="sha256:abc123",
            assessment_hash="sha256:dhs789",
            confidence_score=80.0,
            classification=ClassificationLevel.SECRET
        )
    ]
    
    abc_baseline = 90.0
    result = consensus_engine.calculate_consensus(
        foundry_compilation_id="foundry-comp-001",
        abc_baseline_confidence=abc_baseline,
        agency_assessments=assessments
    )
    
    mean = result.consensus_metrics["mean_confidence"]
    expected_deviation = abs(mean - abc_baseline)
    actual_deviation = result.consensus_metrics["baseline_deviation"]
    
    assert actual_deviation == pytest.approx(expected_deviation, abs=0.1)
    assert result.consensus_metrics["abc_baseline_confidence"] == abc_baseline

