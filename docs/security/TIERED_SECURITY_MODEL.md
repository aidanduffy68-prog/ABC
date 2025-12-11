# ABC Tiered Security Model

**Three-Tier Security Classification for Blockchain Commitments**

## Overview

GH Systems ABC implements a three-tier security model that ensures intelligence compilations are committed to blockchains with appropriate security controls based on classification level.

## Security Tiers

### Tier 1: Unclassified
**Public blockchains, anyone can verify**

- **Blockchain Type:** Public (Bitcoin, Ethereum, Polygon, Arbitrum, Base, Optimism)
- **Data Exposure:** Full - Complete intelligence data visible on-chain
- **Verification Access:** Public - Anyone can verify
- **Authentication:** Not required
- **Authorization:** Not required
- **Hash-Only:** No - Full data committed

**Use Cases:**
- Public threat intelligence
- Open-source intelligence (OSINT)
- Unclassified government assessments
- Public demonstrations

**Example:**
```python
from src.core.nemesis.on_chain_receipt.security_tier import SecurityTier, tiered_security_manager

tier = SecurityTier.TIER_1_UNCLASSIFIED
strategy = tiered_security_manager.get_commitment_strategy(tier, "ethereum")
# Result: Full data committed to Ethereum, public verification
```

---

### Tier 2: SBU (Sensitive But Unclassified)
**Permissioned chains, controlled access**

- **Blockchain Type:** Permissioned (Hyperledger, Corda, Quorum, Besu)
- **Data Exposure:** Controlled - Data visible only to authorized parties
- **Verification Access:** Permissioned - Requires authentication and authorization
- **Authentication:** Required
- **Authorization:** Required
- **Hash-Only:** No - Data committed but access-controlled

**Use Cases:**
- Sensitive but unclassified intelligence
- Inter-agency sharing
- Controlled distribution lists
- Internal government assessments

**Example:**
```python
tier = SecurityTier.TIER_2_SBU
strategy = tiered_security_manager.get_commitment_strategy(tier, "hyperledger")
# Result: Data committed to permissioned chain, access-controlled verification
```

---

### Tier 3: Classified
**Hash-only commitments, zero data exposure**

- **Blockchain Type:** Any (Bitcoin, Ethereum, or permissioned chains)
- **Data Exposure:** Zero - Only hash committed, no data on-chain
- **Verification Access:** Hash-only - Verify hash matches, no data access
- **Authentication:** Required
- **Authorization:** Required
- **Hash-Only:** Yes - Only cryptographic hash committed

**Use Cases:**
- Classified intelligence
- Secret/Top Secret assessments
- Zero-trust environments
- Maximum security requirements

**Example:**
```python
tier = SecurityTier.TIER_3_CLASSIFIED
strategy = tiered_security_manager.get_commitment_strategy(tier, "bitcoin")
# Result: Only hash committed to Bitcoin, zero data exposure
```

---

## Implementation

### Automatic Tier Detection

The system automatically determines the security tier from classification strings:

```python
from src.core.nemesis.on_chain_receipt.security_tier import tiered_security_manager

# Automatic tier detection
classification = "CLASSIFIED"
tier = tiered_security_manager.determine_tier_from_classification(classification)
# Returns: SecurityTier.TIER_3_CLASSIFIED

classification = "SBU"
tier = tiered_security_manager.determine_tier_from_classification(classification)
# Returns: SecurityTier.TIER_2_SBU

classification = "UNCLASSIFIED"
tier = tiered_security_manager.determine_tier_from_classification(classification)
# Returns: SecurityTier.TIER_1_UNCLASSIFIED
```

### Blockchain Validation

The system validates that the selected blockchain is appropriate for the security tier:

```python
# Valid: Ethereum for Tier 1
is_valid, error = tiered_security_manager.validate_blockchain_for_tier(
    SecurityTier.TIER_1_UNCLASSIFIED,
    "ethereum"
)
# Returns: (True, None)

# Invalid: Ethereum for Tier 2 (requires permissioned chain)
is_valid, error = tiered_security_manager.validate_blockchain_for_tier(
    SecurityTier.TIER_2_SBU,
    "ethereum"
)
# Returns: (False, "Blockchain 'ethereum' not allowed for SBU tier")
```

### Commitment Strategy

Get the commitment strategy for a tier and blockchain:

```python
strategy = tiered_security_manager.get_commitment_strategy(
    SecurityTier.TIER_3_CLASSIFIED,
    "bitcoin"
)

# Returns:
# {
#     "tier": "classified",
#     "tier_name": "Classified",
#     "blockchain": "bitcoin",
#     "commit_data": False,  # Hash-only
#     "commit_hash": True,
#     "requires_auth": True,
#     "requires_authorization": True,
#     "data_exposure": "zero",
#     "verification_access": "hash_only"
# }
```

---

## Security Guarantees

### Tier 1 (Unclassified)
- ✅ Full transparency
- ✅ Public verifiability
- ✅ No access controls
- ⚠️  Data visible to anyone

### Tier 2 (SBU)
- ✅ Controlled access
- ✅ Authentication required
- ✅ Authorization enforced
- ✅ Audit trail
- ⚠️  Data visible to authorized parties

### Tier 3 (Classified)
- ✅ Zero data exposure
- ✅ Hash-only commitment
- ✅ Cryptographic proof without data
- ✅ Maximum security
- ✅ Works on any blockchain

---

## Integration with Compilation Engine

The tiered security model integrates with the compilation engine:

```python
from src.core.nemesis.compilation_engine import ABCCompilationEngine
from src.core.nemesis.on_chain_receipt.security_tier import SecurityTier

engine = ABCCompilationEngine()

# Compile with security tier
result = engine.compile_intelligence(
    actor_id="threat_actor_001",
    raw_intelligence=[...],
    security_tier=SecurityTier.TIER_1_UNCLASSIFIED,
    preferred_blockchain="ethereum"
)

# For classified intelligence
result = engine.compile_intelligence(
    actor_id="classified_threat_001",
    raw_intelligence=[...],
    security_tier=SecurityTier.TIER_3_CLASSIFIED,
    preferred_blockchain="bitcoin"  # Hash-only, any chain works
)
```

---

## Comparison Table

| Feature | Tier 1 (Unclassified) | Tier 2 (SBU) | Tier 3 (Classified) |
|---------|----------------------|--------------|---------------------|
| **Blockchain Type** | Public | Permissioned | Any (hash-only) |
| **Data Exposure** | Full | Controlled | Zero |
| **Verification** | Public | Permissioned | Hash-only |
| **Authentication** | Not required | Required | Required |
| **Authorization** | Not required | Required | Required |
| **Hash-Only** | No | No | Yes |
| **Use Case** | Public intel | Sensitive intel | Classified intel |

---

## Best Practices

1. **Always specify security tier** - Don't rely on defaults for classified data
2. **Validate blockchain selection** - Ensure blockchain matches tier requirements
3. **Use Tier 3 for classified** - Never commit classified data, only hashes
4. **Audit tier selection** - Log tier decisions for compliance
5. **Review access controls** - Regularly audit Tier 2 permissions

---

## Compliance

This tiered security model aligns with:

- **NIST Cybersecurity Framework** - Risk-based security controls
- **DoD Information Security** - Classification handling
- **CISA Guidelines** - Zero-trust principles
- **Federal Information Security** - Multi-tier access controls

---

**Status:** ✅ **IMPLEMENTED** - Ready for integration with compilation engine

**Next Steps:**
1. Integrate with `ABCCompilationEngine`
2. Add tier selection to CLI tools
3. Add tier validation to API endpoints
4. Document in user guides

