"""
Predictive Threat Modeling System
Uses Risk Propensity Model (NOT timing predictions)
Assesses mobilization index, volatility score, behavioral similarity
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from .risk_propensity import RiskPropensityModel, RiskPropensity


class ThreatActionType(Enum):
    """Types of predicted threat actions"""
    OFF_RAMP_ATTEMPT = "off_ramp_attempt"
    COORDINATION_ACTIVITY = "coordination_activity"
    ATTACK_EXECUTION = "attack_execution"
    ASSET_MOVEMENT = "asset_movement"
    NETWORK_EXPANSION = "network_expansion"
    EVASION_MANEUVER = "evasion_maneuver"


@dataclass
class PredictedAction:
    """Predicted threat action with timing and confidence"""
    action_type: ThreatActionType
    actor_id: str
    predicted_timestamp: datetime
    confidence: float
    timing_window: Tuple[datetime, datetime]
    location: Optional[str] = None
    amount_range: Optional[Tuple[float, float]] = None
    target_entities: List[str] = field(default_factory=list)
    reasoning: str = ""
    evidence: List[str] = field(default_factory=list)


@dataclass
class ThreatForecast:
    """Complete threat forecast for an actor"""
    actor_id: str
    forecast_id: str
    generated_at: datetime
    predictions: List[PredictedAction]
    overall_risk_score: float
    next_action_window: Optional[Tuple[datetime, datetime]] = None
    recommended_countermeasures: List[str] = field(default_factory=list)
    model_version: str = "1.0.0"


class PredictiveThreatModel:
    """
    Risk Propensity Model (NOT timing predictions)
    Assesses mobilization, volatility, and behavioral similarity
    Provides defensible intelligence without false timing promises
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model_version = "2.0.0"  # Updated to use risk propensity
        self.risk_propensity_model = RiskPropensityModel()
        
    def generate_forecast(
        self,
        actor_id: str,
        behavioral_signature: Dict[str, Any],
        transaction_history: List[Dict[str, Any]],
        network_data: Optional[Dict[str, Any]] = None,
        historical_patterns: Optional[List[Dict[str, Any]]] = None
    ) -> ThreatForecast:
        """
        Generate risk propensity assessment (NOT timing predictions)
        
        Args:
            actor_id: Unique identifier for the actor
            behavioral_signature: AI-generated behavioral signature
            transaction_history: Historical transaction data
            network_data: Echo network coordination data
            historical_patterns: Similar actor patterns from past
            
        Returns:
            ThreatForecast with risk propensity assessment (mobilization index, volatility score, behavioral similarity)
            NO specific timing windows
        """
        # Use risk propensity model instead of timing predictions
        risk_propensity = self.risk_propensity_model.assess_risk_propensity(
            actor_id=actor_id,
            behavioral_signature=behavioral_signature,
            transaction_history=transaction_history,
            network_data=network_data,
            historical_patterns=historical_patterns
        )
        
        # Convert risk propensity to forecast format (without timing predictions)
        predictions = self._convert_risk_propensity_to_predictions(risk_propensity)
        
        # Generate countermeasures based on risk propensity
        countermeasures = self._generate_countermeasures_from_risk(risk_propensity)
        
        # NO next_action_window (we don't predict timing)
        forecast = ThreatForecast(
            actor_id=actor_id,
            forecast_id=f"forecast_{actor_id}_{datetime.now().isoformat()}",
            generated_at=datetime.now(),
            predictions=predictions,
            overall_risk_score=risk_propensity.overall_risk_score,
            next_action_window=None,  # No timing predictions
            recommended_countermeasures=countermeasures,
            model_version=self.model_version
        )
        
        return forecast
    
    def _convert_risk_propensity_to_predictions(
        self,
        risk_propensity: RiskPropensity
    ) -> List[PredictedAction]:
        """Convert risk propensity to prediction format (without timing)"""
        predictions = []
        
        # High mobilization index indicates potential off-ramp
        if risk_propensity.mobilization_index > 0.7:
            predictions.append(PredictedAction(
                action_type=ThreatActionType.OFF_RAMP_ATTEMPT,
                actor_id=risk_propensity.actor_id,
                predicted_timestamp=datetime.now(),  # Placeholder, not used
                confidence=risk_propensity.mobilization_index,
                timing_window=(datetime.now(), datetime.now()),  # Placeholder, not used
                location=risk_propensity.recommended_monitoring_targets[0] if risk_propensity.recommended_monitoring_targets else None,
                reasoning=f"High mobilization index ({risk_propensity.mobilization_index:.2f}). {risk_propensity.reasoning}",
                evidence=risk_propensity.evidence
            ))
        
        # High volatility indicates potential coordination
        if risk_propensity.volatility_score > 0.7:
            predictions.append(PredictedAction(
                action_type=ThreatActionType.COORDINATION_ACTIVITY,
                actor_id=risk_propensity.actor_id,
                predicted_timestamp=datetime.now(),  # Placeholder
                confidence=risk_propensity.volatility_score,
                timing_window=(datetime.now(), datetime.now()),  # Placeholder
                reasoning=f"High volatility score ({risk_propensity.volatility_score:.2f}). {risk_propensity.reasoning}",
                evidence=risk_propensity.evidence
            ))
        
        return predictions
    
    def _generate_countermeasures_from_risk(
        self,
        risk_propensity: RiskPropensity
    ) -> List[str]:
        """Generate countermeasures from risk propensity assessment"""
        countermeasures = []
        
        if risk_propensity.overall_risk_score > 0.8:
            countermeasures.append("Immediate freeze on all associated addresses")
            countermeasures.append("Alert all exchanges and OTC desks")
        
        if risk_propensity.mobilization_index > 0.7:
            countermeasures.append(f"Monitor exchanges: {', '.join(risk_propensity.recommended_monitoring_targets[:3])}")
        
        if risk_propensity.behavioral_similarity:
            top_match = max(risk_propensity.behavioral_similarity.items(), key=lambda x: x[1])
            countermeasures.append(f"High similarity to {top_match[0]} pattern - apply known countermeasures")
        
        if not countermeasures:
            countermeasures.append("Continue monitoring")
        
        return countermeasures
    
    def _predict_off_ramp(
        self,
        actor_id: str,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]]
    ) -> Optional[PredictedAction]:
        """Predict off-ramp attempt"""
        flight_risk = signature.get('traits', {}).get('flight_risk', 0.0)
        
        if flight_risk < 0.6:
            return None
        
        # Analyze timing patterns
        timing = self._analyze_off_ramp_timing(transactions)
        
        # Predict location
        location = self._predict_off_ramp_location(signature, transactions)
        
        # Predict amount
        amount_range = self._predict_off_ramp_amount(transactions)
        
        # Calculate timing window (48-72h from now)
        now = datetime.now()
        window_start = now + timedelta(hours=48)
        window_end = now + timedelta(hours=72)
        
        return PredictedAction(
            action_type=ThreatActionType.OFF_RAMP_ATTEMPT,
            actor_id=actor_id,
            predicted_timestamp=window_start + timedelta(hours=12),
            confidence=flight_risk,
            timing_window=(window_start, window_end),
            location=location,
            amount_range=amount_range,
            reasoning=f"High flight risk ({flight_risk:.2f}) with historical off-ramp pattern",
            evidence=["behavioral_signature", "transaction_history", "timing_analysis"]
        )
    
    def _predict_coordination(
        self,
        actor_id: str,
        signature: Dict[str, Any],
        network_data: Optional[Dict[str, Any]]
    ) -> Optional[PredictedAction]:
        """Predict coordination activity"""
        if not network_data:
            return None
        
        coord_score = signature.get('traits', {}).get('coordination_likelihood', 0.0)
        
        if coord_score < 0.5:
            return None
        
        # Predict coordination partners
        partners = network_data.get('identified_partners', [])
        
        # Predict timing (within 7 days)
        now = datetime.now()
        window_start = now + timedelta(days=3)
        window_end = now + timedelta(days=7)
        
        return PredictedAction(
            action_type=ThreatActionType.COORDINATION_ACTIVITY,
            actor_id=actor_id,
            predicted_timestamp=window_start + timedelta(days=2),
            confidence=coord_score,
            timing_window=(window_start, window_end),
            target_entities=partners,
            reasoning=f"High coordination likelihood ({coord_score:.2f}) with identified network",
            evidence=["echo_network_data", "behavioral_signature"]
        )
    
    def _predict_attack(
        self,
        actor_id: str,
        signature: Dict[str, Any],
        historical_patterns: Optional[List[Dict[str, Any]]]
    ) -> Optional[PredictedAction]:
        """Predict attack execution"""
        if not historical_patterns:
            return None
        
        # Match against historical attack patterns
        pattern_match = self._match_attack_pattern(signature, historical_patterns)
        
        if not pattern_match or pattern_match['confidence'] < 0.6:
            return None
        
        # Predict attack window based on historical timing
        timing = pattern_match.get('predicted_timing', {})
        now = datetime.now()
        window_start = now + timedelta(days=timing.get('days_min', 7))
        window_end = now + timedelta(days=timing.get('days_max', 14))
        
        return PredictedAction(
            action_type=ThreatActionType.ATTACK_EXECUTION,
            actor_id=actor_id,
            predicted_timestamp=window_start + timedelta(days=3),
            confidence=pattern_match['confidence'],
            timing_window=(window_start, window_end),
            target_entities=pattern_match.get('targets', []),
            reasoning=f"Pattern match to historical attack ({pattern_match['pattern_id']})",
            evidence=["historical_patterns", "behavioral_signature", "pattern_matching"]
        )
    
    def _predict_asset_movement(
        self,
        actor_id: str,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]]
    ) -> Optional[PredictedAction]:
        """Predict asset movement"""
        # Analyze recent activity patterns
        recent_activity = self._analyze_recent_activity(transactions)
        
        if recent_activity.get('movement_likelihood', 0.0) < 0.5:
            return None
        
        # Predict movement window
        now = datetime.now()
        window_start = now + timedelta(hours=24)
        window_end = now + timedelta(hours=48)
        
        return PredictedAction(
            action_type=ThreatActionType.ASSET_MOVEMENT,
            actor_id=actor_id,
            predicted_timestamp=window_start + timedelta(hours=12),
            confidence=recent_activity['movement_likelihood'],
            timing_window=(window_start, window_end),
            amount_range=recent_activity.get('amount_range'),
            reasoning="Recent activity pattern suggests imminent asset movement",
            evidence=["transaction_history", "activity_analysis"]
        )
    
    def _calculate_risk_score(
        self,
        predictions: List[PredictedAction],
        signature: Dict[str, Any]
    ) -> float:
        """Calculate overall risk score"""
        if not predictions:
            return 0.3  # Baseline risk
        
        # Weight predictions by confidence and severity
        weighted_scores = []
        for pred in predictions:
            severity = self._get_action_severity(pred.action_type)
            weighted_scores.append(pred.confidence * severity)
        
        # Average weighted scores
        risk_score = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0
        
        # Boost if multiple high-confidence predictions
        if len([p for p in predictions if p.confidence > 0.7]) >= 2:
            risk_score = min(risk_score * 1.2, 1.0)
        
        return risk_score
    
    def _determine_next_window(
        self,
        predictions: List[PredictedAction]
    ) -> Optional[Tuple[datetime, datetime]]:
        """Determine the next action window"""
        if not predictions:
            return None
        
        # Find the earliest prediction
        earliest = min(predictions, key=lambda p: p.timing_window[0])
        return earliest.timing_window
    
    def _generate_countermeasures(
        self,
        predictions: List[PredictedAction],
        risk_score: float
    ) -> List[str]:
        """Generate recommended countermeasures"""
        countermeasures = []
        
        if risk_score > 0.8:
            countermeasures.append("Immediate freeze on all associated addresses")
            countermeasures.append("Alert all exchanges and OTC desks")
        
        for pred in predictions:
            if pred.action_type == ThreatActionType.OFF_RAMP_ATTEMPT:
                countermeasures.append(f"Pre-emptive freeze at {pred.location}")
            elif pred.action_type == ThreatActionType.COORDINATION_ACTIVITY:
                countermeasures.append("Monitor coordination network")
                countermeasures.append("Flag all identified partners")
        
        if not countermeasures:
            countermeasures.append("Continue monitoring")
        
        return countermeasures
    
    # Helper methods (stubs for implementation)
    def _analyze_off_ramp_timing(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timing patterns for off-ramps"""
        return {"preferred_window": "UTC 02:00-04:00"}  # Placeholder
    
    def _predict_off_ramp_location(self, signature: Dict[str, Any], transactions: List[Dict[str, Any]]) -> str:
        """Predict off-ramp location"""
        return "Dubai_OTC_desk_3"  # Placeholder
    
    def _predict_off_ramp_amount(self, transactions: List[Dict[str, Any]]) -> Tuple[float, float]:
        """Predict off-ramp amount range"""
        return (1800000.0, 2500000.0)  # Placeholder
    
    def _match_attack_pattern(self, signature: Dict[str, Any], patterns: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Match signature against historical attack patterns"""
        # Implementation: Pattern matching algorithm
        return None  # Placeholder
    
    def _analyze_recent_activity(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze recent transaction activity"""
        return {"movement_likelihood": 0.6}  # Placeholder
    
    def _get_action_severity(self, action_type: ThreatActionType) -> float:
        """Get severity weight for action type"""
        severity_map = {
            ThreatActionType.ATTACK_EXECUTION: 1.0,
            ThreatActionType.OFF_RAMP_ATTEMPT: 0.9,
            ThreatActionType.COORDINATION_ACTIVITY: 0.7,
            ThreatActionType.ASSET_MOVEMENT: 0.6,
            ThreatActionType.NETWORK_EXPANSION: 0.5,
            ThreatActionType.EVASION_MANEUVER: 0.8
        }
        return severity_map.get(action_type, 0.5)

