"""
Foundry Chain Integration
ABC as Cryptographic Verification Layer for Palantir Foundry

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from .foundry_connector import FoundryConnector
from .compilation_validator import CompilationValidator
from .data_mapper import FoundryDataMapper
from .foundry_integration import FoundryIntegration

# Try to import AIP connector (may not be available if SDK not installed)
try:
    from .foundry_aip_connector import FoundryAIPConnector
    AIP_AVAILABLE = True
except ImportError:
    AIP_AVAILABLE = False
    FoundryAIPConnector = None

# Try to import workflow (includes scenario_forge support)
try:
    from .foundry_workflow import FoundryWorkflow
    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False
    FoundryWorkflow = None

# Build __all__ list
__all__ = [
    "FoundryConnector",
    "CompilationValidator",
    "FoundryDataMapper",
    "FoundryIntegration"
]

if AIP_AVAILABLE:
    __all__.append("FoundryAIPConnector")

if WORKFLOW_AVAILABLE:
    __all__.append("FoundryWorkflow")
