"""
Explainable AI (XAI) Tools
Provides explanations for AI model decisions and outputs

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class DecisionExplanation:
    """Explanation for an AI decision"""
    decision: str
    confidence: float
    contributing_factors: List[Dict[str, Any]]
    reasoning: str
    evidence: List[str]
    limitations: List[str]


@dataclass
class BehavioralExplanation:
    """Explanation for behavioral signature analysis"""
    actor_id: str
    traits_identified: Dict[str, float]
    trait_explanations: Dict[str, str]
    risk_factors: List[str]
    confidence_breakdown: Dict[str, float]


@dataclass
class NetworkExplanation:
    """Explanation for coordination network detection"""
    network_id: str
    entities: List[str]
    relationships: List[Dict[str, Any]]
    relationship_confidence: Dict[str, float]
    coordination_evidence: List[str]
    network_strength: float


class XAIExplainer:
    """
    Provides explainable AI capabilities for GH Systems ABC
    
    Generates human-readable explanations for:
    - Behavioral profiling decisions
    - Coordination network detection
    - Threat forecasting
    - Risk assessments
    """
    
    def explain_behavioral_signature(
        self,
        actor_id: str,
        behavioral_signature: Dict,
        raw_intelligence: List[Dict]
    ) -> BehavioralExplanation:
        """
        Explain behavioral signature analysis
        
        Args:
            actor_id: Actor identifier
            behavioral_signature: Behavioral signature data
            raw_intelligence: Source intelligence data
        
        Returns:
            Behavioral explanation
        """
        traits = behavioral_signature.get('traits', {})
        confidence = behavioral_signature.get('confidence', 0.0)
        
        # Generate trait explanations
        trait_explanations = {}
        for trait_name, trait_value in traits.items():
            trait_explanations[trait_name] = self._explain_trait(trait_name, trait_value)
        
        # Identify risk factors
        risk_factors = []
        if traits.get('flight_risk', 0) > 0.7:
            risk_factors.append("High flight risk detected - actor may attempt to evade detection")
        if traits.get('coordination_likelihood', 0) > 0.7:
            risk_factors.append("High coordination likelihood - actor likely working with others")
        if traits.get('risk_tolerance', 0) > 0.7:
            risk_factors.append("High risk tolerance - actor may take aggressive actions")
        
        # Confidence breakdown
        confidence_breakdown = {
            'data_quality': min(confidence, 0.9),  # Assume good data quality
            'trait_consistency': confidence * 0.8,  # Trait consistency factor
            'sample_size': min(len(raw_intelligence) / 10, 1.0) * confidence  # Sample size factor
        }
        
        return BehavioralExplanation(
            actor_id=actor_id,
            traits_identified=traits,
            trait_explanations=trait_explanations,
            risk_factors=risk_factors,
            confidence_breakdown=confidence_breakdown
        )
    
    def explain_coordination_network(
        self,
        coordination_network: Dict,
        transaction_data: Optional[List[Dict]] = None
    ) -> NetworkExplanation:
        """
        Explain coordination network detection
        
        Args:
            coordination_network: Coordination network data
            transaction_data: Transaction data used for analysis
        
        Returns:
            Network explanation
        """
        partners = coordination_network.get('partners', [])
        facilitators = coordination_network.get('facilitators', [])
        
        # Extract entities
        entities = []
        for partner in partners:
            if isinstance(partner, dict):
                entities.append(partner.get('entity_id', 'unknown'))
            else:
                entities.append(str(partner))
        
        # Extract relationships
        relationships = []
        for partner in partners:
            if isinstance(partner, dict):
                relationships.append({
                    'from': 'primary_actor',
                    'to': partner.get('entity_id', 'unknown'),
                    'type': partner.get('relationship_type', 'COORDINATES_WITH'),
                    'confidence': partner.get('confidence', 0.0)
                })
        
        # Relationship confidence
        relationship_confidence = {
            rel['to']: rel['confidence']
            for rel in relationships
        }
        
        # Coordination evidence
        evidence = []
        if transaction_data:
            evidence.append(f"Analyzed {len(transaction_data)} transactions")
        if len(partners) > 0:
            evidence.append(f"Detected {len(partners)} coordination partners")
        if len(facilitators) > 0:
            evidence.append(f"Identified {len(facilitators)} facilitators")
        
        # Network strength (average confidence)
        if relationships:
            network_strength = sum(rel['confidence'] for rel in relationships) / len(relationships)
        else:
            network_strength = 0.0
        
        return NetworkExplanation(
            network_id=coordination_network.get('network_id', 'unknown'),
            entities=entities,
            relationships=relationships,
            relationship_confidence=relationship_confidence,
            coordination_evidence=evidence,
            network_strength=network_strength
        )
    
    def explain_risk_assessment(
        self,
        risk_assessment: Dict,
        behavioral_explanation: Optional[BehavioralExplanation] = None,
        network_explanation: Optional[NetworkExplanation] = None
    ) -> DecisionExplanation:
        """
        Explain risk assessment decision
        
        Args:
            risk_assessment: Risk assessment data
            behavioral_explanation: Behavioral explanation (optional)
            network_explanation: Network explanation (optional)
        
        Returns:
            Decision explanation
        """
        overall_risk = risk_assessment.get('overall_risk', 0.0)
        threat_level = risk_assessment.get('threat_level', 'unknown')
        
        # Contributing factors
        contributing_factors = []
        
        if behavioral_explanation:
            contributing_factors.append({
                'factor': 'Behavioral Analysis',
                'weight': 0.4,
                'value': behavioral_explanation.traits_identified,
                'explanation': 'Behavioral traits indicate risk level'
            })
        
        if network_explanation:
            contributing_factors.append({
                'factor': 'Coordination Network',
                'weight': 0.3,
                'value': network_explanation.network_strength,
                'explanation': f'Network strength: {network_explanation.network_strength:.2%}'
            })
        
        contributing_factors.append({
            'factor': 'Historical Patterns',
            'weight': 0.3,
            'value': overall_risk,
            'explanation': 'Historical threat patterns'
        })
        
        # Reasoning
        reasoning = f"Risk assessment of {overall_risk:.1%} ({threat_level.upper()}) based on: "
        if behavioral_explanation:
            reasoning += f"behavioral analysis ({len(behavioral_explanation.traits_identified)} traits), "
        if network_explanation:
            reasoning += f"coordination network ({len(network_explanation.entities)} entities), "
        reasoning += "and historical threat patterns."
        
        # Evidence
        evidence = []
        if behavioral_explanation:
            evidence.extend(behavioral_explanation.risk_factors)
        if network_explanation:
            evidence.extend(network_explanation.coordination_evidence)
        
        # Limitations
        limitations = [
            "Analysis based on available data - may not capture all threat indicators",
            "Confidence scores reflect data quality and sample size",
            "Risk assessment is predictive and may change with new information"
        ]
        
        return DecisionExplanation(
            decision=f"Threat Level: {threat_level.upper()} (Risk: {overall_risk:.1%})",
            confidence=overall_risk,
            contributing_factors=contributing_factors,
            reasoning=reasoning,
            evidence=evidence,
            limitations=limitations
        )
    
    def _explain_trait(self, trait_name: str, trait_value: float) -> str:
        """Generate explanation for a behavioral trait"""
        explanations = {
            'risk_tolerance': f"Risk tolerance: {trait_value:.1%} - {'High' if trait_value > 0.7 else 'Moderate' if trait_value > 0.4 else 'Low'} willingness to take risks",
            'flight_risk': f"Flight risk: {trait_value:.1%} - {'High' if trait_value > 0.7 else 'Moderate' if trait_value > 0.4 else 'Low'} likelihood of attempting to evade detection",
            'coordination_likelihood': f"Coordination likelihood: {trait_value:.1%} - {'High' if trait_value > 0.7 else 'Moderate' if trait_value > 0.4 else 'Low'} probability of working with other entities",
            'pattern_repetition': f"Pattern repetition: {trait_value:.1%} - {'High' if trait_value > 0.7 else 'Moderate' if trait_value > 0.4 else 'Low'} tendency to repeat behavioral patterns",
            'timing_preference': f"Timing preference: {trait_value:.1%} - {'Consistent' if trait_value > 0.7 else 'Variable' if trait_value > 0.4 else 'Random'} timing patterns",
            'route_entropy': f"Route entropy: {trait_value:.1%} - {'High' if trait_value > 0.7 else 'Moderate' if trait_value > 0.4 else 'Low'} variability in transaction routes",
            'liquidity_pattern': f"Liquidity pattern: {trait_value:.1%} - {'Predictable' if trait_value > 0.7 else 'Variable' if trait_value > 0.4 else 'Unpredictable'} liquidity movement patterns",
            'off_ramp_preference': f"Off-ramp preference: {trait_value:.1%} - {'Strong' if trait_value > 0.7 else 'Moderate' if trait_value > 0.4 else 'Weak'} preference for specific off-ramps"
        }
        
        return explanations.get(trait_name, f"{trait_name}: {trait_value:.1%}")
    
    def generate_explanation_report(
        self,
        compilation_result: Dict,
        format: str = 'json'
    ) -> str:
        """
        Generate comprehensive explanation report
        
        Args:
            compilation_result: Full compilation result
            format: Output format ('json', 'markdown', 'text')
        
        Returns:
            Formatted explanation report
        """
        # Extract components
        behavioral_signature = compilation_result.get('behavioral_signature', {})
        coordination_network = compilation_result.get('coordination_network', {})
        risk_assessment = compilation_result.get('risk_assessment', {})
        
        # Generate explanations
        behavioral_expl = None
        if behavioral_signature:
            behavioral_expl = self.explain_behavioral_signature(
                compilation_result.get('actor_id', 'unknown'),
                behavioral_signature,
                compilation_result.get('raw_intelligence', [])
            )
        
        network_expl = None
        if coordination_network:
            network_expl = self.explain_coordination_network(
                coordination_network,
                compilation_result.get('transaction_data')
            )
        
        risk_expl = None
        if risk_assessment:
            risk_expl = self.explain_risk_assessment(
                risk_assessment,
                behavioral_expl,
                network_expl
            )
        
        # Format output
        if format == 'json':
            return json.dumps({
                'timestamp': datetime.now().isoformat(),
                'actor_id': compilation_result.get('actor_id'),
                'behavioral_explanation': asdict(behavioral_expl) if behavioral_expl else None,
                'network_explanation': asdict(network_expl) if network_expl else None,
                'risk_explanation': asdict(risk_expl) if risk_expl else None
            }, indent=2)
        
        elif format == 'markdown':
            lines = [
                "# AI Decision Explanation Report",
                f"**Actor ID**: {compilation_result.get('actor_id', 'unknown')}",
                f"**Generated**: {datetime.now().isoformat()}",
                "",
                "## Risk Assessment",
                ""
            ]
            
            if risk_expl:
                lines.extend([
                    f"**Decision**: {risk_expl.decision}",
                    f"**Confidence**: {risk_expl.confidence:.1%}",
                    "",
                    "### Reasoning",
                    risk_expl.reasoning,
                    "",
                    "### Contributing Factors",
                    ""
                ])
                
                for factor in risk_expl.contributing_factors:
                    lines.append(f"- **{factor['factor']}** (Weight: {factor['weight']:.0%}): {factor['explanation']}")
                
                lines.extend([
                    "",
                    "### Evidence",
                    ""
                ])
                
                for evidence in risk_expl.evidence:
                    lines.append(f"- {evidence}")
                
                lines.extend([
                    "",
                    "### Limitations",
                    ""
                ])
                
                for limitation in risk_expl.limitations:
                    lines.append(f"- {limitation}")
            
            if behavioral_expl:
                lines.extend([
                    "",
                    "## Behavioral Analysis",
                    "",
                    f"**Traits Identified**: {len(behavioral_expl.traits_identified)}",
                    "",
                    "### Trait Explanations",
                    ""
                ])
                
                for trait, explanation in behavioral_expl.trait_explanations.items():
                    lines.append(f"- **{trait}**: {explanation}")
            
            if network_expl:
                lines.extend([
                    "",
                    "## Coordination Network",
                    "",
                    f"**Network Strength**: {network_expl.network_strength:.1%}",
                    f"**Entities**: {len(network_expl.entities)}",
                    "",
                    "### Relationships",
                    ""
                ])
                
                for rel in network_expl.relationships:
                    lines.append(f"- {rel['from']} → {rel['to']} ({rel['type']}, Confidence: {rel['confidence']:.1%})")
            
            return "\n".join(lines)
        
        else:  # text format
            lines = [
                "AI Decision Explanation Report",
                "=" * 60,
                f"Actor ID: {compilation_result.get('actor_id', 'unknown')}",
                f"Generated: {datetime.now().isoformat()}",
                "",
                "RISK ASSESSMENT",
                "-" * 60
            ]
            
            if risk_expl:
                lines.extend([
                    f"Decision: {risk_expl.decision}",
                    f"Confidence: {risk_expl.confidence:.1%}",
                    "",
                    "Reasoning:",
                    risk_expl.reasoning,
                    "",
                    "Contributing Factors:",
                ])
                
                for factor in risk_expl.contributing_factors:
                    lines.append(f"  - {factor['factor']}: {factor['explanation']}")
            
            return "\n".join(lines)


# Global explainer instance
_xai_explainer: Optional['XAIExplainer'] = None


def get_xai_explainer() -> 'XAIExplainer':
    """Get or create global XAI explainer instance"""
    global _xai_explainer
    if _xai_explainer is None:
        _xai_explainer = XAIExplainer()
    return _xai_explainer

