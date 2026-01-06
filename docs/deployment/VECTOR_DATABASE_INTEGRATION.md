# Vector Database Integration

**Long-Term Memory and Context-Aware Classification**

## Overview

Vector database integration enables semantic search and context-aware classification for the Hypnos long-term memory system. This allows ABC to:

- Find similar threat patterns using semantic similarity (not just exact matches)
- Provide context-aware classification based on historical patterns
- Store and retrieve behavioral signatures efficiently
- Enable long-term memory for dormant threat tracking

## Architecture

```
┌─────────────────────────────────────┐
│  Hypnos Pattern Consolidation       │
│  (Pattern Consolidator)              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Vector Integration Layer            │
│  (HypnosVectorIntegration)           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Vector Store (Abstract)              │
│  - QdrantVectorStore                  │
│  - FAISSVectorStore                   │
│  - (Future: Weaviate, Chroma)         │
└─────────────────────────────────────┘
```

## Supported Backends

### 1. Qdrant (Recommended for Production)

**Pros:**
- Self-hosted (no external dependencies)
- Production-ready
- Good performance
- Supports filtering and metadata

**Cons:**
- Requires separate service
- More setup complexity

**Installation:**
```bash
pip install qdrant-client
# Run Qdrant server: docker run -p 6333:6333 qdrant/qdrant
```

**Usage:**
```python
from src.core.hypnos.vector_integration import HypnosVectorIntegration

vector_integration = HypnosVectorIntegration(
    vector_backend="qdrant",
    collection_name="hypnos_patterns",
    url="http://localhost:6333"
)
```

### 2. FAISS (Development/Testing)

**Pros:**
- Fast in-memory search
- No external service needed
- Easy to set up
- Good for development

**Cons:**
- Not persistent (data lost on restart)
- Limited metadata support
- Not suitable for production

**Installation:**
```bash
pip install faiss-cpu  # or faiss-gpu for GPU support
```

**Usage:**
```python
from src.core.hypnos.vector_integration import HypnosVectorIntegration

vector_integration = HypnosVectorIntegration(
    vector_backend="faiss",
    collection_name="hypnos_patterns"
)
```

## Embedding Models

**Default:** `all-MiniLM-L6-v2` (Sentence Transformers)
- 384 dimensions
- Fast inference
- Good quality for most use cases
- ~80MB model size

**Installation:**
```bash
pip install sentence-transformers
```

**Alternative Models:**
- `all-mpnet-base-v2` - Higher quality, slower (768 dims)
- `all-distilroberta-v1` - Balanced (768 dims)
- Custom models for domain-specific embeddings

## Usage Examples

### 1. Store Patterns

```python
from src.core.hypnos.vector_integration import HypnosVectorIntegration

vector_integration = HypnosVectorIntegration(vector_backend="faiss")

# Store a behavioral signature pattern
vector_integration.store_pattern(
    pattern_id="pattern_001",
    pattern_type="behavioral_signature",
    description="North Korean hacker group using mixer services for OFAC evasion",
    metadata={
        "actor_id": "lazarus_001",
        "confidence": 0.92,
        "first_seen": "2025-01-15",
        "indicators": ["mixer_usage", "ofac_evasion"]
    },
    confidence=0.92
)
```

### 2. Find Similar Patterns

```python
# Search for similar patterns
similar = vector_integration.find_similar_patterns(
    query_description="Hacker group using cryptocurrency mixers",
    pattern_type="behavioral_signature",
    top_k=5,
    min_similarity=0.7
)

for pattern in similar:
    print(f"Pattern: {pattern['description']}")
    print(f"Similarity: {pattern['similarity']:.2%}")
    print(f"Confidence: {pattern['confidence']:.2%}")
```

### 3. Context-Aware Classification

```python
# Classify entity using similar patterns as context
classification = vector_integration.classify_with_context(
    entity_description="Wallet showing synchronized transaction patterns with known threat actors",
    context={
        "actor_id": "unknown_wallet_001",
        "transaction_history": [...],
        "network_data": {...}
    }
)

print(f"Classification: {classification['classification']}")
print(f"Confidence: {classification['confidence']:.2%}")
print(f"Based on {classification['similar_patterns_found']} similar patterns")
```

### 4. Pattern Consolidation

```python
# Consolidate new pattern with existing similar patterns
new_pattern = {
    "pattern_id": "pattern_002",
    "pattern_type": "behavioral_signature",
    "description": "OFAC evasion through mixer services",
    "metadata": {"actor_id": "lazarus_002"},
    "confidence": 0.88
}

result = vector_integration.consolidate_with_similarity(
    new_pattern=new_pattern,
    similarity_threshold=0.85
)

if result["consolidated"]:
    print(f"Consolidated with {len(result['similar_patterns'])} similar patterns")
    print(f"Final confidence: {result['final_confidence']:.2%}")
```

## Integration with Hypnos

The vector integration is designed to work alongside the existing `PatternConsolidator`:

```python
from src.core.hypnos.pattern_consolidation import PatternConsolidator
from src.core.hypnos.vector_integration import HypnosVectorIntegration

# Initialize both
consolidator = PatternConsolidator()
vector_integration = HypnosVectorIntegration(vector_backend="faiss")

# Consolidate pattern
pattern = {
    "pattern_id": "pattern_001",
    "pattern_type": "behavioral_signature",
    "description": "Threat actor using mixer services",
    "metadata": {...},
    "confidence": 0.9
}

# Use vector similarity to find related patterns
similar = vector_integration.find_similar_patterns(
    query_description=pattern["description"],
    top_k=5
)

# Consolidate with similar patterns
if similar:
    # Merge metadata from similar patterns
    for sim_pattern in similar:
        pattern["metadata"].update(sim_pattern["metadata"])

# Store in vector database
vector_integration.store_pattern(**pattern)

# Also use traditional consolidation
consolidator.consolidate_pattern(pattern)
```

## Docker Integration

### Qdrant in docker-compose.yml

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: abc-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped
    networks:
      - abc-network

volumes:
  qdrant_data:
```

### Docker Compose Deployment

Add to `docker-compose.yml`:

```yaml
  qdrant:
    image: qdrant/qdrant:latest
    container_name: abc-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant-data:/qdrant/storage
    networks:
      - abc-network
    restart: unless-stopped
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
```

## Performance Considerations

### Embedding Generation
- **Speed:** ~10-50ms per embedding (MiniLM-L6-v2)
- **Model Loading:** ~1-2 seconds on first use
- **Caching:** Consider caching embeddings for repeated queries

### Vector Search
- **FAISS:** <1ms for 10K vectors, <10ms for 1M vectors
- **Qdrant:** <5ms for 10K vectors, <50ms for 1M vectors
- **Scaling:** Both scale well to millions of vectors

### Memory Usage
- **FAISS:** ~1.5KB per vector (384 dims)
- **Qdrant:** ~2KB per vector (with metadata)
- **Model:** ~80MB (MiniLM-L6-v2)

## Future Enhancements

- [ ] Weaviate integration (alternative to Qdrant)
- [ ] Chroma integration (lightweight option)
- [ ] Custom embedding models (domain-specific)
- [ ] Embedding caching layer
- [ ] Batch embedding generation
- [ ] Multi-modal embeddings (text + graph structure)
- [ ] Incremental indexing
- [ ] Pattern versioning

## Testing

```python
# Test vector store
python3 -c "
from src.core.hypnos.vector_integration import HypnosVectorIntegration

vector = HypnosVectorIntegration(vector_backend='faiss')

# Store test pattern
vector.store_pattern(
    pattern_id='test_001',
    pattern_type='behavioral_signature',
    description='Test pattern for vector search',
    metadata={'test': True},
    confidence=0.9
)

# Search
results = vector.find_similar_patterns('test pattern', top_k=5)
print(f'Found {len(results)} similar patterns')
"
```

---

**Status:** ✅ **IMPLEMENTED** - Ready for integration with Hypnos pattern consolidation

**Next Steps:**
1. Integrate with `PatternConsolidator`
2. Add to compilation pipeline
3. Deploy Qdrant in production
4. Test with real intelligence data

