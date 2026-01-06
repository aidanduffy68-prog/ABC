"""
Model Drift Detection and Monitoring
Monitors AI model performance and detects drift

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics for drift detection"""
    timestamp: datetime
    confidence_score: float
    compilation_time_ms: float
    behavioral_signature_confidence: Optional[float] = None
    coordination_network_score: Optional[float] = None
    threat_forecast_risk: Optional[float] = None


@dataclass
class DriftAlert:
    """Drift detection alert"""
    alert_id: str
    timestamp: datetime
    alert_type: str  # 'confidence_drift', 'performance_drift', 'behavioral_drift'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    metrics: Dict
    baseline: Dict
    deviation: float


class ModelDriftDetector:
    """
    Detects model drift by monitoring performance metrics over time
    
    Drift types:
    - Confidence drift: Confidence scores degrading over time
    - Performance drift: Compilation times increasing
    - Behavioral drift: Behavioral signature patterns changing
    - Network drift: Coordination network detection changing
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.1,  # 10% drop triggers alert
        performance_threshold: float = 1.5,  # 50% increase triggers alert
        window_size: int = 100,  # Number of recent compilations to track
        min_samples: int = 20  # Minimum samples before detecting drift
    ):
        self.confidence_threshold = confidence_threshold
        self.performance_threshold = performance_threshold
        self.window_size = window_size
        self.min_samples = min_samples
        
        # Performance history
        self.metrics_history: deque = deque(maxlen=window_size)
        
        # Baseline metrics (calculated from first min_samples)
        self.baseline: Optional[Dict[str, float]] = None
        
        # Alert history
        self.alerts: List[DriftAlert] = []
    
    def record_metrics(self, metrics: ModelPerformanceMetrics) -> List[DriftAlert]:
        """
        Record new metrics and check for drift
        
        Returns:
            List of drift alerts (empty if no drift detected)
        """
        self.metrics_history.append(metrics)
        
        # Update baseline if we have enough samples
        if len(self.metrics_history) >= self.min_samples and self.baseline is None:
            self._calculate_baseline()
        
        # Check for drift if baseline exists
        alerts = []
        if self.baseline is not None:
            alerts = self._detect_drift(metrics)
            self.alerts.extend(alerts)
        
        return alerts
    
    def _calculate_baseline(self):
        """Calculate baseline metrics from history"""
        if len(self.metrics_history) < self.min_samples:
            return
        
        recent = list(self.metrics_history)[-self.min_samples:]
        
        self.baseline = {
            'confidence_mean': statistics.mean([m.confidence_score for m in recent]),
            'confidence_std': statistics.stdev([m.confidence_score for m in recent]) if len(recent) > 1 else 0.0,
            'performance_mean': statistics.mean([m.compilation_time_ms for m in recent]),
            'performance_std': statistics.stdev([m.compilation_time_ms for m in recent]) if len(recent) > 1 else 0.0,
            'behavioral_mean': statistics.mean([m.behavioral_signature_confidence for m in recent if m.behavioral_signature_confidence is not None]) if any(m.behavioral_signature_confidence for m in recent) else None,
            'network_mean': statistics.mean([m.coordination_network_score for m in recent if m.coordination_network_score is not None]) if any(m.coordination_network_score for m in recent) else None,
        }
        
        logger.info(f"Baseline calculated from {len(recent)} samples")
    
    def _detect_drift(self, current: ModelPerformanceMetrics) -> List[DriftAlert]:
        """Detect drift in current metrics compared to baseline"""
        alerts = []
        
        # Confidence drift detection
        if self.baseline['confidence_mean'] > 0:
            confidence_drop = (self.baseline['confidence_mean'] - current.confidence_score) / self.baseline['confidence_mean']
            
            if confidence_drop >= self.confidence_threshold:
                severity = self._calculate_severity(confidence_drop, [0.1, 0.2, 0.3])
                alerts.append(DriftAlert(
                    alert_id=f"drift_conf_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    alert_type='confidence_drift',
                    severity=severity,
                    message=f"Confidence score dropped by {confidence_drop:.1%} from baseline",
                    metrics={'confidence_score': current.confidence_score},
                    baseline={'confidence_mean': self.baseline['confidence_mean']},
                    deviation=confidence_drop
                ))
        
        # Performance drift detection
        if self.baseline['performance_mean'] > 0:
            performance_increase = (current.compilation_time_ms - self.baseline['performance_mean']) / self.baseline['performance_mean']
            
            if performance_increase >= (self.performance_threshold - 1.0):
                severity = self._calculate_severity(performance_increase, [0.5, 1.0, 2.0])
                alerts.append(DriftAlert(
                    alert_id=f"drift_perf_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    alert_type='performance_drift',
                    severity=severity,
                    message=f"Compilation time increased by {performance_increase:.1%} from baseline",
                    metrics={'compilation_time_ms': current.compilation_time_ms},
                    baseline={'performance_mean': self.baseline['performance_mean']},
                    deviation=performance_increase
                ))
        
        # Behavioral drift detection
        if (current.behavioral_signature_confidence is not None and 
            self.baseline['behavioral_mean'] is not None and
            self.baseline['behavioral_mean'] > 0):
            
            behavioral_drop = (self.baseline['behavioral_mean'] - current.behavioral_signature_confidence) / self.baseline['behavioral_mean']
            
            if abs(behavioral_drop) >= self.confidence_threshold:
                severity = self._calculate_severity(abs(behavioral_drop), [0.1, 0.2, 0.3])
                alerts.append(DriftAlert(
                    alert_id=f"drift_behav_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    alert_type='behavioral_drift',
                    severity=severity,
                    message=f"Behavioral signature confidence changed by {behavioral_drop:.1%} from baseline",
                    metrics={'behavioral_signature_confidence': current.behavioral_signature_confidence},
                    baseline={'behavioral_mean': self.baseline['behavioral_mean']},
                    deviation=abs(behavioral_drop)
                ))
        
        return alerts
    
    def _calculate_severity(self, deviation: float, thresholds: List[float]) -> str:
        """Calculate alert severity based on deviation"""
        if deviation >= thresholds[2] if len(thresholds) > 2 else 0.3:
            return 'critical'
        elif deviation >= thresholds[1] if len(thresholds) > 1 else 0.2:
            return 'high'
        elif deviation >= thresholds[0]:
            return 'medium'
        else:
            return 'low'
    
    def get_drift_summary(self) -> Dict:
        """Get summary of drift detection status"""
        return {
            'baseline_established': self.baseline is not None,
            'samples_collected': len(self.metrics_history),
            'total_alerts': len(self.alerts),
            'recent_alerts': len([a for a in self.alerts if (datetime.now() - a.timestamp).days < 7]),
            'baseline_metrics': self.baseline,
            'latest_metrics': {
                'confidence_score': self.metrics_history[-1].confidence_score if self.metrics_history else None,
                'compilation_time_ms': self.metrics_history[-1].compilation_time_ms if self.metrics_history else None,
            } if self.metrics_history else None
        }


# Global drift detector instance
_drift_detector: Optional[ModelDriftDetector] = None


def get_drift_detector() -> ModelDriftDetector:
    """Get or create global drift detector instance"""
    global _drift_detector
    if _drift_detector is None:
        _drift_detector = ModelDriftDetector()
    return _drift_detector

