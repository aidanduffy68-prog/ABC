"""
Vector Database Integration for Hypnos
Long-term memory and context-aware classification using vector embeddings

Supports multiple vector databases:
- Qdrant (recommended for self-hosted)
- Weaviate (alternative)
- Chroma (lightweight option)
- FAISS (in-memory, for development)

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")


@dataclass
class VectorPattern:
    """Pattern stored in vector database"""
    pattern_id: str
    pattern_type: str  # behavioral_signature, threat_indicator, coordination_pattern, etc.
    description: str
    embedding: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    confidence: float


class VectorStore:
    """
    Abstract base class for vector database operations
    
    Provides unified interface for different vector databases
    """
    
    def __init__(self, collection_name: str = "hypnos_patterns"):
        """
        Initialize vector store
        
        Args:
            collection_name: Name of the collection/index to use
        """
        self.collection_name = collection_name
        self.embedding_model = None
        self._initialize_embedding_model()
    
    def _initialize_embedding_model(self):
        """Initialize embedding model"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            # Use lightweight model for speed (can upgrade to larger models)
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
                self.embedding_model = None
        else:
            self.embedding_model = None
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not self.embedding_model:
            # Fallback: simple hash-based embedding (not semantic, but works)
            hash_obj = hashlib.sha256(text.encode())
            # Convert hash to 384-dim vector (matching MiniLM-L6-v2)
            hash_bytes = hash_obj.digest()
            embedding = [float(b) / 255.0 for b in hash_bytes[:384]]
            # Pad if needed
            while len(embedding) < 384:
                embedding.append(0.0)
            return embedding[:384]
        
        return self.embedding_model.encode(text).tolist()
    
    def add_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        description: str,
        metadata: Dict[str, Any],
        confidence: float = 0.0
    ) -> bool:
        """
        Add pattern to vector store
        
        Args:
            pattern_id: Unique pattern identifier
            pattern_type: Type of pattern
            description: Pattern description (used for embedding)
            metadata: Additional metadata
            confidence: Confidence score
            
        Returns:
            True if successful
        """
        raise NotImplementedError("Subclass must implement add_pattern")
    
    def search_similar(
        self,
        query_text: str,
        pattern_type: Optional[str] = None,
        top_k: int = 10,
        min_score: float = 0.7
    ) -> List[Tuple[VectorPattern, float]]:
        """
        Search for similar patterns using semantic similarity
        
        Args:
            query_text: Query text to search for
            pattern_type: Optional filter by pattern type
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of (pattern, similarity_score) tuples
        """
        raise NotImplementedError("Subclass must implement search_similar")
    
    def get_pattern(self, pattern_id: str) -> Optional[VectorPattern]:
        """
        Get pattern by ID
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            VectorPattern or None
        """
        raise NotImplementedError("Subclass must implement get_pattern")
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """
        Delete pattern from store
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            True if successful
        """
        raise NotImplementedError("Subclass must implement delete_pattern")


class QdrantVectorStore(VectorStore):
    """
    Qdrant vector database implementation
    
    Recommended for self-hosted deployments
    """
    
    def __init__(self, collection_name: str = "hypnos_patterns", url: str = "http://localhost:6333"):
        """
        Initialize Qdrant vector store
        
        Args:
            collection_name: Collection name
            url: Qdrant server URL
        """
        super().__init__(collection_name)
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct
            self.QdrantClient = QdrantClient
            self.Distance = Distance
            self.VectorParams = VectorParams
            self.PointStruct = PointStruct
            self.client = QdrantClient(url=url)
            self._ensure_collection()
        except ImportError:
            raise ImportError("Qdrant client not installed. Install with: pip install qdrant-client")
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant: {e}")
            self.client = None
    
    def _ensure_collection(self):
        """Ensure collection exists"""
        if not self.client:
            return
        
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection with 384 dimensions (MiniLM-L6-v2)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=self.VectorParams(
                        size=384,
                        distance=self.Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"Warning: Could not ensure collection: {e}")
    
    def add_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        description: str,
        metadata: Dict[str, Any],
        confidence: float = 0.0
    ) -> bool:
        """Add pattern to Qdrant"""
        if not self.client:
            return False
        
        try:
            embedding = self.generate_embedding(description)
            
            point = self.PointStruct(
                id=pattern_id,
                vector=embedding,
                payload={
                    "pattern_type": pattern_type,
                    "description": description,
                    "metadata": metadata,
                    "confidence": confidence,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return True
        except Exception as e:
            print(f"Error adding pattern to Qdrant: {e}")
            return False
    
    def search_similar(
        self,
        query_text: str,
        pattern_type: Optional[str] = None,
        top_k: int = 10,
        min_score: float = 0.7
    ) -> List[Tuple[VectorPattern, float]]:
        """Search for similar patterns in Qdrant"""
        if not self.client:
            return []
        
        try:
            query_embedding = self.generate_embedding(query_text)
            
            # Build filter if pattern_type specified
            query_filter = None
            if pattern_type:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="pattern_type",
                            match=MatchValue(value=pattern_type)
                        )
                    ]
                )
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=min_score
            )
            
            patterns = []
            for result in results:
                payload = result.payload
                pattern = VectorPattern(
                    pattern_id=str(result.id),
                    pattern_type=payload.get("pattern_type", "unknown"),
                    description=payload.get("description", ""),
                    embedding=result.vector if hasattr(result, 'vector') else [],
                    metadata=payload.get("metadata", {}),
                    created_at=datetime.fromisoformat(payload.get("created_at", datetime.now().isoformat())),
                    confidence=payload.get("confidence", 0.0)
                )
                patterns.append((pattern, result.score))
            
            return patterns
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return []
    
    def get_pattern(self, pattern_id: str) -> Optional[VectorPattern]:
        """Get pattern by ID from Qdrant"""
        if not self.client:
            return None
        
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[pattern_id]
            )
            
            if not result:
                return None
            
            point = result[0]
            payload = point.payload
            
            return VectorPattern(
                pattern_id=str(point.id),
                pattern_type=payload.get("pattern_type", "unknown"),
                description=payload.get("description", ""),
                embedding=point.vector if hasattr(point, 'vector') else [],
                metadata=payload.get("metadata", {}),
                created_at=datetime.fromisoformat(payload.get("created_at", datetime.now().isoformat())),
                confidence=payload.get("confidence", 0.0)
            )
        except Exception as e:
            print(f"Error getting pattern from Qdrant: {e}")
            return None
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete pattern from Qdrant"""
        if not self.client:
            return False
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[pattern_id]
            )
            return True
        except Exception as e:
            print(f"Error deleting pattern from Qdrant: {e}")
            return False


class FAISSVectorStore(VectorStore):
    """
    FAISS in-memory vector store (for development/testing)
    
    Fast but not persistent - data lost on restart
    """
    
    def __init__(self, collection_name: str = "hypnos_patterns"):
        """Initialize FAISS vector store"""
        super().__init__(collection_name)
        try:
            import faiss
            import numpy as np
            self.faiss = faiss
            self.np = np
            # Create index (384 dimensions, cosine similarity)
            self.index = faiss.IndexFlatIP(384)  # Inner product for cosine similarity
            self.patterns: Dict[str, VectorPattern] = {}
        except ImportError:
            raise ImportError("FAISS not installed. Install with: pip install faiss-cpu")
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize vector for cosine similarity"""
        import numpy as np
        vec = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
    
    def add_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        description: str,
        metadata: Dict[str, Any],
        confidence: float = 0.0
    ) -> bool:
        """Add pattern to FAISS"""
        try:
            embedding = self.generate_embedding(description)
            normalized_embedding = self._normalize_vector(embedding)
            
            pattern = VectorPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                description=description,
                embedding=normalized_embedding,
                metadata=metadata,
                created_at=datetime.now(),
                confidence=confidence
            )
            
            self.patterns[pattern_id] = pattern
            
            # Add to FAISS index
            vector_array = self.np.array([normalized_embedding], dtype=self.np.float32)
            self.index.add(vector_array)
            
            return True
        except Exception as e:
            print(f"Error adding pattern to FAISS: {e}")
            return False
    
    def search_similar(
        self,
        query_text: str,
        pattern_type: Optional[str] = None,
        top_k: int = 10,
        min_score: float = 0.7
    ) -> List[Tuple[VectorPattern, float]]:
        """Search for similar patterns in FAISS"""
        try:
            query_embedding = self.generate_embedding(query_text)
            normalized_query = self._normalize_vector(query_embedding)
            
            # Search
            query_array = self.np.array([normalized_query], dtype=self.np.float32)
            scores, indices = self.index.search(query_array, top_k)
            
            results = []
            pattern_list = list(self.patterns.values())
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(pattern_list) and score >= min_score:
                    pattern = pattern_list[idx]
                    # Filter by pattern_type if specified
                    if pattern_type is None or pattern.pattern_type == pattern_type:
                        results.append((pattern, float(score)))
            
            return results
        except Exception as e:
            print(f"Error searching FAISS: {e}")
            return []
    
    def get_pattern(self, pattern_id: str) -> Optional[VectorPattern]:
        """Get pattern by ID from FAISS"""
        return self.patterns.get(pattern_id)
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete pattern from FAISS (note: FAISS doesn't support deletion easily)"""
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            # Note: FAISS doesn't support easy deletion, would need to rebuild index
            return True
        return False


def create_vector_store(
    backend: str = "faiss",
    collection_name: str = "hypnos_patterns",
    **kwargs
) -> VectorStore:
    """
    Factory function to create vector store
    
    Args:
        backend: Backend to use ("qdrant", "faiss", "weaviate", "chroma")
        collection_name: Collection name
        **kwargs: Backend-specific arguments
        
    Returns:
        VectorStore instance
    """
    if backend.lower() == "qdrant":
        url = kwargs.get("url", "http://localhost:6333")
        return QdrantVectorStore(collection_name=collection_name, url=url)
    elif backend.lower() == "faiss":
        return FAISSVectorStore(collection_name=collection_name)
    else:
        # Default to FAISS for development
        print(f"Warning: Backend '{backend}' not implemented, using FAISS")
        return FAISSVectorStore(collection_name=collection_name)

