# Docker Configuration

**Docker files and compose configurations for GH Systems ABC**

---

## Main Docker Files

### `Dockerfile`
Main API service container for ABC.

**Build:**
```bash
docker build -f docker/Dockerfile -t gh-systems-abc:latest .
```

**Run:**
```bash
docker run -p 8000:8000 gh-systems-abc:latest
```

### `docker-compose.yml`
Complete development environment with all services (API, PostgreSQL, Neo4j, Redis).

**Start all services:**
```bash
docker-compose -f docker/docker-compose.yml up
```

**Services:**
- `api` - Main FastAPI service (port 8000)
- `postgres` - PostgreSQL database (port 5432)
- `neo4j` - Neo4j graph database (ports 7474, 7687)
- `redis` - Redis cache (port 6379)

---

## Component-Specific Docker Files

### `Dockerfile.ai-ontology`
Dockerfile for AI Ontology component (standalone).

### `docker-compose.ai-ontology.yml`
Docker Compose for AI Ontology component (standalone).

---

## Usage

### Development
```bash
# Start all services
cd docker
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Production
```bash
# Build production image
docker build -f docker/Dockerfile -t gh-systems-abc:latest .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e JWT_SECRET_KEY=your-secret-key \
  -e POSTGRES_HOST=postgres \
  gh-systems-abc:latest
```

---

## Environment Variables

See `docker-compose.yml` for full list of environment variables.

**Required:**
- `JWT_SECRET_KEY` - JWT signing key
- `FLASK_SECRET_KEY` - Flask session secret
- `POSTGRES_PASSWORD` - PostgreSQL password

**Optional:**
- `DEBUG` - Enable debug mode (default: false)
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)

---

**See [Getting Started Guide](../GETTING_STARTED.md) for more details.**

