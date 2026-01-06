# ABC Verification Demo Video Script
## AML Training Use Case: DeFi Protocol Layering

**Duration:** 6-8 minutes  
**Format:** Screen recording with voiceover  
**Use Case:** Training AI models to detect complex AML exploits (DeFi protocol layering) using synthetic data + ABC verification

---

## Video Overview

This demo shows how ABC verifies data integrity for AML compliance training on complex, underrepresented exploits. We use synthetic DeFi protocol layering data to train AI models safely. When models disagree about whether a transaction is suspicious, ABC proves they analyzed the same source data.

---

## Script

### Opening (0:00 - 0:45)

**[Screen: Title slide]**

"Have you ever wanted to build the perfect crypto crime AI for AML?"

**[Screen: Problem statement slide]**

"Here's the challenge: Agencies need to train AI models to detect complex AML exploits like DeFi protocol layering — where criminals move funds through multiple DeFi platforms to obscure transaction trails. But they can't use real customer data due to privacy regulations. The solution? Synthetic AML data with complex patterns, verified by ABC. I'm Aidan from GH Systems, and today I'll show you how ABC makes this possible."

**[Screen: Switch to Foundry]**

---

### Part 1: Synthetic DeFi Layering Data in Foundry (0:45 - 3:30)

**[Screen: Show Foundry pipeline with DeFi layering data]**

"Here's our Foundry pipeline processing synthetic data for a complex AML exploit: DeFi protocol layering."

**[Screen: Point to data source]**

"This is synthetic blockchain transaction data showing DeFi layering patterns — where criminals move funds through multiple DeFi platforms like Uniswap, Aave, and Compound to obscure transaction trails. We use synthetic data because we can't expose real customer transactions for training. This pattern is often missed in traditional AML investigations because it requires tracking across multiple protocols."

**[Screen: Show data preview with DeFi layering transaction]**

"You can see we have block data in a table format. Each row represents a blockchain block. Look at block 835023 — it has 2069 total transactions, and 310 of those are DeFi layering transactions. The `transactions` column shows the count of complex layering patterns in each block. These layering transactions represent complex money laundering patterns where funds move through multiple DeFi protocols like Uniswap, Aave, Compound, and others to obscure transaction trails. This creates a complex trail that's hard to trace — exactly the kind of pattern AI models need to learn to detect."

**[Screen: Point to ABC receipt transform]**

"This transform generates ABC receipts — cryptographic hashes that prove data integrity. Each block of transactions gets a unique ABC receipt hash. This is critical because when AI models disagree about whether a transaction is suspicious, ABC proves they analyzed the same source data."

**[Screen: Show ABC receipt column]**

"Every record now has an `abc_receipt_hash` — this is the cryptographic proof that regulators can verify. When multiple agencies train models on this data and get different results, ABC proves they all analyzed identical source data."

**[Screen: Point to verification transform]**

"This transform verifies the receipts — it recomputes the hash and compares it to ensure data integrity."

**[Screen: Show verification results]**

"All records show `verified: true` — proving our synthetic DeFi layering data is legitimate and ready for model training."

**[Screen: Show final output]**

"Here's our verified synthetic AML dataset — every transaction block has an ABC receipt and is verified. This complex DeFi layering data is now safe to use for training AI models, and when models disagree, ABC proves they analyzed the same data."

---

### Part 2: API Verification (3:30 - 6:00)

**[Screen: Switch to terminal]**

"Now let's verify the same DeFi layering data via our API. This shows ABC works across systems — whether you're using Foundry pipelines or API calls."

**[Screen: Show API running]**

"Our ABC Verification API is running and ready."

**[Screen: Run health check]**

"First, let's check the API is healthy."

**[Run command:]**
```bash
curl http://localhost:8000/health
```

**[Screen: Show response]**

"API is healthy and connected."

**[Screen: Run verification]**

"Now let's verify one of our synthetic DeFi layering transaction blocks from Foundry."

**[Run command:]**
```bash
curl -X POST "http://localhost:8000/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "block_data": {
      "block_height": 835023,
      "block_hash": "7ef012d1074743443383c1",
      "timestamp": 2268429478,
      "tx_count": 2069,
      "transactions": "[{\"txid\":\"defi_layering_835023_1\",\"pattern\":\"defi_layering\",\"value\":84.17}]"
    },
    "abc_receipt_hash": "d7a4f84538834436d513f233a27c232e51689e6c391d57b7e6c762d570775488"
  }' | python3 -m json.tool
```

**[Screen: Show response, highlight "verified": true]**

"Verified: true. The same synthetic DeFi layering data, verified the same way — ABC works consistently across systems."

**[Screen: Point to hash match]**

"The computed hash matches the Foundry hash exactly. This proves to regulators that our synthetic training data is legitimate and hasn't been tampered with. When AI models disagree about whether this DeFi layering pattern is suspicious, ABC proves they all analyzed the same source data."

---

### Part 3: Use Case & Value (6:00 - 7:00)

**[Screen: Show Intelligence Value Protected (IVP) visual]**

"This chart shows Intelligence Value Protected — ABC blockchain-verified data versus traditional information security."

**[Screen: Point to the three phases]**

"Three phases drive ABC's growth: Proof of Value as agencies adopt it for AML training on complex exploits like DeFi layering, Network Effects as agencies share verified data, and Mandate Effect as regulators require ABC verification. ABC grows exponentially while Traditional InfoSec stays flat — it can't provide the cryptographic proof regulators need."

**[Screen: Value proposition]**

"The result: Agencies can train AML detection models safely with synthetic data on complex, underrepresented exploits like DeFi protocol layering. When models disagree about whether a transaction is suspicious, ABC proves they analyzed the same source data. Regulators have cryptographic proof the training data is legitimate. ABC makes synthetic data compliance-ready — and compliance-mandated."

---

### Closing (7:30 - 8:00)

**[Screen: Summary slide]**

"To summarize: ABC verifies synthetic AML data for AI model training, including complex exploits like DeFi protocol layering. When AI models disagree about whether a transaction is suspicious, ABC proves they analyzed the same source data. It provides cryptographic proof of data integrity that regulators can verify. It works in Foundry pipelines and via API, making it ready for compliance use."

**[Screen: Your logo or contact info]**

"Thanks for watching. For more information about ABC verification for AML compliance, visit [your website] or contact [your email]."

---

## Detailed Action Script (AML-Focused)

### Scene 1: Opening & Problem (45 seconds)

| Time | Action | What to Say |
|------|--------|-------------|
| 0:00 | Show title/logo | "Have you ever wanted to build the perfect crypto crime AI for AML?" |
| 0:10 | Show problem slide | "Here's the challenge: Agencies need to train AI models..." |
| 0:20 | Explain the challenge | "But they can't use real customer data due to privacy regulations..." |
| 0:30 | Introduce solution | "The solution? Synthetic AML data verified by ABC. I'm Aidan from GH Systems..." |
| 0:45 | [Transition] | "Let's see how it works." |

---

### Scene 2: Foundry Pipeline - DeFi Layering Data (2:45)

| Time | Action | What to Say |
|------|--------|-------------|
| 0:45 | Show Foundry pipeline | "Here's our pipeline for DeFi protocol layering data..." |
| 1:00 | Point to data source | "This is synthetic data showing complex DeFi layering patterns..." |
| 1:15 | Explain why synthetic | "We use synthetic data because we can't expose real transactions..." |
| 1:30 | Show DeFi layering transaction | "Look at this 5-hop pattern: Curve → Balancer → MakerDAO → Yearn → Sushiswap..." |
| 1:45 | Explain complexity | "This pattern is often missed in traditional AML investigations..." |
| 2:00 | Point to ABC transform | "This generates ABC receipts..." |
| 2:10 | Explain ABC value | "When models disagree, ABC proves they analyzed the same data..." |
| 2:20 | Show receipts column | "Each block gets a cryptographic hash..." |
| 2:25 | Point to verification | "This verifies the receipts..." |
| 2:35 | Show verified results | "All verified — ready for training..." |
| 2:45 | [Transition] | "Now let's verify via API." |

---

### Scene 3: API Verification (2:30)

| Time | Action | What to Say |
|------|--------|-------------|
| 3:30 | Switch to terminal | "Let's verify the same DeFi layering data via API..." |
| 3:40 | Show API running | "Our ABC Verification API is ready..." |
| 3:50 | Run health check | "API is healthy..." |
| 4:00 | Prepare verification | "Now let's verify our synthetic DeFi layering data..." |
| 4:10 | Run curl command | [Paste command with DeFi layering block] |
| 4:30 | Show response | "Verified: true — same result..." |
| 4:40 | Explain consistency | "ABC works consistently across systems..." |
| 4:50 | Highlight model disagreement value | "When models disagree about this DeFi pattern, ABC proves same data..." |
| 5:00 | [Transition] | "Here's why this matters." |

---

### Scene 4: Use Case & Value (1:00)

| Time | Action | What to Say |
|------|--------|-------------|
| 6:00 | Show IVP visual | "Intelligence Value Protected — ABC vs Traditional InfoSec..." |
| 6:10 | Point to three phases | "Three phases: Proof of Value, Network Effects, Mandate Effect..." |
| 6:20 | Explain growth | "ABC grows exponentially, Traditional InfoSec stays flat..." |
| 6:30 | Explain value | "Agencies train safely, regulators have cryptographic proof..." |
| 6:40 | Summarize | "ABC makes synthetic data compliance-ready and mandated..." |
| 7:00 | [Transition] | "Let's summarize." |

---

### Scene 5: Closing (30 seconds)

| Time | Action | What to Say |
|------|--------|-------------|
| 7:30 | Show summary | "ABC verifies synthetic AML data..." |
| 7:40 | List key points | "Provides cryptographic proof..." |
| 7:50 | Show value | "Ready for compliance use..." |
| 8:00 | Show logo/contact | "Thanks for watching..." |

---

## Key Talking Points (AML-Focused)

### Opening
- "Have you ever wanted to build the perfect crypto crime AI for AML?"
- "Challenge: Agencies need to train AI models but can't use real customer data"
- "Solution: Synthetic AML data verified by ABC"

### Foundry Section
- "This is synthetic DeFi protocol layering data"
- "Complex AML exploit: multi-hop transactions through multiple DeFi platforms"
- "Pattern often missed in traditional AML investigations"
- "ABC receipts prove data integrity"
- "When models disagree, ABC proves they analyzed the same source data"

### API Section
- "Same synthetic DeFi layering data, verified via API"
- "ABC works consistently across systems"
- "When models disagree about DeFi patterns, ABC proves same data"

### Use Case
- "Intelligence Value Protected visual — ABC vs Traditional InfoSec"
- "Phase 1: Proof of Value — steady growth as agencies train on complex exploits like DeFi layering"
- "Phase 2: Network Effects — accelerating growth as agencies share verified training data"
- "Phase 3: Mandate Effect — exponential growth as regulators mandate ABC verification"
- "ABC grows exponentially while Traditional InfoSec stays flat — shows value of blockchain verification"
- "When AI models disagree about DeFi layering patterns, ABC proves they analyzed the same data"
- "ABC makes synthetic data compliance-ready — and compliance-mandated"

### Closing
- "ABC verifies synthetic AML data for training"
- "Provides cryptographic proof for regulators"
- "Ready for compliance and regulatory use"

---

## Visual Cues

### Foundry
- Label data as "Synthetic AML Transaction Data"
- Highlight "Synthetic" to emphasize it's not real customer data
- Show ABC receipts as "Regulator-Verifiable Proof"
- Emphasize "Ready for Model Training"

### API
- Frame as "Verifying Synthetic AML Data"
- Highlight "Same data, regulator-verifiable"
- Show consistency across systems

### IVP Visual (Intelligence Value Protected)
- Show the full graph with ABC (green line) vs Traditional InfoSec (black dashed line)
- Point to three phases: Proof of Value (2026), Network Effects (2027), Mandate Effect (2028)
- Highlight the exponential growth of ABC ($1B → $75B) vs flat Traditional InfoSec ($0-2B)
- Emphasize the gap between lines to show ABC's value
- Connect phases to AML compliance adoption timeline

---

## Pro Tips for AML Demo

1. **Emphasize "synthetic"** - Make it clear this is NOT real customer data
2. **Connect to compliance** - Show how regulators can verify
3. **Show training value** - Explain why this data is safe for AI models
4. **Highlight ABC's role** - Cryptographic proof for regulators
5. **Keep it concrete** - AML detection use case throughout

---

## Quick Reference Card (AML Version)

### Opening
- "Have you ever wanted to build the perfect crypto crime AI for AML?"
- "Challenge: Can't use real customer data"
- "Solution: Synthetic AML data verified by ABC"

### Foundry
- "Synthetic DeFi protocol layering data"
- "Complex AML exploit: multi-hop through multiple DeFi platforms"
- "ABC receipts for regulator verification"
- "All verified — ready for training"

### API
- "Verify same synthetic AML data"
- "ABC works across systems"
- "Regulators can verify"

### IVP Visual (Use Case & Value)
- "Intelligence Value Protected — ABC vs Traditional InfoSec"
- "Phase 1: Proof of Value — steady growth as agencies start using ABC"
- "Phase 2: Network Effects — accelerating growth as agencies share verified data"
- "Phase 3: Mandate Effect — exponential growth as regulators mandate ABC"
- "ABC grows exponentially, Traditional InfoSec stays flat"

### Closing
- "ABC verifies synthetic AML data including complex DeFi layering patterns"
- "When models disagree, ABC proves they analyzed the same data"
- "Compliance-ready and compliance-mandated"
- "Ready for regulatory use"

---

## Commands for Demo

### Health Check
```bash
curl http://localhost:8000/health
```

### Verify Record 1
```bash
curl -X POST "http://localhost:8000/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "block_data": {
      "block_height": 825000,
      "block_hash": "94f84c7be087799b54c3e4adce1f9012a7e3c8d4b6f5a2e1c9d8b7a6f5e4d3c2",
      "timestamp": 1735689600,
      "tx_count": 2453,
      "transactions": "[{\"txid\":\"abc123\",\"value\":0.5}]"
    },
    "abc_receipt_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b"
  }' | python3 -m json.tool
```

### One-Liner Version
```bash
curl -X POST "http://localhost:8000/verify" -H "Content-Type: application/json" -d '{"block_data":{"block_height":825000,"block_hash":"94f84c7be087799b54c3e4adce1f9012a7e3c8d4b6f5a2e1c9d8b7a6f5e4d3c2","timestamp":1735689600,"tx_count":2453,"transactions":"[{\"txid\":\"abc123\",\"value\":0.5}]"},"abc_receipt_hash":"472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b"}' | python3 -m json.tool
```

---

## Expected API Response

```json
{
    "success": true,
    "result": {
        "verified": true,
        "block_height": 825000,
        "foundry_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b",
        "computed_hash": "472dc3097fb9f4a1228e6cb5a0202b11a9fe3751dffa1065b781eca848ddb94b",
        "timestamp": "2026-01-01T..."
    },
    "message": "Verification complete"
}
```

---

## Demo Checklist

### Before Recording
- [ ] Foundry pipeline ready with synthetic AML data
- [ ] All records verified (verified: true)
- [ ] API service running
- [ ] Terminal ready with curl commands
- [ ] Screen recording software ready

### During Recording
- [ ] Show Foundry pipeline clearly
- [ ] Highlight synthetic data aspect
- [ ] Show ABC receipts and verification
- [ ] Demonstrate API verification
- [ ] Emphasize compliance/regulator value

### After Recording
- [ ] Review for clarity
- [ ] Check timing (6-8 minutes)
- [ ] Verify all key points covered
- [ ] Add captions if needed

---

**Copyright (c) 2026 GH Systems. All rights reserved.**

