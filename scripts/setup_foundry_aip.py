# -*- coding: utf-8 -*-
"""
Setup and verify Foundry AIP configuration

Usage:
    python scripts/setup_foundry_aip.py
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

def main():
    """Verify Foundry AIP setup"""
    load_dotenv()
    
    print("🔧 Verifying Foundry AIP setup...")
    print()
    
    # Check .env file exists
    env_path = project_root / ".env"
    if not env_path.exists():
        print("❌ .env file not found!")
        print(f"   Expected at: {env_path}")
        print()
        print("Create .env file with:")
        print("FOUNDRY_URL=https://ghsystems.usw-16.palantirfoundry.com")
        print("FOUNDRY_CLIENT_ID=your-client-id")
        print("FOUNDRY_CLIENT_SECRET=your-client-secret")
        print("FOUNDRY_TOKEN=your-token")
        return 1
    
    print(f"✅ .env file found at: {env_path}")
    
    # Check environment variables
    required_vars = {
        "FOUNDRY_URL": "Foundry instance URL",
        "FOUNDRY_CLIENT_ID": "OAuth2 Client ID",
        "FOUNDRY_CLIENT_SECRET": "OAuth2 Client Secret",
    }
    
    optional_vars = {
        "FOUNDRY_TOKEN": "Personal access token (for SDK installation)"
    }
    
    print()
    print("Checking required environment variables:")
    all_present = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "SECRET" in var or "TOKEN" in var:
                display_value = f"{'*' * 20} (hidden)"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Missing ({description})")
            all_present = False
    
    print()
    print("Checking optional environment variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * 20} (hidden)")
        else:
            print(f"  ⚠️  {var}: Not set ({description})")
    
    if not all_present:
        print()
        print("❌ Missing required environment variables!")
        print("   Update your .env file with the missing values.")
        return 1
    
    # Check .gitignore
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            if ".env" in gitignore_content:
                print()
                print("✅ .env is in .gitignore (secrets won't be committed)")
            else:
                print()
                print("⚠️  .env is NOT in .gitignore!")
                print("   Add '.env' to .gitignore to prevent committing secrets")
    
    # Check SDK installation
    print()
    print("Checking Foundry SDK installation:")
    try:
        from abc_integration_sdk import FoundryClient, ConfidentialClientAuth
        print("  ✅ Foundry SDK installed")
    except ImportError:
        print("  ❌ Foundry SDK not installed")
        print()
        print("Install with:")
        print("  export FOUNDRY_TOKEN=your-token")
        print("  pip install abc_integration_sdk==0.1.0 --upgrade \\")
        print("    --index-url \"https://user:$FOUNDRY_TOKEN@ghsystems.usw-16.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.7b7471ff-6f16-4988-b605-7c7beeb68ea3/contents/release/pypi/simple\" \\")
        print("    --extra-index-url \"https://user:$FOUNDRY_TOKEN@ghsystems.usw-16.palantirfoundry.com/artifacts/api/repositories/ri.foundry-sdk-asset-bundle.main.artifacts.repository/contents/release/pypi/simple\"")
        return 1
    
    print()
    print("✅ Foundry AIP setup looks good!")
    print()
    print("Next steps:")
    print("  1. Run: python scripts/test_foundry_connection.py")
    print("  2. If connection succeeds, you're ready to use Foundry!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

