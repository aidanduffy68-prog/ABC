"""
AI-Powered Auto-Classification System
Automatically categorizes threats into ontology schema
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json


class ThreatActorType(Enum):
    """Threat actor classifications"""
    NATION_STATE = "nation_state"
    CRIMINAL_ORG = "criminal_organization"
    INDIVIDUAL = "individual"
    INSIDER = "insider"
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ThreatClassification:
    """Classification result for a threat entity"""
    entity_id: str
    actor_type: ThreatActorType
    threat_level: ThreatLevel
    primary_ttps: List[str]
    risk_score: float  # 0-1
    confidence: float  # 0-1
    reasoning: str


class AutoClassificationSystem:
    """
    ML models for automatic threat classification
    - Threat actor classification
    - TTP extraction
    - Campaign clustering
    - Threat taxonomy evolution
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.ttp_patterns = self._load_ttp_patterns()
        self.campaign_clusters = {}
    
    def _load_ttp_patterns(self) -> Dict[str, List[str]]:
        """Load known TTP patterns for classification"""
        return {
            "money_laundering": [
                "tornado_cash", "mixer", "bridge_hopping", "chain_switching"
            ],
            "sanctions_evasion": [
                "jurisdiction_hopping", "otc_desk", "p2p_exchange", "privacy_coin"
            ],
            "exchange_hack": [
                "bridge_exploit", "flash_loan", "reentrancy", "oracle_manipulation"
            ],
            "coordination": [
                "synchronized_timing", "gas_strategy_match", "route_similarity"
            ]
        }
    
    def classify_threat_actor(self, entity_data: Dict[str, Any]) -> ThreatClassification:
        """
        Classify a threat actor based on behavioral patterns
        
        Args:
            entity_data: Entity attributes from Behavioral Intelligence Graph
        
        Returns:
            ThreatClassification with actor type, threat level, TTPs
        """
        # TODO: Implement ML model inference
        # For now, use rule-based classification as placeholder
        
        behavioral_signatures = entity_data.get("behavioral_signatures", {})
        risk_score = entity_data.get("risk_score", 0.5)
        
        # Determine actor type from patterns
        actor_type = self._infer_actor_type(behavioral_signatures, entity_data)
        
        # Extract TTPs
        ttps = self._extract_ttps(behavioral_signatures, entity_data)
        
        # Determine threat level
        threat_level = self._calculate_threat_level(risk_score, ttps, actor_type)
        
        return ThreatClassification(
            entity_id=entity_data.get("actor_id", "unknown"),
            actor_type=actor_type,
            threat_level=threat_level,
            primary_ttps=ttps,
            risk_score=risk_score,
            confidence=0.85,  # TODO: Calculate from model confidence
            reasoning=self._generate_reasoning(actor_type, threat_level, ttps)
        )
    
    def _infer_actor_type(self, behavioral_signatures: Dict, entity_data: Dict) -> ThreatActorType:
        """Infer threat actor type from behavioral patterns"""
        # Rule-based inference (to be replaced with ML model)
        
        if entity_data.get("nation_state_indicators"):
            return ThreatActorType.NATION_STATE
        
        if entity_data.get("organization_size", 0) > 10:
            return ThreatActorType.CRIMINAL_ORG
        
        return ThreatActorType.INDIVIDUAL
    
    def _extract_ttps(self, behavioral_signatures: Dict, entity_data: Dict) -> List[str]:
        """Extract Tactics, Techniques, and Procedures"""
        ttps = []
        
        # Check transaction patterns
        if "tornado_cash" in str(entity_data.get("transaction_history", "")).lower():
            ttps.append("money_laundering")
        
        if entity_data.get("jurisdiction_switching_count", 0) > 3:
            ttps.append("sanctions_evasion")
        
        # Check coordination patterns
        if entity_data.get("coordination_score", 0) > 0.8:
            ttps.append("coordination")
        
        return ttps
    
    def _calculate_threat_level(self, risk_score: float, ttps: List[str], actor_type: ThreatActorType) -> ThreatLevel:
        """Calculate threat level from risk score and TTPs"""
        if risk_score >= 0.9 or actor_type == ThreatActorType.NATION_STATE:
            return ThreatLevel.CRITICAL
        elif risk_score >= 0.7 or len(ttps) >= 3:
            return ThreatLevel.HIGH
        elif risk_score >= 0.5:
            return ThreatLevel.MEDIUM
        return ThreatLevel.LOW
    
    def _generate_reasoning(self, actor_type: ThreatActorType, threat_level: ThreatLevel, ttps: List[str]) -> str:
        """Generate human-readable reasoning for classification"""
        return f"Classified as {actor_type.value} with {threat_level.value} threat level. Primary TTPs: {', '.join(ttps)}"
    
    def cluster_campaigns(self, entities: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Cluster related operations into campaigns using unsupervised learning
        
        Args:
            entities: List of threat entities
        
        Returns:
            Dictionary mapping campaign_id to list of entity_ids
        """
        # TODO: Implement clustering algorithm (e.g., DBSCAN, hierarchical clustering)
        # For now, return placeholder structure
        
        campaigns = {}
        # Group entities by similar TTPs, timing, and targets
        return campaigns
    
    def evolve_taxonomy(self, new_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evolve threat taxonomy when new patterns are discovered
        
        Args:
            new_patterns: Previously unseen threat patterns
        
        Returns:
            Updated taxonomy schema
        """
        # TODO: Implement taxonomy evolution logic
        # Automatically add new categories when patterns don't fit existing schema
        return {}


if __name__ == "__main__":
    # Example usage
    classifier = AutoClassificationSystem()
    
    sample_entity = {
        "actor_id": "ALPHA_47",
        "risk_score": 0.94,
        "behavioral_signatures": {
            "pattern_repetition": 1.0,
            "flight_risk": 0.96
        },
        "transaction_history": "tornado_cash, bridge_hopping",
        "jurisdiction_switching_count": 5,
        "coordination_score": 0.87
    }
    
    classification = classifier.classify_threat_actor(sample_entity)
    print(f"Classification: {classification}")

