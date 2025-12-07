# Compliance Note - Threat Intelligence Compilations

## Classification Status

**All threat intelligence compilations in this directory are:**
- **UNCLASSIFIED**
- **PUBLIC DEMONSTRATION MATERIALS**
- **NOT CLASSIFIED GOVERNMENT DOCUMENTS**

These are demonstration materials showing GH Systems ABC capabilities. They are:
- Based on publicly available information (OSINT)
- Not derived from classified sources
- Not actual government intelligence assessments
- For demonstration and marketing purposes only

## Cryptographic Claims

References to "cryptographically verifiable" intelligence assessments refer to:
- RSA-PSS signature support (when properly configured with private keys)
- SHA-256 hash-based verification
- Cryptographic receipt generation capabilities

**Production deployment requires:**
- RSA-4096 key pair generation and secure storage
- Proper key management configuration
- JWT_SECRET_KEY environment variable configuration

See `security/SECURITY_AUDIT_RESPONSE.md` for full security implementation details.

## Legal Disclaimer

These compilations are:
- **Demonstration materials** - not actual intelligence assessments
- **Public domain** - available in public GitHub repository
- **OSINT-based** - derived from publicly available sources only
- **Not classified** - do not contain classified information

GH Systems does not claim these represent actual government intelligence assessments or classified information.

---

**Last Updated:** December 7, 2025

