#!/usr/bin/env python3
"""
GH Systems ABC - API Server Runner
Start the FastAPI server for development or production

Usage:
    python scripts/run_api_server.py                    # Development mode (default)
    python scripts/run_api_server.py --host 0.0.0.0       # Listen on all interfaces
    python scripts/run_api_server.py --port 8080         # Custom port
    python scripts/run_api_server.py --reload             # Auto-reload on changes
    python scripts/run_api_server.py --production         # Production mode

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from src.api import app


def main():
    parser = argparse.ArgumentParser(
        description='GH Systems ABC - API Server Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Development mode (default)
  python scripts/run_api_server.py

  # Production mode
  python scripts/run_api_server.py --production --host 0.0.0.0 --port 8080

  # Custom configuration
  python scripts/run_api_server.py --host 127.0.0.1 --port 3000 --reload
        """
    )
    
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port to bind to (default: 8000)')
    parser.add_argument('--reload', action='store_true',
                       help='Enable auto-reload on code changes (development only)')
    parser.add_argument('--production', action='store_true',
                       help='Run in production mode (disables reload, optimizes workers)')
    parser.add_argument('--workers', type=int, default=1,
                       help='Number of worker processes (production only, default: 1)')
    parser.add_argument('--log-level', type=str, default='info',
                       choices=['critical', 'error', 'warning', 'info', 'debug', 'trace'],
                       help='Log level (default: info)')
    
    args = parser.parse_args()
    
    # Production mode settings
    if args.production:
        if args.reload:
            print("⚠️  Warning: --reload is disabled in production mode")
            args.reload = False
        if args.workers < 1:
            args.workers = 1
    
    # Print startup info
    print("=" * 60)
    print("GH Systems ABC - API Server")
    print("=" * 60)
    print(f"Mode: {'PRODUCTION' if args.production else 'DEVELOPMENT'}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Workers: {args.workers if args.production else 1}")
    print(f"Reload: {'Enabled' if args.reload else 'Disabled'}")
    print(f"Log Level: {args.log_level.upper()}")
    print("=" * 60)
    print(f"\n📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Alternative Docs: http://{args.host}:{args.port}/redoc")
    print(f"❤️  Health Check: http://{args.host}:{args.port}/api/v1/status/health")
    print(f"✅ Readiness: http://{args.host}:{args.port}/api/v1/status/readiness")
    print("=" * 60)
    print("\n🚀 Starting server...\n")
    
    # Run server
    uvicorn.run(
        "src.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload and not args.production,
        workers=args.workers if args.production else 1,
        log_level=args.log_level,
        access_log=True
    )


if __name__ == '__main__':
    main()

