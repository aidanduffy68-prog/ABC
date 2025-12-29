"""
Foundry API Connector
Connects ABC to Palantir Foundry output

Copyright (c) 2025 GH Systems. All rights reserved.
"""

import os
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FoundryConnector:
    """
    Connects to Palantir Foundry API to retrieve compilation outputs.
    
    Handles authentication, API calls, and data retrieval from Foundry.
    """
    
    def __init__(
        self,
        foundry_api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize Foundry connector.
        
        Args:
            foundry_api_url: Foundry API base URL (defaults to env var)
            api_key: Foundry API key (defaults to env var)
            timeout: Request timeout in seconds
        """
        self.api_url = foundry_api_url or os.getenv("FOUNDRY_API_URL", "https://foundry.palantir.com/api/v1")
        self.api_key = api_key or os.getenv("FOUNDRY_API_KEY")
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning("Foundry API key not provided. Some operations may fail.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for Foundry API."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def get_compilation(
        self,
        compilation_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve a Foundry compilation by ID.
        
        Args:
            compilation_id: Foundry compilation identifier
            
        Returns:
            Foundry compilation data
            
        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.api_url}/compilations/{compilation_id}"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            compilation = response.json()
            logger.info(f"Retrieved Foundry compilation: {compilation_id}")
            
            return compilation
            
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve Foundry compilation {compilation_id}: {e}")
            raise
    
    def list_recent_compilations(
        self,
        limit: int = 100,
        classification: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        List recent Foundry compilations.
        
        Args:
            limit: Maximum number of compilations to return
            classification: Filter by classification (e.g., "SBU", "UNCLASSIFIED")
            since: Only return compilations after this timestamp
            
        Returns:
            List of compilation summaries
        """
        url = f"{self.api_url}/compilations"
        params = {"limit": limit}
        
        if classification:
            params["classification"] = classification
        
        if since:
            params["since"] = since.isoformat()
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            compilations = response.json().get("compilations", [])
            logger.info(f"Retrieved {len(compilations)} Foundry compilations")
            
            return compilations
            
        except requests.RequestException as e:
            logger.error(f"Failed to list Foundry compilations: {e}")
            return []
    
    def verify_compilation_exists(
        self,
        compilation_id: str
    ) -> bool:
        """
        Verify that a compilation exists in Foundry.
        
        Args:
            compilation_id: Foundry compilation identifier
            
        Returns:
            True if compilation exists, False otherwise
        """
        try:
            self.get_compilation(compilation_id)
            return True
        except requests.RequestException:
            return False
    
    def get_compilation_metadata(
        self,
        compilation_id: str
    ) -> Dict[str, Any]:
        """
        Get metadata for a compilation (without full data).
        
        Args:
            compilation_id: Foundry compilation identifier
            
        Returns:
            Compilation metadata
        """
        url = f"{self.api_url}/compilations/{compilation_id}/metadata"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to get compilation metadata: {e}")
            raise

