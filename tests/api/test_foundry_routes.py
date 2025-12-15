"""
Test Suite for Foundry API Routes
Tests Foundry-related API endpoints

Run with: pytest tests/api/test_foundry_routes.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the app directly from src.api
from src.api import app


@pytest.fixture
def client():
    """Test client for API"""
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication to bypass require_auth decorator"""
    # Patch the require_auth decorator to bypass authentication
    def mock_require_auth(func):
        return func
    return mock_require_auth


def test_verify_foundry_compilation_endpoint(client):
    """Test /api/v1/foundry/verify endpoint"""
    # Mock the authentication and foundry connector
    with patch('src.api.routes.foundry.require_auth', lambda x: x), \
         patch('src.api.routes.foundry.foundry_connector') as mock_connector, \
         patch('src.api.routes.foundry.compilation_engine') as mock_engine, \
         patch('src.api.routes.foundry.data_mapper') as mock_mapper, \
         patch('src.api.routes.foundry.receipt_generator') as mock_receipt:
        
        # Setup mocks
        mock_compilation = {
            "compilation_id": "foundry-comp-2025-12-15-001",
            "data_hash": "sha256:abc123...",
            "timestamp": "2025-12-15T17:00:00Z",
            "sources": [{"provider": "chainalysis"}],
            "compiled_data": {
                "threat_actors": [{"id": "actor_001", "name": "Test Actor"}]
            },
            "classification": "SBU"
        }
        
        mock_connector.get_compilation.return_value = mock_compilation
        mock_connector.verify_compilation_hash.return_value = True
        
        # Mock compilation engine
        mock_compiled_intelligence = MagicMock()
        mock_compiled_intelligence.confidence_score = 88.4
        mock_compiled_intelligence.compilation_time_ms = 342.15
        mock_compiled_intelligence.targeting_package = {
            "risk_assessment": {"threat_level": "HIGH"}
        }
        mock_compiled_intelligence.compilation_id = "abc-comp-001"
        mock_compiled_intelligence.behavioral_signature = MagicMock()
        mock_compiled_intelligence.behavioral_signature.__dict__ = {}
        mock_compiled_intelligence.coordination_network = {}
        mock_compiled_intelligence.threat_forecast = None
        mock_engine.compile_intelligence.return_value = mock_compiled_intelligence
        
        # Mock data mapper
        mock_mapper.map_to_abc_format.return_value = {
            "raw_intelligence": [],
            "transaction_data": [],
            "network_data": {}
        }
        
        # Mock receipt generator
        mock_receipt_obj = MagicMock()
        mock_receipt_obj.receipt_id = "receipt-001"
        mock_receipt_obj.tx_hash = "0x789..."
        mock_receipt.generate_receipt.return_value = mock_receipt_obj
        mock_receipt.commit_to_blockchain.return_value = "0x789..."
        
        # Make request (POST with query parameters)
        response = client.post(
            "/api/v1/foundry/verify?foundry_compilation_id=foundry-comp-2025-12-15-001&blockchain=bitcoin",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert "foundry_compilation_id" in data
        assert "abc_analysis" in data
        assert "blockchain_receipt" in data
        assert data["foundry_verified"] == True


def test_verify_receipt_chain_endpoint(client):
    """Test /api/v1/foundry/verify/{receipt_hash} endpoint"""
    # This is a public endpoint, no auth needed
    response = client.get("/api/v1/foundry/verify/sha256:abc123...")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "foundry_compilation" in data
    assert "abc_analysis" in data
    assert "chain_verified" in data
    assert "verification_timestamp" in data


def test_foundry_status_endpoint(client):
    """Test /api/v1/foundry/status endpoint"""
    response = client.get("/api/v1/foundry/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "enabled" in data
    assert "timestamp" in data


def test_verify_foundry_compilation_not_found(client):
    """Test /api/v1/foundry/verify returns 404 for non-existent compilation"""
    with patch('src.api.routes.foundry.require_auth', lambda x: x), \
         patch('src.api.routes.foundry.foundry_connector') as mock_connector:
        
        mock_connector.get_compilation.return_value = None
        
        response = client.post(
            "/api/v1/foundry/verify?foundry_compilation_id=non-existent-comp&blockchain=bitcoin",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 404


def test_verify_foundry_compilation_hash_mismatch(client):
    """Test /api/v1/foundry/verify returns 400 for hash mismatch"""
    with patch('src.api.routes.foundry.require_auth', lambda x: x), \
         patch('src.api.routes.foundry.foundry_connector') as mock_connector:
        
        mock_compilation = {
            "compilation_id": "foundry-comp-001",
            "data_hash": "sha256:abc123...",
            "timestamp": "2025-12-15T17:00:00Z",
            "sources": [],
            "compiled_data": {}
        }
        
        mock_connector.get_compilation.return_value = mock_compilation
        mock_connector.verify_compilation_hash.return_value = False
        
        response = client.post(
            "/api/v1/foundry/verify?foundry_compilation_id=foundry-comp-001&blockchain=bitcoin",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "Hash verification failed" in response.json()["detail"]


@pytest.mark.skip(reason="Rate limiting test requires specific setup - test manually")
def test_rate_limiting(client):
    """Test rate limiting works"""
    # Note: This test is marked as skip because it requires making 101 requests
    # and may be flaky in test environments. Test manually or with proper rate limit mocking.
    
    # Make 101 requests (limit is 100/min)
    for i in range(101):
        response = client.post(
            f"/api/v1/foundry/verify?foundry_compilation_id=test-{i}&blockchain=bitcoin",
            headers={"Authorization": "Bearer test_token"}
        )
    
    # Last request should be rate limited
    assert response.status_code == 429  # Too Many Requests

