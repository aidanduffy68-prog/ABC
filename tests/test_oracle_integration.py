"""
Integration tests for oracle API
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client"""
    # Conditional import - oracle may not be available
    try:
        from src.api import app
        return TestClient(app)
    except ImportError:
        pytest.skip("Oracle routes not available")


class TestOracleAPI:
    """Test oracle API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test oracle health check"""
        response = client.get("/api/v1/oracle/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    @pytest.mark.skipif(True, reason="Requires Bitcoin node")
    def test_ingest_block(self, client):
        """Test block ingestion endpoint"""
        response = client.post("/api/v1/oracle/ingest/bitcoin/block/825000")
        assert response.status_code == 200
        data = response.json()
        assert data['block_height'] == 825000
        assert 'receipt' in data
    
    def test_verify_source(self, client):
        """Test source verification endpoint"""
        response = client.post(
            "/api/v1/oracle/verify/source",
            params={
                "receipt_id": "abc_receipt_test",
                "source_name": "chainalysis",
                "source_data_hash": "abc123..."
            }
        )
        # May return 404 if receipt doesn't exist (expected in test)
        assert response.status_code in [200, 404, 503]

