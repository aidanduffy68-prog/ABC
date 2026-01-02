"""
Foundry Chain Integration
ABC as Cryptographic Verification Layer for Palantir Foundry

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from .foundry_connector import FoundryConnector
from .compilation_validator import CompilationValidator
from .data_mapper import FoundryDataMapper
from .foundry_integration import FoundryIntegration

# Try to import AIP connector (may not be available if SDK not installed)
try:
    from .foundry_aip_connector import FoundryAIPConnector
    __all__ = [
        "FoundryConnector",
        "FoundryAIPConnector",
        "CompilationValidator",
        "FoundryDataMapper",
        "FoundryIntegration"
    ]
except ImportError:
    __all__ = [
        "FoundryConnector",
        "CompilationValidator",
        "FoundryDataMapper",
        "FoundryIntegration"
    ]

