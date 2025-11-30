"""
Auto-Generated Threat Dossier System
Automatically generates comprehensive threat actor dossiers

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


@dataclass
class ThreatDossier:
    """Auto-generated threat actor dossier"""
    dossier_id: str
    actor_id: str
    actor_name: str
    classification: str
    threat_level: str
    generated_at: datetime
    
    # Behavioral Intelligence
    behavioral_signature: Dict[str, Any] = field(default_factory=dict)
    risk_scores: Dict[str, float] = field(default_factory=dict)
    behavioral_traits: Dict[str, float] = field(default_factory=dict)
    
    # Network Intelligence
    coordination_network: Dict[str, Any] = field(default_factory=dict)
    identified_partners: List[str] = field(default_factory=list)
    facilitator_count: int = 0
    
    # Predictive Intelligence
    threat_forecast: Dict[str, Any] = field(default_factory=dict)
    predicted_actions: List[Dict[str, Any]] = field(default_factory=list)
    next_action_window: Optional[str] = None
    
    # Historical Intelligence
    attack_history: List[Dict[str, Any]] = field(default_factory=list)
    transaction_summary: Dict[str, Any] = field(default_factory=dict)
    pattern_matches: List[str] = field(default_factory=list)
    
    # Operational Intelligence
    recommended_countermeasures: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    evidence_sources: List[str] = field(default_factory=list)
    
    # Counterintelligence Intelligence
    hidden_relationships: List[Dict[str, Any]] = field(default_factory=list)
    multi_source_fusion: Dict[str, Any] = field(default_factory=dict)
    counterintelligence_assessment: Dict[str, Any] = field(default_factory=dict)
    operational_security_indicators: List[str] = field(default_factory=list)
    
    # Regional Intelligence
    regional_intelligence: Dict[str, Any] = field(default_factory=dict)
    regional_exchange_relationships: List[Dict[str, Any]] = field(default_factory=list)
    regional_facilitator_networks: List[Dict[str, Any]] = field(default_factory=list)
    sanctions_evasion_patterns: List[str] = field(default_factory=list)
    
    # Metadata
    model_version: str = "1.0.0"
    classification_level: str = "CONFIDENTIAL"
    distribution: List[str] = field(default_factory=list)


class ThreatDossierGenerator:
    """
    Auto-generates comprehensive threat dossiers by compiling
    intelligence from Hades, Echo, Nemesis, and AI components
    """
    
    def __init__(self):
        self.model_version = "1.0.0"
        # Lazy import to avoid circular dependencies
        self._receipt_generator = None
        
    def generate_dossier(
        self,
        actor_id: str,
        actor_name: str,
        behavioral_signature: Dict[str, Any],
        network_data: Dict[str, Any],
        threat_forecast: Dict[str, Any],
        transaction_history: List[Dict[str, Any]],
        historical_patterns: Optional[List[Dict[str, Any]]] = None,
        intelligence_reports: Optional[List[str]] = None
    ) -> ThreatDossier:
        """
        Generate comprehensive threat dossier
        
        Args:
            actor_id: Unique identifier for the actor
            actor_name: Name/designation of the actor
            behavioral_signature: AI-generated behavioral signature
            network_data: Echo network coordination data
            threat_forecast: Predictive threat forecast
            transaction_history: Historical transaction data
            historical_patterns: Similar actor patterns
            intelligence_reports: Unstructured intelligence
            
        Returns:
            Complete ThreatDossier
        """
        # Determine classification
        classification = self._determine_classification(behavioral_signature, network_data)
        threat_level = self._determine_threat_level(threat_forecast, behavioral_signature)
        
        # Compile behavioral intelligence
        risk_scores = self._extract_risk_scores(behavioral_signature)
        behavioral_traits = self._extract_behavioral_traits(behavioral_signature)
        
        # Compile network intelligence
        coordination_network = self._compile_network_intelligence(network_data)
        identified_partners = network_data.get('partners', [])
        facilitator_count = network_data.get('facilitator_count', 0)
        
        # Compile predictive intelligence
        predicted_actions = threat_forecast.get('predictions', [])
        next_action_window = self._format_action_window(threat_forecast.get('next_action_window'))
        
        # Compile historical intelligence
        attack_history = self._compile_attack_history(transaction_history, historical_patterns)
        transaction_summary = self._summarize_transactions(transaction_history)
        pattern_matches = behavioral_signature.get('pattern_matches', [])
        
        # Generate operational intelligence
        recommended_countermeasures = threat_forecast.get('recommended_countermeasures', [])
        confidence_scores = self._calculate_confidence_scores(
            behavioral_signature, network_data, threat_forecast
        )
        evidence_sources = self._compile_evidence_sources(
            behavioral_signature, network_data, threat_forecast, transaction_history
        )
        
        # Compile counterintelligence intelligence
        hidden_relationships = self._compile_hidden_relationships(network_data, behavioral_signature)
        multi_source_fusion = self._compile_multi_source_fusion(
            behavioral_signature, network_data, threat_forecast, transaction_history, intelligence_reports
        )
        counterintelligence_assessment = self._generate_counterintelligence_assessment(
            behavioral_signature, network_data, threat_forecast
        )
        operational_security_indicators = self._identify_operational_security_indicators(behavioral_signature)
        
        # Determine distribution list
        distribution = self._determine_distribution(threat_level, classification)
        
        dossier = ThreatDossier(
            dossier_id=f"dossier_{actor_id}_{datetime.now().strftime('%Y%m%d')}",
            actor_id=actor_id,
            actor_name=actor_name,
            classification=classification,
            threat_level=threat_level,
            generated_at=datetime.now(),
            behavioral_signature=behavioral_signature,
            risk_scores=risk_scores,
            behavioral_traits=behavioral_traits,
            coordination_network=coordination_network,
            identified_partners=identified_partners,
            facilitator_count=facilitator_count,
            threat_forecast=threat_forecast,
            predicted_actions=predicted_actions,
            next_action_window=next_action_window,
            attack_history=attack_history,
            transaction_summary=transaction_summary,
            pattern_matches=pattern_matches,
            recommended_countermeasures=recommended_countermeasures,
            confidence_scores=confidence_scores,
            evidence_sources=evidence_sources,
            hidden_relationships=hidden_relationships,
            multi_source_fusion=multi_source_fusion,
            counterintelligence_assessment=counterintelligence_assessment,
            operational_security_indicators=operational_security_indicators,
            model_version=self.model_version,
            classification_level=self._determine_classification_level(threat_level),
            distribution=distribution
        )
    
    def generate_receipt(self, dossier: ThreatDossier) -> Dict[str, Any]:
        """
        Generate cryptographic receipt for dossier
        
        Args:
            dossier: ThreatDossier to generate receipt for
            
        Returns:
            Receipt data (minimal on-chain proof)
        """
        # Lazy import
        if self._receipt_generator is None:
            try:
                from nemesis.on_chain_receipt import CryptographicReceiptGenerator
                self._receipt_generator = CryptographicReceiptGenerator()
            except ImportError:
                # If receipt system not available, return None
                return None
        
        # Convert dossier to dict for hashing
        dossier_dict = asdict(dossier)
        # Convert datetime to string for JSON serialization
        dossier_dict['generated_at'] = dossier.generated_at.isoformat()
        
        # Generate receipt
        receipt = self._receipt_generator.generate_receipt(
            intelligence_package=dossier_dict,
            actor_id=dossier.actor_id,
            threat_level=dossier.threat_level,
            package_type="threat_dossier",
            additional_metadata={
                "dossier_id": dossier.dossier_id,
                "classification": dossier.classification
            }
        )
        
        # Return minimal on-chain data
        return self._receipt_generator.prepare_for_on_chain(receipt)
    
    def export_dossier_markdown(self, dossier: ThreatDossier) -> str:
        """Export dossier as markdown (like THREAT_PROFILE_LAZARUS.md format)"""
        md = f"""# GH SYSTEMS // {dossier.classification_level} // OPERATION NEMESIS
Threat Classification: {dossier.classification}
Actor Designation: {dossier.actor_name}
Compiler Status: ACTIVE TRACKING
Dossier ID: {dossier.dossier_id}
Generated: {dossier.generated_at.isoformat()}

## BEHAVIORAL FINGERPRINT (HADES AI)

**Primary Signature:**
"""
        
        # Behavioral traits
        for trait, value in dossier.behavioral_traits.items():
            md += f"- {trait}: {value:.2f}\n"
        
        md += f"\n**Risk Scores:**\n"
        for metric, score in dossier.risk_scores.items():
            md += f"- {metric}: {score:.2f}\n"
        
        md += f"\n**Pattern Matches:**\n"
        for pattern in dossier.pattern_matches:
            md += f"- {pattern}\n"
        
        md += f"""
## COORDINATION NETWORK (ECHO)

**Network Topology:**
- Network size: {dossier.coordination_network.get('size', 'N/A')}
- Identified partners: {len(dossier.identified_partners)}
- Facilitators: {dossier.facilitator_count}

**Partners:**
"""
        for partner in dossier.identified_partners[:10]:  # Limit to 10
            md += f"- {partner}\n"
        
        md += f"""
## PRE-EMPTIVE TARGETING (NEMESIS AI)

**Threat Level:** {dossier.threat_level}
**Next Action Window:** {dossier.next_action_window or 'TBD'}

**Predicted Actions:**
"""
        for action in dossier.predicted_actions[:5]:  # Limit to 5
            md += f"- {action.get('type', 'unknown')}: {action.get('confidence', 0.0):.2f} confidence\n"
            if action.get('timing_window'):
                md += f"  - Window: {action['timing_window']}\n"
            if action.get('location'):
                md += f"  - Location: {action['location']}\n"
        
        md += f"""
**Recommended Countermeasures:**
"""
        for countermeasure in dossier.recommended_countermeasures:
            md += f"- {countermeasure}\n"
        
        md += f"""
## HISTORICAL INTELLIGENCE

**Transaction Summary:**
- Total transactions: {dossier.transaction_summary.get('total', 0)}
- Total volume: ${dossier.transaction_summary.get('total_volume', 0):,.0f}
- First seen: {dossier.transaction_summary.get('first_seen', 'N/A')}
- Last seen: {dossier.transaction_summary.get('last_seen', 'N/A')}

**Attack History:**
"""
        for attack in dossier.attack_history[:5]:  # Limit to 5
            md += f"- {attack.get('date', 'N/A')}: {attack.get('description', 'N/A')}\n"
        
        md += f"""
## CONFIDENCE & EVIDENCE

**Confidence Scores:**
"""
        for source, score in dossier.confidence_scores.items():
            md += f"- {source}: {score:.2f}\n"
        
        md += f"""
**Evidence Sources:**
"""
        for source in dossier.evidence_sources:
            md += f"- {source}\n"
        
        md += f"""
## COUNTERINTELLIGENCE ANALYSIS

**Multi-Source Intelligence Fusion:**
- Sources fused: {len(dossier.multi_source_fusion.get('sources', []))}
- Fusion confidence: {dossier.multi_source_fusion.get('confidence', 0.0):.2f}
- Intelligence gaps: {dossier.multi_source_fusion.get('gaps', [])}

**Hidden Relationship Discovery:**
"""
        for rel in dossier.hidden_relationships[:5]:  # Limit to 5
            md += f"- {rel.get('type', 'unknown')}: {rel.get('target', 'unknown')} (confidence: {rel.get('confidence', 0.0):.2f})\n"
            if rel.get('evidence'):
                md += f"  - Evidence: {', '.join(rel['evidence'][:2])}\n"
        
        md += f"""
**Counterintelligence Assessment:**
- Adversarial sophistication: {dossier.counterintelligence_assessment.get('sophistication', 'N/A')}
- Operational security level: {dossier.counterintelligence_assessment.get('opsec_level', 'N/A')}
- Deception indicators: {len(dossier.counterintelligence_assessment.get('deception_indicators', []))}
- Coordination sophistication: {dossier.counterintelligence_assessment.get('coordination_sophistication', 'N/A')}

**Operational Security Indicators:**
"""
        for indicator in dossier.operational_security_indicators[:5]:  # Limit to 5
            md += f"- {indicator}\n"
        
        md += f"""
**Counterintelligence Recommendations:**
"""
        ci_recommendations = dossier.counterintelligence_assessment.get('recommendations', [])
        for rec in ci_recommendations:
            md += f"- {rec}\n"
        
        md += f"""
## OPERATIONAL CLASSIFICATION

This dossier contains:
- Active targeting methodologies
- Behavioral prediction models
- Counterintelligence analysis
- Hidden relationship discovery
- Multi-source intelligence fusion
- Allied coordination details
- Interdiction protocols

Distribution limited to: {', '.join(dossier.distribution)}

[END DOSSIER]
"""
        
        return md
    
    # Helper methods
    def _determine_classification(self, signature: Dict[str, Any], network: Dict[str, Any]) -> str:
        """Determine threat classification"""
        risk_score = signature.get('risk_score', 0.0)
        if risk_score > 0.9:
            return "NATION-STATE SPONSORED"
        elif risk_score > 0.7:
            return "CRIMINAL ORGANIZATION"
        else:
            return "INDIVIDUAL"
    
    def _determine_threat_level(self, forecast: Dict[str, Any], signature: Dict[str, Any]) -> str:
        """Determine threat level"""
        risk = forecast.get('overall_risk_score', 0.0)
        if risk > 0.8:
            return "CRITICAL"
        elif risk > 0.6:
            return "HIGH"
        elif risk > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_risk_scores(self, signature: Dict[str, Any]) -> Dict[str, float]:
        """Extract risk scores from signature"""
        return signature.get('risk_scores', {})
    
    def _extract_behavioral_traits(self, signature: Dict[str, Any]) -> Dict[str, float]:
        """Extract behavioral traits"""
        return signature.get('traits', {})
    
    def _compile_network_intelligence(self, network: Dict[str, Any]) -> Dict[str, Any]:
        """Compile network intelligence"""
        return {
            "size": network.get('network_size', 0),
            "coordination_score": network.get('coordination_score', 0.0),
            "topology": network.get('topology', 'unknown')
        }
    
    def _format_action_window(self, window: Optional[Any]) -> Optional[str]:
        """Format action window"""
        if not window:
            return None
        if isinstance(window, tuple) and len(window) == 2:
            return f"{window[0].isoformat()} to {window[1].isoformat()}"
        return str(window)
    
    def _compile_attack_history(self, transactions: List[Dict[str, Any]], patterns: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Compile attack history"""
        history = []
        # Implementation: Extract attack events from transactions and patterns
        return history
    
    def _summarize_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize transaction history"""
        if not transactions:
            return {}
        
        amounts = [t.get('amount', 0) for t in transactions if 'amount' in t]
        timestamps = [t.get('timestamp') for t in transactions if 'timestamp' in t]
        
        return {
            "total": len(transactions),
            "total_volume": sum(amounts),
            "first_seen": min(timestamps) if timestamps else None,
            "last_seen": max(timestamps) if timestamps else None
        }
    
    def _calculate_confidence_scores(
        self,
        signature: Dict[str, Any],
        network: Dict[str, Any],
        forecast: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate confidence scores"""
        return {
            "behavioral_signature": signature.get('confidence', 0.0),
            "network_analysis": network.get('confidence', 0.0),
            "threat_forecast": forecast.get('confidence', 0.0),
            "overall": (signature.get('confidence', 0.0) + network.get('confidence', 0.0) + forecast.get('confidence', 0.0)) / 3
        }
    
    def _compile_evidence_sources(
        self,
        signature: Dict[str, Any],
        network: Dict[str, Any],
        forecast: Dict[str, Any],
        transactions: List[Dict[str, Any]]
    ) -> List[str]:
        """Compile evidence sources"""
        sources = []
        sources.extend(signature.get('evidence_sources', []))
        sources.extend(network.get('sources', []))
        sources.extend(forecast.get('sources', []))
        if transactions:
            sources.append(f"transaction_history_{len(transactions)}_txns")
        return list(set(sources))  # Remove duplicates
    
    def _determine_distribution(self, threat_level: str, classification: str) -> List[str]:
        """Determine distribution list"""
        base_distribution = ["Treasury / OFAC", "FBI Cyber Division"]
        
        if threat_level == "CRITICAL":
            base_distribution.extend(["NSA Cybersecurity", "DoD Cyber Command"])
        
        if "NATION-STATE" in classification:
            base_distribution.extend(["Allied partners (UK FIU, EU AML)"])
        
        return base_distribution
    
    def _determine_classification_level(self, threat_level: str) -> str:
        """Determine classification level"""
        if threat_level == "CRITICAL":
            return "TOP SECRET"
        elif threat_level == "HIGH":
            return "SECRET"
        else:
            return "CONFIDENTIAL"
    
    def _compile_hidden_relationships(
        self,
        network_data: Dict[str, Any],
        behavioral_signature: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Compile hidden relationships discovered through GNN inference"""
        relationships = []
        
        # Extract coordination relationships
        if network_data.get('coordination_rings'):
            for ring in network_data['coordination_rings']:
                relationships.append({
                    "type": "COORDINATES_WITH",
                    "target": ring.get('partner_id', 'unknown'),
                    "confidence": ring.get('confidence', 0.0),
                    "evidence": ring.get('evidence', [])
                })
        
        # Extract control relationships
        if network_data.get('control_structures'):
            for control in network_data['control_structures']:
                relationships.append({
                    "type": "CONTROLS",
                    "target": control.get('controlled_entity', 'unknown'),
                    "confidence": control.get('confidence', 0.0),
                    "evidence": control.get('evidence', [])
                })
        
        # Extract behavioral similarity relationships
        if behavioral_signature.get('similar_actors'):
            for similar in behavioral_signature['similar_actors']:
                relationships.append({
                    "type": "BEHAVES_LIKE",
                    "target": similar.get('actor_id', 'unknown'),
                    "confidence": similar.get('similarity_score', 0.0),
                    "evidence": ["behavioral_signature_similarity"]
                })
        
        return relationships
    
    def _compile_multi_source_fusion(
        self,
        behavioral_signature: Dict[str, Any],
        network_data: Dict[str, Any],
        threat_forecast: Dict[str, Any],
        transaction_history: List[Dict[str, Any]],
        intelligence_reports: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Compile multi-source intelligence fusion summary"""
        sources = []
        
        if behavioral_signature:
            sources.append("behavioral_signature")
        if network_data:
            sources.append("network_analysis")
        if threat_forecast:
            sources.append("threat_forecast")
        if transaction_history:
            sources.append("transaction_history")
        if intelligence_reports:
            sources.append("intelligence_reports")
        
        # Calculate fusion confidence (weighted average)
        confidences = []
        if behavioral_signature.get('confidence'):
            confidences.append(behavioral_signature['confidence'])
        if network_data.get('confidence'):
            confidences.append(network_data['confidence'])
        if threat_forecast.get('confidence'):
            confidences.append(threat_forecast['confidence'])
        
        fusion_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Identify intelligence gaps
        gaps = []
        if not transaction_history:
            gaps.append("transaction_history")
        if not intelligence_reports:
            gaps.append("intelligence_reports")
        if not network_data.get('coordination_rings'):
            gaps.append("coordination_network")
        
        return {
            "sources": sources,
            "confidence": fusion_confidence,
            "gaps": gaps,
            "fusion_method": "multi_source_weighted_average"
        }
    
    def _generate_counterintelligence_assessment(
        self,
        behavioral_signature: Dict[str, Any],
        network_data: Dict[str, Any],
        threat_forecast: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate counterintelligence assessment"""
        # Assess adversarial sophistication
        sophistication = "LOW"
        if behavioral_signature.get('pattern_repetition', 0.0) > 0.7:
            sophistication = "MEDIUM"
        if network_data.get('coordination_score', 0.0) > 0.7:
            sophistication = "HIGH"
        if threat_forecast.get('overall_risk_score', 0.0) > 0.8:
            sophistication = "CRITICAL"
        
        # Assess operational security level
        opsec_level = "BASIC"
        if behavioral_signature.get('route_entropy', 0.0) > 0.7:
            opsec_level = "INTERMEDIATE"
        if behavioral_signature.get('pattern_repetition', 0.0) < 0.3:  # Low repetition = high opsec
            opsec_level = "ADVANCED"
        
        # Identify deception indicators
        deception_indicators = []
        if behavioral_signature.get('route_entropy', 0.0) > 0.8:
            deception_indicators.append("high_route_diversity")
        if network_data.get('coordination_score', 0.0) > 0.7 and network_data.get('facilitator_count', 0) > 5:
            deception_indicators.append("complex_coordination_network")
        
        # Assess coordination sophistication
        coordination_sophistication = "NONE"
        if network_data.get('coordination_score', 0.0) > 0.5:
            coordination_sophistication = "BASIC"
        if network_data.get('coordination_score', 0.0) > 0.7:
            coordination_sophistication = "ADVANCED"
        if network_data.get('facilitator_count', 0) > 10:
            coordination_sophistication = "SOPHISTICATED"
        
        # Generate counterintelligence recommendations
        recommendations = []
        if sophistication in ["HIGH", "CRITICAL"]:
            recommendations.append("Prioritize multi-source intelligence collection")
        if opsec_level == "ADVANCED":
            recommendations.append("Focus on behavioral pattern analysis over transaction tracking")
        if coordination_sophistication in ["ADVANCED", "SOPHISTICATED"]:
            recommendations.append("Target facilitator network disruption")
        if deception_indicators:
            recommendations.append("Investigate deception patterns for operational security vulnerabilities")
        
        return {
            "sophistication": sophistication,
            "opsec_level": opsec_level,
            "deception_indicators": deception_indicators,
            "coordination_sophistication": coordination_sophistication,
            "recommendations": recommendations
        }
    
    def _identify_operational_security_indicators(self, behavioral_signature: Dict[str, Any]) -> List[str]:
        """Identify operational security indicators from behavioral signature"""
        indicators = []
        
        traits = behavioral_signature.get('traits', {})
        
        # High route entropy = trying to obfuscate
        if traits.get('route_entropy', 0.0) > 0.7:
            indicators.append("High route diversity (potential obfuscation attempt)")
        
        # Low pattern repetition = operational security
        if traits.get('pattern_repetition', 1.0) < 0.3:
            indicators.append("Low pattern repetition (operational security discipline)")
        
        # Systematic mixer usage = privacy focus
        if behavioral_signature.get('pattern_matches'):
            if any('mixer' in p.lower() for p in behavioral_signature['pattern_matches']):
                indicators.append("Systematic privacy tool usage")
        
        # Timing patterns = operational windows
        if traits.get('timing_preference'):
            indicators.append(f"Consistent timing patterns (operational window: {traits['timing_preference']})")
        
        # Rapid chain switching = evasion attempt
        if traits.get('route_entropy', 0.0) > 0.8:
            indicators.append("Rapid chain switching (potential evasion maneuver)")
        
        return indicators

