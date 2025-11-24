"""
Example: Generating Intelligence Audits
Demonstrates how to reframe threat dossiers as intelligence audits
"""

from nemesis.intelligence_audit import (
    IntelligenceAuditGenerator,
    AuditType
)


def example_pre_deployment_audit():
    """Example: Pre-deployment intelligence audit for DoD AI system"""
    
    generator = IntelligenceAuditGenerator()
    
    # Generate audit
    audit = generator.generate_audit(
        audit_type=AuditType.PRE_DEPLOYMENT,
        target_scope="DoD AI Infrastructure",
        actor_id="DoD_AI_001",
        actor_name="DoD Defense Innovation Unit AI Programs",
        behavioral_signature={
            "risk_score": 0.88,
            "confidence": 0.91,
            "pattern_matches": ["Commercial AI Integration", "Supply Chain Vulnerability"]
        },
        network_data={
            "coordination_score": 0.75,
            "network_size": 12,
            "facilitator_count": 3
        },
        threat_forecast={
            "overall_risk_score": 0.88,
            "predictions": [
                {
                    "type": "Supply chain compromise",
                    "confidence": 0.91,
                    "timing_window": "12-24 hours"
                }
            ]
        },
        transaction_history=[],
        intelligence_reports=["DoD DIU website analysis", "Commercial AI vendor assessment"]
    )
    
    # Export as markdown
    markdown = generator.export_audit_markdown(audit)
    print(markdown)
    
    return audit


def example_post_incident_audit():
    """Example: Post-incident intelligence audit"""
    
    generator = IntelligenceAuditGenerator()
    
    audit = generator.generate_audit(
        audit_type=AuditType.POST_INCIDENT,
        target_scope="Security Incident: AI System Compromise",
        actor_id="incident_001",
        actor_name="Unknown Threat Actor",
        behavioral_signature={
            "risk_score": 0.95,
            "confidence": 0.88,
            "pattern_matches": ["Nation-state attack pattern"]
        },
        network_data={
            "coordination_score": 0.85,
            "network_size": 25,
            "facilitator_count": 5
        },
        threat_forecast={
            "overall_risk_score": 0.95,
            "predictions": [
                {
                    "type": "Follow-on attack",
                    "confidence": 0.90,
                    "timing_window": "24-48 hours"
                }
            ]
        },
        transaction_history=[],
        intelligence_reports=["Incident timeline", "Attack vector analysis"]
    )
    
    markdown = generator.export_audit_markdown(audit)
    print(markdown)
    
    return audit


if __name__ == "__main__":
    print("=== Pre-Deployment Intelligence Audit ===")
    example_pre_deployment_audit()
    
    print("\n=== Post-Incident Intelligence Audit ===")
    example_post_incident_audit()

