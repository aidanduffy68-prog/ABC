#!/usr/bin/env python3
"""
Test Validation Agents
Test suite for Chaos Agents-inspired validation system

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.validation.agent_hub import (
    ValidationAgentHub,
    create_default_agent_hub
)
from src.core.validation.base_agent import (
    RangeValidationAgent,
    ExpirationWindowAgent,
    CircuitBreakerAgent,
    MinimumDelayAgent
)


def test_range_validation():
    """Test range validation agent"""
    print("🧪 Testing Range Validation Agent")
    
    agent = RangeValidationAgent(
        agent_id="test_range",
        field_name="risk_score",
        min_value=0.0,
        max_value=100.0
    )
    
    # Valid range
    result = agent.validate(
        {"risk_score": 85.0, "actor_id": "test"},
        update_type="risk_score"
    )
    assert result.is_valid, f"Should accept valid range: {result.reason}"
    print("   ✅ Valid range accepted")
    
    # Below minimum
    result = agent.validate(
        {"risk_score": -10.0, "actor_id": "test"},
        update_type="risk_score"
    )
    assert not result.is_valid, "Should reject below minimum"
    print("   ✅ Below minimum rejected")
    
    # Above maximum
    result = agent.validate(
        {"risk_score": 150.0, "actor_id": "test"},
        update_type="risk_score"
    )
    assert not result.is_valid, "Should reject above maximum"
    print("   ✅ Above maximum rejected")
    
    print("   ✅ Range validation tests passed\n")


def test_expiration_window():
    """Test expiration window agent"""
    print("🧪 Testing Expiration Window Agent")
    
    agent = ExpirationWindowAgent(
        agent_id="test_expiration",
        max_age_seconds=3600  # 1 hour
    )
    
    # Fresh intelligence
    result = agent.validate(
        {
            "timestamp": datetime.now().isoformat(),
            "actor_id": "test"
        },
        update_type="threat_assessment"
    )
    assert result.is_valid, f"Should accept fresh intelligence: {result.reason}"
    print("   ✅ Fresh intelligence accepted")
    
    # Expired intelligence
    old_timestamp = (datetime.now() - timedelta(hours=2)).isoformat()
    result = agent.validate(
        {
            "timestamp": old_timestamp,
            "actor_id": "test"
        },
        update_type="threat_assessment"
    )
    assert not result.is_valid, "Should reject expired intelligence"
    print("   ✅ Expired intelligence rejected")
    
    print("   ✅ Expiration window tests passed\n")


def test_circuit_breaker():
    """Test circuit breaker agent"""
    print("🧪 Testing Circuit Breaker Agent")
    
    agent = CircuitBreakerAgent(
        agent_id="test_circuit_breaker",
        max_change_percent=50.0
    )
    
    # First update (no current state)
    result = agent.validate(
        {"risk_score": 85.0, "actor_id": "test"},
        update_type="risk_score",
        current_state=None
    )
    assert result.is_valid, "Should accept first update"
    print("   ✅ First update accepted")
    
    # Small change
    result = agent.validate(
        {"risk_score": 90.0, "actor_id": "test"},
        update_type="risk_score",
        current_state={"risk_score": 85.0}
    )
    assert result.is_valid, "Should accept small change"
    print("   ✅ Small change accepted")
    
    # Large change (should trigger circuit breaker)
    result = agent.validate(
        {"risk_score": 95.0, "actor_id": "test"},
        update_type="risk_score",
        current_state={"risk_score": 30.0}  # 65 point change = 217% change
    )
    assert not result.is_valid, "Should reject large change"
    print("   ✅ Large change rejected (circuit breaker triggered)")
    
    print("   ✅ Circuit breaker tests passed\n")


def test_minimum_delay():
    """Test minimum delay agent"""
    print("🧪 Testing Minimum Delay Agent")
    
    agent = MinimumDelayAgent(
        agent_id="test_min_delay",
        min_delay_seconds=60  # 1 minute
    )
    
    # First update
    result = agent.validate(
        {"actor_id": "test_actor", "timestamp": datetime.now().isoformat()},
        update_type="risk_score"
    )
    assert result.is_valid, "Should accept first update"
    print("   ✅ First update accepted")
    
    # Immediate second update (should be rejected)
    result = agent.validate(
        {"actor_id": "test_actor", "timestamp": datetime.now().isoformat()},
        update_type="risk_score"
    )
    assert not result.is_valid, "Should reject immediate second update"
    print("   ✅ Immediate second update rejected")
    
    print("   ✅ Minimum delay tests passed\n")


def test_agent_hub():
    """Test agent hub integration"""
    print("🧪 Testing Agent Hub Integration")
    
    hub = create_default_agent_hub()
    
    # Valid intelligence update
    intelligence_data = {
        "actor_id": "test_actor",
        "timestamp": datetime.now().isoformat(),
        "risk_score": 85.0
    }
    
    result = hub.validate_update(
        intelligence_data=intelligence_data,
        update_type="risk_score"
    )
    assert result.is_valid, f"Should accept valid update: {result.reason}"
    print("   ✅ Valid update accepted by hub")
    
    # Invalid update (expired timestamp)
    old_timestamp = (datetime.now() - timedelta(hours=2)).isoformat()
    intelligence_data["timestamp"] = old_timestamp
    result = hub.validate_update(
        intelligence_data=intelligence_data,
        update_type="risk_score"
    )
    assert not result.is_valid, "Should reject expired update"
    print("   ✅ Expired update rejected by hub")
    
    # Check hub status
    status = hub.get_hub_status()
    assert status["total_agents"] == 3, "Should have 3 default agents (expiration, circuit breaker, min delay)"
    print(f"   ✅ Hub status: {status['total_agents']} agents registered")
    
    print("   ✅ Agent hub tests passed\n")


def test_red_team_scenarios():
    """Test red team attack scenarios"""
    print("🧪 Testing Red Team Attack Scenarios")
    
    hub = create_default_agent_hub()
    
    # Scenario 1: Rapid-fire updates (should be blocked by minimum delay)
    print("   🔴 Scenario 1: Rapid-fire updates")
    for i in range(3):
        intelligence_data = {
            "actor_id": "attack_actor",
            "timestamp": datetime.now().isoformat(),
            "risk_score": 50.0 + i
        }
        result = hub.validate_update(
            intelligence_data=intelligence_data,
            update_type="risk_score"
        )
        if i == 0:
            assert result.is_valid, "First update should pass"
        else:
            # Subsequent updates should be blocked by minimum delay
            if not result.is_valid:
                print(f"      ✅ Update {i+1} blocked: {result.reason}")
    
    # Scenario 2: Extreme risk score change (should be blocked by circuit breaker)
    print("   🔴 Scenario 2: Extreme risk score change")
    intelligence_data = {
        "actor_id": "attack_actor_2",
        "timestamp": datetime.now().isoformat(),
        "risk_score": 95.0
    }
    result = hub.validate_update(
        intelligence_data=intelligence_data,
        update_type="risk_score",
        current_state={"risk_score": 10.0}  # 850% change
    )
    assert not result.is_valid, "Extreme change should be blocked"
    print(f"      ✅ Extreme change blocked: {result.reason}")
    
    # Scenario 3: Expired intelligence (should be blocked)
    print("   🔴 Scenario 3: Expired intelligence")
    old_timestamp = (datetime.now() - timedelta(hours=2)).isoformat()
    intelligence_data = {
        "actor_id": "attack_actor_3",
        "timestamp": old_timestamp,
        "risk_score": 85.0
    }
    result = hub.validate_update(
        intelligence_data=intelligence_data,
        update_type="threat_assessment"
    )
    assert not result.is_valid, "Expired intelligence should be blocked"
    print(f"      ✅ Expired intelligence blocked: {result.reason}")
    
    print("   ✅ Red team scenarios passed\n")


def main():
    """Run all validation agent tests"""
    print("=" * 60)
    print("🔬 VALIDATION AGENTS TEST SUITE")
    print("Inspired by Chaos Labs' Chaos Agents Architecture")
    print("=" * 60)
    print()
    
    try:
        test_range_validation()
        test_expiration_window()
        test_circuit_breaker()
        test_minimum_delay()
        test_agent_hub()
        test_red_team_scenarios()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

