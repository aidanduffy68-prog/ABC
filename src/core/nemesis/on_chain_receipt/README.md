# On-Chain Cryptographic Receipt System

**Everything proprietary stays off-chain. Only tiny cryptographic proofs go on-chain.**

## Overview

The on-chain receipt system generates minimal cryptographic proofs of intelligence outputs without revealing proprietary systems. This turns intelligence into verifiable objects that can be used everywhere—beyond settlements, into workflows.

## Core Principle

- **Off-Chain:** All AI models, full intelligence packages, proprietary systems
- **On-Chain:** Tiny cryptographic receipt (hash, timestamp, signature, minimal metadata)

## What This Enables

1. **Verifiable Intelligence Objects** — Intelligence becomes cryptographically provable
2. **Beyond Settlements → Workflows** — Usable in any system, not just payments
3. **Usable Everywhere** — Portable, trustworthy intelligence

## Usage

```python
from nemesis.on_chain_receipt import CryptographicReceiptGenerator

# Initialize generator
generator = CryptographicReceiptGenerator()

# Generate receipt for intelligence package
intelligence_package = {
    "actor_id": "LAZARUS_GROUP",
    "threat_level": "critical",
    # ... full proprietary intelligence
}

receipt = generator.generate_receipt(
    intelligence_package=intelligence_package,
    actor_id="LAZARUS_GROUP",
    threat_level="critical",
    package_type="targeting_package"
)

# Verify receipt
is_valid = generator.verify_receipt(receipt, intelligence_package)

# Prepare for on-chain commitment
on_chain_data = generator.prepare_for_on_chain(receipt)

# Commit to Bitcoin blockchain
tx_hash = generator.commit_to_blockchain(receipt)
```

## Receipt Structure

**On-Chain (Minimal):**
- `receipt_id` — Unique receipt identifier
- `intelligence_hash` — SHA-256 hash of full intelligence package
- `timestamp` — ISO format timestamp
- `actor_id` — Target actor ID (optional)
- `threat_level` — Threat classification (optional)
- `package_type` — Type of package (optional)
- `signature` — GH Systems cryptographic signature
- `version` — Receipt version

**Off-Chain (Full Intelligence):**
- Complete behavioral signatures
- Full threat dossiers
- Predictive forecasts
- All proprietary analysis
- Full context and evidence

## Integration

The receipt system integrates with:
- **Nemesis** — Generate receipts for targeting packages
- **Threat Dossiers** — Receipts for dossier outputs
- **Predictive Models** — Receipts for forecasts
- **Bitcoin Settlement** — Link receipts to payments

## Licensee Contributions

**Licensees can contribute intelligence via BTC without revealing proprietary information.**

The receipt system enables bidirectional intelligence flow:
- **GH Systems → Licensees:** Receive intelligence with cryptographic receipts
- **Licensees → GH Systems:** Contribute intelligence with cryptographic receipts

Licensees submit intelligence packages and receive cryptographic receipts, just like they receive intelligence from GH Systems. This creates a network where intelligence flows both ways while keeping all proprietary systems private.

```python
# Licensee contributes intelligence
generator = CryptographicReceiptGenerator(licensee_id="licensee_001")
receipt = generator.generate_licensee_contribution_receipt(
    intelligence_package=licensee_intelligence,
    licensee_id="licensee_001",
    actor_id="SUSPECT_ACTOR",
    threat_level="high"
)

# Commit to blockchain for BTC settlement
tx_hash = generator.commit_to_blockchain(receipt)
```

## Benefits

1. **Privacy** — Proprietary systems stay private
2. **Verifiability** — Output is cryptographically provable
3. **Portability** — Intelligence can be used anywhere
4. **Trust** — Proof of authenticity without revealing methods
5. **Workflow Integration** — Not just payments, but actual intelligence workflows
6. **Bidirectional Flow** — Licensees can contribute intelligence via BTC without revealing proprietary info

---

*GH Systems — Turning intelligence into verifiable objects.*

