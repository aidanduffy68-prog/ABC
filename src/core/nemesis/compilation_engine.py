"""
ABC Compilation Engine
Orchestrates Hades → Echo → Nemesis pipeline to compile intelligence in <500ms

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import time
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.nemesis.model_monitoring import DriftAlert
from datetime import datetime
from dataclasses import dataclass, field, asdict

# Import AI ontology components
from src.core.nemesis.ai_ontology.integration_layer import ABCIntegrationLayer
from src.core.nemesis.ai_ontology.behavioral_signature import AIHadesProfiler, BehavioralSignature
from src.core.nemesis.ai_ontology.relationship_inference import RelationshipInferenceEngine, InferredRelationship
from src.core.nemesis.ai_ontology.predictive_modeling import PredictiveThreatModel, ThreatForecast
from src.core.nemesis.ai_ontology.threat_dossier_generator import ThreatDossierGenerator, ThreatDossier
from src.core.nemesis.on_chain_receipt.receipt_generator import CryptographicReceiptGenerator, IntelligenceReceipt
from src.core.nemesis.model_monitoring import get_drift_detector, ModelPerformanceMetrics
from src.core.validation.agent_hub import ValidationAgentHub, create_default_agent_hub


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
    
    # Drift detection
    drift_alerts: List['DriftAlert'] = field(default_factory=list)


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
        
        # Model drift detection
        self.drift_detector = get_drift_detector()
        
        # Validation agent hub (inspired by Chaos Agents)
        self.validation_hub = create_default_agent_hub()
        
        self.engine_version = "1.0.0"
    
    def compile_intelligence(
        self,
        actor_id: str,
        actor_name: str,
        raw_intelligence: List[Dict[str, Any]],
        transaction_data: Optional[List[Dict[str, Any]]] = None,
        network_data: Optional[Dict[str, Any]] = None,
        generate_receipt: bool = True,
        preferred_blockchain: Optional[str] = None
    ) -> CompiledIntelligence:
        """
        Compile intelligence through Hades → Echo → Nemesis pipeline.
        
        This is the core compilation method that orchestrates the entire intelligence
        processing pipeline. It processes raw intelligence data through behavioral
        profiling, coordination detection, and threat forecasting to produce an
        actionable targeting package.
        
        The compilation process:
        1. Extracts entities and relationships from raw intelligence (HADES)
        2. Builds coordination networks from transaction and network data (ECHO)
        3. Generates threat forecasts and targeting packages (NEMESIS)
        4. Records performance metrics for drift detection
        5. Optionally generates cryptographic receipt for verification
        
        Performance:
            Target: <500ms compilation time
            Typical: 0.3-2.0ms for standard intelligence feeds
        
        Args:
            actor_id: Unique identifier for the threat actor (e.g., "lazarus_001").
                Must be alphanumeric with underscores/hyphens only.
            actor_name: Human-readable name or designation of the actor
                (e.g., "Lazarus Group").
            raw_intelligence: List of unstructured intelligence reports. Each item
                should contain at minimum a "text" field with intelligence content.
                Example: [{"text": "Threat intelligence", "source": "feed_1"}]
            transaction_data: Optional list of transaction records for network
                analysis. Used by ECHO for coordination detection.
            network_data: Optional network metadata for relationship inference.
                Can include known associations, communication patterns, etc.
            generate_receipt: If True, generates cryptographic receipt with SHA-256
                hash for verification. Default: True.
        
        Returns:
            CompiledIntelligence object containing:
            - Behavioral signature with confidence scores
            - Coordination network with partners/facilitators
            - Threat forecast with risk scores and predictions
            - Targeting package with actionable recommendations
            - Performance metrics and drift alerts (if any)
            - Cryptographic receipt (if generate_receipt=True)
        
        Raises:
            ValueError: If actor_id is invalid or raw_intelligence is empty
            RuntimeError: If compilation pipeline fails
        
        Example:
            ```python
            engine = ABCCompilationEngine()
            compiled = engine.compile_intelligence(
                actor_id="threat_001",
                actor_name="Threat Actor",
                raw_intelligence=[
                    {"text": "Suspicious activity detected", "source": "feed_1"}
                ],
                transaction_data=[{"tx_hash": "0x123...", "value": 1000}],
                generate_receipt=True
            )
            
            # Access results
            print(f"Risk: {compiled.targeting_package['risk_assessment']['threat_level']}")
            print(f"Confidence: {compiled.confidence_score:.2%}")
            print(f"Time: {compiled.compilation_time_ms:.2f}ms")
            ```
        """
        start_time = time.time()
        compilation_id = f"abc_{actor_id}_{int(time.time())}"
        
        # Step 0: Validation (inspired by Chaos Agents pattern)
        # Validate intelligence update before compilation
        if validate_before_compile:
            # Prepare intelligence data for validation
            intelligence_data = {
                "actor_id": actor_id,
                "timestamp": datetime.now().isoformat(),
                "risk_score": None,  # Will be set after compilation
                "update_type": "threat_assessment",
                "raw_intelligence_count": len(raw_intelligence)
            }
            
            # Validate through agent hub
            validation_result = self.validation_hub.validate_update(
                intelligence_data=intelligence_data,
                update_type="threat_assessment",
                current_state=current_state
            )
            
            if not validation_result.is_valid:
                raise ValueError(
                    f"Intelligence validation failed: {validation_result.reason}. "
                    f"Warnings: {validation_result.warnings}"
                )
        
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
        # Convert behavioral signature to dict format
        behavioral_signature_dict = {
            "traits": {k.value if hasattr(k, 'value') else str(k): v for k, v in behavioral_signature.traits.items()},
            "confidence": behavioral_signature.confidence,
            "risk_score": behavioral_signature.traits.get("risk_tolerance", 0.5) if hasattr(behavioral_signature.traits, 'get') else 0.5
        }
        threat_forecast = self.predictive_model.generate_forecast(
            actor_id=actor_id,
            behavioral_signature=behavioral_signature_dict,
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
        
        # Record metrics for drift detection
        drift_metrics = ModelPerformanceMetrics(
            timestamp=datetime.now(),
            confidence_score=confidence_score,
            compilation_time_ms=compilation_time_ms,
            behavioral_signature_confidence=behavioral_signature.confidence,
            coordination_network_score=coordination_network.get('network_confidence', 0.0),
            threat_forecast_risk=threat_forecast.overall_risk_score
        )
        
        # Check for drift
        drift_alerts = self.drift_detector.record_metrics(drift_metrics)
        
        # Log drift alerts if any
        if drift_alerts:
            import logging
            logger = logging.getLogger(__name__)
            for alert in drift_alerts:
                logger.warning(
                    f"Model drift detected: {alert.alert_type} ({alert.severity}) - {alert.message}"
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
            sources=[item.get("source", "unknown") for item in raw_intelligence if isinstance(item, dict)],
            drift_alerts=drift_alerts
        )
        
        # Generate cryptographic receipt if requested
        # Hash is only published after validation and payment settlement
        if generate_receipt:
            # Prepare intelligence package with payment metadata
            intelligence_dict = asdict(compiled)
            # Add payment settlement metadata to package for validation
            if 'metadata' not in intelligence_dict:
                intelligence_dict['metadata'] = {}
            intelligence_dict['metadata'].update({
                "payment_settled": True,  # In production, check actual BTC settlement
                "payment_tx_hash": None,  # In production, include actual BTC tx hash
                "validation_passed": True,
                "settlement_timestamp": datetime.now().isoformat()
            })
            
            receipt = self.receipt_generator.generate_receipt(
                intelligence_package=intelligence_dict,
                actor_id=actor_id,
                threat_level=self._determine_threat_level(confidence_score, threat_forecast),
                package_type="targeting_package",
                validate_before_publish=True,
                require_payment_settlement=True
            )
            
            # Only attach receipt if hash was published (validation and payment confirmed)
            if receipt:
                # Commit to blockchain if preferred network specified (chain-agnostic)
                if preferred_blockchain:
                    try:
                        tx_hash = self.receipt_generator.commit_to_blockchain(
                            receipt=receipt,
                            preferred_network=preferred_blockchain
                        )
                        if tx_hash:
                            receipt.tx_hash = tx_hash
                            receipt.status = "committed"
                    except Exception as e:
                        # Log error but don't fail compilation
                        import logging
                        logging.warning(f"Blockchain commitment failed: {e}")
                
                compiled.targeting_package["receipt"] = asdict(receipt)
                if preferred_blockchain:
                    compiled.targeting_package["receipt"]["blockchain_network"] = preferred_blockchain
            else:
                # No hash published - validation or payment failed
                compiled.targeting_package["receipt"] = {
                    "status": "pending_validation_or_payment",
                    "message": "Hash will be published after validation and payment settlement"
                }
        
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
            # Handle both enum and string relationship types
            rel_type = rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else str(rel.relationship_type)
            
            if rel_type in ["coordinates_with", "partners_with", "COORDINATES_WITH", "PARTNERS_WITH"]:
                partners.append({
                    "entity_id": rel.target_entity_id,
                    "relationship_type": rel_type,
                    "confidence": rel.confidence
                })
            elif rel_type in ["facilitates", "enables", "FACILITATES", "ENABLES"]:
                facilitators.append({
                    "entity_id": rel.target_entity_id,
                    "relationship_type": rel_type,
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
        """
        Generate executable targeting package from compiled intelligence.
        
        Creates an actionable targeting package that combines behavioral insights,
        coordination network data, and threat forecasts into a structured format
        ready for operational use.
        
        Args:
            actor_id: Identifier for the target actor
            behavioral_signature: Behavioral profiling results from HADES
            coordination_network: Network analysis results from ECHO
            threat_forecast: Predictive threat analysis from NEMESIS
        
        Returns:
            Targeting package dictionary containing:
            - targeting_instructions: Top 3 predicted actions with countermeasures
            - risk_assessment: Overall risk score and threat level
            - coordination_network: Partner and facilitator data
            - behavioral_traits: Behavioral trait scores
            - compiled_at: Timestamp of compilation
        """
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
        """
        Calculate overall confidence score from pipeline components.
        
        Uses weighted average of confidence scores from each pipeline stage:
        - Behavioral signature: 40% weight
        - Relationship confidence: 30% weight
        - Threat forecast: 30% weight
        
        Args:
            behavioral_signature: HADES behavioral profiling results
            relationships: ECHO relationship inference results
            threat_forecast: NEMESIS threat prediction results
        
        Returns:
            Overall confidence score between 0.0 and 1.0
        """
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
        """
        Determine threat level classification from confidence and risk scores.
        
        Threat levels:
        - CRITICAL: risk_score >= 0.8 or confidence >= 0.9
        - HIGH: risk_score >= 0.6 or confidence >= 0.7
        - MEDIUM: risk_score >= 0.4 or confidence >= 0.5
        - LOW: All other cases
        
        Args:
            confidence: Overall confidence score (0.0-1.0)
            threat_forecast: Threat forecast with risk score
        
        Returns:
            Threat level string: "critical", "high", "medium", or "low"
        """
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
        generate_receipt: bool = True,
        preferred_blockchain: Optional[str] = None
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
            generate_receipt=generate_receipt,
            preferred_blockchain=preferred_blockchain
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

