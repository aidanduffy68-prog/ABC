"""
Vector Database Integration for Hypnos Pattern Consolidation
Integrates vector similarity search with pattern consolidation

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from src.core.hypnos.vector_store import (
    VectorStore,
    VectorPattern,
    create_vector_store,
    QdrantVectorStore,
    FAISSVectorStore
)


class HypnosVectorIntegration:
    """
    Integrates vector database with Hypnos pattern consolidation
    
    Provides:
    - Semantic search for similar patterns
    - Context-aware classification
    - Long-term memory storage
    - Pattern similarity matching
    """
    
    def __init__(
        self,
        vector_backend: str = "faiss",
        collection_name: str = "hypnos_patterns",
        **kwargs
    ):
        """
        Initialize vector integration
        
        Args:
            vector_backend: Backend to use ("qdrant", "faiss", etc.)
            collection_name: Collection name
            **kwargs: Backend-specific arguments
        """
        self.vector_store = create_vector_store(
            backend=vector_backend,
            collection_name=collection_name,
            **kwargs
        )
        self.pattern_types = [
            "behavioral_signature",
            "threat_indicator",
            "coordination_pattern",
            "risk_pattern",
            "transaction_pattern",
            "network_pattern"
        ]
    
    def store_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        description: str,
        metadata: Dict[str, Any],
        confidence: float = 0.0
    ) -> bool:
        """
        Store pattern in vector database
        
        Args:
            pattern_id: Unique pattern identifier
            pattern_type: Type of pattern
            description: Pattern description (used for embedding)
            metadata: Additional metadata (actor_id, timestamps, etc.)
            confidence: Confidence score
            
        Returns:
            True if successful
        """
        if pattern_type not in self.pattern_types:
            print(f"Warning: Unknown pattern type: {pattern_type}")
        
        return self.vector_store.add_pattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            description=description,
            metadata=metadata,
            confidence=confidence
        )
    
    def find_similar_patterns(
        self,
        query_description: str,
        pattern_type: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar patterns using semantic search
        
        Args:
            query_description: Description to search for
            pattern_type: Optional filter by pattern type
            top_k: Number of results
            min_similarity: Minimum similarity score (0-1)
            
        Returns:
            List of similar patterns with metadata
        """
        results = self.vector_store.search_similar(
            query_text=query_description,
            pattern_type=pattern_type,
            top_k=top_k,
            min_score=min_similarity
        )
        
        similar_patterns = []
        for pattern, similarity_score in results:
            similar_patterns.append({
                "pattern_id": pattern.pattern_id,
                "pattern_type": pattern.pattern_type,
                "description": pattern.description,
                "similarity": similarity_score,
                "confidence": pattern.confidence,
                "metadata": pattern.metadata,
                "created_at": pattern.created_at.isoformat()
            })
        
        return similar_patterns
    
    def consolidate_with_similarity(
        self,
        new_pattern: Dict[str, Any],
        similarity_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Consolidate new pattern with existing similar patterns
        
        Uses vector similarity to find related patterns and merge them
        
        Args:
            new_pattern: New pattern to consolidate
            similarity_threshold: Minimum similarity to consider for consolidation
            
        Returns:
            Consolidated pattern with similarity information
        """
        pattern_id = new_pattern.get("pattern_id", f"pattern_{datetime.now().timestamp()}")
        pattern_type = new_pattern.get("pattern_type", "unknown")
        description = new_pattern.get("description", "")
        metadata = new_pattern.get("metadata", {})
        confidence = new_pattern.get("confidence", 0.0)
        
        # Find similar patterns
        similar = self.find_similar_patterns(
            query_description=description,
            pattern_type=pattern_type,
            top_k=10,
            min_similarity=similarity_threshold
        )
        
        if similar:
            # Merge with most similar pattern
            most_similar = similar[0]
            
            # Update metadata with consolidation info
            metadata["consolidated_with"] = most_similar["pattern_id"]
            metadata["similarity_score"] = most_similar["similarity"]
            metadata["consolidation_timestamp"] = datetime.now().isoformat()
            
            # Increase confidence if similar patterns found
            if len(similar) > 1:
                avg_confidence = sum(p["confidence"] for p in similar) / len(similar)
                confidence = max(confidence, avg_confidence * 0.9)  # Slight boost
        
        # Store the pattern
        self.store_pattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            description=description,
            metadata=metadata,
            confidence=confidence
        )
        
        return {
            "pattern_id": pattern_id,
            "consolidated": len(similar) > 0,
            "similar_patterns": similar,
            "final_confidence": confidence
        }
    
    def classify_with_context(
        self,
        entity_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Context-aware classification using vector similarity
        
        Finds similar patterns to inform classification
        
        Args:
            entity_description: Description of entity to classify
            context: Optional context (actor_id, transaction_history, etc.)
            
        Returns:
            Classification with context from similar patterns
        """
        # Build query from description and context
        query_parts = [entity_description]
        if context:
            if "actor_id" in context:
                query_parts.append(f"actor: {context['actor_id']}")
            if "transaction_history" in context:
                query_parts.append("transaction patterns")
            if "network_data" in context:
                query_parts.append("network coordination")
        
        query = " ".join(query_parts)
        
        # Search for similar patterns
        similar_patterns = self.find_similar_patterns(
            query_description=query,
            top_k=5,
            min_similarity=0.7
        )
        
        # Aggregate classification from similar patterns
        pattern_type_counts = {}
        total_confidence = 0.0
        
        for pattern in similar_patterns:
            ptype = pattern["pattern_type"]
            pattern_type_counts[ptype] = pattern_type_counts.get(ptype, 0) + 1
            total_confidence += pattern["confidence"] * pattern["similarity"]
        
        # Determine most likely classification
        if pattern_type_counts:
            most_common_type = max(pattern_type_counts.items(), key=lambda x: x[1])[0]
            avg_confidence = total_confidence / len(similar_patterns) if similar_patterns else 0.0
        else:
            most_common_type = "unknown"
            avg_confidence = 0.0
        
        return {
            "classification": most_common_type,
            "confidence": avg_confidence,
            "similar_patterns_found": len(similar_patterns),
            "context_patterns": similar_patterns[:3],  # Top 3 for context
            "reasoning": f"Classified based on {len(similar_patterns)} similar patterns"
        }
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored patterns
        
        Returns:
            Statistics dictionary
        """
        # This would query the vector store for statistics
        # For now, return basic info
        return {
            "backend": type(self.vector_store).__name__,
            "collection_name": self.vector_store.collection_name,
            "pattern_types": self.pattern_types,
            "note": "Statistics require backend-specific implementation"
        }

