"""
Signal Intake Module
Automated monitoring and intelligence feed generation from federal AI systems
"""

from .federal_ai_monitor import (
    FederalAIMonitor,
    FederalAISystem,
    VulnerabilityFinding,
    monitor_federal_ai_systems
)

__all__ = [
    "FederalAIMonitor",
    "FederalAISystem",
    "VulnerabilityFinding",
    "monitor_federal_ai_systems"
]

