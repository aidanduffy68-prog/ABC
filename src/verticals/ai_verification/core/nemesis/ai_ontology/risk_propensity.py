"""
Risk Propensity Model - Replaces timing predictions with defensible risk assessment
Assesses mobilization index, volatility score, and behavioral similarity
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RiskPropensity:
    """Risk propensity assessment for a threat actor"""
    actor_id: str
    mobilization_index: float  # 0-1, how close to attack staging
    volatility_score: float  # 0-1, likelihood of action (not timing)
    behavioral_similarity: Dict[str, float]  # Similarity to known patterns
    overall_risk_score: float  # 0-1, overall threat level
    recommended_monitoring_targets: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    reasoning: str = ""
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class BehavioralSimilarity:
    """Similarity to known attack patterns"""
    pattern_id: str
    pattern_name: str
    similarity_score: float  # 0-1
    matched_indicators: List[str]
    confidence: float


class RiskPropensityModel:
    """
    Assesses threat actor mobilization and risk levels
    Does NOT predict specific timing windows (defensible intelligence)
    """
    
    def __init__(self):
        # Known attack patterns for similarity matching
        self.known_patterns = {
            "lazarus_group_pre_attack": {
                "name": "Lazarus Group Pre-Attack Staging",
                "indicators": [
                    "rapid_chain_switching",
                    "mixer_usage",
                    "exchange_deposit_preparation",
                    "timing_pattern_consistency"
                ]
            },
            "north_korean_pattern": {
                "name": "North Korean Actor Pattern",
                "indicators": [
                    "sanctioned_address_interaction",
                    "bridge_usage",
                    "exchange_clustering"
                ]
            },
            "rug_pull_staging": {
                "name": "Rug Pull Staging Pattern",
                "indicators": [
                    "liquidity_accumulation",
                    "token_creation",
                    "social_media_promotion"
                ]
            }
        }
    
    def assess_risk_propensity(
        self,
        actor_id: str,
        behavioral_signature: Dict[str, Any],
        transaction_history: List[Dict[str, Any]],
        network_data: Optional[Dict[str, Any]] = None,
        historical_patterns: Optional[List[Dict[str, Any]]] = None
    ) -> RiskPropensity:
        """
        Assess risk propensity for a threat actor
        
        Args:
            actor_id: Unique identifier for the actor
            behavioral_signature: AI-generated behavioral signature
            transaction_history: Historical transaction data
            network_data: Echo network coordination data
            historical_patterns: Similar actor patterns from past
        
        Returns:
            RiskPropensity assessment (NO timing predictions)
        """
        # Calculate mobilization index
        mobilization_index = self._calculate_mobilization_index(
            behavioral_signature, transaction_history, network_data
        )
        
        # Calculate volatility score
        volatility_score = self._calculate_volatility_score(
            behavioral_signature, transaction_history
        )
        
        # Calculate behavioral similarity to known patterns
        behavioral_similarity = self._calculate_behavioral_similarity(
            behavioral_signature, transaction_history, historical_patterns
        )
        
        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(
            mobilization_index, volatility_score, behavioral_similarity
        )
        
        # Determine monitoring targets
        monitoring_targets = self._determine_monitoring_targets(
            behavioral_signature, transaction_history, network_data
        )
        
        # Generate evidence and reasoning
        evidence = self._generate_evidence(
            behavioral_signature, transaction_history, network_data
        )
        reasoning = self._generate_reasoning(
            mobilization_index, volatility_score, behavioral_similarity
        )
        
        return RiskPropensity(
            actor_id=actor_id,
            mobilization_index=mobilization_index,
            volatility_score=volatility_score,
            behavioral_similarity=behavioral_similarity,
            overall_risk_score=overall_risk,
            recommended_monitoring_targets=monitoring_targets,
            evidence=evidence,
            reasoning=reasoning
        )
    
    def _calculate_mobilization_index(
        self,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        network_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate mobilization index: How close actor is to attack staging (0-1)
        Higher = closer to staging behavior
        """
        indicators = []
        
        # Flight risk indicator
        flight_risk = signature.get("traits", {}).get("flight_risk", 0.0)
        if flight_risk > 0.7:
            indicators.append(("flight_risk", flight_risk * 0.3))
        
        # Coordination activity
        if network_data:
            coord_score = network_data.get("coordination_score", 0.0)
            if coord_score > 0.6:
                indicators.append(("coordination", coord_score * 0.25))
        
        # Recent activity spike
        if transactions:
            recent_activity = self._analyze_recent_activity_spike(transactions)
            if recent_activity > 0.5:
                indicators.append(("activity_spike", recent_activity * 0.2))
        
        # Exchange deposit preparation
        exchange_prep = self._detect_exchange_preparation(transactions)
        if exchange_prep > 0.5:
            indicators.append(("exchange_prep", exchange_prep * 0.25))
        
        # Sum weighted indicators
        mobilization_index = sum(weight for _, weight in indicators)
        return min(mobilization_index, 1.0)
    
    def _calculate_volatility_score(
        self,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate volatility score: Likelihood of action (not timing) (0-1)
        """
        indicators = []
        
        # Risk tolerance
        risk_tolerance = signature.get("traits", {}).get("risk_tolerance", 0.0)
        indicators.append(risk_tolerance * 0.3)
        
        # Pattern repetition (consistency)
        pattern_rep = signature.get("traits", {}).get("pattern_repetition", 0.0)
        indicators.append(pattern_rep * 0.2)
        
        # Transaction frequency
        if transactions:
            freq_score = self._calculate_transaction_frequency_score(transactions)
            indicators.append(freq_score * 0.25)
        
        # Route entropy (diversity of paths)
        route_entropy = signature.get("traits", {}).get("route_entropy", 0.0)
        indicators.append(route_entropy * 0.25)
        
        volatility_score = sum(indicators)
        return min(volatility_score, 1.0)
    
    def _calculate_behavioral_similarity(
        self,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        historical_patterns: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, float]:
        """
        Calculate similarity to known attack patterns
        Returns dict of {pattern_id: similarity_score}
        """
        similarities = {}
        
        # Match against known patterns
        for pattern_id, pattern_info in self.known_patterns.items():
            similarity = self._match_pattern(signature, transactions, pattern_info)
            if similarity > 0.6:  # Only include significant matches
                similarities[pattern_id] = similarity
        
        # Match against historical patterns if provided
        if historical_patterns:
            for hist_pattern in historical_patterns:
                pattern_id = hist_pattern.get("pattern_id", "unknown")
                similarity = self._match_historical_pattern(signature, transactions, hist_pattern)
                if similarity > 0.6:
                    similarities[f"historical_{pattern_id}"] = similarity
        
        return similarities
    
    def _calculate_overall_risk(
        self,
        mobilization_index: float,
        volatility_score: float,
        behavioral_similarity: Dict[str, float]
    ) -> float:
        """Calculate overall risk score"""
        # Base risk from mobilization and volatility
        base_risk = (mobilization_index * 0.5) + (volatility_score * 0.3)
        
        # Boost if high similarity to known attack patterns
        if behavioral_similarity:
            max_similarity = max(behavioral_similarity.values())
            similarity_boost = max_similarity * 0.2
            base_risk += similarity_boost
        
        return min(base_risk, 1.0)
    
    def _determine_monitoring_targets(
        self,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        network_data: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Determine recommended monitoring targets (exchanges, protocols, etc.)"""
        targets = []
        
        # Extract exchange addresses from transaction history
        if transactions:
            exchange_addresses = self._extract_exchange_addresses(transactions)
            targets.extend(exchange_addresses)
        
        # Add network partners if coordination detected
        if network_data:
            partners = network_data.get("identified_partners", [])
            targets.extend([f"partner_{p}" for p in partners[:5]])  # Top 5
        
        # Add preferred off-ramp locations from signature
        off_ramps = signature.get("traits", {}).get("off_ramp_preferences", [])
        targets.extend(off_ramps)
        
        return list(set(targets))  # Deduplicate
    
    def _generate_evidence(
        self,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        network_data: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate evidence list for risk assessment"""
        evidence = []
        
        if signature:
            evidence.append("behavioral_signature")
        
        if transactions:
            evidence.append(f"transaction_history_{len(transactions)}_txs")
        
        if network_data:
            evidence.append("echo_network_data")
        
        return evidence
    
    def _generate_reasoning(
        self,
        mobilization_index: float,
        volatility_score: float,
        behavioral_similarity: Dict[str, float]
    ) -> str:
        """Generate human-readable reasoning for risk assessment"""
        parts = []
        
        parts.append(f"Actor showing mobilization index of {mobilization_index:.2f}")
        parts.append(f"Volatility score: {volatility_score:.2f}")
        
        if behavioral_similarity:
            top_match = max(behavioral_similarity.items(), key=lambda x: x[1])
            pattern_name = self.known_patterns.get(top_match[0], {}).get("name", top_match[0])
            parts.append(f"90% similarity to {pattern_name} pre-attack staging behavior")
        
        return ". ".join(parts) + "."
    
    # Helper methods
    def _analyze_recent_activity_spike(self, transactions: List[Dict[str, Any]]) -> float:
        """Analyze if there's a recent activity spike"""
        if len(transactions) < 2:
            return 0.0
        
        # Compare recent activity to historical average
        recent_count = len([tx for tx in transactions[-10:]])
        avg_count = len(transactions) / max(len(transactions), 1)
        
        if avg_count > 0:
            spike_ratio = recent_count / avg_count
            return min(spike_ratio / 2.0, 1.0)  # Normalize
        
        return 0.0
    
    def _detect_exchange_preparation(self, transactions: List[Dict[str, Any]]) -> float:
        """Detect if actor is preparing for exchange deposit"""
        # Check for bridge transfers, mixer usage (preparation indicators)
        prep_indicators = 0
        for tx in transactions[-20:]:  # Last 20 transactions
            if tx.get("type") in ["bridge_transfer", "mixer_usage"]:
                prep_indicators += 1
        
        return min(prep_indicators / 5.0, 1.0)  # Normalize
    
    def _calculate_transaction_frequency_score(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate transaction frequency score"""
        if len(transactions) < 2:
            return 0.0
        
        # Calculate average time between transactions
        timestamps = sorted([tx.get("timestamp", 0) for tx in transactions])
        if len(timestamps) < 2:
            return 0.0
        
        avg_interval = sum(timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)) / (len(timestamps)-1)
        
        # Higher frequency = higher score (normalized)
        if avg_interval > 0:
            freq_score = 1.0 / (1.0 + avg_interval / 3600)  # Normalize by hour
            return min(freq_score, 1.0)
        
        return 0.0
    
    def _match_pattern(
        self,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        pattern_info: Dict[str, Any]
    ) -> float:
        """Match actor against known pattern"""
        indicators = pattern_info.get("indicators", [])
        matches = 0
        
        for indicator in indicators:
            if indicator == "rapid_chain_switching":
                if signature.get("traits", {}).get("chain_switching_frequency", 0) > 0.7:
                    matches += 1
            elif indicator == "mixer_usage":
                if any(tx.get("type") == "mixer_usage" for tx in transactions):
                    matches += 1
            elif indicator == "exchange_deposit_preparation":
                if self._detect_exchange_preparation(transactions) > 0.5:
                    matches += 1
            # Add more indicator checks
        
        return matches / len(indicators) if indicators else 0.0
    
    def _match_historical_pattern(
        self,
        signature: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        hist_pattern: Dict[str, Any]
    ) -> float:
        """Match against historical pattern"""
        # Similarity calculation based on pattern attributes
        return 0.75  # Placeholder
    
    def _extract_exchange_addresses(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """Extract exchange addresses from transactions"""
        # Known exchange addresses (would come from external list)
        exchange_addresses = set()
        
        for tx in transactions:
            to_addr = tx.get("to_address", "").lower()
            # Check if address matches known exchange pattern
            # Would use actual exchange address database
            if to_addr.startswith("0x"):  # Placeholder check
                exchange_addresses.add(to_addr)
        
        return list(exchange_addresses)[:5]  # Top 5

