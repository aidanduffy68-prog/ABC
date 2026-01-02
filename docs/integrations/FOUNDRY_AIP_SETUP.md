# Foundry AIP Setup Guide

**Complete setup guide for Foundry Application Integration Platform (AIP)**

Copyright (c) 2025 GH Systems. All rights reserved.

---

## Overview

This guide walks you through setting up Foundry AIP integration with ABC. Foundry AIP uses OAuth2 authentication and provides SDK-based access to Foundry datasets.

---

## Prerequisites

- Foundry AIP developer account (free tier available)
- Python 3.9-3.11
- Access to Foundry instance: `https://ghsystems.usw-16.palantirfoundry.com`

---

## Step 1: Get Your Credentials

### 1.1 Get Client ID and Client Secret

1. Log into Foundry
2. Navigate to Settings → Third-party applications
3. Create a new application:
   - Application type: **Backend service**
   - Ontology: Select your ontology
   - Organization: Select your organization
4. Copy your **Client ID** and **Client Secret**

### 1.2 Get Personal Access Token

1. In Foundry, go to Settings → Tokens
2. Generate a new token (or use existing)
3. Copy the token (starts with `eyJ...`)

**Note:** This token is used for SDK installation. For production, generate a long-lived token.

---

## Step 2: Create .env File

Create a `.env` file in your project root with:

```bash
# Foundry AIP Configuration
FOUNDRY_URL=https://ghsystems.usw-16.palantirfoundry.com
FOUNDRY_CLIENT_ID=your-client-id-here
FOUNDRY_CLIENT_SECRET=your-client-secret-here

# Personal Access Token (for SDK installation)
FOUNDRY_TOKEN=your-token-here
```

**Important:** 
- Never commit `.env` to git (it's already in `.gitignore`)
- Never share your `.env` file
- Keep credentials secure

---

## Step 3: Install Foundry SDK

The Foundry SDK is installed from a private repository. You need your `FOUNDRY_TOKEN`:

```bash
# Set token (from .env or export directly)
export FOUNDRY_TOKEN=your-token-here

# Install SDK
pip install abc_integration_sdk==0.1.0 --upgrade \
  --index-url "https://user:$FOUNDRY_TOKEN@ghsystems.usw-16.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.7b7471ff-6f16-4988-b605-7c7beeb68ea3/contents/release/pypi/simple" \
  --extra-index-url "https://user:$FOUNDRY_TOKEN@ghsystems.usw-16.palantirfoundry.com/artifacts/api/repositories/ri.foundry-sdk-asset-bundle.main.artifacts.repository/contents/release/pypi/simple"
```

**Note:** If your organization requires certificates, set:
```bash
export SSL_CERT_FILE="/path/to/certificate.crt"
export REQUESTS_CA_BUNDLE="/path/to/certificate.crt"
```

---

## Step 4: Verify Setup

### 4.1 Check Configuration

```bash
python scripts/setup_foundry_aip.py
```

This verifies:
- `.env` file exists
- All required environment variables are set
- `.env` is in `.gitignore`
- Foundry SDK is installed

### 4.2 Test Connection

```bash
python scripts/test_foundry_connection.py
```

This tests:
- OAuth2 authentication
- Foundry client initialization
- Connection to Foundry instance

If successful, you'll see:
```
✅ SUCCESS! Connected to Foundry AIP!
```

---

## Step 5: Use Foundry in Your Code

### Basic Usage

```python
from src.verticals.ai_verification.core.nemesis.foundry_integration import FoundryIntegration

# Initialize with AIP (default)
foundry = FoundryIntegration(use_aip=True)

# List recent compilations
compilations = foundry.list_recent_compilations(limit=10)

# Get specific compilation
compilation = foundry.ingest_compilation("foundry-comp-2025-12-15-001")
```

### Direct AIP Connector Usage

```python
from src.verticals.ai_verification.core.nemesis.foundry_integration import FoundryAIPConnector

connector = FoundryAIPConnector()

# Read dataset
records = connector.read_dataset("gh_systems/intelligence_compilations", limit=10)

# Write data
result = connector.write_dataset(
    dataset_path="gh_systems/intelligence_compilations",
    data=[{"compilation_id": "test_001", "status": "success"}],
    mode="append"
)
```

---

## Troubleshooting

### Error: "Foundry SDK not installed"

**Solution:** Install the SDK using Step 3 above. Make sure `FOUNDRY_TOKEN` is set.

### Error: "Missing required environment variables"

**Solution:** 
1. Check `.env` file exists in project root
2. Verify all required variables are set:
   - `FOUNDRY_URL`
   - `FOUNDRY_CLIENT_ID`
   - `FOUNDRY_CLIENT_SECRET`

### Error: "Connection failed" or "Authentication failed"

**Solution:**
1. Verify `FOUNDRY_URL` is correct
2. Check `FOUNDRY_CLIENT_ID` and `FOUNDRY_CLIENT_SECRET` are correct
3. Ensure credentials haven't expired
4. Check network connectivity

### Error: "Dataset not found"

**Solution:**
1. Verify dataset path is correct
2. Check you have permission to access the dataset
3. Create the dataset in Foundry if it doesn't exist

### Error: "SSL certificate verification failed"

**Solution:**
```bash
export SSL_CERT_FILE="/path/to/certificate.crt"
export REQUESTS_CA_BUNDLE="/path/to/certificate.crt"
```

---

## Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore` for a reason
2. **Use environment variables** - Code reads from `os.getenv()`, never hardcoded
3. **Rotate credentials** - Regularly update Client Secret and tokens
4. **Use long-lived tokens for production** - Generate in Foundry settings
5. **Limit permissions** - Only grant necessary permissions to your application

---

## Next Steps

1. **Test connection** - Run `python scripts/test_foundry_connection.py`
2. **Read data** - Try reading from a Foundry dataset
3. **Write data** - Push ABC receipts to Foundry
4. **Integrate with ABC** - Use `FoundryIntegration` in your workflows

---

## Related Documentation

- [Foundry Integration Quickstart](FOUNDRY_INTEGRATION_QUICKSTART.md)
- [Foundry Connection Guide](FOUNDRY_CONNECTION_GUIDE.md)
- [Foundry Chain Specification](FOUNDRY_CHAIN_SPEC.md)

---

**Last Updated:** January 2025

