"""
GH Systems ABC API
FastAPI application with all routes

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from src.api.routes import ingest, status, monitoring, foundry, agency
from src.core.middleware.request_logger import RequestLoggerMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="GH Systems ABC API",
    description="Truth verification for post-AGI intelligence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "ingestion",
            "description": "Vendor feed ingestion endpoints for threat intelligence data",
        },
        {
            "name": "status",
            "description": "Health, readiness, and version information endpoints",
        },
    ],
    contact={
        "name": "GH Systems",
        "url": "https://github.com/aidanduffy68-prog/ABC",
    },
    license_info={
        "name": "Proprietary",
    },
)

# Add request logging middleware (first, so it logs everything)
app.add_middleware(RequestLoggerMiddleware)

# SECURITY: CORS configuration from environment variable
allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if os.getenv('CORS_ALLOWED_ORIGINS') else []
if allowed_origins and allowed_origins != ['']:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(ingest.router)
app.include_router(status.router)
app.include_router(monitoring.router)
app.include_router(foundry.router)
app.include_router(agency.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GH Systems ABC",
        "description": "Truth verification for post-AGI intelligence",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/status/health",
        "readiness": "/api/v1/status/readiness"
    }

