"""
Workflow: scenario_forge → ABC Verification → Hades/Echo/Nemesis Processing

Orchestrates the complete workflow from scenario_forge generation through
ABC verification to Hades/Echo/Nemesis processing.

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from .scenario_forge_verification import ScenarioForgeVerifier
from .compilation_engine import ABCCompilationEngine, CompiledIntelligence

logger = logging.getLogger(__name__)


class ScenarioForgeWorkflow:
    """
    Workflow orchestrator for scenario_forge → ABC → Hades/Echo/Nemesis.
    
    **ABC verifies inputs, not outputs.** This workflow:
    1. Verifies scenario_forge artificial data with ABC (checks labeling, intent, provenance)
    2. If verified, processes through Hades/Echo/Nemesis pipeline
    3. Returns compiled intelligence with cryptographic receipt
    
    This ensures all processed data is ABC-verified before entering the analysis pipeline.
    """
    
    def __init__(self):
        self.verifier = ScenarioForgeVerifier()
        self.compilation_engine = ABCCompilationEngine()
    
    def process_scenario(
        self,
        scenario_data: Dict[str, Any],
        declared_intent: str = "model_evaluation",
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None,
        generate_receipt: bool = True
    ) -> Tuple[bool, Optional[CompiledIntelligence], Optional[Dict[str, Any]]]:
        """
        Process scenario_forge data through ABC verification and Hades/Echo/Nemesis.
        
        Args:
            scenario_data: scenario_forge scenario data (dict with scenario_id, intent, graph, etc.)
            declared_intent: Declared use case (e.g., "model_evaluation", "demo", "testing")
            actor_id: Optional actor ID for compilation (if None, uses scenario_id)
            actor_name: Optional actor name for compilation
            generate_receipt: Whether to generate ABC receipt
        
        Returns:
            Tuple of (verified: bool, compiled_intelligence: CompiledIntelligence or None, verification_details: dict)
        """
        # Step 1: ABC Verification
        verified, receipt, verification_details = self.verifier.verify_scenario(
            scenario_data=scenario_data,
            declared_intent=declared_intent,
            require_artificial_label=True
        )
        
        if not verified:
            logger.warning(
                f"Scenario {scenario_data.get('scenario_id')} failed ABC verification: "
                f"{verification_details.get('errors', [])}"
            )
            return False, None, verification_details
        
        # Step 2: Convert scenario data to format for Hades/Echo/Nemesis
        try:
            # Extract transaction data from scenario graph
            transaction_data = self._extract_transactions(scenario_data)
            
            # Extract network/relationship data
            network_data = self._extract_network_data(scenario_data)
            
            # Extract intelligence text from scenario
            raw_intelligence = self._extract_intelligence(scenario_data)
            
            # Use scenario_id as actor_id if not provided
            actor_id = actor_id or scenario_data.get("scenario_id", "unknown")
            actor_name = actor_name or f"Scenario {scenario_data.get('scenario_id', 'unknown')}"
            
            # Step 3: Process through Hades/Echo/Nemesis
            compiled_intelligence = self.compilation_engine.compile_intelligence(
                actor_id=actor_id,
                actor_name=actor_name,
                raw_intelligence=raw_intelligence,
                transaction_data=transaction_data,
                network_data=network_data,
                generate_receipt=generate_receipt
            )
            
            # Add ABC verification metadata to compiled intelligence
            verification_details["abc_verification"] = {
                "verified": True,
                "receipt_id": receipt.receipt_id if receipt else None,
                "verification_timestamp": verification_details["timestamp"]
            }
            
            logger.info(
                f"Successfully processed scenario {scenario_data.get('scenario_id')} "
                f"through ABC → Hades/Echo/Nemesis (compilation_id: {compiled_intelligence.compilation_id})"
            )
            
            return True, compiled_intelligence, verification_details
        
        except Exception as e:
            logger.error(f"Error processing scenario through Hades/Echo/Nemesis: {e}", exc_info=True)
            verification_details["processing_error"] = str(e)
            return False, None, verification_details
    
    def _extract_transactions(self, scenario_data: Dict[str, Any]) -> list:
        """Extract transaction data from scenario_forge scenario"""
        transactions = []
        
        # Try to get transactions from scenario data
        if "transactions" in scenario_data:
            transactions = scenario_data["transactions"]
        elif "transaction_graph" in scenario_data:
            # Extract from NetworkX graph if present
            graph = scenario_data["transaction_graph"]
            if hasattr(graph, "edges"):
                for edge in graph.edges(data=True):
                    transactions.append({
                        "from": edge[0],
                        "to": edge[1],
                        "data": edge[2] if len(edge) > 2 else {}
                    })
        elif "graph" in scenario_data:
            # Try graph attribute
            graph = scenario_data["graph"]
            if hasattr(graph, "edges"):
                for edge in graph.edges(data=True):
                    transactions.append({
                        "from": edge[0],
                        "to": edge[1],
                        "data": edge[2] if len(edge) > 2 else {}
                    })
        
        return transactions
    
    def _extract_network_data(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract network/relationship data from scenario_forge scenario"""
        network_data = {}
        
        # Extract entity roles if present
        if "entity_roles" in scenario_data:
            network_data["entity_roles"] = scenario_data["entity_roles"]
        
        # Extract motifs used
        if "motifs_used" in scenario_data:
            network_data["motifs"] = scenario_data["motifs_used"]
        
        # Extract jurisdiction assumptions
        if "jurisdiction_assumptions" in scenario_data:
            network_data["jurisdictions"] = scenario_data["jurisdiction_assumptions"]
        
        return network_data
    
    def _extract_intelligence(self, scenario_data: Dict[str, Any]) -> list:
        """Extract intelligence text from scenario_forge scenario"""
        intelligence = []
        
        # Try to get narrative
        if "narrative" in scenario_data:
            intelligence.append({
                "text": scenario_data["narrative"],
                "source": "scenario_forge_narrative",
                "type": "narrative"
            })
        
        # Try to get description
        if "description" in scenario_data:
            intelligence.append({
                "text": scenario_data["description"],
                "source": "scenario_forge_description",
                "type": "description"
            })
        
        # Try to get intent as intelligence
        if "intent" in scenario_data:
            intelligence.append({
                "text": f"Scenario intent: {scenario_data['intent']}",
                "source": "scenario_forge_intent",
                "type": "intent"
            })
        
        # If no intelligence found, create default
        if not intelligence:
            intelligence.append({
                "text": f"AML scenario {scenario_data.get('scenario_id', 'unknown')} - {scenario_data.get('intent', 'unknown intent')}",
                "source": "scenario_forge",
                "type": "scenario"
            })
        
        return intelligence

