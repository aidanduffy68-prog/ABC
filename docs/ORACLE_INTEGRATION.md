# ABC Oracle Integration Guide

## Overview

The ABC Oracle provides verified blockchain data feeds for enterprise systems like Palantir Foundry. This guide covers integration, API usage, and best practices.

**Use Case:** Foundry for AML enables banks to deploy ML models for risk scoring. ABC Oracle provides cryptographic verification that all models analyzed identical customer data—critical for regulatory audit and explainability.

---

## Quick Start

### 1. Start Bitcoin Node

```bash
docker-compose up bitcoin-node -d
```

### 2. Configure Environment

Copy `.env.oracle.example` to `.env` and configure:

```bash
ORACLE_ENABLED=true
BITCOIN_RPC_URL=http://localhost:8332
BITCOIN_RPC_USER=abc_oracle
BITCOIN_RPC_PASSWORD=your_password
```

### 3. Start ABC API

```bash
python src/cli/run_api_server.py
```

### 4. Ingest Blockchain Data

```bash
curl -X POST http://localhost:8000/api/v1/oracle/ingest/bitcoin/block/825000
```

### 5. Stream Real-Time Data

```bash
wscat -c ws://localhost:8000/api/v1/oracle/stream/bitcoin
```

---

## API Reference

### Health Check

**Endpoint:** `GET /api/v1/oracle/health`

**Response:**

```json
{
  "status": "healthy",
  "bitcoin": {
    "connected": true,
    "latest_block": 825000
  }
}
```

### Ingest Block

**Endpoint:** `POST /api/v1/oracle/ingest/bitcoin/block/{block_height}`

**Parameters:**
- `block_height`: Block height to ingest
- `generate_receipt`: Generate cryptographic receipt (default: true)
- `anchor_to_blockchain`: Anchor receipt to blockchain (default: false)

**Response:**

```json
{
  "block_height": 825000,
  "block_hash": "00000000000000000002a...",
  "tx_count": 2453,
  "receipt": {
    "receipt_id": "abc_receipt_bitcoin_block_825000_1735516800",
    "intelligence_hash": "a3f5b8c2d9e1f4a7...",
    "timestamp": "2026-01-15T10:30:00Z"
  },
  "ingested_at": "2026-01-15T10:30:05Z"
}
```

### Verify External Source

**Endpoint:** `POST /api/v1/oracle/verify/source`

**Parameters:**
- `receipt_id`: ABC receipt ID
- `source_name`: Name of external source (e.g., "chainalysis")
- `source_data_hash`: Hash of data used by source

**Response:**

```json
{
  "verified": true,
  "receipt_id": "abc_receipt_...",
  "source": "chainalysis",
  "abc_hash": "a3f5b8c2...",
  "source_hash": "a3f5b8c2...",
  "match": true
}
```

### WebSocket Stream

**Endpoint:** `ws://localhost:8000/api/v1/oracle/stream/bitcoin`

**Message Format:**

```json
{
  "type": "block",
  "blockchain": "bitcoin",
  "block_height": 825001,
  "block_hash": "00000000000000000003b...",
  "tx_count": 2567,
  "receipt_id": "abc_receipt_...",
  "data_hash": "b4c6d8e2...",
  "timestamp": "2026-01-15T10:40:00Z"
}
```

---

## Foundry Integration

### Ingest Blockchain Data

```python
import requests

# Ingest Bitcoin blocks for Foundry
response = requests.post(
    "http://localhost:8000/api/v1/foundry/ingest/blockchain",
    json={
        "blockchain": "bitcoin",
        "start_height": 825000,
        "end_height": 825100,
        "generate_receipts": True
    },
    headers={"Authorization": "Bearer your_token"}
)

receipts = response.json()['receipts']
```

### Verify ML Models

```python
# After Foundry ML models analyze data
response = requests.post(
    "http://localhost:8000/api/v1/foundry/verify/ml-models",
    json={
        "receipt_id": "abc_receipt_...",
        "model_results": [
            {
                "model_id": "kyc-risk-v2",
                "data_hash": "a3f5b8c2...",
                "output": {"risk_score": 0.85}
            },
            {
                "model_id": "txn-monitor-v1",
                "data_hash": "a3f5b8c2...",
                "output": {"risk_score": 0.62}
            }
        ]
    },
    headers={"Authorization": "Bearer your_token"}
)

verification = response.json()
print(f"All models used identical data: {verification['verified']}")
```

---

## Best Practices

### 1. Receipt Storage

Store ABC receipts alongside your data for audit trails:

```python
# When ingesting data
result = requests.post(
    "http://localhost:8000/api/v1/oracle/ingest/bitcoin/block/825000"
).json()

receipt = result['receipt']

# Store receipt with your data
database.store({
    "data": result['data_package'],
    "abc_receipt": receipt,
    "ingested_at": datetime.utcnow()
})
```

### 2. Verification Workflow

Always verify external sources against ABC receipts:

```python
# When consuming data from Chainalysis
chainalysis_data = get_chainalysis_data()
chainalysis_hash = compute_hash(chainalysis_data)

# Verify against ABC receipt
verification = requests.post(
    "http://localhost:8000/api/v1/oracle/verify/source",
    params={
        "receipt_id": "abc_receipt_...",
        "source_name": "chainalysis",
        "source_data_hash": chainalysis_hash
    }
).json()

if verification['verified']:
    # Safe to use data
    process_data(chainalysis_data)
else:
    # Data mismatch - investigate
    log_warning("Chainalysis data does not match ABC receipt")
```

### 3. Real-Time Streaming

Use WebSocket streams for real-time data:

```python
import websockets
import asyncio
import json

async def stream_bitcoin_data():
    uri = "ws://localhost:8000/api/v1/oracle/stream/bitcoin"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            # Process new block
            process_block(data)

asyncio.run(stream_bitcoin_data())
```

---

## Troubleshooting

### Bitcoin Node Not Connected

```bash
# Check Bitcoin node status
docker logs abc-bitcoin-node

# Restart Bitcoin node
docker-compose restart bitcoin-node

# Check connection
curl http://localhost:8332 -u abc_oracle:password -d '{"method":"getblockcount","params":[]}'
```

### Oracle Disabled

If oracle endpoints return 503, check:

1. `ORACLE_ENABLED=true` in environment
2. Bitcoin node is running and accessible
3. Dependencies installed: `pip install python-bitcoinlib websockets`

### Receipt Not Found

Receipts are stored in memory (database layer pending). Check API logs for receipt IDs.

---

## Architecture

```
ABC Oracle Layer
├── Bitcoin Ingestion
│   ├── RPC Connection
│   ├── Block Parsing
│   └── Receipt Generation
├── Data Feed API
│   ├── REST Endpoints
│   └── WebSocket Streams
└── Multi-Source Verification
    ├── External Source Verification
    └── ML Model Verification
```

---

## Next Steps

- [Foundry Chain Specification](integrations/FOUNDRY_CHAIN_SPEC.md) - Complete Foundry integration guide
- [Architecture Specification](architecture/ARCHITECTURE_SPEC.md) - Full technical details
- [Partnership Model](PARTNERSHIP_MODEL.md) - ABC + Foundry partnership structure

