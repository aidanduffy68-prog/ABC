# -*- coding: utf-8 -*-
"""
Test Foundry AIP Connection
Tests connection to Foundry using OAuth2 credentials

Usage:
    python scripts/test_foundry_connection.py
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Test Foundry AIP connection"""
    print("🔧 Testing Foundry AIP connection...")
    print()
    
    # Check environment variables
    required_vars = ["FOUNDRY_URL", "FOUNDRY_CLIENT_ID", "FOUNDRY_CLIENT_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("\nSet them in .env file:")
        print("FOUNDRY_URL=https://your-instance.palantirfoundry.com")
        print("FOUNDRY_CLIENT_ID=your-client-id")
        print("FOUNDRY_CLIENT_SECRET=your-client-secret")
        return 1
    
    # Check if SDK is installed
    try:
        from abc_integration_sdk import FoundryClient, ConfidentialClientAuth
        print("✅ Foundry SDK installed")
    except ImportError:
        print("❌ Foundry SDK not installed!")
        print("\nInstall with:")
        print("export FOUNDRY_TOKEN=your-token")
        print("pip install abc_integration_sdk==0.1.0 --upgrade \\")
        print("  --index-url \"https://user:$FOUNDRY_TOKEN@ghsystems.usw-16.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.7b7471ff-6f16-4988-b605-7c7beeb68ea3/contents/release/pypi/simple\" \\")
        print("  --extra-index-url \"https://user:$FOUNDRY_TOKEN@ghsystems.usw-16.palantirfoundry.com/artifacts/api/repositories/ri.foundry-sdk-asset-bundle.main.artifacts.repository/contents/release/pypi/simple\"")
        return 1
    
    # Get credentials
    foundry_url = os.getenv("FOUNDRY_URL")
    client_id = os.getenv("FOUNDRY_CLIENT_ID")
    client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")
    
    print(f"✅ Found URL: {foundry_url}")
    print(f"✅ Found Client ID: {client_id[:10]}...")
    print(f"✅ Found Client Secret: {'*' * 20}")
    print()
    
    # Try to connect
    print("🔌 Connecting to Foundry...")
    
    try:
        from src.verticals.ai_verification.core.nemesis.foundry_integration.foundry_aip_connector import FoundryAIPConnector
        
        connector = FoundryAIPConnector(
            foundry_url=foundry_url,
            client_id=client_id,
            client_secret=client_secret
        )
        
        print("✅ SUCCESS! Connected to Foundry AIP!")
        print()
        print("You can now use Foundry in your code!")
        print()
        print("Example usage:")
        print("  from src.verticals.ai_verification.core.nemesis.foundry_integration import FoundryIntegration")
        print("  foundry = FoundryIntegration(use_aip=True)")
        print("  compilations = foundry.list_recent_compilations(limit=10)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check FOUNDRY_URL is correct")
        print("2. Check FOUNDRY_CLIENT_ID is correct")
        print("3. Check FOUNDRY_CLIENT_SECRET is correct")
        print("4. Verify you have internet connection")
        print("5. Check if Foundry SDK is properly installed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

