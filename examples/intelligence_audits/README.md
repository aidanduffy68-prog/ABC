# Intelligence Audits

**Demonstration artifacts showcasing intelligence audit capabilities.**

These intelligence audits are AI-generated examples for demonstration purposes. They showcase the capability of the ABC compilation engine to produce systematic threat assessments in audit format.

## Purpose

- **Demonstration**: Show how ABC compiles intelligence into systematic audits
- **Testing**: Validate audit generation templates and formats
- **Documentation**: Provide examples for security researchers transitioning to intelligence

## Structure

- `INTELLIGENCE_AUDIT_DOD_DHS_002.md` - Pre-deployment intelligence audit for DoD & DHS AI infrastructure
- `THREAT_DOSSIER_NASA_001.md` - Federal AI infrastructure threat assessment (NASA)

## Operational Intelligence

Real operational intelligence audits are generated on-demand from the intelligence graph. The audit generator (`nemesis/intelligence_audit/audit_generator.py`) creates audits in <500ms from compiled intelligence data.

## Templates

The audit generation templates and scripts are in:
- `nemesis/intelligence_audit/audit_generator.py` - Intelligence audit generator
- `nemesis/intelligence_audit/example_usage.py` - Usage examples

---

*GH Systems — Systematic threat assessment in <500ms*
