# ABC: Adversarial Behavior Compiler (v2.0)
**High-Frequency Threat Intelligence System for Crypto-Native Defense**

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-High_Performance-green?style=flat-square)
![PyTorch Geometric](https://img.shields.io/badge/PyTorch-Geometric-orange?style=flat-square)
![Architecture](https://img.shields.io/badge/Architecture-Event_Driven-purple?style=flat-square)

Copyright (c) 2025 GH Systems. All rights reserved.

<div align="left">
  <img src="Deal%20Room/Assets/gh-systems-logo.png" alt="GH Systems Logo" width="150"/>
</div>

---

## ⚡ Quick Summary (TL;DR)

ABC is an AI-driven ingestion engine that compiles raw threat telemetry (Chainalysis, TRM, Research Feeds) into actionable targeting packages in **<500ms**. It replaces manual, 7-day analyst workflows with a real-time, automated graph pipeline.

### Key Engineering Features:

- **Behavioral Graph**: Uses Graph Neural Networks (GNN) to identify hidden clusters between hostile wallets
- **Event-Driven Pipeline**: Asynchronous ingestion system handling multi-source intelligence feeds
- **Deterministic Schemas**: Strict Pydantic models ensuring data integrity across the "Semantic Layer"
- **Cryptographic Provenance**: Merkle-tree based hashing to create on-chain proofs of intelligence snapshots

---

## 🏗 System Architecture

<div align="center">
  <img src="docs/ontology_to_target_intel.png" alt="ABC System Architecture: Ontology to Target Intelligence" width="800"/>
</div>

---

## 📂 Repository Map (Where the Code Lives)

- **`src/core/ingestion/`** - Adapters for external APIs and data normalization logic
- **`src/schemas/`** - Strict Pydantic definitions for Threat Actors and Events
- **`src/api/routes/`** - FastAPI endpoints for the intelligence dashboard
- **`src/graph/builder.py`** - NetworkX graph manipulation and relationship inference
- **`hades/`** - Behavioral profiling engine (PyTorch implementation for risk scoring)
- **`echo/`** - Coordination detection engine (network mapping, facilitator networks)
- **`nemesis/`** - Pre-emptive targeting engine (AI-powered threat ontology)
- **`nemesis/intelligence_audit/`** - Intelligence audit generator (for security researchers transitioning to intel)
- **`hypnos/`** - Long-term memory system (pattern consolidation, dormant threat tracking)
- **`settlements/`** - Fiat-to-BTC bridge for FAR-compliant government payments
- **`nemesis/on_chain_receipt/`** - Cryptographic receipt system with Merkle trees
- **`docs/`** - Full Whitepaper and Defense-Grade Specifications

---

## 🔍 Intelligence Audits (For Security Researchers)

**The Metaphor:** If you've done security audits (Cantina, Spearbit, etc.), intelligence audits work the same way—just applied to threats instead of code.

- **Same structure:** Findings with severity (P0-P3), methodology documentation, remediation roadmap
- **Same methodology:** Systematic assessment, just different domain
- **Easy transition:** Familiar format for security researchers getting into intelligence

---

## ⚖️ ABC as Intelligence Oracle

**The Oracle Comparison:**

| Platform | Oracle | Problem | Solution |
|----------|--------|---------|----------|
| **Polymarket** | UMA Oracle | Who won? What's the truth? | Decentralized truth verification |
| **Cantina** | Expert Triage | Is this a real bug? | Expert review + reputation |
| **Government** | **GH Systems ABC** | Is this a threat? What's the risk? | **Cryptographically verifiable intelligence in <500ms** |
| **Crypto Intelligence Platforms** | **GH Systems ABC (Licensed)** | Real-time wallet risk? Exchange security? | **White-label API or custom deployment** |

**The Intelligence Oracle Problem:**

**Current State:** Government disputes take 14+ days, are subjective, unverifiable, and agencies disagree.

**ABC Solution:** Objective threat assessments in <500ms with cryptographic proof—instant consensus, no political bias.

**Use Cases:**

1. **Intelligence Bounty Resolution** — Automatically evaluate submissions, determine winners based on verifiable metrics
2. **Inter-Agency Dispute Resolution** — Resolve disagreements with objective, cryptographically provable assessments
3. **Real-Time Threat Verification** — Instant threat assessment vs. 14-day investigations

**Value Prop:** "The UMA Oracle for Intelligence" — Trustless, automated, verifiable intelligence resolution.

**Private Sector Licensing:**
- **Platform Licensing:** $500K-$2M/year (white-label ABC for crypto intelligence platforms)
- **API Access:** $0.10-$1.00 per compilation (exchanges, DeFi protocols)
- **Custom Deployments:** $1M-$5M one-time (institutional custody, large exchanges)

**Use Cases:** Exchange risk scoring, DeFi protocol security, custody compliance, KYC/AML automation

See **[Oracle Positioning Framework](docs/ORACLE_POSITIONING_FRAMEWORK.md)** for complete sales framework.

```python
from nemesis.intelligence_audit import IntelligenceAuditGenerator, AuditType

generator = IntelligenceAuditGenerator()
audit = generator.generate_audit(
    audit_type=AuditType.PRE_DEPLOYMENT,
    target_scope="DoD AI Infrastructure",
    behavioral_signature={...},
    network_data={...},
    threat_forecast={...}
)
markdown = generator.export_audit_markdown(audit)
```

See `nemesis/intelligence_audit/example_usage.py` for complete examples.

---

## 📖 Full Documentation

This system is designed for Defense & Intelligence use cases. For the full operational specification, including the Semantic Understanding Layer and Predictive Threat Modeling, please see:

- **[📄 Full Architecture Specification](docs/ARCHITECTURE_SPEC.md)** - Complete technical spec
- **[⚖️ Oracle Positioning Framework](docs/ORACLE_POSITIONING_FRAMEWORK.md)** - Central sales framework
- **[📊 Intelligence Audit Examples](examples/intelligence_audits/)** - Operational audit examples
- **[🧠 Ontology Specification](Deal%20Room/GH_ONTOLOGY_SPEC.md)** - Behavioral Intelligence Graph schema
- **[📖 Glossary](GLOSSARY.md)** - Maps Greek god names to engineering domains

---

## 🔧 Tech Stack

- **Python 3.11+** - Core language
- **FastAPI** - High-performance async API framework
- **Pydantic** - Strict type validation and data schemas
- **NetworkX** - Graph data structure manipulation
- **PyTorch Geometric** - Graph Neural Networks (in development)
- **Bitcoin** - On-chain cryptographic receipts (OP_RETURN)
- **PostgreSQL/Neo4j** - Graph database for Hypnos Core

---

## 🎯 Current Status

**Core ingestion pipeline is production-ready.** Advanced AI features (GNN inference, vector DB) are in active development.

See [Current Status](docs/ARCHITECTURE_SPEC.md#current-status) for detailed implementation status.

---

**GH Systems** — Compiling behavioral bytecode so lawful actors win the economic battlefield.
