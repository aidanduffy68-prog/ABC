"""
ABC Compilation Engine
Orchestrates Hades → Echo → Nemesis pipeline to compile intelligence in <500ms

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

# Import AI ontology components
from nemesis.ai_ontology.integration_layer import ABCIntegrationLayer
from nemesis.ai_ontology.behavioral_signature import AIHadesProfiler, BehavioralSignature
from nemesis.ai_ontology.relationship_inference import RelationshipInferenceEngine, InferredRelationship
from nemesis.ai_ontology.predictive_modeling import PredictiveThreatModel, ThreatForecast
from nemesis.ai_ontology.threat_dossier_generator import ThreatDossierGenerator, ThreatDossier
from nemesis.on_chain_receipt.receipt_generator import CryptographicReceiptGenerator, IntelligenceReceipt


@dataclass
class CompiledIntelligence:
    """Complete compiled intelligence package"""
    compilation_id: str
    actor_id: str
    actor_name: str
    compiled_at: datetime
    
    # Hades output
    behavioral_signature: BehavioralSignature
    
    # Echo output
    coordination_network: Dict[str, Any] = field(default_factory=dict)
    relationships: List[InferredRelationship] = field(default_factory=list)
    
    # Nemesis output
    targeting_package: Dict[str, Any] = field(default_factory=dict)
    threat_forecast: ThreatForecast = None
    
    # Metadata
    compilation_time_ms: float = 0.0
    confidence_score: float = 0.0
    sources: List[str] = field(default_factory=list)


class ABCCompilationEngine:
    """
    Core compilation engine that orchestrates Hades → Echo → Nemesis
    
    Compiles intelligence in <500ms from raw telemetry to executable targeting packages
    """
    
    def __init__(self):
        """Initialize compilation engine with all components"""
        # AI integration layer
        self.ai_layer = ABCIntegrationLayer()
        
        # Hades: Behavioral profiling
        self.hades = AIHadesProfiler()
        
        # Echo: Coordination detection
        self.echo = RelationshipInferenceEngine()
        
        # Nemesis: Targeting packages
        self.dossier_generator = ThreatDossierGenerator()
        self.predictive_model = PredictiveThreatModel()
        
        # Cryptographic receipts
        self.receipt_generator = CryptographicReceiptGenerator()
        
        self.engine_version = "1.0.0"
    
    def compile_intelligence(
        self,
        actor_id: str,
        actor_name: str,
        raw_intelligence: List[Dict[str, Any]],
        transaction_data: Optional[List[Dict[str, Any]]] = None,
        network_data: Optional[Dict[str, Any]] = None,
        generate_receipt: bool = True
    ) -> CompiledIntelligence:
        """
        Compile intelligence through Hades → Echo → Nemesis pipeline
        
        Args:
            actor_id: Unique identifier for the actor
            actor_name: Name/designation of the actor
            raw_intelligence: Unstructured intelligence feeds
            transaction_data: Historical transaction data
            network_data: Network coordination data
            generate_receipt: Whether to generate cryptographic receipt
            
        Returns:
            CompiledIntelligence package ready for delivery
        """
        start_time = time.time()
        compilation_id = f"abc_{actor_id}_{int(time.time())}"
        
        # Step 1: HADES - Behavioral Profiling
        # Compile raw telemetry into actor signatures & risk posture
        behavioral_signature = self.hades.generate_signature(
            actor_id=actor_id,
            transaction_history=transaction_data or [],
            network_data=network_data,
            intelligence_reports=[item.get("text", str(item)) for item in raw_intelligence if isinstance(item, dict)]
        )
        
        # Step 2: ECHO - Coordination Detection
        # Surface coordination networks with confidence/provenance
        # Process intelligence through AI layer for relationship inference
        ai_output = self.ai_layer.process_intelligence_feed(raw_intelligence, transaction_data)
        
        # Infer relationships
        relationships = self.echo.infer_relationships({
            "entities": ai_output.get("entities", []),
            "behavioral_signatures": {actor_id: behavioral_signature}
        })
        
        # Build coordination network
        coordination_network = self._build_coordination_network(
            relationships,
            network_data or {}
        )
        
        # Step 3: NEMESIS - Targeting Package Generation
        # Generate executable targeting packages
        threat_forecast = self.predictive_model.forecast_threat(
            actor_id=actor_id,
            behavioral_signature=behavioral_signature,
            network_data=coordination_network,
            transaction_history=transaction_data or []
        )
        
        # Generate targeting package
        targeting_package = self._generate_targeting_package(
            actor_id=actor_id,
            behavioral_signature=behavioral_signature,
            coordination_network=coordination_network,
            threat_forecast=threat_forecast
        )
        
        # Calculate compilation time
        compilation_time_ms = (time.time() - start_time) * 1000
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence(
            behavioral_signature,
            relationships,
            threat_forecast
        )
        
        # Build compiled intelligence
        compiled = CompiledIntelligence(
            compilation_id=compilation_id,
            actor_id=actor_id,
            actor_name=actor_name,
            compiled_at=datetime.now(),
            behavioral_signature=behavioral_signature,
            coordination_network=coordination_network,
            relationships=relationships,
            targeting_package=targeting_package,
            threat_forecast=threat_forecast,
            compilation_time_ms=compilation_time_ms,
            confidence_score=confidence_score,
            sources=[item.get("source", "unknown") for item in raw_intelligence if isinstance(item, dict)]
        )
        
        # Generate cryptographic receipt if requested
        if generate_receipt:
            receipt = self.receipt_generator.generate_receipt(
                intelligence_package=asdict(compiled),
                actor_id=actor_id,
                threat_level=self._determine_threat_level(confidence_score, threat_forecast),
                package_type="targeting_package"
            )
            # Attach receipt to compiled intelligence
            compiled.targeting_package["receipt"] = asdict(receipt)
        
        return compiled
    
    def _build_coordination_network(
        self,
        relationships: List[InferredRelationship],
        network_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build coordination network from relationships"""
        partners = []
        facilitators = []
        
        for rel in relationships:
            if rel.relationship_type.value in ["coordinates_with", "partners_with"]:
                partners.append({
                    "entity_id": rel.target_entity_id,
                    "relationship_type": rel.relationship_type.value,
                    "confidence": rel.confidence
                })
            elif rel.relationship_type.value in ["facilitates", "enables"]:
                facilitators.append({
                    "entity_id": rel.target_entity_id,
                    "relationship_type": rel.relationship_type.value,
                    "confidence": rel.confidence
                })
        
        return {
            "partners": partners,
            "facilitators": facilitators,
            "partner_count": len(partners),
            "facilitator_count": len(facilitators),
            "network_confidence": sum(r.confidence for r in relationships) / len(relationships) if relationships else 0.0
        }
    
    def _generate_targeting_package(
        self,
        actor_id: str,
        behavioral_signature: BehavioralSignature,
        coordination_network: Dict[str, Any],
        threat_forecast: ThreatForecast
    ) -> Dict[str, Any]:
        """Generate executable targeting package"""
        # Get top predicted actions
        top_predictions = sorted(
            threat_forecast.predictions,
            key=lambda p: p.confidence,
            reverse=True
        )[:3]
        
        return {
            "actor_id": actor_id,
            "targeting_instructions": [
                {
                    "action": pred.action_type.value,
                    "description": pred.description,
                    "confidence": pred.confidence,
                    "timeframe": pred.estimated_timeframe,
                    "recommended_countermeasure": pred.recommended_countermeasure
                }
                for pred in top_predictions
            ],
            "risk_assessment": {
                "overall_risk": threat_forecast.overall_risk_score,
                "threat_level": self._determine_threat_level(
                    behavioral_signature.confidence,
                    threat_forecast
                ),
                "next_action_window": threat_forecast.next_action_window
            },
            "coordination_network": {
                "partners": coordination_network.get("partners", []),
                "facilitators": coordination_network.get("facilitators", [])
            },
            "behavioral_traits": {
                trait.value: score
                for trait, score in behavioral_signature.traits.items()
            },
            "compiled_at": datetime.now().isoformat()
        }
    
    def _calculate_confidence(
        self,
        behavioral_signature: BehavioralSignature,
        relationships: List[InferredRelationship],
        threat_forecast: ThreatForecast
    ) -> float:
        """Calculate overall confidence score"""
        sig_confidence = behavioral_signature.confidence
        rel_confidence = sum(r.confidence for r in relationships) / len(relationships) if relationships else 0.0
        forecast_confidence = threat_forecast.overall_risk_score
        
        # Weighted average
        return (sig_confidence * 0.4 + rel_confidence * 0.3 + forecast_confidence * 0.3)
    
    def _determine_threat_level(
        self,
        confidence: float,
        threat_forecast: ThreatForecast
    ) -> str:
        """Determine threat level from confidence and forecast"""
        risk_score = threat_forecast.overall_risk_score
        
        if risk_score >= 0.8 or confidence >= 0.9:
            return "critical"
        elif risk_score >= 0.6 or confidence >= 0.7:
            return "high"
        elif risk_score >= 0.4 or confidence >= 0.5:
            return "medium"
        else:
            return "low"
    
    def compile_federal_ai_intelligence(
        self,
        target_agency: str,
        ai_system_data: Dict[str, Any],
        vulnerability_data: List[Dict[str, Any]],
        generate_receipt: bool = True
    ) -> CompiledIntelligence:
        """
        Specialized compilation for federal AI security intelligence
        
        Args:
            target_agency: Agency name (NASA, DoD, DHS, etc.)
            ai_system_data: AI system information
            vulnerability_data: Vulnerability findings
            generate_receipt: Whether to generate cryptographic receipt
            
        Returns:
            CompiledIntelligence for federal AI system
        """
        actor_id = f"federal_ai_{target_agency.lower()}"
        actor_name = f"{target_agency} AI Infrastructure"
        
        # Format as intelligence feed
        raw_intelligence = [
            {
                "text": f"{target_agency} AI system: {ai_system_data.get('name', 'Unknown')}",
                "source": "federal_ai_analysis",
                "type": "ai_system"
            }
        ]
        
        # Add vulnerability data
        for vuln in vulnerability_data:
            raw_intelligence.append({
                "text": f"Vulnerability: {vuln.get('type', 'Unknown')} - {vuln.get('description', '')}",
                "source": "vulnerability_scan",
                "type": "vulnerability"
            })
        
        # Compile using standard pipeline
        return self.compile_intelligence(
            actor_id=actor_id,
            actor_name=actor_name,
            raw_intelligence=raw_intelligence,
            transaction_data=None,
            network_data=ai_system_data,
            generate_receipt=generate_receipt
        )


# Convenience function for quick compilation
def compile_intelligence(
    actor_id: str,
    actor_name: str,
    raw_intelligence: List[Dict[str, Any]],
    transaction_data: Optional[List[Dict[str, Any]]] = None,
    network_data: Optional[Dict[str, Any]] = None
) -> CompiledIntelligence:
    """
    Quick compilation function
    
    Usage:
        compiled = compile_intelligence(
            actor_id="lazarus_001",
            actor_name="Lazarus Group",
            raw_intelligence=[{"text": "..."}],
            transaction_data=[...]
        )
    """
    engine = ABCCompilationEngine()
    return engine.compile_intelligence(
        actor_id=actor_id,
        actor_name=actor_name,
        raw_intelligence=raw_intelligence,
        transaction_data=transaction_data,
        network_data=network_data
    )

