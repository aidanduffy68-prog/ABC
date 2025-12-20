"""
Palantir Foundry Data Export (Legacy)
This module is deprecated. Use src.integrations.foundry instead.

Copyright (c) 2025 GH Systems. All rights reserved.
"""

# Re-export from integrations for backward compatibility
from src.integrations.foundry.connector import FoundryDataExportConnector
from src.integrations.foundry.export import FoundryDataExporter
from src.integrations.foundry import FoundryConnector  # Alias defined in __init__.py

__all__ = ['FoundryDataExportConnector', 'FoundryConnector', 'FoundryDataExporter']

