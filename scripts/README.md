# GH Systems ABC - Scripts

Utility scripts for GH Systems ABC platform.

## compile_intelligence.py

Command-line tool to compile threat intelligence using the ABC engine.

### Installation

```bash
chmod +x scripts/compile_intelligence.py
```

### Usage

#### Standard Actor Compilation

```bash
python scripts/compile_intelligence.py \
  --actor-id "lazarus_001" \
  --actor-name "Lazarus Group" \
  --intel-file intelligence.json
```

#### Federal AI Compilation

```bash
python scripts/compile_intelligence.py \
  --federal-ai \
  --agency "DoD" \
  --vuln-file vulnerabilities.json \
  --ai-system-file ai_systems.json
```

#### With Transaction Data

```bash
python scripts/compile_intelligence.py \
  --actor-id "threat_actor_001" \
  --actor-name "Threat Actor" \
  --intel-file intelligence.json \
  --transaction-file transactions.json \
  --network-file network.json
```

#### Save Output

```bash
python scripts/compile_intelligence.py \
  --actor-id "lazarus_001" \
  --actor-name "Lazarus Group" \
  --intel-file intelligence.json \
  --output compiled_intelligence.json
```

### Arguments

**Standard Mode:**
- `--actor-id` - Actor identifier (required)
- `--actor-name` - Actor name/designation (required)
- `--intel-file` - Path to intelligence data JSON (required)
- `--transaction-file` - Path to transaction data JSON (optional)
- `--network-file` - Path to network data JSON (optional)

**Federal AI Mode:**
- `--federal-ai` - Enable federal AI compilation mode
- `--agency` - Agency name (DoD, DHS, NASA, etc.) (required)
- `--vuln-file` - Path to vulnerability data JSON (optional)
- `--ai-system-file` - Path to AI system data JSON (optional)

**Output Options:**
- `--output` - Save compiled intelligence to JSON file
- `--no-receipt` - Skip cryptographic receipt generation

### Example Intelligence Data Format

```json
[
  {
    "text": "North Korean hackers coordinating with Russian facilitators",
    "source": "intel_feed_1",
    "type": "intelligence_report"
  },
  {
    "text": "Multiple wallets showing synchronized transaction patterns",
    "source": "blockchain_analysis",
    "type": "transaction_analysis"
  }
]
```

### Example Transaction Data Format

```json
[
  {
    "tx_hash": "0x123...",
    "from": "0xabc...",
    "to": "0xdef...",
    "value": 1000000,
    "timestamp": "2025-11-29T10:00:00Z"
  }
]
```

