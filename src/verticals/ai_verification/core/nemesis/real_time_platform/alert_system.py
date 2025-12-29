"""
Alert System for Critical Threats
Monitors compilations and triggers alerts for critical threats

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Alert types"""
    THREAT_DETECTED = "threat_detected"
    CRITICAL_VULNERABILITY = "critical_vulnerability"
    FEDERAL_AI_BREACH = "federal_ai_breach"
    HIGH_CONFIDENCE_THREAT = "high_confidence_threat"
    RAPID_COMPILATION = "rapid_compilation"


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    created_at: datetime
    actor_id: Optional[str] = None
    target_agency: Optional[str] = None
    compilation_id: Optional[str] = None
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


class AlertSystem:
    """
    Alert system for critical threats
    
    Monitors compilations and triggers alerts based on:
    - Threat level (critical/high)
    - Confidence scores
    - Federal AI vulnerabilities
    - Rapid compilation patterns
    """
    
    def __init__(self):
        self.alerts = []
        self.alert_handlers: List[Callable] = []
        self.alert_rules = self._initialize_rules()
        self.alert_version = "1.0.0"
    
    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize alert rules"""
        return {
            "critical_threat_threshold": 0.8,
            "high_confidence_threshold": 0.9,
            "federal_ai_critical_severity": True,
            "rapid_compilation_threshold": 5,  # Compilations per minute
        }
    
    def evaluate_compilation(self, compilation_data: Dict[str, Any]) -> List[Alert]:
        """
        Evaluate compilation and generate alerts if needed
        
        Args:
            compilation_data: Compiled intelligence data
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        # Rule 1: Critical threat level
        threat_level = compilation_data.get("targeting_package", {}).get("risk_assessment", {}).get("threat_level")
        if threat_level == "critical":
            alert = self._create_alert(
                alert_type=AlertType.THREAT_DETECTED,
                severity=AlertSeverity.CRITICAL,
                title=f"Critical Threat Detected: {compilation_data.get('actor_id', 'Unknown')}",
                description=f"Critical threat level detected with confidence {compilation_data.get('confidence_score', 0):.2%}",
                compilation_data=compilation_data
            )
            alerts.append(alert)
        
        # Rule 2: High confidence score
        confidence = compilation_data.get("confidence_score", 0.0)
        if confidence >= self.alert_rules["high_confidence_threshold"]:
            alert = self._create_alert(
                alert_type=AlertType.HIGH_CONFIDENCE_THREAT,
                severity=AlertSeverity.HIGH,
                title=f"High Confidence Threat: {compilation_data.get('actor_id', 'Unknown')}",
                description=f"Threat detected with {confidence:.2%} confidence",
                compilation_data=compilation_data
            )
            alerts.append(alert)
        
        # Rule 3: Federal AI critical vulnerability
        target_agency = compilation_data.get("target_agency")
        if target_agency and threat_level == "critical":
            alert = self._create_alert(
                alert_type=AlertType.FEDERAL_AI_BREACH,
                severity=AlertSeverity.CRITICAL,
                title=f"Critical Federal AI Vulnerability: {target_agency}",
                description=f"Critical vulnerability detected in {target_agency} AI infrastructure",
                compilation_data=compilation_data
            )
            alerts.append(alert)
        
        # Store and trigger alerts
        for alert in alerts:
            self.alerts.append(alert)
            self._trigger_alert(alert)
        
        return alerts
    
    def evaluate_federal_ai_scan(self, scan_data: Dict[str, Any]) -> List[Alert]:
        """
        Evaluate federal AI scan and generate alerts
        
        Args:
            scan_data: Federal AI scan results
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        vulnerabilities = scan_data.get("vulnerabilities", [])
        for vuln in vulnerabilities:
            if vuln.get("severity") == "critical":
                alert = self._create_alert(
                    alert_type=AlertType.CRITICAL_VULNERABILITY,
                    severity=AlertSeverity.CRITICAL,
                    title=f"Critical Vulnerability: {vuln.get('system_id', 'Unknown')}",
                    description=f"Critical vulnerability detected: {vuln.get('type', 'Unknown')}",
                    metadata={
                        "vulnerability_id": vuln.get("vulnerability_id"),
                        "system_id": vuln.get("system_id"),
                        "vulnerability_type": vuln.get("type"),
                        "confidence": vuln.get("confidence")
                    }
                )
                alerts.append(alert)
                self.alerts.append(alert)
                self._trigger_alert(alert)
        
        return alerts
    
    def _create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        compilation_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """Create alert from data"""
        alert_id = f"alert_{int(datetime.now().timestamp())}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            created_at=datetime.now(),
            actor_id=compilation_data.get("actor_id") if compilation_data else None,
            target_agency=compilation_data.get("target_agency") if compilation_data else None,
            compilation_id=compilation_data.get("compilation_id") if compilation_data else None,
            confidence_score=compilation_data.get("confidence_score", 0.0) if compilation_data else 0.0,
            metadata=metadata or {}
        )
        
        return alert
    
    def _trigger_alert(self, alert: Alert):
        """Trigger alert handlers"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Error in alert handler: {e}")
    
    def register_alert_handler(self, handler: Callable[[Alert], None]):
        """Register alert handler function"""
        self.alert_handlers.append(handler)
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active (unacknowledged) alerts"""
        alerts = [a for a in self.alerts if not a.acknowledged]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                return True
        return False
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total = len(self.alerts)
        active = len([a for a in self.alerts if not a.acknowledged])
        by_severity = {}
        by_type = {}
        
        for severity in AlertSeverity:
            by_severity[severity.value] = len([a for a in self.alerts if a.severity == severity])
        
        for alert_type in AlertType:
            by_type[alert_type.value] = len([a for a in self.alerts if a.alert_type == alert_type])
        
        return {
            "total_alerts": total,
            "active_alerts": active,
            "acknowledged_alerts": total - active,
            "by_severity": by_severity,
            "by_type": by_type,
            "timestamp": datetime.now().isoformat()
        }


# Global alert system instance
alert_system = AlertSystem()

