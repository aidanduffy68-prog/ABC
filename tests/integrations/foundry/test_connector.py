"""
Test Suite for Foundry Connector
Tests Foundry data export and ingestion connector functionality

Run with: pytest tests/integrations/foundry/test_connector.py -v
"""

import pytest
import json
import hashlib
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.integrations.foundry.connector import FoundryDataExportConnector


@pytest.fixture
def foundry_connector():
    """Fixture for FoundryDataExportConnector with mock credentials"""
    return FoundryDataExportConnector(
        foundry_url="https://foundry.example.com",
        api_token="test_token_123"
    )


@pytest.fixture
def foundry_connector_disabled():
    """Fixture for FoundryDataExportConnector without credentials"""
    return FoundryDataExportConnector()


def test_connector_initialization(foundry_connector):
    """Test connector initializes correctly with credentials"""
    assert foundry_connector.foundry_url == "https://foundry.example.com"
    assert foundry_connector.api_token == "test_token_123"
    assert foundry_connector.enabled == True


def test_connector_disabled_without_credentials(foundry_connector_disabled):
    """Test connector gracefully handles missing credentials"""
    assert foundry_connector_disabled.enabled == False
    
    result = foundry_connector_disabled.push_compilation({"test": "data"})
    assert result["status"] == "disabled"


def test_get_compilation(foundry_connector):
    """Test fetching Foundry compilation"""
    # Mock compilation data
    compilation_id = "foundry-comp-2025-12-15-001"
    compiled_data = {"threat_actors": [{"id": "actor_001", "name": "Test Actor"}]}
    
    # Calculate hash for mock
    serialized = json.dumps(compiled_data, sort_keys=True, ensure_ascii=False)
    data_hash = f"sha256:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"
    
    mock_compilation = {
        "compilation_id": compilation_id,
        "data_hash": data_hash,
        "timestamp": "2025-12-15T17:00:00Z",
        "sources": [
            {"provider": "chainalysis", "dataset": "sanctions_list_v2"},
            {"provider": "trm_labs", "dataset": "threat_actors_q4"}
        ],
        "compiled_data": compiled_data
    }
    
    # Mock the session.get call
    mock_response = Mock()
    mock_response.json.return_value = mock_compilation
    mock_response.raise_for_status = Mock()
    mock_response.status_code = 200
    
    with patch.object(foundry_connector.session, 'get', return_value=mock_response):
        result = foundry_connector.get_compilation(compilation_id)
        
        assert result["compilation_id"] == compilation_id
        assert "data_hash" in result
        assert "compiled_data" in result
        assert "sources" in result


def test_get_compilation_disabled(foundry_connector_disabled):
    """Test get_compilation returns mock data when connector is disabled"""
    result = foundry_connector_disabled.get_compilation("test-comp-001")
    
    assert result["compilation_id"] == "test-comp-001"
    assert "data_hash" in result
    assert "compiled_data" in result


def test_verify_compilation_hash(foundry_connector):
    """Test hash verification"""
    # Create compilation with valid hash
    compiled_data = {"test": "data", "value": 123}
    serialized = json.dumps(compiled_data, sort_keys=True, ensure_ascii=False)
    data_hash = f"sha256:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"
    
    compilation = {
        "data_hash": data_hash,
        "compiled_data": compiled_data
    }
    
    # Should verify hash matches content
    result = foundry_connector.verify_compilation_hash(compilation)
    assert result == True


def test_verify_compilation_hash_mismatch(foundry_connector):
    """Test hash verification detects mismatches"""
    compiled_data = {"test": "data"}
    compilation = {
        "data_hash": "sha256:wronghash123",
        "compiled_data": compiled_data
    }
    
    # Should detect hash mismatch
    result = foundry_connector.verify_compilation_hash(compilation)
    assert result == False


def test_verify_compilation_hash_missing_fields(foundry_connector):
    """Test hash verification handles missing fields"""
    # Missing compiled_data
    compilation1 = {"data_hash": "sha256:abc123"}
    result1 = foundry_connector.verify_compilation_hash(compilation1)
    assert result1 == False
    
    # Missing data_hash
    compilation2 = {"compiled_data": {"test": "data"}}
    result2 = foundry_connector.verify_compilation_hash(compilation2)
    assert result2 == False


def test_list_recent_compilations(foundry_connector):
    """Test listing recent compilations"""
    # Mock API response
    mock_compilations = [
        {
            "compilation_id": "foundry-comp-001",
            "data_hash": "sha256:abc123",
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "compiled_data": {}
        }
    ]
    
    mock_response = Mock()
    mock_response.json.return_value = {"compilations": mock_compilations}
    mock_response.raise_for_status = Mock()
    
    with patch.object(foundry_connector.session, 'get', return_value=mock_response):
        result = foundry_connector.list_recent_compilations(hours=24, limit=10)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["compilation_id"] == "foundry-comp-001"


def test_list_recent_compilations_disabled(foundry_connector_disabled):
    """Test list_recent_compilations returns mock data when disabled"""
    result = foundry_connector_disabled.list_recent_compilations(hours=24, limit=5)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all("compilation_id" in comp for comp in result)


def test_push_compilation(foundry_connector):
    """Test pushing compilation to Foundry"""
    compilation_data = {
        "compilation_id": "abc-comp-001",
        "actor_id": "actor_001",
        "confidence_score": 0.85
    }
    
    result = foundry_connector.push_compilation(compilation_data)
    
    assert result["status"] == "success"
    assert result["record_id"] == "abc-comp-001"
    assert "timestamp" in result


def test_push_compilation_disabled(foundry_connector_disabled):
    """Test push_compilation returns disabled status when connector is disabled"""
    result = foundry_connector_disabled.push_compilation({"test": "data"})
    
    assert result["status"] == "disabled"
    assert "message" in result


def test_push_batch(foundry_connector):
    """Test pushing batch of compilations"""
    compilations = [
        {"compilation_id": "abc-comp-001", "confidence_score": 0.85},
        {"compilation_id": "abc-comp-002", "confidence_score": 0.90}
    ]
    
    result = foundry_connector.push_batch(compilations)
    
    assert result["status"] == "success"
    assert result["records_pushed"] == 2
    assert "timestamp" in result

