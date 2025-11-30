#!/usr/bin/env python3
"""
Test Deployment Readiness
Quick validation of core imports and basic functionality
"""

import sys
sys.path.insert(0, '.')

def test_imports():
    """Test core imports"""
    print("Testing core imports...")
    
    try:
        from src.schemas.threat_actor import ThreatActor, ActorType, RiskBand
        print("  ✓ ThreatActor schema")
    except Exception as e:
        print(f"  ✗ ThreatActor schema: {e}")
        return False
    
    try:
        from src.ingestion.validator import IngestionValidator
        print("  ✓ IngestionValidator")
    except Exception as e:
        print(f"  ✗ IngestionValidator: {e}")
        return False
    
    try:
        from src.api.routes.ingest import router
        print("  ✓ API routes")
    except Exception as e:
        print(f"  ✗ API routes: {e}")
        return False
    
    try:
        import src.graph.builder as graph_builder
        print("  ✓ Graph builder module")
    except Exception as e:
        print(f"  ✗ Graph builder: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from src.schemas.threat_actor import ThreatActor, ActorType, RiskBand
        
        # Create a test actor
        actor = ThreatActor(
            actor_id="TEST_001",
            name="Test Actor",
            type=ActorType.WALLET,
            address="0x1234567890123456789012345678901234567890",
            risk_score=0.75,
            risk_band=RiskBand.HIGH
        )
        print("  ✓ ThreatActor creation")
        
        # Test serialization
        actor_dict = actor.to_dict()
        assert 'actor_id' in actor_dict
        print("  ✓ ThreatActor serialization")
        
    except Exception as e:
        print(f"  ✗ ThreatActor functionality: {e}")
        return False
    
    try:
        from src.ingestion.validator import IngestionValidator
        
        validator = IngestionValidator()
        print("  ✓ IngestionValidator instantiation")
        
    except Exception as e:
        print(f"  ✗ IngestionValidator functionality: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("GH Systems ABC - Deployment Readiness Test")
    print("=" * 50)
    
    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if imports_ok and functionality_ok:
        print("✓ All tests passed - System is deployment ready")
        sys.exit(0)
    else:
        print("✗ Some tests failed - Review errors above")
        sys.exit(1)

