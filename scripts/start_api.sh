#!/bin/bash
# Start ABC Verification API Service

cd "$(dirname "$0")/.."

echo "=" | cat
echo "Starting ABC Verification API Service"
echo "=" | cat
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Make sure FOUNDRY_CLIENT_ID, FOUNDRY_CLIENT_SECRET, and FOUNDRY_URL are set"
    echo ""
fi

# Start the API service
echo "Starting server on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 api/abc_verification_service.py

