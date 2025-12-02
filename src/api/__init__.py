"""
GH Systems ABC API
FastAPI application with all routes

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.api.routes import ingest, status

# Create FastAPI app
app = FastAPI(
    title="GH Systems ABC API",
    description="Truth verification for post-AGI intelligence",
    version="1.0.0"
)

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

