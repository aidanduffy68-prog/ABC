# ABC Architecture Documentation Index

**Quick navigation to all architecture specifications**

---

## 🎯 Start Here

### For Everyone

- **[ARCHITECTURE_SPEC.md](ARCHITECTURE_SPEC.md)** - Complete system architecture, "Foundry's Chainlink" positioning

### For Technical Teams

- **[CHAIN_AGNOSTIC_ARCHITECTURE.md](CHAIN_AGNOSTIC_ARCHITECTURE.md)** - Multi-blockchain support (Bitcoin, Ethereum, Hyperledger)

### For Developers

- **[components/COMPILATION_ENGINE.md](components/COMPILATION_ENGINE.md)** - Hades → Echo → Nemesis pipeline

---

## 📚 Core Architecture Specs

### System Architecture

| Document | Purpose | Audience |
|----------|---------|----------|
| [ARCHITECTURE_SPEC.md](ARCHITECTURE_SPEC.md) | Complete system architecture | All |
| [CHAIN_AGNOSTIC_ARCHITECTURE.md](CHAIN_AGNOSTIC_ARCHITECTURE.md) | Multi-blockchain integration | Technical |

### Intelligence Ontology

| Document | Purpose | Audience |
|----------|---------|----------|
| [GH_ONTOLOGY_SPEC.md](GH_ONTOLOGY_SPEC.md) | Behavioral Intelligence Graph schema | Technical |
| [AI_THREAT_ONTOLOGY_SPEC.md](AI_THREAT_ONTOLOGY_SPEC.md) | AI-powered threat classification | Technical |
| [AI_ONTOLOGY_INTEGRATION.md](AI_ONTOLOGY_INTEGRATION.md) | AI ontology integration guide | Developers |

### Integration Specs

| Document | Purpose | Audience |
|----------|---------|----------|
| [../integrations/FOUNDRY_CHAIN_SPEC.md](../integrations/FOUNDRY_CHAIN_SPEC.md) | Foundry Chain technical spec | Technical |
| [../integrations/FOUNDRY_CONNECTION_GUIDE.md](../integrations/FOUNDRY_CONNECTION_GUIDE.md) | Foundry API connection guide | Developers |
| [../integrations/FOUNDRY_DATA_EXPORT.md](../integrations/FOUNDRY_DATA_EXPORT.md) | Foundry data export documentation | Developers |

---

## 🏗️ Component Documentation

### Core Engines (in src/core/)

| Engine | Purpose | Documentation |
|--------|---------|---------------|
| **Hades** | Behavioral profiling | [src/core/hades/README.md](../../src/core/hades/README.md) |
| **Echo** | Coordination detection | [src/core/echo/README.md](../../src/core/echo/README.md) |
| **Nemesis** | Pre-emptive targeting | [src/core/nemesis/ai_ontology/README.md](../../src/core/nemesis/ai_ontology/README.md) |
| **Hypnos** | Long-term memory | [src/core/hypnos/README.md](../../src/core/hypnos/README.md) |

### Compilation Pipeline

- [components/COMPILATION_ENGINE.md](components/COMPILATION_ENGINE.md) - Complete pipeline documentation

---

## 🎯 By Use Case

### "I need to understand ABC for a partnership pitch"

1. Read: [ARCHITECTURE_SPEC.md](ARCHITECTURE_SPEC.md) (focus on "Foundry's Chainlink" section)
2. Read: [../integrations/FOUNDRY_CHAIN_SPEC.md](../integrations/FOUNDRY_CHAIN_SPEC.md)
3. Review: Integration examples in `examples/intelligence_audits/`

### "I need to evaluate ABC's technical capabilities"

1. Read: [ARCHITECTURE_SPEC.md](ARCHITECTURE_SPEC.md)
2. Read: [CHAIN_AGNOSTIC_ARCHITECTURE.md](CHAIN_AGNOSTIC_ARCHITECTURE.md)
3. Explore: Component READMEs in `src/core/*/README.md`

### "I need to integrate with ABC"

1. Read: [../integrations/FOUNDRY_CHAIN_SPEC.md](../integrations/FOUNDRY_CHAIN_SPEC.md)
2. Read: [../integrations/FOUNDRY_CONNECTION_GUIDE.md](../integrations/FOUNDRY_CONNECTION_GUIDE.md)
3. Review: API documentation in `src/api/`

### "I'm a developer joining the team"

1. Read: [ARCHITECTURE_SPEC.md](ARCHITECTURE_SPEC.md) (overview)
2. Read: [components/COMPILATION_ENGINE.md](components/COMPILATION_ENGINE.md)
3. Explore: `src/core/hades/`, `src/core/echo/`, `src/core/nemesis/`
4. Run: `./scripts/instant_demo.sh`

---

## 🔐 Security & Compliance

| Document | Purpose |
|----------|---------|
| [../security/AI_INCIDENT_RESPONSE.md](../security/AI_INCIDENT_RESPONSE.md) | AI security incident response |
| [../security/AI_OT_SECURITY_COMPLIANCE.md](../security/AI_OT_SECURITY_COMPLIANCE.md) | OT security compliance |
| [../security/TIERED_SECURITY_MODEL.md](../security/TIERED_SECURITY_MODEL.md) | Tiered security classification system |
| [../security/](../security/) | All security specifications and audits |

---

## 🎬 Demos & Guides

| Document | Purpose |
|----------|---------|
| [../../scripts/instant_demo.sh](../../scripts/instant_demo.sh) | Quick demo script |

---

## 🗂️ Document Organization

```
ABC/
├── docs/
│   ├── architecture/
│   │   ├── ARCHITECTURE_INDEX.md          ← YOU ARE HERE
│   │   ├── ARCHITECTURE_SPEC.md           ← Main architecture spec
│   │   ├── CHAIN_AGNOSTIC_ARCHITECTURE.md ← Blockchain integration
│   │   ├── GH_ONTOLOGY_SPEC.md            ← Behavioral Intelligence Graph
│   │   ├── AI_THREAT_ONTOLOGY_SPEC.md     ← AI-powered threat ontology
│   │   ├── components/
│   │   │   └── COMPILATION_ENGINE.md      ← Compilation pipeline
│   │   └── README.md                      ← Architecture overview
│   │
│   ├── integrations/
│   │   ├── FOUNDRY_CHAIN_SPEC.md          ← Foundry Chain spec
│   │   └── FOUNDRY_CONNECTION_GUIDE.md    ← API connection guide
│   │
│   └── security/                          ← Security docs
│
├── src/core/
│   ├── hades/README.md                    ← Hades engine docs
│   ├── echo/README.md                     ← Echo engine docs
│   ├── nemesis/
│   │   └── ai_ontology/README.md          ← Nemesis AI ontology docs
│   └── hypnos/README.md                   ← Hypnos engine docs
│
└── scripts/
    └── instant_demo.sh                    ← Quick demo script
```

---

## 🔄 Document Maintenance

### When to Update This Index

- Adding new architecture specifications
- Reorganizing documentation structure
- Adding new component documentation

### How to Update

1. Add document to appropriate table above
2. Update "By Use Case" section if relevant
3. Update document organization diagram
4. Commit with message: `docs: update architecture index`

---

## 📖 Additional Resources

- **[Main README](../../README.md)** - Project overview and quick start
- **[Getting Started](../../GETTING_STARTED.md)** - Setup and development guide
- **[Repository Structure](../../REPOSITORY_STRUCTURE.md)** - Codebase organization

---

**Questions?** See [../../GETTING_STARTED.md](../../GETTING_STARTED.md) or contact the team.

*Last updated: December 16, 2025*

