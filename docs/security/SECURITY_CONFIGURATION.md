# Security Configuration Guide

**GH Systems ABC - Government Deployment Security Configuration**

---

## Environment Variables

### Required Security Variables

```bash
# Flask Secret Keys (REQUIRED)
# Generate with: python3 -c "import secrets; print(secrets.token_hex(32))"
FLASK_SECRET_KEY=<64-character-hex-string>
DASHBOARD_SECRET_KEY=<64-character-hex-string>

# JWT Configuration (REQUIRED)
JWT_SECRET=<64-character-hex-string>
JWT_EXPIRATION_HOURS=24

# CORS Configuration (REQUIRED for production)
# Comma-separated list of allowed origins
# Example: CORS_ALLOWED_ORIGINS=https://app.ghsystems.com,https://admin.ghsystems.com
# Leave empty to disable CORS (most secure)
CORS_ALLOWED_ORIGINS=

# API Keys
FEDERAL_AI_API_KEY=<your-api-key>

# Environment
ENVIRONMENT=production  # or development
DEBUG=false  # MUST be false in production
```

### Optional Security Variables

```bash
# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60

# Request Size Limits
MAX_REQUEST_SIZE_BYTES=10485760  # 10MB default

# Audit Logging
AUDIT_LOGGING_ENABLED=true
AUDIT_LOG_FILE=audit.log

# Logging
LOG_LEVEL=INFO
LOG_SANITIZATION_ENABLED=true
```

---

## Generating Secrets

### Generate Secret Keys

```bash
# Generate a secure random secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Generate JWT Secret

```bash
# Generate JWT secret (same command)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All secret keys generated and stored securely
- [ ] Environment variables configured
- [ ] CORS origins whitelisted (production only)
- [ ] DEBUG mode disabled (`DEBUG=false`)
- [ ] Audit logging enabled
- [ ] Log sanitization enabled
- [ ] HTTPS configured at reverse proxy/load balancer
- [ ] Security headers configured
- [ ] Dependencies installed (`pip install -r requirements-security.txt`)

### Post-Deployment

- [ ] Authentication tested
- [ ] Rate limiting verified
- [ ] Request size limits tested
- [ ] Error messages sanitized (no system info leaked)
- [ ] Audit logs being written
- [ ] Logs reviewed for sensitive data
- [ ] Security headers present in responses

---

## Security Best Practices

### 1. Secret Management

**DO:**
- Use environment variables or secret management service (AWS Secrets Manager, HashiCorp Vault)
- Rotate secrets regularly
- Use different secrets for each environment

**DON'T:**
- Commit secrets to version control
- Share secrets via email/chat
- Use default or weak secrets

### 2. CORS Configuration

**Production:**
```bash
CORS_ALLOWED_ORIGINS=https://app.ghsystems.com,https://admin.ghsystems.com
```

**Development:**
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000
```

**Most Secure (No CORS):**
```bash
CORS_ALLOWED_ORIGINS=
```

### 3. Authentication

All API endpoints (except `/api/v1/health`) require authentication:

```bash
# Generate token
python3 -c "
from src.core.middleware.auth import generate_token
token = generate_token('user123', roles=['admin', 'operator'])
print(token)
"

# Use in requests
curl -H "Authorization: Bearer <token>" https://api.ghsystems.com/api/v1/compile
```

### 4. Rate Limiting

Default limits:
- General endpoints: 10 requests/minute
- Sensitive operations: 5 requests/minute
- Read-only endpoints: 20-30 requests/minute

Adjust via environment variables if needed.

### 5. Audit Logging

Audit logs are written to `audit.log` by default. In production:
- Use centralized logging (CloudWatch, Splunk, ELK)
- Set `AUDIT_LOG_FILE` to appropriate path
- Rotate logs regularly
- Monitor for suspicious activity

---

## Compliance Notes

### NIST 800-53 Controls Addressed

- **AC-2** (Account Management): ✅ JWT-based authentication
- **AC-3** (Access Enforcement): ✅ Role-based authorization
- **IA-5** (Authenticator Management): ✅ Environment-based secrets
- **SC-5** (Denial of Service Protection): ✅ Rate limiting
- **SC-7** (Boundary Protection): ✅ CORS configuration
- **SC-12** (Cryptographic Key Management): ✅ Environment-based keys
- **SI-10** (Information Input Validation): ✅ Enhanced validation
- **SI-11** (Error Handling): ✅ Sanitized error messages
- **AU-2** (Audit Events): ✅ Comprehensive audit logging

---

## Troubleshooting

### Authentication Fails

1. Check `JWT_SECRET` is set correctly
2. Verify token hasn't expired
3. Check token format: `Bearer <token>`

### Rate Limiting Too Strict

Adjust environment variables:
```bash
RATE_LIMIT_MAX_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
```

### CORS Errors

1. Verify `CORS_ALLOWED_ORIGINS` includes your origin
2. Check origin format (must include protocol: `https://`)
3. Restart application after changing CORS config

### Audit Logs Not Writing

1. Check `AUDIT_LOGGING_ENABLED=true`
2. Verify write permissions on log file directory
3. Check disk space

---

## Support

For security-related issues, contact the security team immediately.

**Security Contact:** security@ghsystems.com

