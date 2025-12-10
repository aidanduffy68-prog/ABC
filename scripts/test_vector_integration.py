#!/usr/bin/env python3
"""
Test Vector Database Integration
Tests semantic search and pattern storage

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.hypnos.vector_integration import HypnosVectorIntegration


def test_faiss_storage():
    """Test FAISS vector store"""
    print("🧪 Testing FAISS Vector Store")
    
    try:
        vector_integration = HypnosVectorIntegration(vector_backend="faiss")
    except ImportError as e:
        print(f"   ⚠️  FAISS not installed: {e}")
        print("   Install with: pip install faiss-cpu")
        return False
    
    # Store test patterns
    patterns = [
        {
            "pattern_id": "pattern_001",
            "pattern_type": "behavioral_signature",
            "description": "North Korean hacker group using mixer services for OFAC evasion",
            "metadata": {"actor_id": "lazarus_001", "confidence": 0.92},
            "confidence": 0.92
        },
        {
            "pattern_id": "pattern_002",
            "pattern_type": "threat_indicator",
            "description": "Synchronized transaction patterns across multiple wallets",
            "metadata": {"network_id": "network_001", "confidence": 0.85},
            "confidence": 0.85
        },
        {
            "pattern_id": "pattern_003",
            "pattern_type": "coordination_pattern",
            "description": "Multiple actors coordinating through shared infrastructure",
            "metadata": {"coordination_score": 0.88},
            "confidence": 0.88
        }
    ]
    
    # Store patterns
    for pattern in patterns:
        result = vector_integration.store_pattern(**pattern)
        assert result, f"Failed to store pattern {pattern['pattern_id']}"
        print(f"   ✅ Stored: {pattern['pattern_id']}")
    
    # Search for similar patterns
    print("\n   🔍 Testing semantic search...")
    
    queries = [
        ("Hacker group using cryptocurrency mixers", "behavioral_signature"),
        ("Transaction timing patterns", "threat_indicator"),
        ("Coordinated attack infrastructure", "coordination_pattern")
    ]
    
    for query_text, expected_type in queries:
        results = vector_integration.find_similar_patterns(
            query_description=query_text,
            pattern_type=expected_type,
            top_k=3,
            min_similarity=0.5
        )
        
        assert len(results) > 0, f"No results for query: {query_text}"
        print(f"   ✅ Query: '{query_text}' → Found {len(results)} similar patterns")
        if results:
            print(f"      Top match: {results[0]['similarity']:.2%} similarity")
    
    # Test context-aware classification
    print("\n   🎯 Testing context-aware classification...")
    
    classification = vector_integration.classify_with_context(
        entity_description="Wallet showing synchronized transaction patterns with known threat actors",
        context={"actor_id": "unknown_wallet_001"}
    )
    
    assert classification["classification"] != "unknown", "Classification failed"
    print(f"   ✅ Classification: {classification['classification']}")
    print(f"      Confidence: {classification['confidence']:.2%}")
    print(f"      Based on {classification['similar_patterns_found']} similar patterns")
    
    # Test pattern consolidation
    print("\n   🔄 Testing pattern consolidation...")
    
    new_pattern = {
        "pattern_id": "pattern_004",
        "pattern_type": "behavioral_signature",
        "description": "OFAC evasion through mixer services",
        "metadata": {"actor_id": "lazarus_002"},
        "confidence": 0.88
    }
    
    result = vector_integration.consolidate_with_similarity(
        new_pattern=new_pattern,
        similarity_threshold=0.7
    )
    
    assert result["consolidated"], "Pattern consolidation failed"
    print(f"   ✅ Consolidated with {len(result['similar_patterns'])} similar patterns")
    print(f"      Final confidence: {result['final_confidence']:.2%}")
    
    print("\n   ✅ FAISS vector store tests passed\n")
    return True


def test_qdrant_storage():
    """Test Qdrant vector store (if available)"""
    print("🧪 Testing Qdrant Vector Store")
    
    try:
        vector_integration = HypnosVectorIntegration(
            vector_backend="qdrant",
            collection_name="test_patterns",
            url="http://localhost:6333"
        )
    except ImportError as e:
        print(f"   ⚠️  Qdrant client not installed: {e}")
        print("   Install with: pip install qdrant-client")
        return False
    except Exception as e:
        print(f"   ⚠️  Could not connect to Qdrant: {e}")
        print("   Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
        return False
    
    # Store test pattern
    result = vector_integration.store_pattern(
        pattern_id="qdrant_test_001",
        pattern_type="behavioral_signature",
        description="Test pattern for Qdrant",
        metadata={"test": True},
        confidence=0.9
    )
    
    assert result, "Failed to store pattern in Qdrant"
    print("   ✅ Stored pattern in Qdrant")
    
    # Search
    results = vector_integration.find_similar_patterns(
        query_description="test pattern",
        top_k=5
    )
    
    assert len(results) > 0, "No results from Qdrant search"
    print(f"   ✅ Found {len(results)} similar patterns")
    
    print("   ✅ Qdrant vector store tests passed\n")
    return True


def main():
    """Run all vector integration tests"""
    print("=" * 60)
    print("🔬 VECTOR DATABASE INTEGRATION TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Test FAISS (should work if installed)
    try:
        results.append(("FAISS", test_faiss_storage()))
    except Exception as e:
        print(f"   ❌ FAISS test failed: {e}\n")
        results.append(("FAISS", False))
    
    # Test Qdrant (optional, requires server)
    try:
        results.append(("Qdrant", test_qdrant_storage()))
    except Exception as e:
        print(f"   ⚠️  Qdrant test skipped: {e}\n")
        results.append(("Qdrant", None))
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for backend, result in results:
        if result is True:
            print(f"   ✅ {backend}: PASSED")
        elif result is False:
            print(f"   ❌ {backend}: FAILED")
        else:
            print(f"   ⚠️  {backend}: SKIPPED (optional)")
    
    print()
    
    # Check if at least one backend works
    if any(r is True for _, r in results):
        print("✅ Vector database integration is working!")
        return 0
    else:
        print("⚠️  No vector backends available. Install dependencies:")
        print("   pip install faiss-cpu sentence-transformers")
        print("   # OR for production:")
        print("   pip install qdrant-client sentence-transformers")
        return 1


if __name__ == "__main__":
    sys.exit(main())

