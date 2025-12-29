"""
GH Systems ABC API
FastAPI application with all routes

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Import routes from verticals
from src.verticals.ai_verification.api import ingest, agency, foundry_verification
from src.api.routes import status, monitoring

# Conditional import for oracle routes
try:
    from src.verticals.aml_oracle.api import oracle, foundry_aml
    ORACLE_ROUTES_AVAILABLE = True
except ImportError:
    ORACLE_ROUTES_AVAILABLE = False
    oracle = None
    foundry_aml = None

from src.shared.middleware.request_logger import RequestLoggerMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="GH Systems ABC API",
    description="""
    **ABC (Adversarial Behavior Compiler) - Foundry's Chainlink**
    
    ABC is the cryptographic verification layer for Palantir Foundry—the Chainlink for government intelligence.
    
    ## Features
    
    * **Foundry Verification**: Verify Foundry compilations and commit to blockchain
    * **Agency Assessments**: Submit AI assessments and calculate multi-agency consensus
    * **Cryptographic Receipts**: Generate blockchain receipts for intelligence outputs
    * **Consensus Engine**: Detect outliers and generate recommendations across agency assessments
    
    ## Authentication
    
    Most endpoints require authentication via `Authorization: Bearer <token>` header.
    
    ## Foundry Chain Workflow
    
    1. **Foundry Compilation** → Palantir Foundry generates intelligence compilation
    2. **ABC Verification** → `/api/v1/foundry/verify` verifies and commits to blockchain
    3. **Agency Assessment** → Agencies submit assessments via `/api/v1/agency/assessment`
    4. **Consensus** → Retrieve multi-agency consensus via `/api/v1/agency/consensus/{compilation_id}`
    
    See [Foundry Chain Specification](docs/integrations/FOUNDRY_CHAIN_SPEC.md) for details.
    """,
    version="2.0.0",
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
        {
            "name": "foundry",
            "description": "Palantir Foundry integration endpoints. Verify Foundry compilations and commit to blockchain.",
        },
        {
            "name": "agency",
            "description": "Agency AI assessment submission and multi-agency consensus endpoints. Submit assessments and retrieve consensus calculations.",
        },
        {
            "name": "monitoring",
            "description": "System monitoring and metrics endpoints",
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
# AI Verification vertical
app.include_router(ingest.router)
app.include_router(agency.router)
app.include_router(foundry_verification.router)

# AML Oracle vertical (if enabled)
ORACLE_ENABLED = os.getenv("ORACLE_ENABLED", "false").lower() == "true"
if ORACLE_ROUTES_AVAILABLE and ORACLE_ENABLED:
    app.include_router(oracle.router)
    app.include_router(foundry_aml.router)
    # Add oracle tags to OpenAPI tags
    app.openapi_tags.extend([
        {
            "name": "oracle",
            "description": "Blockchain oracle endpoints. Ingest blockchain data and provide verified data feeds.",
        },
        {
            "name": "foundry-aml",
            "description": "Foundry AML integration endpoints. Blockchain data ingestion and ML model verification.",
        }
    ])

# Shared routes
app.include_router(status.router)
app.include_router(monitoring.router)


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

