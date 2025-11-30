"""
AI Ontology Integration Layer
Integrates AI components with existing Hades/Echo/Nemesis systems

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .semantic_understanding import SemanticUnderstandingLayer, ExtractedEntity
from .auto_classification import AutoClassificationSystem, ThreatClassification
from .relationship_inference import RelationshipInferenceEngine, InferredRelationship
from .behavioral_signature import AIHadesProfiler, BehavioralSignature
from .predictive_modeling import PredictiveThreatModel, ThreatForecast
from .continuous_learning import ContinuousLearningSystem, LearningFeedback
from .natural_language_interface import NaturalLanguageInterface, NLQuery
from .threat_dossier_generator import ThreatDossierGenerator, ThreatDossier


class ABCIntegrationLayer:
    """
    Integration layer that connects AI ontology components
    with existing Hades/Echo/Nemesis systems
    """
    
    def __init__(self):
        # Initialize AI components
        self.semantic_layer = SemanticUnderstandingLayer()
        self.classifier = AutoClassificationSystem()
        self.relationship_engine = RelationshipInferenceEngine()
        self.hades_ai = AIHadesProfiler()
        self.predictive_model = PredictiveThreatModel()
        self.learning_system = ContinuousLearningSystem()
        self.nl_interface = NaturalLanguageInterface()
        self.dossier_generator = ThreatDossierGenerator()
        
    def process_intelligence_feed(
        self,
        raw_intelligence: List[Dict[str, Any]],
        transaction_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process raw intelligence through full AI pipeline
        
        Args:
            raw_intelligence: Unstructured intelligence (reports, tweets, etc.)
            transaction_data: Transaction history (if available)
            
        Returns:
            Compiled intelligence package
        """
        # Step 1: Semantic understanding - extract entities
        entities = []
        for item in raw_intelligence:
            # Handle both dict and string formats
            text = item.get("text", item) if isinstance(item, dict) else str(item)
            source_type = item.get("source", "report") if isinstance(item, dict) else "report"
            extracted = self.semantic_layer.extract_entities(text, source_type)
            entities.extend(extracted)
        
        # Step 2: Auto-classification
        classified_entities = []
        for entity in entities:
            classification = self.classifier.classify_entity(entity)
            classified_entities.append({
                "entity": entity,
                "classification": classification
            })
        
        # Step 3: Relationship inference
        relationships = self.relationship_engine.infer_relationships(classified_entities)
        
        # Step 4: Behavioral signatures (if transaction data available)
        behavioral_signatures = {}
        if transaction_data:
            for entity in classified_entities:
                actor_id = entity["entity"].entity_id
                signature = self.hades_ai.generate_signature(
                    actor_id=actor_id,
                    transaction_history=transaction_data,
                    network_data=None,
                    intelligence_reports=[item.get("text", "") for item in raw_intelligence]
                )
                behavioral_signatures[actor_id] = signature
        
        # Step 5: Threat forecasting
        forecasts = {}
        for actor_id, signature in behavioral_signatures.items():
            forecast = self.predictive_model.generate_forecast(
                actor_id=actor_id,
                behavioral_signature={
                    "traits": {k.value: v for k, v in signature.traits.items()},
                    "confidence": signature.confidence,
                    "risk_score": signature.traits.get("risk_tolerance", 0.5)
                },
                transaction_history=transaction_data or [],
                network_data=None,
                historical_patterns=None
            )
            forecasts[actor_id] = forecast
        
        return {
            "entities": classified_entities,
            "relationships": relationships,
            "behavioral_signatures": behavioral_signatures,
            "threat_forecasts": forecasts,
            "processed_at": datetime.now().isoformat()
        }
    
    def generate_targeting_package(
        self,
        actor_id: str,
        intelligence_package: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Nemesis targeting package from AI-compiled intelligence
        
        Args:
            actor_id: Target actor ID
            intelligence_package: Output from process_intelligence_feed
            
        Returns:
            Executable targeting package
        """
        signature = intelligence_package["behavioral_signatures"].get(actor_id)
        forecast = intelligence_package["threat_forecasts"].get(actor_id)
        
        if not signature or not forecast:
            return {"error": "Insufficient intelligence for targeting package"}
        
        # Generate dossier
        dossier = self.dossier_generator.generate_dossier(
            actor_id=actor_id,
            actor_name=f"Actor_{actor_id}",
            behavioral_signature={
                "traits": {k.value: v for k, v in signature.traits.items()},
                "confidence": signature.confidence,
                "pattern_matches": signature.pattern_matches
            },
            network_data={},
            threat_forecast={
                "predictions": [pred.__dict__ for pred in forecast.predictions],
                "overall_risk_score": forecast.overall_risk_score,
                "next_action_window": forecast.next_action_window,
                "recommended_countermeasures": forecast.recommended_countermeasures
            },
            transaction_history=[],
            historical_patterns=None
        )
        
        return {
            "package_id": f"nemesis_{actor_id}_{datetime.now().strftime('%Y%m%d')}",
            "actor_id": actor_id,
            "confidence": forecast.overall_risk_score,
            "predicted_actions": [pred.__dict__ for pred in forecast.predictions],
            "recommended_countermeasures": forecast.recommended_countermeasures,
            "timing_window": forecast.next_action_window,
            "behavioral_signature": {
                "traits": {k.value: v for k, v in signature.traits.items()},
                "confidence": signature.confidence
            },
            "dossier": dossier,
            "generated_at": datetime.now().isoformat()
        }
    
    def query_natural_language(self, query: str, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Process natural language query
        
        Args:
            query: Natural language query
            user: User making query
            
        Returns:
            Query response with structured data
        """
        response = self.nl_interface.process_query(query, user)
        return {
            "query": query,
            "response": response.response_text,
            "structured_data": response.structured_data,
            "confidence": response.confidence,
            "sources": response.sources,
            "follow_up_suggestions": response.follow_up_suggestions
        }
    
    def record_feedback(
        self,
        feedback_type: str,
        entity_id: str,
        actual_outcome: Dict[str, Any],
        predicted_outcome: Optional[Dict[str, Any]] = None
    ) -> LearningFeedback:
        """
        Record feedback for continuous learning
        
        Args:
            feedback_type: Type of feedback (true_positive, false_positive, etc.)
            entity_id: Entity the feedback relates to
            actual_outcome: What actually happened
            predicted_outcome: What was predicted
            
        Returns:
            LearningFeedback entry
        """
        from .continuous_learning import FeedbackType
        
        feedback_type_enum = FeedbackType[feedback_type.upper()]
        
        return self.learning_system.record_feedback(
            feedback_type=feedback_type_enum,
            entity_id=entity_id,
            actual_outcome=actual_outcome,
            predicted_outcome=predicted_outcome
        )

