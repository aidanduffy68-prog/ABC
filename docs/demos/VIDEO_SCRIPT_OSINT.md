# ABC Core Mechanism Demo Video Script
## OSINT: Synthetic (Good) vs Artificial (Bad) Data Detection

**Duration:** 5-6 minutes  
**Format:** Screen recording with voiceover  
**Focus:** Core ABC mechanism applied to OSINT - hash match = good, hash mismatch = bad

---

## Video Overview

This demo shows ABC's core mechanism applied to OSINT (Open Source Intelligence): detecting synthetic (good) vs artificial (bad) data through hash verification. When threat intelligence models struggle, ABC identifies whether the issue is legitimate complex OSINT or deceptive data injection.

---

## Script

### Opening (0:00 - 0:30)

**[Screen: Title slide]**

"ABC for OSINT: Hash Match = Good, Hash Mismatch = Bad"

**[Screen: Problem statement]**

"Threat intelligence models training on OSINT data struggle. Is it complex legitimate intelligence, or deceptive data injection? ABC detects the difference. I'm Aidan from GH Systems, and I'll show you how ABC verifies OSINT data integrity."

**[Screen: Switch to terminal/API]**

---

### Part 1: The Problem - Threat Intelligence Model Struggles (0:30 - 1:30)

**[Screen: Show threat intelligence model output with low confidence]**

"Here's a threat intelligence model analyzing OSINT data - social media posts, forum discussions, public records. It's struggling with certain patterns - low confidence, inconsistent threat assessments. The question is: why?"

**[Screen: Show OSINT data table]**

"Is this legitimate complex OSINT that's hard to analyze? Or is it artificial data injection - fake social media posts, manipulated forum discussions - corrupting the model?"

**[Screen: Highlight the core question]**

"Without ABC, there's no way to tell. That's the bottleneck for threat intelligence."

---

### Part 2: Core Mechanism - Hash Verification for OSINT (1:30 - 2:30)

**[Screen: Show ABC core mechanism diagram]**

"ABC's core mechanism is simple, and it works for OSINT too:"

**[Screen: Show hash match]**

"Hash match = Synthetic (good) OSINT data ✅"
"Legitimate OSINT sources - real social media, authentic forum posts, verified public records. Data integrity verified."

**[Screen: Show hash mismatch]**

"Hash mismatch = Artificial (bad) OSINT data ❌"
"Deceptive OSINT injection - fake posts, manipulated discussions, fabricated intelligence. Data integrity compromised."

**[Screen: Show the verification process]**

"ABC generates a cryptographic hash for each OSINT record. When you verify, it recomputes the hash and compares. If they match, the OSINT is good. If they don't, it's bad."

---

### Part 3: Human Workflow - Scan OSINT and Detect (2:30 - 4:00)

**[Screen: Switch to terminal]**

"Let's see this in action. Our threat intelligence model is struggling, so a human analyst scans the Foundry compilation of OSINT data for hash mismatches."

**[Screen: Run scan command]**

```bash
curl -X POST "http://localhost:8000/foundry/scan-hash-mismatches" \
  -H "Content-Type: application/json" \
  -d '{
    "compilation_id": "osint_verification_output",
    "dataset_path": "gh_systems/osint_compilations"
  }'
```

**[Screen: Show response]**

"Look at the results:"
- "Total OSINT records: 5000"
- "Synthetic (good): 4750 ✅"
- "Artificial (bad): 250 ❌"

**[Screen: Highlight artificial records]**

"ABC detected 250 OSINT records with hash mismatches - artificial (bad) data. These are corrupting the threat intelligence model."

**[Screen: Show one artificial record]**

"Here's one: OSINT record ID 2026-01-05-1432. It's supposed to be a social media post about a potential threat. But the hash from Foundry doesn't match what ABC computes. This is artificial (bad) OSINT - deceptive injection, possibly fake posts or manipulated intelligence."

---

### Part 4: Human Verifies and Commits OSINT Classification On-Chain (4:00 - 5:30)

**[Screen: Show human verification]**

"The human analyst verifies this is indeed artificial (bad) OSINT data and commits the classification on-chain."

**[Screen: Run commit command]**

```bash
curl -X POST "http://localhost:8000/commit-on-chain" \
  -H "Content-Type: application/json" \
  -d '{
    "block_data": {
      "block_height": 20260105,
      "block_hash": "osint_20260105_1432",
      "timestamp": 1736088000,
      "tx_count": 1,
      "transactions": "[{\"source\":\"social_media\",\"content\":\"potential_threat_discussion\",\"platform\":\"twitter\",\"verified\":false}]"
    },
    "abc_receipt_hash": "WRONG_HASH_TO_SIMULATE_ARTIFICIAL_OSINT",
    "human_analyst": "osint_analyst_001",
    "data_classification": "artificial",
    "verification_notes": "Hash mismatch indicates artificial (bad) OSINT data injection - fake social media post"
  }'
```

**[Screen: Show response]**

"Committed to blockchain. The OSINT classification is now publicly verifiable. Anyone can verify this OSINT data was classified as artificial (bad)."

**[Screen: Show transaction hash]**

"Transaction hash: [blockchain_tx_hash]"
"Publicly verifiable on Bitcoin blockchain."

---

### Part 5: Bottleneck Resolved for Threat Intelligence (5:30 - 6:00)

**[Screen: Show threat intelligence model after filtering]**

"Now the threat intelligence model can filter out the artificial (bad) OSINT data. The bottleneck is resolved."

**[Screen: Show improved results]**

"Threat assessment confidence improved. Models train only on verified synthetic (good) OSINT data."

**[Screen: Summary]**

"ABC's core mechanism for OSINT:"
- "Hash match = Synthetic (good) OSINT data ✅"
- "Hash mismatch = Artificial (bad) OSINT data ❌"
- "Human verifies and commits on-chain"
- "Threat intelligence bottleneck resolved"

---

## Key Talking Points

### Opening
- "Threat intelligence models struggle - is it complex OSINT or deceptive injection?"
- "ABC detects the difference for OSINT data"

### Core Mechanism
- "Hash match = Synthetic (good) OSINT data ✅"
- "Hash mismatch = Artificial (bad) OSINT data ❌"
- "Same mechanism, works for OSINT too"

### Workflow
- "Threat model struggles → Human scans OSINT → ABC detects artificial (bad) data"
- "Human verifies → Commits on-chain → Publicly verifiable"
- "Model filters bad OSINT → Bottleneck resolved"

### Closing
- "ABC's core mechanism works for OSINT"
- "Hash verification detects OSINT data integrity issues"
- "On-chain commitment makes OSINT provenance publicly verifiable"

---

## Visual Cues

### OSINT Data
- Show social media posts, forum discussions, public records
- Highlight legitimate vs fake/manipulated content
- Use green checkmark for hash match (good OSINT)
- Use red X for hash mismatch (bad OSINT)

### Workflow
- Show the flow: Threat Model → Human → ABC → Blockchain
- Highlight the bottleneck resolution for threat intelligence
- Emphasize public verifiability of OSINT provenance

### Data Sources
- Social media (Twitter, Reddit, forums)
- Public records and databases
- News articles and reports
- Clear distinction between synthetic (good) and artificial (bad) OSINT

---

## Pro Tips

1. **Emphasize OSINT sources** - Social media, forums, public records
2. **Show the threat intelligence angle** - Models need clean OSINT data
3. **Highlight deception** - Fake posts, manipulated discussions are the bad data
4. **Keep core mechanism clear** - Hash match = good, hash mismatch = bad
5. **Show value** - Threat intelligence bottleneck resolution

---

## Quick Reference Card

### Opening
- "Threat intelligence models struggle - complex OSINT or deceptive injection?"
- "ABC detects the difference for OSINT"

### Core Mechanism
- "Hash match = Synthetic (good) OSINT ✅"
- "Hash mismatch = Artificial (bad) OSINT ❌"

### Workflow
- "Scan OSINT → Detect → Verify → Commit → Resolve"

### Closing
- "Same mechanism, works for OSINT"
- "Publicly verifiable OSINT provenance"

---

## OSINT-Specific Examples

### Synthetic (Good) OSINT
- Real social media posts from verified accounts
- Authentic forum discussions
- Verified public records
- Legitimate news articles

### Artificial (Bad) OSINT
- Fake social media posts
- Manipulated forum discussions
- Fabricated public records
- Deceptive news articles

---

**Copyright (c) 2025 GH Systems. All rights reserved.**

