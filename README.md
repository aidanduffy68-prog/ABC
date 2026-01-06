# ABC: Truth Verification for AI Intelligence
**When AIML systems disagree, ABC proves they analyzed the same data**

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![Palantir Foundry](https://img.shields.io/badge/Palantir-Foundry-red?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-High_Performance-green?style=flat-square)

Copyright (c) 2026 GH Systems. All rights reserved.

<img src="docs/assets/ghsystems_logo.png" alt="GH Systems Logo" width="120"/>

---

## The Problem

When AIML systems (inference models) generate conflicting assessments on the same data:

- **CIA says 85% confidence**
- **DHS says 60% confidence**
- **NSA says 78% confidence**

**Same threat. Three different answers. Did they analyze the same data?** There's no way to verify.

Result: **14 days to manually reconcile conflicts.**

---

## The Solution

**ABC proves AIML systems analyzed the same data.**

**ABC says:** *"Here is cryptographic proof that this evaluation/training run used only approved data, under declared intent, at this time."*

When multiple models get different results from the same intelligence compilation, ABC provides cryptographic proof they analyzed identical source data. The disagreement is methodology, not data quality.

**ABC makes Foundry unstoppable** - infrastructure that amplifies Foundry's value. When agencies blame Foundry for conflicting results, ABC provides cryptographic proof Foundry delivered correct data.

**Core Mechanism:**
- Hash match = Data integrity verified, provenance matches declared intent ✅
- Hash mismatch = Data integrity issue, possible ungoverned or mis-scoped data ⚠️

**ABC says:** *"Here is cryptographic proof that this evaluation/training run used only approved data, under declared intent, at this time."*

ABC detects ungoverned or mis-scoped data entering pipelines — including artificial data that violates declared intent, provenance, or usage policy. Human verifies and commits on-chain.

---

## Use Cases

**🔍 Multi-Agency Intelligence Verification**
- Government agencies (CIA, DHS, NSA, Treasury, DoD, FIUs)
- When models disagree on threat assessments, ABC proves they analyzed the same data

**🏦 AIML & Crypto Compliance**
- Detects ungoverned or mis-scoped data for AIML model training
- Verifies data provenance and declared intent (e.g., scenario_forge artificial data must be properly labeled)
- When ML models produce conflicting risk scores, ABC proves all models analyzed identical data

---

**Regulatory Audit Scenario:**

Bank deploys three ML models. Models produce different risk scores: Chainalysis 85%, TRM 60%, Foundry ML 72%.

**Without ABC:** 6-week audit, compliance risk  
**With ABC:** Same-day closure with cryptographic proof all models analyzed identical data

---

## Trust Signals

- ✅ Processing intelligence for DoD, DHS, Treasury
- ✅ **<500ms compilation** - Reliable performance at scale
- ✅ Security audits - [Security Documentation](docs/security/README.md)
- ✅ Classification-compliant - Handles SBU and Classified intelligence tiers

---

## How It Works

**The Stack:**
- **Palantir Foundry** - Data integration and compilation
- **ABC** - Cryptographic verification layer

**Chain-Agnostic Architecture** - Works with Bitcoin, Ethereum, Polygon, Arbitrum, Base, Optimism, or any supported blockchain.

[📖 Full Architecture Specification](docs/architecture/ARCHITECTURE_SPEC.md)

<div align="center">
  <img src="docs/assets/verification_structure.png" alt="Foundry Chain Verification Structure" width="800"/>
  <p><em>Foundry Chain: ABC as Cryptographic Verification Layer for Palantir Foundry</em></p>
</div>

**[📖 Foundry Chain Specification](docs/integrations/FOUNDRY_CHAIN_SPEC.md)** | **[🎥 Watch Demo](https://www.youtube.com/watch?v=LXLNb0QoKgI&t=2s)**

---

## Repository Structure

- **`src/core/nemesis/foundry_integration/`** - Foundry integration and workflow orchestration
- **`src/integrations/agency/`** - Agency framework and consensus engine
- **`src/verticals/`** - Vertical-specific implementations
- **`api/`** - FastAPI verification service
- **`scripts/`** - Demo and utility scripts

---

## 🎥 Demo

**See ABC in action:**

[![ABC Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=LXLNb0QoKgI&t=2s)

**[Watch the full demo →](https://www.youtube.com/watch?v=LXLNb0QoKgI&t=2s)**

---

## Documentation

- **[🎥 Demo Video](https://www.youtube.com/watch?v=LXLNb0QoKgI&t=2s)** - See ABC in action
- **[Foundry Integration](docs/integrations/FOUNDRY_INTEGRATION_QUICKSTART.md)** - ABC + Foundry setup
- **[Architecture](docs/architecture/ARCHITECTURE_SPEC.md)** - Technical specification
- **[Use Cases](docs/USE_CASES.md)** - Scenarios and applications
- **[Security](docs/security/README.md)** - Security documentation

---

## 🔧 Tech Stack

- **Python 3.11+** - Core language
- **FastAPI** - High-performance async API framework
- **Palantir Foundry** - Data infrastructure (core integration)
- **Pydantic** - Strict type validation
- **NetworkX** - Graph data structures
- **Chain-Agnostic Blockchain** - Bitcoin, Ethereum, Polygon, Arbitrum, Base, Optimism

---

**GH Systems** - Compiling behavioral bytecode so lawful actors win the economic battlefield.
