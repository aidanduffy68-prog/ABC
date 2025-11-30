"""
Basic Usage Examples for AI-Powered Threat Ontology
"""

from nemesis.ai_ontology import (
    ABCIntegrationLayer,
    AIHadesProfiler,
    PredictiveThreatModel,
    NaturalLanguageInterface,
    ThreatDossierGenerator
)

# Example 1: Process Intelligence Feed
def example_process_intelligence():
    """Process raw intelligence through AI pipeline"""
    abc = ABCIntegrationLayer()
    
    intelligence = [
        {
            "text": "Lazarus Group detected moving $2.3M through Tornado Cash",
            "source": "twitter",
            "timestamp": "2024-11-15T10:00:00Z"
        },
        {
            "text": "North Korean hackers coordinating with Russian facilitators",
            "source": "intelligence_report",
            "timestamp": "2024-11-15T11:00:00Z"
        }
    ]
    
    result = abc.process_intelligence_feed(intelligence)
    print(f"Extracted {len(result['entities'])} entities")
    print(f"Found {len(result['relationships'])} relationships")


# Example 2: Generate Behavioral Signature
def example_behavioral_signature():
    """Generate AI-powered behavioral signature"""
    profiler = AIHadesProfiler()
    
    transaction_history = [
        {"amount": 1000000, "timestamp": "2024-11-01", "chain": "ethereum"},
        {"amount": 500000, "timestamp": "2024-11-05", "chain": "arbitrum"},
        {"amount": 800000, "timestamp": "2024-11-10", "chain": "polygon"}
    ]
    
    signature = profiler.generate_signature(
        actor_id="actor_123",
        transaction_history=transaction_history
    )
    
    print(f"Risk tolerance: {signature.traits.get('risk_tolerance', 0.0):.2f}")
    print(f"Flight risk: {signature.traits.get('flight_risk', 0.0):.2f}")
    print(f"Confidence: {signature.confidence:.2f}")


# Example 3: Generate Threat Forecast
def example_threat_forecast():
    """Generate predictive threat forecast"""
    model = PredictiveThreatModel()
    
    behavioral_signature = {
        "traits": {
            "risk_tolerance": 0.94,
            "flight_risk": 0.96,
            "pattern_repetition": 1.00
        },
        "confidence": 0.87
    }
    
    forecast = model.generate_forecast(
        actor_id="actor_123",
        behavioral_signature=behavioral_signature,
        transaction_history=[],
        network_data=None
    )
    
    print(f"Overall risk score: {forecast.overall_risk_score:.2f}")
    print(f"Predicted actions: {len(forecast.predictions)}")
    for pred in forecast.predictions:
        print(f"  - {pred.action_type.value}: {pred.confidence:.2f} confidence")


# Example 4: Natural Language Query
def example_natural_language():
    """Query threat intelligence in plain English"""
    nl = NaturalLanguageInterface()
    
    queries = [
        "Who is coordinating with Lazarus Group?",
        "What is the threat level of actor ALPHA_47?",
        "Predict next actions for wallet 0x4a9f...",
        "Show me the coordination network for North Korean hackers"
    ]
    
    for query in queries:
        response = nl.process_query(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response.response_text}")
        print(f"Confidence: {response.confidence:.2f}")


# Example 5: Generate Threat Dossier
def example_threat_dossier():
    """Generate comprehensive threat dossier"""
    generator = ThreatDossierGenerator()
    
    dossier = generator.generate_dossier(
        actor_id="LAZARUS_GROUP",
        actor_name="Lazarus Group (DPRK)",
        behavioral_signature={
            "traits": {"risk_tolerance": 0.97, "flight_risk": 0.96},
            "confidence": 0.89
        },
        network_data={
            "network_size": 47,
            "coordination_score": 0.85,
            "partners": ["Actor_A", "Actor_B"]
        },
        threat_forecast={
            "predictions": [
                {
                    "type": "off_ramp_attempt",
                    "confidence": 0.87,
                    "timing_window": "48-72h"
                }
            ],
            "overall_risk_score": 0.89,
            "recommended_countermeasures": ["Pre-emptive freeze", "Alert exchanges"]
        },
        transaction_history=[],
        historical_patterns=None
    )
    
    # Export as markdown
    markdown = generator.export_dossier_markdown(dossier)
    print(markdown)


if __name__ == "__main__":
    print("=== Example 1: Process Intelligence ===")
    example_process_intelligence()
    
    print("\n=== Example 2: Behavioral Signature ===")
    example_behavioral_signature()
    
    print("\n=== Example 3: Threat Forecast ===")
    example_threat_forecast()
    
    print("\n=== Example 4: Natural Language Query ===")
    example_natural_language()
    
    print("\n=== Example 5: Threat Dossier ===")
    example_threat_dossier()

