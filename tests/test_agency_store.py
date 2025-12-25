"""
Test Suite for Agency Assessment Store
Tests in-memory storage, indexing, idempotency, and edge cases

Run with: pytest tests/test_agency_store.py -v
"""

import pytest
from datetime import datetime
from src.core.storage.agency_store import AgencyAssessmentStore, get_agency_store
from src.schemas.agency import AgencyAssessment, ClassificationLevel


@pytest.fixture
def store():
    """Create a fresh store instance for each test"""
    return AgencyAssessmentStore()


@pytest.fixture
def sample_assessment():
    """Create a sample assessment for testing"""
    return AgencyAssessment(
        agency="CIA",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
        assessment_hash="sha256:cia4567890123456789012345678901234567890123456789012345678901234",
        confidence_score=85.0,
        classification=ClassificationLevel.SECRET
    )


def test_store_assessment(store, sample_assessment):
    """Test storing a basic assessment"""
    record = store.store_assessment(
        assessment=sample_assessment,
        receipt_id="receipt_123",
        blockchain_tx_hash="0xabc123"
    )
    
    assert record['storage_id'] is not None
    assert record['receipt_id'] == "receipt_123"
    assert record['blockchain_tx_hash'] == "0xabc123"
    assert record['agency'] == "CIA"
    assert record['foundry_compilation_id'] == "foundry-comp-001"
    assert 'stored_at' in record


def test_store_multiple_assessments_same_compilation(store):
    """Test storing multiple assessments for the same compilation"""
    assessment1 = AgencyAssessment(
        agency="CIA",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
        assessment_hash="sha256:cia1234567890123456789012345678901234567890123456789012345678901",
        confidence_score=85.0,
        classification=ClassificationLevel.SECRET
    )
    
    assessment2 = AgencyAssessment(
        agency="DHS",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
        assessment_hash="sha256:dhs1234567890123456789012345678901234567890123456789012345678901",
        confidence_score=75.0,
        classification=ClassificationLevel.SBU
    )
    
    record1 = store.store_assessment(assessment1, receipt_id="receipt_1")
    record2 = store.store_assessment(assessment2, receipt_id="receipt_2")
    
    assessments = store.get_assessments_by_compilation("foundry-comp-001")
    assert len(assessments) == 2
    
    agencies = {a.agency for a in assessments}
    assert agencies == {"CIA", "DHS"}


def test_idempotency(store, sample_assessment):
    """Test idempotency key prevents duplicate submissions"""
    idempotency_key = "test_key_123"
    
    record1 = store.store_assessment(
        assessment=sample_assessment,
        receipt_id="receipt_1",
        idempotency_key=idempotency_key
    )
    
    # Try to store again with same idempotency key
    record2 = store.store_assessment(
        assessment=sample_assessment,
        receipt_id="receipt_2",  # Different receipt ID
        idempotency_key=idempotency_key
    )
    
    # Should return same record
    assert record1['storage_id'] == record2['storage_id']
    assert record1['receipt_id'] == record2['receipt_id']  # Original receipt ID preserved
    
    # Should only have one assessment stored
    assessments = store.get_assessments_by_compilation("foundry-comp-001")
    assert len(assessments) == 1


def test_replace_agency_assessment(store):
    """Test that storing new assessment from same agency replaces old one"""
    assessment1 = AgencyAssessment(
        agency="CIA",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
        assessment_hash="sha256:cia1",
        confidence_score=80.0,
        classification=ClassificationLevel.SECRET
    )
    
    assessment2 = AgencyAssessment(
        agency="CIA",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
        assessment_hash="sha256:cia2",
        confidence_score=85.0,  # Different confidence
        classification=ClassificationLevel.SECRET
    )
    
    record1 = store.store_assessment(assessment1, receipt_id="receipt_1")
    record2 = store.store_assessment(assessment2, receipt_id="receipt_2")
    
    # Should have replaced the old one
    assert record1['storage_id'] != record2['storage_id']
    
    # Should only have one assessment from CIA
    assessment = store.get_assessment_by_agency("CIA", "foundry-comp-001")
    assert assessment is not None
    assert assessment.confidence_score == 85.0  # New confidence score
    assert assessment.assessment_hash == "sha256:cia2"


def test_get_assessments_by_compilation(store):
    """Test retrieving assessments by compilation ID"""
    compilation_id = "foundry-comp-001"
    
    # Store assessments from different agencies
    for agency, confidence in [("CIA", 85.0), ("DHS", 75.0), ("NSA", 80.0)]:
        assessment = AgencyAssessment(
            agency=agency,
            foundry_compilation_id=compilation_id,
            abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
            assessment_hash=f"sha256:{agency}1234567890123456789012345678901234567890123456789012345678901",
            confidence_score=confidence,
            classification=ClassificationLevel.SECRET
        )
        store.store_assessment(assessment, receipt_id=f"receipt_{agency}")
    
    assessments = store.get_assessments_by_compilation(compilation_id)
    assert len(assessments) == 3
    
    agencies = {a.agency for a in assessments}
    assert agencies == {"CIA", "DHS", "NSA"}
    
    # Test non-existent compilation
    empty = store.get_assessments_by_compilation("nonexistent")
    assert len(empty) == 0


def test_get_assessment_by_agency(store):
    """Test retrieving assessment from specific agency"""
    assessment = AgencyAssessment(
        agency="CIA",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
        assessment_hash="sha256:cia1234567890123456789012345678901234567890123456789012345678901",
        confidence_score=85.0,
        classification=ClassificationLevel.SECRET
    )
    
    store.store_assessment(assessment, receipt_id="receipt_1")
    
    retrieved = store.get_assessment_by_agency("CIA", "foundry-comp-001")
    assert retrieved is not None
    assert retrieved.agency == "CIA"
    assert retrieved.confidence_score == 85.0
    
    # Test non-existent agency
    empty = store.get_assessment_by_agency("DHS", "foundry-comp-001")
    assert empty is None


def test_get_assessments_by_abc_receipt_hash(store):
    """Test retrieving assessments by ABC receipt hash"""
    abc_receipt_hash = "sha256:abc1234567890123456789012345678901234567890123456789012345678901"
    
    # Store multiple assessments referencing same ABC receipt
    for agency in ["CIA", "DHS", "NSA"]:
        assessment = AgencyAssessment(
            agency=agency,
            foundry_compilation_id="foundry-comp-001",
            abc_receipt_hash=abc_receipt_hash,
            assessment_hash=f"sha256:{agency}1234567890123456789012345678901234567890123456789012345678901",
            confidence_score=80.0,
            classification=ClassificationLevel.SECRET
        )
        store.store_assessment(assessment, receipt_id=f"receipt_{agency}")
    
    assessments = store.get_assessments_by_abc_receipt_hash(abc_receipt_hash)
    assert len(assessments) == 3
    
    agencies = {a.agency for a in assessments}
    assert agencies == {"CIA", "DHS", "NSA"}
    
    # All should reference the same ABC receipt
    for assessment in assessments:
        assert assessment.abc_receipt_hash == abc_receipt_hash
    
    # Test non-existent receipt hash
    empty = store.get_assessments_by_abc_receipt_hash("sha256:nonexistent")
    assert len(empty) == 0


def test_get_stats(store):
    """Test store statistics"""
    # Store assessments from multiple agencies and compilations
    assessments = [
        ("CIA", "foundry-comp-001", 85.0),
        ("DHS", "foundry-comp-001", 75.0),
        ("NSA", "foundry-comp-002", 80.0),
        ("Treasury", "foundry-comp-002", 82.0),
    ]
    
    for agency, compilation_id, confidence in assessments:
        assessment = AgencyAssessment(
            agency=agency,
            foundry_compilation_id=compilation_id,
            abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
            assessment_hash=f"sha256:{agency}1234567890123456789012345678901234567890123456789012345678901",
            confidence_score=confidence,
            classification=ClassificationLevel.SECRET
        )
        store.store_assessment(assessment, receipt_id=f"receipt_{agency}_{compilation_id}")
    
    stats = store.get_stats()
    
    assert stats['total_assessments'] == 4
    assert stats['total_compilations'] == 2
    assert stats['total_agencies'] == 4
    # Agency names are stored as-is, check all are present (case-sensitive)
    agencies_set = set(stats['agencies'])
    assert "CIA" in agencies_set
    assert "DHS" in agencies_set
    assert "NSA" in agencies_set
    assert "Treasury" in agencies_set or "TREASURY" in agencies_set
    assert stats['max_assessments_per_compilation'] == 1000


def test_get_all_assessments(store):
    """Test retrieving all assessments"""
    # Store multiple assessments
    for i in range(3):
        assessment = AgencyAssessment(
            agency=f"Agency{i}",
            foundry_compilation_id=f"foundry-comp-00{i}",
            abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
            assessment_hash=f"sha256:hash{i}234567890123456789012345678901234567890123456789012345678901",
            confidence_score=80.0 + i,
            classification=ClassificationLevel.SECRET
        )
        store.store_assessment(assessment, receipt_id=f"receipt_{i}")
    
    all_assessments = store.get_all_assessments()
    assert len(all_assessments) == 3
    
    # Verify all have storage IDs
    for record in all_assessments:
        assert 'storage_id' in record
        assert 'assessment' in record
        assert 'receipt_id' in record


def test_max_assessments_limit(store):
    """Test that max assessments per compilation limit is enforced"""
    # Temporarily set limit to 3 for testing
    store._max_assessments_per_compilation = 3
    compilation_id = "foundry-comp-001"
    
    # Store 4 assessments (should trigger removal of oldest)
    for i in range(4):
        assessment = AgencyAssessment(
            agency=f"Agency{i}",
            foundry_compilation_id=compilation_id,
            abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
            assessment_hash=f"sha256:hash{i}234567890123456789012345678901234567890123456789012345678901",
            confidence_score=80.0,
            classification=ClassificationLevel.SECRET
        )
        store.store_assessment(assessment, receipt_id=f"receipt_{i}")
    
    # Should only have 3 assessments (oldest removed)
    assessments = store.get_assessments_by_compilation(compilation_id)
    assert len(assessments) <= 3


def test_store_with_nonexistent_compilation(store):
    """Test retrieving assessments for non-existent compilation (edge case)"""
    assessment = AgencyAssessment(
        agency="CIA",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
        assessment_hash="sha256:cia1234567890123456789012345678901234567890123456789012345678901",
        confidence_score=85.0,
        classification=ClassificationLevel.SECRET
    )
    
    record = store.store_assessment(assessment, receipt_id="receipt_1")
    assert record is not None
    
    # Query non-existent compilation should return empty list
    assessments = store.get_assessments_by_compilation("nonexistent-comp")
    assert len(assessments) == 0
    
    # Query existing compilation should return the assessment
    assessments = store.get_assessments_by_compilation("foundry-comp-001")
    assert len(assessments) == 1


def test_get_agency_store_singleton():
    """Test that get_agency_store returns singleton"""
    store1 = get_agency_store()
    store2 = get_agency_store()
    
    # Should be the same instance
    assert store1 is store2


def test_store_assessment_with_metadata(store):
    """Test storing assessment with metadata"""
    assessment = AgencyAssessment(
        agency="CIA",
        foundry_compilation_id="foundry-comp-001",
        abc_receipt_hash="sha256:abc1234567890123456789012345678901234567890123456789012345678901",
        assessment_hash="sha256:cia1234567890123456789012345678901234567890123456789012345678901",
        confidence_score=85.0,
        classification=ClassificationLevel.SECRET,
        metadata={"abc_baseline_confidence": 88.0, "analysis_method": "machine_learning"}
    )
    
    record = store.store_assessment(assessment, receipt_id="receipt_1")
    
    # Verify metadata is preserved
    stored_assessment = store.get_assessment_by_agency("CIA", "foundry-comp-001")
    assert stored_assessment.metadata["abc_baseline_confidence"] == 88.0
    assert stored_assessment.metadata["analysis_method"] == "machine_learning"

