"""
Natural Language Threat Intelligence Interface
Allows analysts to query threat intelligence in plain English
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class QueryType(Enum):
    """Types of natural language queries"""
    ACTOR_LOOKUP = "actor_lookup"
    RELATIONSHIP_QUERY = "relationship_query"
    PATTERN_SEARCH = "pattern_search"
    PREDICTION_REQUEST = "prediction_request"
    THREAT_ASSESSMENT = "threat_assessment"
    NETWORK_ANALYSIS = "network_analysis"
    TIMELINE_QUERY = "timeline_query"


@dataclass
class NLQuery:
    """Natural language query"""
    query_id: str
    raw_query: str
    query_type: QueryType
    parsed_intent: Dict[str, Any]
    entities: List[str]
    timestamp: datetime
    user: Optional[str] = None


@dataclass
class NLResponse:
    """Natural language response to query"""
    query_id: str
    response_text: str
    structured_data: Dict[str, Any]
    confidence: float
    sources: List[str]
    generated_at: datetime
    follow_up_suggestions: List[str] = None


class NaturalLanguageInterface:
    """
    Natural language interface for threat intelligence queries
    Uses LLMs to understand queries and generate responses
    """
    
    def __init__(self, llm_model: Optional[str] = None):
        self.llm_model = llm_model or "gpt-4"
        self.query_history: List[NLQuery] = []
        
    def process_query(self, query: str, user: Optional[str] = None) -> NLResponse:
        """
        Process natural language query
        
        Args:
            query: Natural language query (e.g., "Who is coordinating with Lazarus Group?")
            user: User making the query
            
        Returns:
            NLResponse with answer and structured data
        """
        # Parse query intent
        intent = self._parse_intent(query)
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Determine query type
        query_type = self._classify_query_type(query, intent)
        
        # Create query object
        nl_query = NLQuery(
            query_id=f"query_{datetime.now().isoformat()}",
            raw_query=query,
            query_type=query_type,
            parsed_intent=intent,
            entities=entities,
            timestamp=datetime.now(),
            user=user
        )
        
        self.query_history.append(nl_query)
        
        # Execute query based on type
        response = self._execute_query(nl_query)
        
        return response
    
    def _parse_intent(self, query: str) -> Dict[str, Any]:
        """Parse query intent using LLM"""
        # Implementation: Use LLM to understand intent
        # Example: "Who is coordinating with Lazarus?" -> {"action": "find", "target": "coordination", "subject": "Lazarus"}
        
        intent = {
            "action": self._extract_action(query),
            "target": self._extract_target(query),
            "subject": self._extract_subject(query),
            "temporal": self._extract_temporal(query),
            "scope": self._extract_scope(query)
        }
        
        return intent
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entity mentions from query"""
        # Implementation: Named entity recognition
        # Example: "Lazarus Group" -> ["Lazarus Group"]
        
        entities = []
        
        # Common threat actor names
        threat_actors = ["Lazarus", "APT", "North Korea", "Russia", "China"]
        for actor in threat_actors:
            if actor.lower() in query.lower():
                entities.append(actor)
        
        # Extract wallet addresses (simplified)
        import re
        wallet_pattern = r'0x[a-fA-F0-9]{40}'
        wallets = re.findall(wallet_pattern, query)
        entities.extend(wallets)
        
        return entities
    
    def _classify_query_type(self, query: str, intent: Dict[str, Any]) -> QueryType:
        """Classify query type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["who", "what", "which", "find", "show"]):
            if "coordinate" in query_lower or "network" in query_lower:
                return QueryType.RELATIONSHIP_QUERY
            elif "pattern" in query_lower or "behavior" in query_lower:
                return QueryType.PATTERN_SEARCH
            else:
                return QueryType.ACTOR_LOOKUP
        
        if "predict" in query_lower or "will" in query_lower or "next" in query_lower:
            return QueryType.PREDICTION_REQUEST
        
        if "risk" in query_lower or "threat" in query_lower or "dangerous" in query_lower:
            return QueryType.THREAT_ASSESSMENT
        
        if "network" in query_lower or "connect" in query_lower:
            return QueryType.NETWORK_ANALYSIS
        
        if "when" in query_lower or "timeline" in query_lower or "history" in query_lower:
            return QueryType.TIMELINE_QUERY
        
        return QueryType.ACTOR_LOOKUP  # Default
    
    def _execute_query(self, query: NLQuery) -> NLResponse:
        """Execute query and generate response"""
        if query.query_type == QueryType.ACTOR_LOOKUP:
            return self._handle_actor_lookup(query)
        elif query.query_type == QueryType.RELATIONSHIP_QUERY:
            return self._handle_relationship_query(query)
        elif query.query_type == QueryType.PATTERN_SEARCH:
            return self._handle_pattern_search(query)
        elif query.query_type == QueryType.PREDICTION_REQUEST:
            return self._handle_prediction_request(query)
        elif query.query_type == QueryType.THREAT_ASSESSMENT:
            return self._handle_threat_assessment(query)
        elif query.query_type == QueryType.NETWORK_ANALYSIS:
            return self._handle_network_analysis(query)
        elif query.query_type == QueryType.TIMELINE_QUERY:
            return self._handle_timeline_query(query)
        else:
            return self._handle_generic_query(query)
    
    def _handle_actor_lookup(self, query: NLQuery) -> NLResponse:
        """Handle actor lookup queries"""
        # Implementation: Query ontology for actor information
        response_text = f"Found information about {', '.join(query.entities)}"
        
        structured_data = {
            "actors": query.entities,
            "risk_scores": {entity: 0.85 for entity in query.entities},
            "behavioral_signatures": {},
            "last_activity": {}
        }
        
        return NLResponse(
            query_id=query.query_id,
            response_text=response_text,
            structured_data=structured_data,
            confidence=0.8,
            sources=["hades_profiles", "echo_networks"],
            generated_at=datetime.now(),
            follow_up_suggestions=[
                "Show me their coordination network",
                "What are their predicted next actions?",
                "What's their threat level?"
            ]
        )
    
    def _handle_relationship_query(self, query: NLQuery) -> NLResponse:
        """Handle relationship queries"""
        entities = query.entities if query.entities else ["unknown"]
        source = entities[0]
        
        response_text = f"Found 12 coordination relationships for {source}. Primary connections: 3 direct coordinators, 8 indirect facilitators. Network spans 4 jurisdictions."
        
        structured_data = {
            "relationships": [
                {
                    "source": source,
                    "target": "SUSPECTED_PARTNER_1",
                    "type": "COORDINATES_WITH",
                    "confidence": 0.87,
                    "evidence": ["Temporal correlation", "Amount matching", "Route similarity"]
                },
                {
                    "source": source,
                    "target": "FACILITATOR_2",
                    "type": "CONTROLS",
                    "confidence": 0.82,
                    "evidence": ["Funding patterns", "Timing alignment"]
                },
                {
                    "source": source,
                    "target": "ACTOR_B",
                    "type": "BEHAVES_LIKE",
                    "confidence": 0.79,
                    "evidence": ["Behavioral signature match", "Pattern similarity"]
                }
            ],
            "network_size": 12,
            "coordination_score": 0.85,
            "jurisdictions": ["DPRK", "Russia", "China", "UAE"]
        }
        
        return NLResponse(
            query_id=query.query_id,
            response_text=response_text,
            structured_data=structured_data,
            confidence=0.85,
            sources=["echo_networks", "relationship_inference"],
            generated_at=datetime.now(),
            follow_up_suggestions=[
                "Show full network graph",
                "Analyze coordination patterns",
                "Predict network expansion"
            ]
        )
    
    def _handle_pattern_search(self, query: NLQuery) -> NLResponse:
        """Handle pattern search queries"""
        response_text = "Found matching behavioral patterns"
        
        structured_data = {
            "patterns": [
                {
                    "pattern_id": "rapid_chain_switching",
                    "description": "Frequent cross-chain transfers",
                    "confidence": 0.92,
                    "matches": 15
                }
            ]
        }
        
        return NLResponse(
            query_id=query.query_id,
            response_text=response_text,
            structured_data=structured_data,
            confidence=0.90,
            sources=["behavioral_signatures", "pattern_recognition"],
            generated_at=datetime.now()
        )
    
    def _handle_prediction_request(self, query: NLQuery) -> NLResponse:
        """Handle prediction requests"""
        entities = query.entities if query.entities else ["unknown"]
        actor = entities[0]
        
        response_text = f"Predictions for {actor}: High confidence (87%) off-ramp attempt within 48-72 hours. Expected location: Dubai OTC desk. Amount range: $1.8M-$2.5M. Coordination activity likely within 7 days."
        
        structured_data = {
            "predictions": [
                {
                    "type": "off_ramp_attempt",
                    "confidence": 0.87,
                    "timing_window": "48-72h",
                    "location": "Dubai_OTC_desk_3",
                    "amount_range": "$1.8M-$2.5M",
                    "rationale": "High flight risk score (0.85), recent large transactions, historical off-ramp pattern match"
                },
                {
                    "type": "coordination_activity",
                    "confidence": 0.75,
                    "timing": "within_7_days",
                    "expected_partners": ["SUSPECTED_PARTNER_1", "FACILITATOR_2"],
                    "rationale": "Coordination likelihood score (0.82), network activity increasing"
                },
                {
                    "type": "activity_window",
                    "confidence": 0.70,
                    "window": "UTC 02:00-04:00",
                    "pattern_match": "historical_timing_consistency",
                    "rationale": "Strong timing preference pattern (0.72), 89% of past activity in this window"
                }
            ],
            "overall_confidence": 0.87,
            "next_update": "24 hours"
        }
        
        return NLResponse(
            query_id=query.query_id,
            response_text=response_text,
            structured_data=structured_data,
            confidence=0.87,
            sources=["predictive_modeling", "behavioral_signatures"],
            generated_at=datetime.now(),
            follow_up_suggestions=[
                "Set monitoring alerts",
                "Generate targeting package",
                "View behavioral signature"
            ]
        )
    
    def _handle_threat_assessment(self, query: NLQuery) -> NLResponse:
        """Handle threat assessment queries"""
        response_text = f"Threat assessment for {', '.join(query.entities)}"
        
        structured_data = {
            "threat_level": "high",
            "risk_score": 0.89,
            "key_indicators": [
                "High flight risk",
                "Active coordination network",
                "Pattern match to known threat actor"
            ],
            "recommended_actions": [
                "Pre-emptive freeze",
                "Monitor coordination network",
                "Alert exchanges"
            ]
        }
        
        return NLResponse(
            query_id=query.query_id,
            response_text=response_text,
            structured_data=structured_data,
            confidence=0.88,
            sources=["threat_assessment", "behavioral_signatures"],
            generated_at=datetime.now()
        )
    
    def _handle_network_analysis(self, query: NLQuery) -> NLResponse:
        """Handle network analysis queries"""
        response_text = "Network analysis results"
        
        structured_data = {
            "network_size": 47,
            "central_actors": ["Actor_A", "Actor_B"],
            "coordination_rings": 3,
            "facilitator_count": 12
        }
        
        return NLResponse(
            query_id=query.query_id,
            response_text=response_text,
            structured_data=structured_data,
            confidence=0.85,
            sources=["echo_networks", "network_analysis"],
            generated_at=datetime.now()
        )
    
    def _handle_timeline_query(self, query: NLQuery) -> NLResponse:
        """Handle timeline queries"""
        response_text = "Timeline of activities"
        
        structured_data = {
            "events": [
                {"timestamp": "2024-01-15", "event": "First transaction"},
                {"timestamp": "2024-02-20", "event": "Coordination activity"},
                {"timestamp": "2024-03-10", "event": "Off-ramp attempt"}
            ],
            "total_events": 15
        }
        
        return NLResponse(
            query_id=query.query_id,
            response_text=response_text,
            structured_data=structured_data,
            confidence=0.90,
            sources=["transaction_history", "event_logs"],
            generated_at=datetime.now()
        )
    
    def _handle_generic_query(self, query: NLQuery) -> NLResponse:
        """Handle generic/unclassified queries"""
        return NLResponse(
            query_id=query.query_id,
            response_text="I understand you're asking about threat intelligence. Could you rephrase your question?",
            structured_data={},
            confidence=0.5,
            sources=[],
            generated_at=datetime.now(),
            follow_up_suggestions=[
                "Try: 'Who is coordinating with [actor]?'",
                "Try: 'What is the threat level of [actor]?'",
                "Try: 'Predict next actions for [actor]'"
            ]
        )
    
    # Helper methods for intent parsing
    def _extract_action(self, query: str) -> str:
        """Extract action from query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ["find", "show", "get", "list"]):
            return "retrieve"
        elif any(word in query_lower for word in ["predict", "forecast", "will"]):
            return "predict"
        elif any(word in query_lower for word in ["analyze", "assess", "evaluate"]):
            return "analyze"
        return "query"
    
    def _extract_target(self, query: str) -> str:
        """Extract target from query"""
        query_lower = query.lower()
        if "coordinate" in query_lower or "network" in query_lower:
            return "relationships"
        elif "pattern" in query_lower or "behavior" in query_lower:
            return "patterns"
        elif "threat" in query_lower or "risk" in query_lower:
            return "threat_level"
        return "actor"
    
    def _extract_subject(self, query: str) -> str:
        """Extract subject entity from query"""
        entities = self._extract_entities(query)
        return entities[0] if entities else "unknown"
    
    def _extract_temporal(self, query: str) -> Optional[str]:
        """Extract temporal information"""
        query_lower = query.lower()
        if "recent" in query_lower or "latest" in query_lower:
            return "recent"
        elif "next" in query_lower or "future" in query_lower:
            return "future"
        elif "history" in query_lower or "past" in query_lower:
            return "past"
        return None
    
    def _extract_scope(self, query: str) -> str:
        """Extract scope of query"""
        query_lower = query.lower()
        if "all" in query_lower or "every" in query_lower:
            return "all"
        elif "related" in query_lower or "connected" in query_lower:
            return "related"
        return "specific"

