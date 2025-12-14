FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements/requirements.txt .
COPY requirements/requirements-security.txt ./requirements/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements/requirements-security.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Make run script executable
RUN chmod +x scripts/run_api_server.py

# Create non-root user
RUN useradd -m -u 1000 abc && chown -R abc:abc /app
USER abc

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/status/health || exit 1

# Default command (can be overridden)
CMD ["python", "scripts/run_api_server.py", "--production", "--host", "0.0.0.0", "--port", "8000"]

