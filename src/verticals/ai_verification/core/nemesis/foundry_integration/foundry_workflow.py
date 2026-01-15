"""
Foundry Workflow with scenario_forge → ABC → Hades/Echo/Nemesis Integration

Enhanced Foundry integration that supports:
1. Foundry compilations (existing)
2. scenario_forge artificial data (new)
3. ABC verification before processing
4. Hades/Echo/Nemesis compilation pipeline

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Dict, Any, Optional, Tuple
import logging

from .foundry_integration import FoundryIntegration
from .data_mapper import FoundryDataMapper

# Import ABC components
from src.verticals.ai_verification.core.nemesis.compilation_engine import (
    ABCCompilationEngine,
    CompiledIntelligence
)

# Import scenario_forge verification (if available)
try:
    from src.verticals.ai_verification.core.nemesis.scenario_forge_verification import (
        ScenarioForgeVerifier
    )
    SCENARIO_FORGE_VERIFIER_AVAILABLE = True
except ImportError:
    SCENARIO_FORGE_VERIFIER_AVAILABLE = False
    ScenarioForgeVerifier = None

logger = logging.getLogger(__name__)


class FoundryWorkflow:
    """
    Enhanced Foundry workflow with scenario_forge → ABC → Hades/Echo/Nemesis integration.
    
    **ABC verifies inputs, not outputs.** This workflow:
    1. Ingests data from Foundry OR scenario_forge
    2. Verifies with ABC (checks labeling, intent, provenance for scenario_forge)
    3. Processes through Hades/Echo/Nemesis pipeline
    4. Returns compiled intelligence with cryptographic receipt
    
    Supports both:
    - Foundry compilations (existing workflow)
    - scenario_forge artificial data (new workflow)
    """
    
    def __init__(
        self,
        foundry_api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        use_aip: bool = True
    ):
        """
        Initialize Foundry workflow.
        
        Args:
            foundry_api_url: Foundry API base URL
            api_key: Foundry API key (legacy mode)
            use_aip: If True, use Foundry AIP connector (OAuth2)
        """
        self.foundry_integration = FoundryIntegration(
            foundry_api_url=foundry_api_url,
            api_key=api_key,
            use_aip=use_aip
        )
        self.mapper = FoundryDataMapper()
        self.compilation_engine = ABCCompilationEngine()
        
        # Initialize scenario_forge verifier if available
        if SCENARIO_FORGE_VERIFIER_AVAILABLE:
            self.scenario_verifier = ScenarioForgeVerifier()
        else:
            self.scenario_verifier = None
            logger.warning(
                "scenario_forge verifier not available. "
                "scenario_forge data will be processed without ABC verification."
            )
    
    def process_foundry_compilation(
        self,
        compilation_id: str,
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None,
        generate_receipt: bool = True
    ) -> Tuple[bool, Optional[CompiledIntelligence], Dict[str, Any]]:
        """
        Process Foundry compilation through ABC → Hades/Echo/Nemesis.
        
        Args:
            compilation_id: Foundry compilation identifier
            actor_id: Optional actor ID for compilation
            actor_name: Optional actor name for compilation
            generate_receipt: Whether to generate ABC receipt
        
        Returns:
            Tuple of (success: bool, compiled_intelligence: CompiledIntelligence or None, details: dict)
        """
        try:
            # Step 1: Ingest Foundry compilation
            compilation = self.foundry_integration.ingest_compilation(compilation_id)
            
            # Step 2: Prepare for ABC analysis
            abc_data = self.foundry_integration.prepare_for_abc_analysis(compilation)
            
            # Step 3: Extract actor info from compilation
            if not actor_id:
                # Try to extract from compilation
                threat_actors = compilation.get("compiled_data", {}).get("threat_actors", [])
                if threat_actors:
                    actor_id = threat_actors[0].get("id", compilation_id)
                    actor_name = actor_name or threat_actors[0].get("name", compilation_id)
                else:
                    actor_id = compilation_id
                    actor_name = actor_name or f"Foundry Compilation {compilation_id}"
            
            # Step 4: Process through Hades/Echo/Nemesis
            compiled_intelligence = self.compilation_engine.compile_intelligence(
                actor_id=actor_id,
                actor_name=actor_name,
                raw_intelligence=abc_data["raw_intelligence"],
                transaction_data=abc_data.get("transaction_data", []),
                network_data=abc_data.get("network_data", {}),
                generate_receipt=generate_receipt,
                classification=compilation.get("classification", "UNCLASSIFIED")
            )
            
            details = {
                "compilation_id": compilation_id,
                "foundry_compilation_id": compilation_id,
                "foundry_data_hash": compilation.get("data_hash"),
                "foundry_timestamp": compilation.get("timestamp"),
                "processed_at": compiled_intelligence.compiled_at.isoformat() if compiled_intelligence.compiled_at else None
            }
            
            logger.info(
                f"Successfully processed Foundry compilation {compilation_id} "
                f"through ABC → Hades/Echo/Nemesis (compilation_id: {compiled_intelligence.compilation_id})"
            )
            
            return True, compiled_intelligence, details
        
        except Exception as e:
            logger.error(f"Error processing Foundry compilation: {e}", exc_info=True)
            return False, None, {"error": str(e), "compilation_id": compilation_id}
    
    def process_scenario_forge_data(
        self,
        scenario_data: Dict[str, Any],
        declared_intent: str = "model_evaluation",
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None,
        generate_receipt: bool = True
    ) -> Tuple[bool, Optional[CompiledIntelligence], Dict[str, Any]]:
        """
        Process scenario_forge data through ABC verification → Hades/Echo/Nemesis.
        
        Args:
            scenario_data: scenario_forge scenario data
            declared_intent: Declared use case (e.g., "model_evaluation", "demo", "testing")
            actor_id: Optional actor ID for compilation
            actor_name: Optional actor name for compilation
            generate_receipt: Whether to generate ABC receipt
        
        Returns:
            Tuple of (verified: bool, compiled_intelligence: CompiledIntelligence or None, details: dict)
        """
        if not self.scenario_verifier:
            logger.error("scenario_forge verifier not available")
            return False, None, {
                "error": "scenario_forge verifier not available",
                "scenario_id": scenario_data.get("scenario_id")
            }
        
        # Step 1: ABC Verification
        verified, receipt, verification_details = self.scenario_verifier.verify_scenario(
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
        
        # Step 2: Extract data from scenario_forge format
        try:
            # Extract transaction data
            transaction_data = []
            if "transaction_graph" in scenario_data:
                graph = scenario_data["transaction_graph"]
                if hasattr(graph, "edges"):
                    for edge in graph.edges(data=True):
                        transaction_data.append({
                            "from": edge[0],
                            "to": edge[1],
                            "data": edge[2] if len(edge) > 2 else {}
                        })
            
            # Extract network data
            network_data = {}
            if "entity_roles" in scenario_data:
                network_data["entity_roles"] = scenario_data["entity_roles"]
            if "motifs_used" in scenario_data:
                network_data["motifs"] = scenario_data["motifs_used"]
            
            # Extract intelligence text
            raw_intelligence = []
            if "narrative" in scenario_data:
                raw_intelligence.append({
                    "text": scenario_data["narrative"],
                    "source": "scenario_forge_narrative",
                    "type": "narrative"
                })
            if "intent" in scenario_data:
                raw_intelligence.append({
                    "text": f"Scenario intent: {scenario_data['intent']}",
                    "source": "scenario_forge_intent",
                    "type": "intent"
                })
            
            if not raw_intelligence:
                raw_intelligence.append({
                    "text": f"AML scenario {scenario_data.get('scenario_id', 'unknown')} - {scenario_data.get('intent', 'unknown intent')}",
                    "source": "scenario_forge",
                    "type": "scenario"
                })
            
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
            
            # Add ABC verification metadata
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
    
    def process_data(
        self,
        data: Dict[str, Any],
        data_type: str = "auto",
        declared_intent: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None,
        generate_receipt: bool = True
    ) -> Tuple[bool, Optional[CompiledIntelligence], Dict[str, Any]]:
        """
        Process data (auto-detects Foundry vs scenario_forge).
        
        Args:
            data: Data to process (Foundry compilation or scenario_forge scenario)
            data_type: "foundry", "scenario_forge", or "auto" (auto-detect)
            declared_intent: Declared use case (for scenario_forge)
            actor_id: Optional actor ID for compilation
            actor_name: Optional actor name for compilation
            generate_receipt: Whether to generate ABC receipt
        
        Returns:
            Tuple of (success: bool, compiled_intelligence: CompiledIntelligence or None, details: dict)
        """
        # Auto-detect data type
        if data_type == "auto":
            if "compilation_id" in data or "foundry_compilation_id" in data:
                data_type = "foundry"
            elif "scenario_id" in data or "intent" in data:
                data_type = "scenario_forge"
            else:
                return False, None, {
                    "error": "Could not auto-detect data type. Specify data_type='foundry' or 'scenario_forge'"
                }
        
        if data_type == "foundry":
            compilation_id = data.get("compilation_id") or data.get("foundry_compilation_id")
            if not compilation_id:
                return False, None, {"error": "Missing compilation_id for Foundry data"}
            
            return self.process_foundry_compilation(
                compilation_id=compilation_id,
                actor_id=actor_id,
                actor_name=actor_name,
                generate_receipt=generate_receipt
            )
        
        elif data_type == "scenario_forge":
            return self.process_scenario_forge_data(
                scenario_data=data,
                declared_intent=declared_intent or "model_evaluation",
                actor_id=actor_id,
                actor_name=actor_name,
                generate_receipt=generate_receipt
            )
        
        else:
            return False, None, {
                "error": f"Unknown data_type: {data_type}. Use 'foundry' or 'scenario_forge'"
            }

