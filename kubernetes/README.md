# Kubernetes Deployment Guide

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Docker registry access (for pushing images)

## Quick Start

### 1. Create Namespace

```bash
kubectl apply -f kubernetes/namespace.yaml
```

### 2. Create ConfigMap

```bash
kubectl apply -f kubernetes/configmap.yaml
```

### 3. Create Secrets

```bash
# Copy example and fill in values
cp kubernetes/secrets.yaml.example kubernetes/secrets.yaml
# Edit secrets.yaml with actual values
kubectl apply -f kubernetes/secrets.yaml
```

### 4. Deploy Dependencies

```bash
# PostgreSQL
kubectl apply -f kubernetes/postgres-deployment.yaml

# Neo4j
kubectl apply -f kubernetes/neo4j-deployment.yaml

# Redis
kubectl apply -f kubernetes/redis-deployment.yaml
```

### 5. Build and Push Docker Image

```bash
# Build image
docker build -t gh-systems-abc:latest .

# Tag for registry (replace with your registry)
docker tag gh-systems-abc:latest your-registry/gh-systems-abc:latest

# Push to registry
docker push your-registry/gh-systems-abc:latest
```

### 6. Update API Deployment Image

Edit `kubernetes/api-deployment.yaml` and update the image reference:

```yaml
image: your-registry/gh-systems-abc:latest
```

### 7. Deploy API

```bash
kubectl apply -f kubernetes/api-deployment.yaml
```

### 8. (Optional) Deploy Ingress

```bash
# Update ingress.yaml with your domain
kubectl apply -f kubernetes/ingress.yaml
```

## Verify Deployment

```bash
# Check pods
kubectl get pods -n abc-intelligence

# Check services
kubectl get svc -n abc-intelligence

# Check logs
kubectl logs -f deployment/abc-api -n abc-intelligence

# Test health endpoint
kubectl port-forward svc/abc-api 8000:8000 -n abc-intelligence
curl http://localhost:8000/api/v1/status/health
```

## Scaling

```bash
# Scale API replicas
kubectl scale deployment abc-api --replicas=5 -n abc-intelligence
```

## Updates

```bash
# Update image
docker build -t your-registry/gh-systems-abc:v1.1.0 .
docker push your-registry/gh-systems-abc:v1.1.0

# Update deployment
kubectl set image deployment/abc-api api=your-registry/gh-systems-abc:v1.1.0 -n abc-intelligence

# Rollout status
kubectl rollout status deployment/abc-api -n abc-intelligence
```

## Troubleshooting

```bash
# Describe pod
kubectl describe pod <pod-name> -n abc-intelligence

# Get events
kubectl get events -n abc-intelligence --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n abc-intelligence
```

## Production Considerations

1. **Secrets Management**: Use external secret management (Vault, AWS Secrets Manager)
2. **Monitoring**: Add Prometheus/Grafana
3. **Logging**: Add centralized logging (ELK, Loki)
4. **Backup**: Set up database backups
5. **Security**: Enable network policies, pod security policies
6. **Resource Limits**: Adjust based on load testing

