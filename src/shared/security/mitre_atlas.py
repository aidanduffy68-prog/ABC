"""
MITRE ATLAS Integration
AI-specific threat modeling and attack pattern detection

MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)
provides tactics, techniques, and procedures (TTPs) specific to AI systems.

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ATLASTactic(Enum):
    """MITRE ATLAS Tactics"""
    RECONNAISSANCE = "Reconnaissance"
    RESOURCE_DEVELOPMENT = "Resource Development"
    INITIAL_ACCESS = "Initial Access"
    EXECUTION = "Execution"
    PERSISTENCE = "Persistence"
    PRIVILEGE_ESCALATION = "Privilege Escalation"
    DEFENSE_EVASION = "Defense Evasion"
    CREDENTIAL_ACCESS = "Credential Access"
    DISCOVERY = "Discovery"
    COLLECTION = "Collection"
    EXFILTRATION = "Exfiltration"
    IMPACT = "Impact"


class ATLASTechnique(Enum):
    """MITRE ATLAS Techniques relevant to GH Systems ABC"""
    # Reconnaissance
    T1589_GATHER_VICTIM_AI_INFO = "T1589 - Gather Victim AI Information"
    T1590_GATHER_VICTIM_AI_DATA = "T1590 - Gather Victim AI Data"
    
    # Resource Development
    T1608_STAGE_AI_CAPABILITIES = "T1608 - Stage AI Capabilities"
    
    # Initial Access
    T1190_EXPLOIT_PUBLIC_FACING_AI = "T1190 - Exploit Public-Facing AI Application"
    
    # Execution
    T1059_COMMAND_AND_SCRIPTING_INTERPRETER = "T1059 - Command and Scripting Interpreter"
    T1560_AI_POWERED_EXECUTION = "T1560 - AI-Powered Execution"
    
    # Persistence
    T1543_CREATE_OR_MODIFY_SYSTEM_PROCESS = "T1543 - Create or Modify System Process"
    T1574_HIJACK_EXECUTION_FLOW = "T1574 - Hijack Execution Flow"
    
    # Defense Evasion
    T1070_INDICATOR_REMOVAL = "T1070 - Indicator Removal"
    T1562_IMPAIR_DEFENSES = "T1562 - Impair Defenses"
    T1647_OBFUSCATE_AI_MODEL = "T1647 - Obfuscate AI Model"
    
    # Discovery
    T1083_FILE_AND_DIRECTORY_DISCOVERY = "T1083 - File and Directory Discovery"
    T1520_AI_MODEL_DISCOVERY = "T1520 - AI Model Discovery"
    
    # Collection
    T1005_DATA_FROM_LOCAL_SYSTEM = "T1005 - Data from Local System"
    T1557_ADVERSARIAL_COLLECTION = "T1557 - Adversarial Collection"
    
    # Exfiltration
    T1041_EXFILTRATE_OVER_C2_CHANNEL = "T1041 - Exfiltrate Over C2 Channel"
    T1648_STEAL_AI_MODEL = "T1648 - Steal AI Model"
    
    # Impact
    T1498_NETWORK_DENIAL_OF_SERVICE = "T1498 - Network Denial of Service"
    T1649_COMPROMISE_AI_MODEL = "T1649 - Compromise AI Model"
    T1650_DEGRADE_AI_MODEL = "T1650 - Degrade AI Model"


@dataclass
class ATLASThreat:
    """Represents an ATLAS threat pattern"""
    technique: ATLASTechnique
    tactic: ATLASTactic
    description: str
    detection_indicators: List[str]
    mitigation: List[str]
    severity: str  # 'low', 'medium', 'high', 'critical'


class MITREATLASAnalyzer:
    """
    Analyzes system for MITRE ATLAS threat patterns
    
    Provides AI-specific threat modeling and detection
    """
    
    def __init__(self):
        self.threat_patterns = self._initialize_threat_patterns()
        self.detected_threats: List[ATLASThreat] = []
    
    def _initialize_threat_patterns(self) -> Dict[ATLASTechnique, ATLASThreat]:
        """Initialize ATLAS threat patterns relevant to GH Systems ABC"""
        patterns = {}
        
        # Data Poisoning / Adversarial Collection
        patterns[ATLASTechnique.T1557_ADVERSARIAL_COLLECTION] = ATLASThreat(
            technique=ATLASTechnique.T1557_ADVERSARIAL_COLLECTION,
            tactic=ATLASTactic.COLLECTION,
            description="Adversary collects data to poison AI model training or inference",
            detection_indicators=[
                "Unusual data patterns in training inputs",
                "Sudden drop in model confidence scores",
                "Anomalous input data sources",
                "Unexpected model behavior on specific inputs"
            ],
            mitigation=[
                "Input validation and sanitization",
                "Data quality monitoring",
                "Anomaly detection on inputs",
                "Regular model retraining with clean data"
            ],
            severity="high"
        )
        
        # Model Theft / Exfiltration
        patterns[ATLASTechnique.T1648_STEAL_AI_MODEL] = ATLASThreat(
            technique=ATLASTechnique.T1648_STEAL_AI_MODEL,
            tactic=ATLASTactic.EXFILTRATION,
            description="Adversary steals AI model files or weights",
            detection_indicators=[
                "Unauthorized access to model storage",
                "Large data transfers from model repository",
                "Unusual API calls to model endpoints",
                "Model file access outside normal operations"
            ],
            mitigation=[
                "Access control on model files",
                "Encryption of model artifacts",
                "Audit logging of model access",
                "Network segmentation"
            ],
            severity="critical"
        )
        
        # Model Compromise
        patterns[ATLASTechnique.T1649_COMPROMISE_AI_MODEL] = ATLASThreat(
            technique=ATLASTechnique.T1649_COMPROMISE_AI_MODEL,
            tactic=ATLASTactic.IMPACT,
            description="Adversary modifies AI model to produce incorrect outputs",
            detection_indicators=[
                "Model file integrity violations",
                "Unexpected model behavior",
                "Model version mismatches",
                "Unauthorized model updates"
            ],
            mitigation=[
                "Model file integrity checks",
                "Version control and signing",
                "Read-only model storage in production",
                "Regular model validation"
            ],
            severity="critical"
        )
        
        # Model Degradation
        patterns[ATLASTechnique.T1650_DEGRADE_AI_MODEL] = ATLASThreat(
            technique=ATLASTechnique.T1650_DEGRADE_AI_MODEL,
            tactic=ATLASTactic.IMPACT,
            description="Adversary degrades AI model performance through adversarial inputs",
            detection_indicators=[
                "Sudden performance degradation",
                "Increased false positives/negatives",
                "Model drift alerts",
                "Unusual input patterns causing errors"
            ],
            mitigation=[
                "Input validation and filtering",
                "Adversarial input detection",
                "Model drift monitoring",
                "Output validation and confidence thresholds"
            ],
            severity="high"
        )
        
        # Prompt Injection (for LLM-based systems)
        patterns[ATLASTechnique.T1190_EXPLOIT_PUBLIC_FACING_AI] = ATLASThreat(
            technique=ATLASTechnique.T1190_EXPLOIT_PUBLIC_FACING_AI,
            tactic=ATLASTactic.INITIAL_ACCESS,
            description="Adversary exploits public-facing AI application through malicious inputs",
            detection_indicators=[
                "Suspicious input patterns",
                "Unexpected model outputs",
                "Input validation failures",
                "Anomalous API usage"
            ],
            mitigation=[
                "Input validation and sanitization",
                "Rate limiting",
                "Output filtering",
                "Human-in-the-loop validation"
            ],
            severity="high"
        )
        
        # Model Obfuscation
        patterns[ATLASTechnique.T1647_OBFUSCATE_AI_MODEL] = ATLASThreat(
            technique=ATLASTechnique.T1647_OBFUSCATE_AI_MODEL,
            tactic=ATLASTactic.DEFENSE_EVASION,
            description="Adversary obfuscates AI model to evade detection",
            detection_indicators=[
                "Encrypted or obfuscated model files",
                "Unusual model structure",
                "Model loading errors",
                "Unexpected model behavior"
            ],
            mitigation=[
                "Model integrity verification",
                "Standardized model formats",
                "Model validation on load",
                "Regular security scanning"
            ],
            severity="medium"
        )
        
        return patterns
    
    def analyze_system(self, system_state: Dict) -> List[ATLASThreat]:
        """
        Analyze system for ATLAS threat patterns
        
        Args:
            system_state: Current system state including:
                - model_files: List of model file paths
                - access_logs: Recent access logs
                - performance_metrics: Current performance metrics
                - input_patterns: Recent input patterns
                - security_alerts: Recent security alerts
        
        Returns:
            List of detected ATLAS threats
        """
        detected = []
        
        # Check for model theft indicators
        if self._check_model_theft(system_state):
            detected.append(self.threat_patterns[ATLASTechnique.T1648_STEAL_AI_MODEL])
        
        # Check for model compromise indicators
        if self._check_model_compromise(system_state):
            detected.append(self.threat_patterns[ATLASTechnique.T1649_COMPROMISE_AI_MODEL])
        
        # Check for adversarial collection
        if self._check_adversarial_collection(system_state):
            detected.append(self.threat_patterns[ATLASTechnique.T1557_ADVERSARIAL_COLLECTION])
        
        # Check for model degradation
        if self._check_model_degradation(system_state):
            detected.append(self.threat_patterns[ATLASTechnique.T1650_DEGRADE_AI_MODEL])
        
        # Check for prompt injection / exploitation
        if self._check_ai_exploitation(system_state):
            detected.append(self.threat_patterns[ATLASTechnique.T1190_EXPLOIT_PUBLIC_FACING_AI])
        
        self.detected_threats = detected
        return detected
    
    def _check_model_theft(self, state: Dict) -> bool:
        """Check for indicators of model theft"""
        # Check for large unauthorized data transfers
        access_logs = state.get('access_logs', [])
        model_files = state.get('model_files', [])
        
        # Look for unusual access patterns
        for log in access_logs:
            if any(model_file in log.get('resource', '') for model_file in model_files):
                if log.get('action') == 'read' and log.get('size', 0) > 100 * 1024 * 1024:  # >100MB
                    return True
        
        return False
    
    def _check_model_compromise(self, state: Dict) -> bool:
        """Check for indicators of model compromise"""
        # Check for model file integrity violations
        security_alerts = state.get('security_alerts', [])
        
        for alert in security_alerts:
            if 'integrity' in alert.get('type', '').lower() or 'model' in alert.get('type', '').lower():
                return True
        
        return False
    
    def _check_adversarial_collection(self, state: Dict) -> bool:
        """Check for adversarial data collection"""
        input_patterns = state.get('input_patterns', [])
        performance_metrics = state.get('performance_metrics', {})
        
        # Check for sudden drop in confidence
        if performance_metrics.get('confidence_drop', 0) > 0.2:  # 20% drop
            return True
        
        # Check for unusual input patterns
        if len(input_patterns) > 0:
            # Look for patterns that might indicate adversarial inputs
            suspicious_patterns = ['test', 'adversarial', 'poison', 'inject']
            for pattern in input_patterns:
                if any(susp in str(pattern).lower() for susp in suspicious_patterns):
                    return True
        
        return False
    
    def _check_model_degradation(self, state: Dict) -> bool:
        """Check for model degradation indicators"""
        performance_metrics = state.get('performance_metrics', {})
        
        # Check for performance degradation
        if performance_metrics.get('performance_degradation', False):
            return True
        
        # Check for increased error rate
        if performance_metrics.get('error_rate', 0) > 0.1:  # 10% error rate
            return True
        
        return False
    
    def _check_ai_exploitation(self, state: Dict) -> bool:
        """Check for AI exploitation indicators"""
        input_patterns = state.get('input_patterns', [])
        security_alerts = state.get('security_alerts', [])
        
        # Check for suspicious input patterns
        injection_patterns = ['<script>', 'javascript:', 'eval(', 'exec(', 'import os']
        for pattern in input_patterns:
            pattern_str = str(pattern).lower()
            if any(inj in pattern_str for inj in injection_patterns):
                return True
        
        # Check for security alerts related to input validation
        for alert in security_alerts:
            if 'input' in alert.get('type', '').lower() or 'validation' in alert.get('type', '').lower():
                return True
        
        return False
    
    def get_threat_report(self) -> Dict:
        """Generate threat analysis report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_threats_detected': len(self.detected_threats),
            'threats_by_severity': {
                'critical': len([t for t in self.detected_threats if t.severity == 'critical']),
                'high': len([t for t in self.detected_threats if t.severity == 'high']),
                'medium': len([t for t in self.detected_threats if t.severity == 'medium']),
                'low': len([t for t in self.detected_threats if t.severity == 'low'])
            },
            'detected_threats': [
                {
                    'technique': t.technique.value,
                    'tactic': t.tactic.value,
                    'description': t.description,
                    'severity': t.severity,
                    'detection_indicators': t.detection_indicators,
                    'mitigation': t.mitigation
                }
                for t in self.detected_threats
            ],
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on detected threats"""
        recommendations = []
        
        if any(t.severity == 'critical' for t in self.detected_threats):
            recommendations.append("Immediate action required: Critical threats detected")
            recommendations.append("Review and implement all critical severity mitigations")
        
        if any(t.technique == ATLASTechnique.T1648_STEAL_AI_MODEL for t in self.detected_threats):
            recommendations.append("Enhance model file access controls and encryption")
            recommendations.append("Implement model access audit logging")
        
        if any(t.technique == ATLASTechnique.T1557_ADVERSARIAL_COLLECTION for t in self.detected_threats):
            recommendations.append("Implement adversarial input detection")
            recommendations.append("Review and retrain model with clean data")
        
        if not recommendations:
            recommendations.append("No immediate threats detected. Continue regular monitoring.")
        
        return recommendations


# Global analyzer instance
_atlas_analyzer: Optional[MITREATLASAnalyzer] = None


def get_atlas_analyzer() -> MITREATLASAnalyzer:
    """Get or create global ATLAS analyzer instance"""
    global _atlas_analyzer
    if _atlas_analyzer is None:
        _atlas_analyzer = MITREATLASAnalyzer()
    return _atlas_analyzer

