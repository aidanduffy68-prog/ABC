FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY nemesis/ai_ontology/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY nemesis/ai_ontology/ ./ai_ontology/
COPY nemesis/ai_ontology/api_endpoints.py .

# Create non-root user
RUN useradd -m -u 1000 abc && chown -R abc:abc /app
USER abc

# Set PYTHONPATH so imports work
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/v1/health')"

# Run API server
CMD ["python", "api_endpoints.py"]

