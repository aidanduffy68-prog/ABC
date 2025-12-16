#!/bin/bash
# GH Systems ABC - Security Configuration Setup Script
# This script helps set up security environment variables

set -e

echo "=========================================="
echo "GH Systems ABC - Security Configuration"
echo "=========================================="
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists. Backing up to .env.backup"
    cp .env .env.backup
fi

# Generate secure secrets
echo "Generating secure secret keys..."
FLASK_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DASHBOARD_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create .env file
cat > .env << EOF
# GH Systems ABC - Environment Variables
# Generated: $(date)
# NEVER commit this file to version control

# Flask Secret Keys (REQUIRED)
FLASK_SECRET_KEY=${FLASK_SECRET}
DASHBOARD_SECRET_KEY=${DASHBOARD_SECRET}

# JWT Configuration (REQUIRED)
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRATION_HOURS=24

# CORS Configuration
# Comma-separated list of allowed origins
# Example: CORS_ALLOWED_ORIGINS=https://app.ghsystems.com,https://admin.ghsystems.com
# Leave empty to disable CORS (most secure for production)
CORS_ALLOWED_ORIGINS=

# API Keys
FEDERAL_AI_API_KEY=

# Environment
ENVIRONMENT=development
DEBUG=false

# Rate Limiting (optional)
RATE_LIMIT_MAX_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60

# Request Size Limits
MAX_REQUEST_SIZE_BYTES=10485760

# Audit Logging
AUDIT_LOGGING_ENABLED=true
AUDIT_LOG_FILE=audit.log

# Logging
LOG_LEVEL=INFO
LOG_SANITIZATION_ENABLED=true
EOF

echo "✅ .env file created successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Review .env file and update CORS_ALLOWED_ORIGINS if needed"
echo "2. Set FEDERAL_AI_API_KEY if you have one"
echo "3. For production, set ENVIRONMENT=production and DEBUG=false"
echo ""
echo "⚠️  IMPORTANT: Add .env to .gitignore if not already present"
echo ""
