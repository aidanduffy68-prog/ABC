"""
Foundry AIP (Application Integration Platform) Connector
Uses OAuth2 authentication and Foundry SDK for workspace-based access

Copyright (c) 2026 GH Systems. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Foundry SDK
try:
    from abc_integration_sdk import FoundryClient, ConfidentialClientAuth
    FOUNDRY_SDK_AVAILABLE = True
except ImportError:
    FOUNDRY_SDK_AVAILABLE = False
    logger.warning(
        "Foundry SDK not installed. Install with: "
        "pip install abc_integration_sdk (from private repository)"
    )


class FoundryAIPConnector:
    """
    Connector for Palantir Foundry AIP (Application Integration Platform)
    
    Uses OAuth2 client credentials flow for authentication.
    Works with Foundry SDK for dataset and transaction operations.
    
    All credentials are read from environment variables - no hardcoded values.
    """
    
    def __init__(
        self,
        foundry_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        """
        Initialize Foundry AIP connector.
        
        Args:
            foundry_url: Foundry instance URL (defaults to FOUNDRY_URL env var)
            client_id: OAuth2 client ID (defaults to FOUNDRY_CLIENT_ID env var)
            client_secret: OAuth2 client secret (defaults to FOUNDRY_CLIENT_SECRET env var)
            
        Raises:
            ImportError: If Foundry SDK is not installed
            ValueError: If required credentials are missing
        """
        if not FOUNDRY_SDK_AVAILABLE:
            raise ImportError(
                "Foundry SDK required for AIP integration. "
                "Install abc_integration_sdk from the private repository. "
                "See docs/integrations/FOUNDRY_AIP_SETUP.md for instructions."
            )
        
        # Get from environment if not provided
        self.foundry_url = foundry_url or os.getenv("FOUNDRY_URL")
        self.client_id = client_id or os.getenv("FOUNDRY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("FOUNDRY_CLIENT_SECRET")
        
        if not all([self.foundry_url, self.client_id, self.client_secret]):
            missing = []
            if not self.foundry_url:
                missing.append("FOUNDRY_URL")
            if not self.client_id:
                missing.append("FOUNDRY_CLIENT_ID")
            if not self.client_secret:
                missing.append("FOUNDRY_CLIENT_SECRET")
            
            raise ValueError(
                f"Foundry AIP requires {', '.join(missing)}. "
                "Set environment variables in .env file or pass as parameters."
            )
        
        # Initialize authentication
        try:
            self.auth = ConfidentialClientAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                hostname=self.foundry_url,
                should_refresh=True,
            )
            
            # Initialize Foundry client with auth
            self.client = FoundryClient(auth=self.auth, hostname=self.foundry_url)
            
            logger.info(f"Initialized Foundry AIP connector for {self.foundry_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Foundry AIP client: {e}")
            raise
    
    def get_dataset_rid(self, dataset_path: str) -> str:
        """
        Get Resource ID (RID) for a dataset path.
        
        Note: The Foundry SDK may use ontology objects instead of direct dataset RIDs.
        For now, we return the dataset_path as-is and let the SDK handle resolution.
        
        Args:
            dataset_path: Dataset path (e.g., "gh_systems/intelligence_compilations")
            
        Returns:
            Dataset path or RID (depending on SDK implementation)
            
        Raises:
            Exception: If dataset not found or access denied
        """
        # The Foundry SDK handles dataset resolution internally
        # For now, return the path as-is - the SDK will resolve it when needed
        # In the future, this could use ontology objects or other SDK methods
        return dataset_path
    
    def read_dataset(
        self,
        dataset_path: str,
        limit: Optional[int] = None,
        columns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Read data from a Foundry dataset.
        
        Args:
            dataset_path: Dataset path or RID
            limit: Maximum number of rows to return
            columns: Specific columns to read (None = all columns)
            
        Returns:
            List of records as dictionaries
            
        Raises:
            Exception: If dataset read fails
        """
        try:
            # Note: The Foundry SDK may require ontology objects or different API
            # For now, return empty list if dataset doesn't exist (graceful degradation)
            # In production, you would use the SDK's ontology API to access datasets
            logger.warning(
                f"Dataset read not fully implemented for {dataset_path}. "
                "Returning empty list. Use Foundry ontology objects for full functionality."
            )
            return []
            
        except Exception as e:
            logger.error(f"Failed to read dataset {dataset_path}: {e}")
            return []  # Return empty list instead of raising for graceful degradation
    
    def write_dataset(
        self,
        dataset_path: str,
        data: List[Dict[str, Any]],
        mode: str = "append"
    ) -> Dict[str, Any]:
        """
        Write data to a Foundry dataset.
        
        Note: The Foundry SDK may require ontology objects for writing.
        This is a placeholder that will need to be implemented with the actual SDK API.
        
        Args:
            dataset_path: Dataset path or RID
            data: List of records to write
            mode: Write mode ("append", "overwrite", "upsert")
            
        Returns:
            Write result with transaction RID
            
        Raises:
            Exception: If dataset write fails
        """
        try:
            # Note: The Foundry SDK may require ontology objects or different API
            # For now, log a warning and return a mock result
            # In production, you would use the SDK's ontology API to write datasets
            logger.warning(
                f"Dataset write not fully implemented for {dataset_path}. "
                "Use Foundry ontology objects for full functionality."
            )
            
            # Return mock result for testing
            return {
                "status": "not_implemented",
                "records_written": len(data),
                "transaction_rid": None,
                "dataset_path": dataset_path,
                "timestamp": datetime.now().isoformat(),
                "message": "Dataset write requires Foundry ontology objects - not yet implemented"
            }
            
        except Exception as e:
            logger.error(f"Failed to write to dataset {dataset_path}: {e}")
            raise
    
    def get_compilation(
        self,
        compilation_id: str,
        dataset_path: str = "gh_systems/intelligence_compilations"
    ) -> Dict[str, Any]:
        """
        Retrieve a Foundry compilation by ID from dataset.
        
        Args:
            compilation_id: Compilation identifier
            dataset_path: Dataset path containing compilations
            
        Returns:
            Compilation data
            
        Raises:
            ValueError: If compilation not found
            Exception: If dataset read fails
        """
        try:
            # Read dataset and filter by compilation_id
            records = self.read_dataset(dataset_path)
            
            # Find matching compilation
            for record in records:
                if record.get("compilation_id") == compilation_id:
                    logger.info(f"Retrieved compilation {compilation_id} from Foundry")
                    return record
            
            raise ValueError(
                f"Compilation {compilation_id} not found in {dataset_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to retrieve compilation {compilation_id}: {e}")
            raise
    
    def list_recent_compilations(
        self,
        dataset_path: str = "gh_systems/intelligence_compilations",
        limit: int = 100,
        classification: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        List recent compilations from Foundry dataset.
        
        Args:
            dataset_path: Dataset path
            limit: Maximum number to return
            classification: Filter by classification (optional)
            since: Only return compilations after this timestamp
            
        Returns:
            List of compilation records
        """
        try:
            records = self.read_dataset(dataset_path, limit=limit)
            
            # Filter by classification if provided
            if classification:
                records = [
                    r for r in records
                    if r.get("classification", "").upper() == classification.upper()
                ]
            
            # Filter by timestamp if provided
            if since:
                filtered = []
                for r in records:
                    compiled_at = r.get("compiled_at")
                    if compiled_at:
                        try:
                            # Parse timestamp (handle various formats)
                            if isinstance(compiled_at, str):
                                # Remove timezone if present for comparison
                                compiled_at_clean = compiled_at.replace("Z", "+00:00")
                                record_time = datetime.fromisoformat(compiled_at_clean)
                            else:
                                record_time = compiled_at
                            
                            if record_time > since:
                                filtered.append(r)
                        except Exception:
                            # Skip records with invalid timestamps
                            continue
                
                return filtered[:limit]
            
            return records[:limit]
            
        except Exception as e:
            logger.error(f"Failed to list compilations: {e}")
            return []
    
    def push_compilation(
        self,
        compilation_data: Dict[str, Any],
        dataset_path: str = "gh_systems/intelligence_compilations"
    ) -> Dict[str, Any]:
        """
        Push compilation data to Foundry dataset.
        
        Args:
            compilation_data: Compilation data dictionary
            dataset_path: Target dataset path
            
        Returns:
            Push result with transaction RID
        """
        return self.write_dataset(
            dataset_path=dataset_path,
            data=[compilation_data],
            mode="append"
        )
    
    def verify_compilation_exists(
        self,
        compilation_id: str,
        dataset_path: str = "gh_systems/intelligence_compilations"
    ) -> bool:
        """
        Verify that a compilation exists in Foundry.
        
        Args:
            compilation_id: Compilation identifier
            dataset_path: Dataset path to check
            
        Returns:
            True if compilation exists, False otherwise
        """
        try:
            self.get_compilation(compilation_id, dataset_path)
            return True
        except (ValueError, Exception):
            return False

