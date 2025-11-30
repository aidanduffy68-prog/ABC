"""
Audit Logging Middleware
Provides comprehensive audit trail for security-relevant events

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict


class AuditEventType(Enum):
    """Types of audit events"""
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_DENIED = "authorization_denied"
    INTELLIGENCE_COMPILED = "intelligence_compiled"
    FEDERAL_AI_SCAN = "federal_ai_scan"
    ALERT_ACKNOWLEDGED = "alert_acknowledged"
    RECEIPT_VERIFIED = "receipt_verified"
    DATA_ACCESSED = "data_accessed"
    CONFIGURATION_CHANGED = "configuration_changed"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    ip_address: Optional[str]
    resource: Optional[str]
    action: str
    result: str  # success, failure, denied
    details: Dict[str, Any]
    severity: str = "info"  # info, warning, critical


class AuditLogger:
    """Centralized audit logging"""
    
    def __init__(self):
        self.enabled = os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true'
        self.log_file = os.getenv('AUDIT_LOG_FILE', 'audit.log')
    
    def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        resource: Optional[str] = None,
        action: str = "",
        result: str = "success",
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ) -> AuditEvent:
        """
        Log an audit event
        
        Args:
            event_type: Type of audit event
            user_id: User identifier (if authenticated)
            ip_address: Client IP address
            resource: Resource being accessed
            action: Action performed
            result: Result (success, failure, denied)
            details: Additional details
            severity: Event severity
            
        Returns:
            AuditEvent object
        """
        if not self.enabled:
            return None
        
        import hashlib
        import time
        
        # Generate event ID
        event_id = hashlib.sha256(
            f"{event_type.value}{user_id}{ip_address}{time.time()}".encode()
        ).hexdigest()[:16]
        
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            severity=severity
        )
        
        # Write to log file
        self._write_audit_log(event)
        
        return event
    
    def _write_audit_log(self, event: AuditEvent):
        """Write audit event to log file"""
        try:
            log_entry = {
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'user_id': event.user_id,
                'ip_address': event.ip_address,
                'resource': event.resource,
                'action': event.action,
                'result': event.result,
                'details': event.details,
                'severity': event.severity
            }
            
            # In production, use structured logging (JSON)
            log_line = json.dumps(log_entry, default=str)
            
            with open(self.log_file, 'a') as f:
                f.write(log_line + '\n')
        
        except Exception as e:
            # Don't fail if audit logging fails
            import logging
            logging.error(f"Failed to write audit log: {e}")


# Global audit logger instance
audit_logger = AuditLogger()


# Convenience functions
def log_authentication_success(user_id: str, ip_address: str):
    """Log successful authentication"""
    return audit_logger.log_event(
        event_type=AuditEventType.AUTHENTICATION_SUCCESS,
        user_id=user_id,
        ip_address=ip_address,
        action="login",
        result="success",
        severity="info"
    )


def log_authentication_failure(user_id: Optional[str], ip_address: str, reason: str):
    """Log failed authentication"""
    return audit_logger.log_event(
        event_type=AuditEventType.AUTHENTICATION_FAILURE,
        user_id=user_id,
        ip_address=ip_address,
        action="login",
        result="failure",
        details={"reason": reason},
        severity="warning"
    )


def log_authorization_denied(user_id: str, ip_address: str, resource: str, required_roles: list):
    """Log authorization denial"""
    return audit_logger.log_event(
        event_type=AuditEventType.AUTHORIZATION_DENIED,
        user_id=user_id,
        ip_address=ip_address,
        resource=resource,
        action="access",
        result="denied",
        details={"required_roles": required_roles},
        severity="warning"
    )


def log_intelligence_compiled(user_id: str, ip_address: str, actor_id: str, compilation_id: str):
    """Log intelligence compilation"""
    return audit_logger.log_event(
        event_type=AuditEventType.INTELLIGENCE_COMPILED,
        user_id=user_id,
        ip_address=ip_address,
        resource=f"actor:{actor_id}",
        action="compile_intelligence",
        result="success",
        details={"actor_id": actor_id, "compilation_id": compilation_id},
        severity="info"
    )


def log_federal_ai_scan(user_id: str, ip_address: str, agencies: list):
    """Log federal AI system scan"""
    return audit_logger.log_event(
        event_type=AuditEventType.FEDERAL_AI_SCAN,
        user_id=user_id,
        ip_address=ip_address,
        resource="federal_ai_systems",
        action="scan",
        result="success",
        details={"agencies": agencies},
        severity="info"
    )

