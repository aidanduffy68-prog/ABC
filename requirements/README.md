# Requirements Files

**Python dependency files for GH Systems ABC**

---

## Main Requirements

### `requirements.txt`
Core dependencies for ABC.

**Install:**
```bash
pip install -r requirements/requirements.txt
```

**Includes:**
- FastAPI, Uvicorn (API framework)
- Pydantic (data validation)
- NetworkX (graph processing)
- Flask, Flask-SocketIO (real-time platform)
- Requests (HTTP client)
- Cryptography (cryptographic operations)

### `requirements-security.txt`
Security-related dependencies.

**Install:**
```bash
pip install -r requirements/requirements-security.txt
```

**Includes:**
- PyJWT (JWT authentication)
- Additional security libraries

### `requirements-vector.txt`
Vector database dependencies (optional).

**Install:**
```bash
pip install -r requirements/requirements-vector.txt
```

**Includes:**
- qdrant-client (Qdrant backend)
- faiss-cpu (FAISS backend)
- sentence-transformers (embeddings)

---

## Component-Specific Requirements

### `requirements-ai-ontology.txt`
Dependencies for AI Ontology component.

### `requirements-real-time-platform.txt`
Dependencies for Real-Time Platform component.

---

## Installation Order

**For full installation:**
```bash
# 1. Core dependencies
pip install -r requirements/requirements.txt

# 2. Security dependencies
pip install -r requirements/requirements-security.txt

# 3. Optional: Vector database
pip install -r requirements/requirements-vector.txt

# 4. Component-specific (if needed)
pip install -r requirements/requirements-ai-ontology.txt
pip install -r requirements/requirements-real-time-platform.txt
```

**For minimal installation:**
```bash
pip install -r requirements/requirements.txt
pip install -r requirements/requirements-security.txt
```

---

## Docker Usage

Docker builds automatically install all requirements:
- `requirements.txt` (core)
- `requirements-security.txt` (security)

See `docker/Dockerfile` for details.

---

**See [Getting Started Guide](../GETTING_STARTED.md) for setup instructions.**

