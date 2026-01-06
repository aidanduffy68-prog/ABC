#!/usr/bin/env python3
"""
Run ABC API Server
Production-ready FastAPI server with all middleware

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from src.api import app

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run ABC API Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload (development)')
    parser.add_argument('--workers', type=int, default=4, help='Number of worker processes')
    parser.add_argument('--production', action='store_true', help='Production mode (no reload, multiple workers)')
    
    args = parser.parse_args()
    
    if args.production:
        # Production: multiple workers, no reload
        uvicorn.run(
            "src.api:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level="info",
            access_log=True
        )
    else:
        # Development: single worker, reload enabled
        uvicorn.run(
            "src.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="debug" if args.reload else "info"
        )
