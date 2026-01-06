"""
Hypnos: Long-Term Memory System
Pattern consolidation and dormant threat tracking with vector database integration

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from src.core.hypnos.pattern_consolidation import HypnosPatternConsolidator
from src.core.hypnos.vector_store import (
    VectorStore,
    VectorPattern,
    create_vector_store,
    QdrantVectorStore,
    FAISSVectorStore
)
from src.core.hypnos.vector_integration import HypnosVectorIntegration

__all__ = [
    "HypnosPatternConsolidator",
    "VectorStore",
    "VectorPattern",
    "create_vector_store",
    "QdrantVectorStore",
    "FAISSVectorStore",
    "HypnosVectorIntegration"
]
