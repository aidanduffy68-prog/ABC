"""
Test Suite for Agency API Routes
Tests agency assessment submission and consensus endpoints

Run with: pytest tests/api/test_agency_routes.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.api import app
from src.schemas.agency import AgencyAssessment, ClassificationLevel


@pytest.fixture
def client():
    """Test client for API"""
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication to bypass require_auth decorator"""
    return lambda x: x


@pytest.fixture
def sample_assessment():
    """Sample agency assessment for testing"""
    return {
        "agency": "CIA",
        "foundry_compilation_id": "foundry-comp-2025-12-15-001",
        "abc_receipt_hash": "sha256:abc123def456",
        "assessment_hash": "sha256:cia789xyz",
        "confidence_score": 85.2,
        "classification": "SECRET",
        "metadata": {"source": "test"}
    }


@pytest.fixture
def reset_store():
    """Reset agency store before each test"""
    from src.core.storage.agency_store import get_agency_store
    store = get_agency_store()
    # Clear all data
    store._assessments.clear()
    store._assessments_by_compilation.clear()
    store._assessments_by_receipt.clear()
    store._assessments_by_agency.clear()
    yield
    # Cleanup after test
    store._assessments.clear()
    store._assessments_by_compilation.clear()
    store._assessments_by_receipt.clear()
    store._assessments_by_agency.clear()


def test_submit_agency_assessment(client, mock_auth, sample_assessment, reset_store):
    """Test agency assessment submission"""
    with patch('src.api.routes.agency.require_auth', mock_auth), \
         patch('src.api.routes.agency.receipt_gen') as mock_receipt:
        
        # Mock receipt generator
        mock_receipt_obj = MagicMock()
        mock_receipt_obj.receipt_id = "receipt-001"
        mock_receipt_obj.intelligence_hash = "sha256:receipt123"
        mock_receipt_obj.timestamp = datetime.now().isoformat()
        mock_receipt_obj.tx_hash = "0xabc123"
        mock_receipt.generate_receipt.return_value = mock_receipt_obj
        
        response = client.post(
            "/api/v1/agency/assessment",
            json=sample_assessment,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["status"] == "submitted"
        assert data["agency"] == "CIA"
        assert data["foundry_compilation_id"] == "foundry-comp-2025-12-15-001"
        assert "blockchain_receipt" in data
        assert "storage_id" in data
        assert "idempotency_key" in data


def test_submit_agency_assessment_idempotency(client, mock_auth, sample_assessment, reset_store):
    """Test idempotency - submitting same assessment twice"""
    with patch('src.api.routes.agency.require_auth', mock_auth), \
         patch('src.api.routes.agency.receipt_gen') as mock_receipt:
        
        # Mock receipt generator
        mock_receipt_obj = MagicMock()
        mock_receipt_obj.receipt_id = "receipt-001"
        mock_receipt_obj.intelligence_hash = "sha256:receipt123"
        mock_receipt_obj.timestamp = datetime.now().isoformat()
        mock_receipt_obj.tx_hash = "0xabc123"
        mock_receipt.generate_receipt.return_value = mock_receipt_obj
        
        # First submission
        response1 = client.post(
            "/api/v1/agency/assessment",
            json=sample_assessment,
            headers={
                "Authorization": "Bearer test_token",
                "Idempotency-Key": "test-key-123"
            }
        )
        assert response1.status_code == 201
        
        # Second submission with same idempotency key
        response2 = client.post(
            "/api/v1/agency/assessment",
            json=sample_assessment,
            headers={
                "Authorization": "Bearer test_token",
                "Idempotency-Key": "test-key-123"
            }
        )
        assert response2.status_code == 201
        data2 = response2.json()
        assert data2["status"] == "duplicate"
        assert "duplicate" in data2["message"].lower()


def test_submit_agency_assessment_validation(client, mock_auth):
    """Test validation errors on bad input"""
    with patch('src.api.routes.agency.require_auth', mock_auth):
        
        # Missing required field
        bad_assessment = {
            "agency": "CIA",
            # Missing foundry_compilation_id
            "abc_receipt_hash": "sha256:abc123",
            "assessment_hash": "sha256:cia456",
            "confidence_score": 85.2,
            "classification": "SECRET"
        }
        
        response = client.post(
            "/api/v1/agency/assessment",
            json=bad_assessment,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422  # Validation error


def test_submit_agency_assessment_invalid_confidence(client, mock_auth):
    """Test validation error for invalid confidence score"""
    with patch('src.api.routes.agency.require_auth', mock_auth):
        
        bad_assessment = {
            "agency": "CIA",
            "foundry_compilation_id": "foundry-comp-001",
            "abc_receipt_hash": "sha256:abc123",
            "assessment_hash": "sha256:cia456",
            "confidence_score": 150,  # Invalid: > 100
            "classification": "SECRET"
        }
        
        response = client.post(
            "/api/v1/agency/assessment",
            json=bad_assessment,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422


def test_get_consensus_no_assessments(client, mock_auth, reset_store):
    """Test consensus endpoint when no assessments exist"""
    with patch('src.api.routes.agency.require_auth', mock_auth):
        
        response = client.get(
            "/api/v1/agency/consensus/non-existent-comp",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 404
        assert "No agency assessments found" in response.json()["detail"]


def test_get_consensus_with_assessments(client, mock_auth, sample_assessment, reset_store):
    """Test consensus calculation with multiple assessments"""
    with patch('src.api.routes.agency.require_auth', mock_auth), \
         patch('src.api.routes.agency.receipt_gen') as mock_receipt:
        
        # Mock receipt generator
        mock_receipt_obj = MagicMock()
        mock_receipt_obj.receipt_id = "receipt-001"
        mock_receipt_obj.intelligence_hash = "sha256:receipt123"
        mock_receipt_obj.timestamp = datetime.now().isoformat()
        mock_receipt_obj.tx_hash = "0xabc123"
        mock_receipt.generate_receipt.return_value = mock_receipt_obj
        
        # Submit first assessment (CIA)
        response1 = client.post(
            "/api/v1/agency/assessment",
            json=sample_assessment,
            headers={"Authorization": "Bearer test_token"}
        )
        assert response1.status_code == 201
        
        # Submit second assessment (DHS)
        dhs_assessment = sample_assessment.copy()
        dhs_assessment["agency"] = "DHS"
        dhs_assessment["assessment_hash"] = "sha256:dhs789"
        dhs_assessment["confidence_score"] = 60.1
        dhs_assessment["classification"] = "SBU"
        
        response2 = client.post(
            "/api/v1/agency/assessment",
            json=dhs_assessment,
            headers={"Authorization": "Bearer test_token"}
        )
        assert response2.status_code == 201
        
        # Get consensus
        response = client.get(
            f"/api/v1/agency/consensus/{sample_assessment['foundry_compilation_id']}",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["foundry_compilation_id"] == sample_assessment["foundry_compilation_id"]
        assert "consensus_metrics" in data
        assert "mean_confidence" in data["consensus_metrics"]
        assert "std_deviation" in data["consensus_metrics"]
        assert "outliers" in data["consensus_metrics"]
        assert "recommendation" in data
        assert "verified" in data
        assert len(data["agency_assessments"]) == 2


def test_get_agency_store_stats(client, mock_auth, reset_store):
    """Test store statistics endpoint"""
    with patch('src.api.routes.agency.require_auth', mock_auth):
        
        response = client.get(
            "/api/v1/agency/stats",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "stats" in data
        assert "total_assessments" in data["stats"]
        assert "total_compilations" in data["stats"]
        assert "total_agencies" in data["stats"]


def test_agency_assessment_replace_existing(client, mock_auth, sample_assessment, reset_store):
    """Test that submitting from same agency for same compilation replaces old assessment"""
    with patch('src.api.routes.agency.require_auth', mock_auth), \
         patch('src.api.routes.agency.receipt_gen') as mock_receipt:
        
        # Mock receipt generator
        mock_receipt_obj = MagicMock()
        mock_receipt_obj.receipt_id = "receipt-001"
        mock_receipt_obj.intelligence_hash = "sha256:receipt123"
        mock_receipt_obj.timestamp = datetime.now().isoformat()
        mock_receipt_obj.tx_hash = "0xabc123"
        mock_receipt.generate_receipt.return_value = mock_receipt_obj
        
        # First submission
        response1 = client.post(
            "/api/v1/agency/assessment",
            json=sample_assessment,
            headers={"Authorization": "Bearer test_token"}
        )
        assert response1.status_code == 201
        storage_id1 = response1.json()["storage_id"]
        
        # Second submission from same agency (should replace)
        updated_assessment = sample_assessment.copy()
        updated_assessment["confidence_score"] = 90.0  # Different confidence
        updated_assessment["assessment_hash"] = "sha256:newhash"
        
        response2 = client.post(
            "/api/v1/agency/assessment",
            json=updated_assessment,
            headers={"Authorization": "Bearer test_token"}
        )
        assert response2.status_code == 201
        storage_id2 = response2.json()["storage_id"]
        
        # Should be different storage IDs (old one replaced)
        assert storage_id1 != storage_id2
        
        # Consensus should only have one assessment from CIA
        response = client.get(
            f"/api/v1/agency/consensus/{sample_assessment['foundry_compilation_id']}",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        cia_assessments = [
            a for a in data["agency_assessments"]
            if a["agency"] == "CIA"
        ]
        assert len(cia_assessments) == 1
        assert cia_assessments[0]["confidence_score"] == 90.0

