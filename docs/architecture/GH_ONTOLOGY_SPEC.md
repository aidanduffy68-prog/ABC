# GH Systems Behavioral Intelligence Graph (BIG) Specification
**Adversarial Behavior Compiler (ABC) Core Ontology v2.0**

## Overview

The Behavioral Intelligence Graph (BIG) is the shared semantic model for crypto risk intelligence. It defines entities, relationships, and intelligence objects that enable the Adversarial Behavior Compiler (ABC) to transform raw telemetry into executable behavioral playbooks.

---

## Entity Types

### Actor
**Subtypes:** `Wallet`, `Individual`, `Organization`, `ServiceProvider`, `NationState`

**Core Attributes:**
- `actor_id` — Unique identifier
- `source_ids` — Source system identifiers (TRM, Chainalysis, etc.)
- `risk_score` — Overall risk score (0-1)
- `risk_band` — Risk classification (low/medium/high/critical)
- `behavioral_signatures` — AI-generated behavioral fingerprints
- `jurisdiction` — Legal jurisdiction
- `hades_profile_ref` — Reference to Hades behavioral profile
- `metadata` — Additional attributes

### Event
**Subtypes:** `Transaction`, `Liquidation`, `BridgeTransfer`, `SanctionUpdate`, `Alert`, `Seizure`, `PaymentRelease`

**Core Attributes:**
- `event_id` — Unique identifier
- `event_type` — Type of event
- `timestamp` — When event occurred
- `chain` — Blockchain network
- `tx_hash` — Transaction hash
- `value_usd` — Value in USD
- `participants` — List of actor IDs involved
- `nemesis_assessment_ref` — Reference to Nemesis assessment
- `evidence_objects` — Linked evidence

### Pattern
**Subtypes:** `BehavioralSignature`, `RiskIndicator`, `Cluster`, `TTP` (Tactics, Techniques, Procedures), `AdversaryPlaybook`

**Core Attributes:**
- `pattern_id` — Unique identifier
- `category` — Pattern category
- `description` — Human-readable description
- `confidence` — Confidence score (0-1)
- `supporting_evidence` — Evidence supporting pattern
- `echo_cluster_ref` — Reference to Echo coordination cluster
- `detection_rules` — Rules that detected pattern
- `version` — Pattern version

### Location
**Subtypes:** `Chain`, `Bridge`, `Jurisdiction`, `Protocol`, `Exchange`, `OTCDesk`

**Core Attributes:**
- `location_id` — Unique identifier
- `type` — Location type
- `name` — Human-readable name
- `regime` — Regulatory regime
- `risk_profile` — Risk assessment
- `metadata` — Additional attributes

### Package
**Subtypes:** `TargetingPackage`, `SanctionsPackage`, `BountyPackage`

**Core Attributes:**
- `package_id` — Unique identifier
- `package_type` — Type of package
- `generated_by_nemesis_ref` — Reference to Nemesis generation
- `status` — Package status (draft/active/executed)
- `target_actors` — List of target actor IDs
- `recommended_actions` — Recommended countermeasures
- `timing_window` — When to execute
- `confidence` — Overall confidence
- `evidence_objects` — Supporting evidence

### Payment
**Subtypes:** `BountyPayment`, `LicenseFee`, `RevenueShare`

**Core Attributes:**
- `payment_id` — Unique identifier
- `payment_type` — Type of payment
- `amount_btc` — Amount in Bitcoin
- `status` — Payment status
- `initiating_actor` — Who initiated payment
- `receiving_actor` — Who receives payment
- `related_package_id` — Related package (if applicable)
- `tx_hash` — Bitcoin transaction hash
- `timestamp` — When payment occurred
- `conditions` — Payment conditions

### Contract
**Subtypes:** `LicensingAgreement`, `ServiceAgreement`, `BountyAgreement`

**Core Attributes:**
- `contract_id` — Unique identifier
- `contract_type` — Type of contract
- `parties` — Contract parties
- `terms` — Contract terms
- `start_date` — Contract start
- `end_date` — Contract end
- `payment_terms` — Payment structure
- `related_payments` — Related payment IDs

---

## Relationship Types

### Actor Relationships
- `OWNS` — Actor owns wallet/asset
- `CONTROLS` — Actor controls wallet/asset
- `COORDINATES_WITH` — Actors coordinate activities (Echo)
- `BEHAVES_LIKE` — Similar behavioral patterns (Hades)
- `CLUSTERS_WITH` — Behavioral clustering
- `SANCTIONED_BY` — Sanctioned by entity
- `SUSPECTED_OF` — Suspected of activity

### Event Relationships
- `TRIGGERS` — Event triggers other event
- `EVIDENCES` — Event provides evidence for pattern/actor
- `GENERATES` — Event generates intelligence object

### Pattern Relationships
- `MATCHES` — Pattern matches another pattern
- `INDICATES` — Pattern indicates risk/threat

### Package Relationships
- `TARGETS` — Package targets actor
- `RECOMMENDS` — Package recommends action

### Payment Relationships
- `SETTLES` — Payment settles bounty/contract
- `COMPENSATES` — Payment compensates actor

---

## Intelligence Objects

### EvidenceObject
**Purpose:** Legal-grade evidence with chain-of-custody

**Attributes:**
- `evidence_id` — Unique identifier
- `evidence_type` — Type of evidence
- `timestamp` — When evidence was created
- `hash` — Cryptographic hash
- `source` — Evidence source
- `chain_of_custody` — Custody history
- `related_entities` — Related actors/events

### RiskScore
**Purpose:** Versioned, auditable risk assessment

**Attributes:**
- `risk_score_id` — Unique identifier
- `entity_id` — Entity being scored
- `score` — Risk score (0-1)
- `components` — Score components (Hades, Echo, Nemesis)
- `version` — Score version
- `timestamp` — When score calculated
- `model_version` — AI model version used

### NetworkMap
**Purpose:** Anonymized, shareable network graph

**Attributes:**
- `network_map_id` — Unique identifier
- `central_actor` — Central actor (anonymized)
- `network_topology` — Graph structure
- `coordination_score` — Coordination likelihood
- `anonymization_level` — Privacy level
- `shareable` — Can be shared in federated mesh

---

## Data Provenance

All entities and relationships include:
- `source_system` — Origin system (TRM, Chainalysis, Chaos, etc.)
- `source_id` — Original identifier in source system
- `ingestion_timestamp` — When ingested into BIG
- `confidence` — Confidence in data quality
- `last_updated` — Last update timestamp
- `version` — Data version

---

## Integration Touchpoints

### Hades Integration
- **Input:** Transaction history, behavioral patterns
- **Output:** Behavioral signatures, risk scores, predicted off-ramps
- **Entities:** Actor behavioral profiles

### Echo Integration
- **Input:** Network graphs, coordination patterns
- **Output:** Coordination rings, facilitator networks
- **Entities:** Network clusters, coordination relationships

### Nemesis Integration
- **Input:** Behavioral signatures (Hades) + network data (Echo)
- **Output:** Targeting packages, pre-emptive assessments
- **Entities:** Packages, recommended actions

### AI Ontology Integration
- **Input:** Unstructured intelligence, transaction data
- **Output:** Auto-classified entities, inferred relationships, predictions
- **Entities:** AI-enhanced entities with semantic understanding

---

## Federated Mesh Alignment

The ontology supports privacy-preserving intelligence sharing:
- **Anonymized projections** — Share risk scores without raw data
- **Hash-based linking** — Link entities across nodes without exposing identities
- **Confidence propagation** — Share confidence scores with intelligence
- **Provenance tracking** — Track intelligence lineage across nodes

---

## Legal Considerations

### Chain-of-Custody
- All evidence objects maintain immutable chain-of-custody
- Timestamps and hashes for legal validity
- Audit trails for all intelligence operations

### Classification Handling
- Entities support classification levels (CONFIDENTIAL, SECRET, TOP SECRET)
- Distribution lists for intelligence sharing
- Access controls based on classification

### Compliance
- SAR (Suspicious Activity Report) generation support
- OFAC sanctions integration
- Regulatory reporting capabilities

---

## Bitcoin Settlement Layer

The ontology includes payment entities for automated BTC settlement:
- **Bounty payments** — Automated payouts for validated intelligence
- **License fees** — Vendor licensing payments
- **Revenue shares** — Contract uplift revenue sharing
- **All coordination funds** — Multi-party bounty pools

All payments are:
- Bitcoin-exclusive
- Programmatically executed
- Immutably recorded on-chain
- Linked to intelligence packages

---

## Version History

- **v2.0** — AI-powered ontology with semantic understanding, auto-classification, relationship inference
- **v1.0** — Initial Behavioral Intelligence Graph specification

---

*GH Systems — Compiling behavioral bytecode so lawful actors win the economic battlefield.*

