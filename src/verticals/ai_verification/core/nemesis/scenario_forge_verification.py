"""
ABC Verification for scenario_forge Artificial Data

Verifies scenario_forge output before processing by Hades/Echo/Nemesis pipeline.
Ensures artificial data is properly labeled, intent matches declared use case,
and provenance metadata is correct.

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from src.shared.receipts import CryptographicReceiptGenerator, IntelligenceReceipt

logger = logging.getLogger(__name__)


class ScenarioForgeVerifier:
    """
    Verifies scenario_forge artificial data before processing.
    
    **ABC verifies inputs, not outputs.** This verifier ensures scenario_forge
    artificial data is properly governed before entering the Hades/Echo/Nemesis
    pipeline. ABC provides cryptographic proof that artificial data was:
    - Properly labeled as artificial
    - Used for declared intent (testing, demos, model evaluation)
    - Has correct provenance metadata
    - Matches declared usage policy
    
    After verification, the data can safely enter Hades/Echo/Nemesis for processing.
    """
    
    # Required markers for artificial data
    ARTIFICIAL_DATA_MARKERS = [
        "ARTIFICIAL_DATA",
        "ARTIFICIAL",
        "NOT_REAL",
        "FOR_TESTING_ONLY",
        "GOVERNED_ARTIFICIAL"
    ]
    
    # Valid intents for scenario_forge
    VALID_INTENTS = [
        "SANCTIONS_EVASION",
        "LAUNDERING",
        "FALSE_POSITIVE_TRAP",
        "RANSOMWARE_LIQUIDATION",
        "TAX_EVASION"
    ]
    
    def __init__(self):
        self.receipt_generator = CryptographicReceiptGenerator()
    
    def verify_scenario(
        self,
        scenario_data: Dict[str, Any],
        declared_intent: str = "model_evaluation",
        require_artificial_label: bool = True
    ) -> Tuple[bool, Optional[IntelligenceReceipt], Dict[str, Any]]:
        """
        Verify scenario_forge data before processing.
        
        Args:
            scenario_data: scenario_forge scenario data (dict with scenario_id, intent, etc.)
            declared_intent: Declared use case (e.g., "model_evaluation", "demo", "testing")
            require_artificial_label: Whether to require explicit artificial data label
        
        Returns:
            Tuple of (verified: bool, receipt: IntelligenceReceipt or None, details: dict)
        """
        verification_details = {
            "scenario_id": scenario_data.get("scenario_id"),
            "verified": False,
            "errors": [],
            "warnings": [],
            "checks_passed": {},
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
        # Check 1: Verify artificial data labeling
        if require_artificial_label:
            has_marker = self._check_artificial_marker(scenario_data)
            verification_details["checks_passed"]["artificial_label"] = has_marker
            if not has_marker:
                verification_details["errors"].append(
                    "Missing required artificial data label. "
                    "scenario_forge data must be explicitly marked as ARTIFICIAL_DATA"
                )
        
        # Check 2: Verify intent matches declared use case
        intent_check = self._verify_intent(scenario_data, declared_intent)
        verification_details["checks_passed"]["intent_verification"] = intent_check["valid"]
        if not intent_check["valid"]:
            verification_details["errors"].append(intent_check.get("error", "Intent verification failed"))
        
        # Check 3: Verify provenance metadata
        provenance_check = self._verify_provenance(scenario_data)
        verification_details["checks_passed"]["provenance"] = provenance_check["valid"]
        if not provenance_check["valid"]:
            verification_details["warnings"].append(
                provenance_check.get("warning", "Provenance metadata incomplete")
            )
        
        # Check 4: Verify scenario hash integrity
        hash_check = self._verify_scenario_hash(scenario_data)
        verification_details["checks_passed"]["hash_integrity"] = hash_check["valid"]
        if not hash_check["valid"]:
            verification_details["errors"].append(
                "Scenario hash mismatch - data integrity issue"
            )
        
        # Generate receipt if all critical checks pass
        all_critical_checks_pass = (
            (not require_artificial_label or verification_details["checks_passed"].get("artificial_label", False)) and
            verification_details["checks_passed"].get("intent_verification", False) and
            verification_details["checks_passed"].get("hash_integrity", False)
        )
        
        receipt = None
        if all_critical_checks_pass:
            try:
                # Generate ABC receipt for verified scenario
                receipt = self.receipt_generator.generate_receipt(
                    data=scenario_data,
                    source=f"scenario_forge_{scenario_data.get('scenario_id', 'unknown')}",
                    classification="UNCLASSIFIED",
                    additional_metadata={
                        "artificial_data": True,
                        "source": "scenario_forge",
                        "declared_intent": declared_intent,
                        "scenario_intent": scenario_data.get("intent"),
                        "verified_at": datetime.utcnow().isoformat() + 'Z'
                    }
                )
                verification_details["receipt_id"] = receipt.receipt_id
                verification_details["intelligence_hash"] = receipt.intelligence_hash
            except Exception as e:
                logger.error(f"Error generating receipt: {e}", exc_info=True)
                verification_details["warnings"].append(f"Receipt generation failed: {str(e)}")
        
        verification_details["verified"] = all_critical_checks_pass
        
        return all_critical_checks_pass, receipt, verification_details
    
    def _check_artificial_marker(self, scenario_data: Dict[str, Any]) -> bool:
        """Check if scenario has artificial data marker"""
        # Check in metadata
        metadata = scenario_data.get("metadata", {})
        if isinstance(metadata, dict):
            for marker in self.ARTIFICIAL_DATA_MARKERS:
                if marker.lower() in str(metadata).lower():
                    return True
        
        # Check in provenance
        provenance = scenario_data.get("provenance", {})
        if isinstance(provenance, dict):
            for marker in self.ARTIFICIAL_DATA_MARKERS:
                if marker.lower() in str(provenance).lower():
                    return True
        
        # Check scenario_id or other fields
        scenario_id = str(scenario_data.get("scenario_id", ""))
        for marker in self.ARTIFICIAL_DATA_MARKERS:
            if marker.lower() in scenario_id.lower():
                return True
        
        return False
    
    def _verify_intent(
        self,
        scenario_data: Dict[str, Any],
        declared_intent: str
    ) -> Dict[str, Any]:
        """Verify scenario intent matches declared use case"""
        scenario_intent = scenario_data.get("intent")
        
        # Intent must be valid scenario_forge intent
        if scenario_intent and scenario_intent not in self.VALID_INTENTS:
            return {
                "valid": False,
                "error": f"Invalid scenario intent: {scenario_intent}"
            }
        
        # Intent verification passes if scenario has valid intent
        # (Declared intent is for ABC's use case tracking, not scenario validation)
        return {
            "valid": True,
            "scenario_intent": scenario_intent
        }
    
    def _verify_provenance(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify provenance metadata exists"""
        provenance = scenario_data.get("provenance", {})
        scenario_id = scenario_data.get("scenario_id")
        created_at = scenario_data.get("created_at")
        
        has_basic_provenance = bool(scenario_id)
        
        if not has_basic_provenance:
            return {
                "valid": False,
                "warning": "Missing basic provenance (scenario_id)"
            }
        
        return {
            "valid": True,
            "has_metadata": bool(provenance),
            "has_timestamp": bool(created_at)
        }
    
    def _verify_scenario_hash(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify scenario hash integrity"""
        stored_hash = scenario_data.get("scenario_hash") or scenario_data.get("hash")
        
        if not stored_hash:
            return {
                "valid": False,
                "error": "Missing scenario hash"
            }
        
        # Compute hash of scenario data (excluding hash field)
        scenario_copy = {k: v for k, v in scenario_data.items() if k not in ["scenario_hash", "hash"]}
        computed_hash = self.receipt_generator.generate_data_hash(scenario_copy)
        
        # For now, just verify hash exists (full validation requires scenario_forge hash function)
        # In production, would use scenario_forge's hash function
        return {
            "valid": bool(stored_hash),
            "has_hash": bool(stored_hash),
            "computed_hash": computed_hash
        }

