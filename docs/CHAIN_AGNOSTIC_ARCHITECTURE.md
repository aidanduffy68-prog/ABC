# Chain-Agnostic Architecture

**GH Systems ABC supports multiple blockchain networks for cryptographic verification and settlement**

## Overview

GH Systems ABC is designed to be **chain-agnostic**, allowing both vendors and agencies to choose their preferred blockchain network for receipt commitment and settlement. This flexibility ensures compatibility with different organizational requirements, regulatory constraints, and technical preferences.

## Supported Networks

### Currently Supported

- **Bitcoin** (`bitcoin`) - OP_RETURN transactions (80 bytes max)
- **Ethereum** (`ethereum`) - Event logs or contract storage
- **Polygon** (`polygon`) - EVM-compatible, lower fees
- **Arbitrum** (`arbitrum`) - EVM-compatible, Layer 2
- **Base** (`base`) - EVM-compatible, Coinbase L2
- **Optimism** (`optimism`) - EVM-compatible, Layer 2

### Adding New Networks

New blockchain networks can be added by implementing the `BlockchainAdapter` interface:

```python
from src.core.nemesis.on_chain_receipt.blockchain_abstraction import BlockchainAdapter

class MyChainAdapter(BlockchainAdapter):
    def commit_data(self, data: bytes, config: ChainConfig) -> OnChainCommitment:
        # Implement chain-specific commitment logic
        pass
    
    def verify_commitment(self, tx_hash: str, config: ChainConfig) -> Dict[str, Any]:
        # Implement chain-specific verification
        pass
    
    # ... implement other required methods
```

Then register the adapter:

```python
from src.core.nemesis.on_chain_receipt import BlockchainAdapterFactory, BlockchainNetwork

BlockchainAdapterFactory.register_adapter(BlockchainNetwork.MY_CHAIN, MyChainAdapter)
```

## Vendor Side (Ingestion)

### Specifying Preferred Blockchain

Vendors can specify their preferred blockchain network when submitting intelligence feeds:

```json
{
  "vendor": "Chainalysis",
  "timestamp": "2025-12-07T10:00:00Z",
  "data": [...],
  "preferred_blockchain": "ethereum"
}
```

### Supported Values

- `"bitcoin"` - Bitcoin mainnet
- `"ethereum"` - Ethereum mainnet
- `"polygon"` - Polygon network
- `"arbitrum"` - Arbitrum One
- `"base"` - Base network
- `"optimism"` - Optimism mainnet

If not specified, defaults to `"bitcoin"`.

### API Endpoint

```http
POST /api/v1/ingest/feed
Content-Type: application/json
Authorization: Bearer <vendor_token>

{
  "vendor": "TRM",
  "preferred_blockchain": "polygon",
  "data": [...]
}
```

## Agency Side (Compilation)

### Specifying Preferred Blockchain

Agencies can specify their preferred blockchain when requesting intelligence compilations:

```python
from src.core.nemesis.compilation_engine import ABCCompilationEngine

engine = ABCCompilationEngine()

compiled = engine.compile_intelligence(
    actor_id="threat_actor_001",
    actor_name="Lazarus Group",
    raw_intelligence=[...],
    preferred_blockchain="ethereum"  # Agency's preferred chain
)
```

### API Endpoint

```http
POST /api/v1/compile
Content-Type: application/json
Authorization: Bearer <agency_token>

{
  "actor_id": "threat_actor_001",
  "raw_intelligence": [...],
  "preferred_blockchain": "polygon"
}
```

## Receipt Structure

Receipts include blockchain network information:

```json
{
  "receipt_id": "abc_receipt_123",
  "intelligence_hash": "sha256:abc123...",
  "timestamp": "2025-12-07T10:00:00Z",
  "tx_hash": "0x1234...",
  "blockchain_network": "ethereum",
  "status": "committed"
}
```

## Chain-Specific Considerations

### Bitcoin

- **Data Size:** Maximum 80 bytes (OP_RETURN limit)
- **Fee Model:** Satoshis per byte
- **Confirmation Time:** ~10 minutes per block
- **Use Case:** Maximum security, immutable proof

### Ethereum & EVM Chains

- **Data Size:** Larger capacity (event logs or contract storage)
- **Fee Model:** Gas price (Wei)
- **Confirmation Time:** ~12 seconds (Ethereum), faster on L2s
- **Use Case:** Faster confirmations, lower fees on L2s

### Layer 2 Networks (Polygon, Arbitrum, Base, Optimism)

- **Data Size:** Same as Ethereum
- **Fee Model:** Significantly lower than Ethereum mainnet
- **Confirmation Time:** Faster than Ethereum mainnet
- **Use Case:** Cost-effective for high-volume operations

## Migration & Compatibility

### Default Behavior

- If no blockchain preference is specified, **Bitcoin is used as the default**
- Existing receipts without blockchain network specified are assumed to be Bitcoin
- Receipt verification works with any supported network

### Backward Compatibility

- Existing Bitcoin receipts continue to work
- New chain-agnostic features are opt-in
- No breaking changes to existing APIs

## Security Considerations

### Multi-Chain Verification

- Receipts can be verified on any supported network
- Cryptographic signatures are chain-agnostic (RSA-PSS)
- Hash verification works identically across all chains

### Network Selection

- Agencies should choose networks based on:
  - **Security requirements:** Bitcoin for maximum immutability
  - **Speed requirements:** EVM L2s for faster confirmations
  - **Cost considerations:** L2s for lower fees
  - **Regulatory compliance:** Some agencies may require specific chains

## Examples

### Vendor Submitting to Ethereum

```python
import requests

response = requests.post(
    "https://api.ghsystems.com/api/v1/ingest/feed",
    headers={"Authorization": "Bearer <vendor_token>"},
    json={
        "vendor": "TRM",
        "preferred_blockchain": "ethereum",
        "data": [...]
    }
)
```

### Agency Requesting Polygon Compilation

```python
from src.core.nemesis.compilation_engine import ABCCompilationEngine

engine = ABCCompilationEngine()

compiled = engine.compile_intelligence(
    actor_id="threat_actor_001",
    actor_name="Lazarus Group",
    raw_intelligence=[...],
    preferred_blockchain="polygon"  # Lower fees, faster confirmations
)

# Receipt will be committed to Polygon
print(compiled.targeting_package["receipt"]["blockchain_network"])  # "polygon"
print(compiled.targeting_package["receipt"]["tx_hash"])  # Polygon transaction hash
```

## Future Enhancements

- **Multi-chain commitments:** Commit same receipt to multiple chains for redundancy
- **Chain-specific optimizations:** Network-specific data formatting
- **Cross-chain verification:** Verify receipts across different chains
- **Automatic network selection:** AI-driven network selection based on requirements

---

**For technical implementation details, see:**
- `src/core/nemesis/on_chain_receipt/blockchain_abstraction.py`
- `src/core/nemesis/on_chain_receipt/bitcoin_adapter.py`
- `src/core/nemesis/on_chain_receipt/ethereum_adapter.py`

