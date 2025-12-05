"""
Model Monitoring and Drift Detection API Endpoints
Provides access to drift detection status and alerts

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from src.core.nemesis.model_monitoring import get_drift_detector

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


@router.get("/drift/status", status_code=status.HTTP_200_OK)
async def get_drift_status() -> Dict[str, Any]:
    """
    Get current drift detection status
    
    Returns:
        Drift detection summary including baseline status, alerts, and metrics
    """
    detector = get_drift_detector()
    summary = detector.get_drift_summary()
    
    return {
        "status": "operational",
        "drift_detection": summary,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/drift/alerts", status_code=status.HTTP_200_OK)
async def get_drift_alerts() -> Dict[str, Any]:
    """
    Get recent drift detection alerts
    
    Returns:
        List of drift alerts with severity and details
    """
    detector = get_drift_detector()
    
    # Get recent alerts (last 7 days)
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=7)
    recent_alerts = [
        alert for alert in detector.alerts
        if alert.timestamp >= cutoff
    ]
    
    return {
        "total_alerts": len(detector.alerts),
        "recent_alerts": len(recent_alerts),
        "alerts": [
            {
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp.isoformat(),
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "deviation": alert.deviation
            }
            for alert in recent_alerts[-10:]  # Last 10 alerts
        ],
        "timestamp": datetime.now().isoformat()
    }

