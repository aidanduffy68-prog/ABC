"""
Hypnos — Pattern Consolidation Engine
Consolidates behavioral patterns over extended time periods
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class PatternType(Enum):
    """Types of patterns that can be consolidated"""
    BEHAVIORAL_SIGNATURE = "behavioral_signature"
    COORDINATION_PATTERN = "coordination_pattern"
    TTP = "ttp"
    EVASION_PATTERN = "evasion_pattern"
    OPERATIONAL_WINDOW = "operational_window"


@dataclass
class ConsolidatedPattern:
    """A pattern consolidated from multiple time periods"""
    pattern_id: str
    pattern_type: PatternType
    consolidated_at: datetime
    
    # Pattern characteristics
    description: str
    confidence: float
    frequency: int  # How many times this pattern has been observed
    first_seen: datetime
    last_seen: datetime
    time_span_days: int
    
    # Pattern evolution
    evolution_timeline: List[Dict[str, Any]] = field(default_factory=list)
    pattern_stability: float = 0.0  # How stable the pattern is over time
    
    # Related entities
    associated_actors: List[str] = field(default_factory=list)
    associated_networks: List[str] = field(default_factory=list)
    
    # Evidence
    supporting_evidence: List[str] = field(default_factory=list)
    validation_count: int = 0


@dataclass
class DormantThreat:
    """A threat actor that has gone dormant"""
    actor_id: str
    actor_name: str
    last_active: datetime
    dormancy_period_days: int
    
    # Historical activity
    historical_activity: Dict[str, Any] = field(default_factory=dict)
    behavioral_signature: Dict[str, Any] = field(default_factory=dict)
    coordination_network: Dict[str, Any] = field(default_factory=dict)
    
    # Re-emergence indicators
    re_emergence_probability: float = 0.0
    re_emergence_indicators: List[str] = field(default_factory=list)
    
    # Monitoring
    monitoring_status: str = "ACTIVE"
    last_checked: datetime = field(default_factory=datetime.now)


class HypnosPatternConsolidator:
    """
    Consolidates patterns from multiple time periods into long-term knowledge
    """
    
    def __init__(self):
        self.consolidated_patterns: Dict[str, ConsolidatedPattern] = {}
        self.dormant_threats: Dict[str, DormantThreat] = {}
        
    def consolidate_pattern(
        self,
        pattern_data: Dict[str, Any],
        time_period: datetime,
        pattern_type: PatternType
    ) -> ConsolidatedPattern:
        """
        Consolidate a pattern from a specific time period
        
        Args:
            pattern_data: Pattern data from current time period
            time_period: When this pattern was observed
            pattern_type: Type of pattern
            
        Returns:
            Consolidated pattern
        """
        pattern_id = pattern_data.get('pattern_id', f"{pattern_type.value}_{time_period.isoformat()}")
        
        # Check if pattern already exists
        if pattern_id in self.consolidated_patterns:
            existing = self.consolidated_patterns[pattern_id]
            # Update existing pattern
            existing.frequency += 1
            existing.last_seen = time_period
            existing.time_span_days = (existing.last_seen - existing.first_seen).days
            
            # Add to evolution timeline
            existing.evolution_timeline.append({
                "timestamp": time_period,
                "pattern_data": pattern_data,
                "confidence": pattern_data.get('confidence', 0.0)
            })
            
            # Update pattern stability
            existing.pattern_stability = self._calculate_stability(existing)
            
            return existing
        else:
            # Create new consolidated pattern
            consolidated = ConsolidatedPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                consolidated_at=datetime.now(),
                description=pattern_data.get('description', ''),
                confidence=pattern_data.get('confidence', 0.0),
                frequency=1,
                first_seen=time_period,
                last_seen=time_period,
                time_span_days=0,
                evolution_timeline=[{
                    "timestamp": time_period,
                    "pattern_data": pattern_data,
                    "confidence": pattern_data.get('confidence', 0.0)
                }],
                pattern_stability=1.0,  # New patterns are fully stable
                associated_actors=pattern_data.get('actors', []),
                associated_networks=pattern_data.get('networks', []),
                supporting_evidence=pattern_data.get('evidence', [])
            )
            
            self.consolidated_patterns[pattern_id] = consolidated
            return consolidated
    
    def detect_dormant_threat(
        self,
        actor_id: str,
        actor_name: str,
        last_activity: datetime,
        historical_data: Dict[str, Any]
    ) -> DormantThreat:
        """
        Detect and track a dormant threat
        
        Args:
            actor_id: Actor identifier
            actor_name: Actor name
            last_activity: When actor was last active
            historical_data: Historical activity data
            
        Returns:
            Dormant threat record
        """
        dormancy_period = (datetime.now() - last_activity).days
        
        dormant = DormantThreat(
            actor_id=actor_id,
            actor_name=actor_name,
            last_active=last_activity,
            dormancy_period_days=dormancy_period,
            historical_activity=historical_data.get('activity', {}),
            behavioral_signature=historical_data.get('behavioral_signature', {}),
            coordination_network=historical_data.get('coordination_network', {}),
            re_emergence_probability=self._calculate_re_emergence_probability(
                historical_data, dormancy_period
            ),
            re_emergence_indicators=self._identify_re_emergence_indicators(historical_data)
        )
        
        self.dormant_threats[actor_id] = dormant
        return dormant
    
    def match_historical_pattern(
        self,
        current_pattern: Dict[str, Any],
        lookback_days: int = 365
    ) -> List[ConsolidatedPattern]:
        """
        Match current pattern to historical patterns
        
        Args:
            current_pattern: Current pattern to match
            lookback_days: How far back to look
            
        Returns:
            List of matching historical patterns
        """
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        matches = []
        for pattern in self.consolidated_patterns.values():
            if pattern.last_seen < cutoff_date:
                continue
            
            similarity = self._calculate_pattern_similarity(current_pattern, pattern)
            if similarity > 0.7:  # 70% similarity threshold
                matches.append(pattern)
        
        # Sort by similarity (would need similarity scores)
        return sorted(matches, key=lambda p: p.confidence, reverse=True)
    
    def get_temporal_intelligence(
        self,
        actor_id: str,
        time_period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Get temporal intelligence for an actor across time periods
        
        Args:
            actor_id: Actor identifier
            time_period_days: Time period to analyze
            
        Returns:
            Temporal intelligence summary
        """
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        
        # Find patterns associated with this actor
        actor_patterns = [
            p for p in self.consolidated_patterns.values()
            if actor_id in p.associated_actors and p.last_seen >= cutoff_date
        ]
        
        # Analyze pattern evolution
        pattern_evolution = self._analyze_pattern_evolution(actor_patterns)
        
        return {
            "actor_id": actor_id,
            "time_period_days": time_period_days,
            "patterns_found": len(actor_patterns),
            "pattern_evolution": pattern_evolution,
            "pattern_stability": sum(p.pattern_stability for p in actor_patterns) / len(actor_patterns) if actor_patterns else 0.0,
            "temporal_trends": self._identify_temporal_trends(actor_patterns)
        }
    
    def _calculate_stability(self, pattern: ConsolidatedPattern) -> float:
        """Calculate pattern stability over time"""
        if len(pattern.evolution_timeline) < 2:
            return 1.0
        
        # Calculate variance in confidence scores
        confidences = [e['confidence'] for e in pattern.evolution_timeline]
        mean_confidence = sum(confidences) / len(confidences)
        variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(confidences)
        
        # Stability is inverse of variance (normalized)
        stability = 1.0 / (1.0 + variance)
        return stability
    
    def _calculate_re_emergence_probability(
        self,
        historical_data: Dict[str, Any],
        dormancy_period: int
    ) -> float:
        """Calculate probability of threat re-emergence"""
        # Base probability decreases with dormancy period
        base_prob = max(0.0, 1.0 - (dormancy_period / 365.0))
        
        # Adjust based on historical activity patterns
        activity_level = historical_data.get('activity', {}).get('level', 0.5)
        pattern_stability = historical_data.get('pattern_stability', 0.5)
        
        # Higher activity and stability = higher re-emergence probability
        adjusted_prob = base_prob * (0.5 + activity_level * 0.3 + pattern_stability * 0.2)
        
        return min(1.0, adjusted_prob)
    
    def _identify_re_emergence_indicators(
        self,
        historical_data: Dict[str, Any]
    ) -> List[str]:
        """Identify indicators that suggest threat may re-emerge"""
        indicators = []
        
        # Check for historical patterns that suggest re-emergence
        if historical_data.get('behavioral_signature', {}).get('pattern_repetition', 0.0) > 0.7:
            indicators.append("high_pattern_repetition")
        
        if historical_data.get('coordination_network', {}).get('network_size', 0) > 5:
            indicators.append("large_coordination_network")
        
        if historical_data.get('activity', {}).get('frequency', 0) > 10:
            indicators.append("high_historical_activity")
        
        return indicators
    
    def _calculate_pattern_similarity(
        self,
        current: Dict[str, Any],
        historical: ConsolidatedPattern
    ) -> float:
        """Calculate similarity between current and historical pattern"""
        # Simplified similarity calculation
        # In practice, this would use more sophisticated matching
        current_desc = current.get('description', '').lower()
        historical_desc = historical.description.lower()
        
        # Simple word overlap
        current_words = set(current_desc.split())
        historical_words = set(historical_desc.split())
        
        if not current_words or not historical_words:
            return 0.0
        
        overlap = len(current_words & historical_words)
        total = len(current_words | historical_words)
        
        return overlap / total if total > 0 else 0.0
    
    def _analyze_pattern_evolution(
        self,
        patterns: List[ConsolidatedPattern]
    ) -> Dict[str, Any]:
        """Analyze how patterns have evolved over time"""
        if not patterns:
            return {}
        
        # Analyze confidence trends
        confidences = [p.confidence for p in patterns]
        confidence_trend = "stable"
        if len(confidences) > 1:
            if confidences[-1] > confidences[0]:
                confidence_trend = "increasing"
            elif confidences[-1] < confidences[0]:
                confidence_trend = "decreasing"
        
        # Analyze frequency trends
        frequencies = [p.frequency for p in patterns]
        frequency_trend = "stable"
        if len(frequencies) > 1:
            if frequencies[-1] > frequencies[0]:
                frequency_trend = "increasing"
            elif frequencies[-1] < frequencies[0]:
                frequency_trend = "decreasing"
        
        return {
            "confidence_trend": confidence_trend,
            "frequency_trend": frequency_trend,
            "average_stability": sum(p.pattern_stability for p in patterns) / len(patterns),
            "pattern_count": len(patterns)
        }
    
    def _identify_temporal_trends(
        self,
        patterns: List[ConsolidatedPattern]
    ) -> List[str]:
        """Identify temporal trends in patterns"""
        trends = []
        
        if not patterns:
            return trends
        
        # Check for increasing frequency
        if len(patterns) > 1:
            recent_freq = sum(1 for p in patterns if (datetime.now() - p.last_seen).days < 30)
            older_freq = sum(1 for p in patterns if (datetime.now() - p.last_seen).days >= 30)
            
            if recent_freq > older_freq:
                trends.append("increasing_pattern_frequency")
        
        # Check for pattern stability
        avg_stability = sum(p.pattern_stability for p in patterns) / len(patterns)
        if avg_stability > 0.8:
            trends.append("high_pattern_stability")
        
        return trends

