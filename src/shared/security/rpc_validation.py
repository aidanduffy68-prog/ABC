"""
RPC URL Validation
Validates blockchain RPC endpoints to prevent connection to malicious servers

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Optional, List
from urllib.parse import urlparse
import re


# Whitelist of allowed RPC domains
ALLOWED_RPC_DOMAINS = [
    # Ethereum Mainnet
    "mainnet.infura.io",
    "mainnet.alchemyapi.io",
    "eth-mainnet.g.alchemy.com",
    "eth-mainnet.public.blastapi.io",
    "ethereum.publicnode.com",
    
    # Bitcoin Mainnet
    "blockstream.info",
    "mempool.space",
    "blockchain.info",
    
    # Polygon
    "polygon-mainnet.infura.io",
    "polygon-mainnet.g.alchemy.com",
    
    # Arbitrum
    "arbitrum-mainnet.infura.io",
    "arb-mainnet.g.alchemy.com",
    
    # Base
    "base-mainnet.g.alchemy.com",
    "base-mainnet.infura.io",
    
    # Optimism
    "opt-mainnet.g.alchemy.com",
    "optimism-mainnet.infura.io",
    
    # Local development
    "localhost",
    "127.0.0.1",
]

# Allowed RPC URL patterns (for flexibility)
ALLOWED_RPC_PATTERNS = [
    r"^https?://.*\.infura\.io/.*$",
    r"^https?://.*\.alchemyapi\.io/.*$",
    r"^https?://.*\.alchemy\.com/.*$",
    r"^https?://.*\.blastapi\.io/.*$",
    r"^https?://.*\.publicnode\.com/.*$",
    r"^https?://blockstream\.info/.*$",
    r"^https?://mempool\.space/.*$",
    r"^https?://blockchain\.info/.*$",
    r"^https?://localhost.*$",
    r"^https?://127\.0\.0\.1.*$",
]


def validate_rpc_url(url: str, allow_local: bool = True) -> bool:
    """
    Validate RPC URL against whitelist
    
    Checks if the RPC URL is from an allowed domain or matches
    an allowed pattern. Prevents connection to malicious RPC endpoints.
    
    Args:
        url: RPC URL to validate
        allow_local: Whether to allow localhost URLs (default: True)
        
    Returns:
        True if URL is allowed, False otherwise
        
    Example:
        >>> validate_rpc_url("https://mainnet.infura.io/v3/abc123")
        True
        >>> validate_rpc_url("http://malicious-site.com:8545")
        False
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.split(':')[0]  # Remove port if present
        
        # Check domain whitelist
        if domain in ALLOWED_RPC_DOMAINS:
            # Additional check: don't allow localhost in production
            if not allow_local and domain in ["localhost", "127.0.0.1"]:
                return False
            return True
        
        # Check pattern whitelist
        for pattern in ALLOWED_RPC_PATTERNS:
            if re.match(pattern, url):
                return True
        
        return False
        
    except Exception:
        # Invalid URL format
        return False


def validate_rpc_url_strict(url: str) -> bool:
    """
    Strict RPC URL validation (production mode)
    
    Only allows HTTPS URLs from whitelisted domains.
    Localhost is not allowed.
    
    Args:
        url: RPC URL to validate
        
    Returns:
        True if URL is allowed in production
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        
        # Must be HTTPS in production
        if parsed.scheme != "https":
            return False
        
        # Must be from whitelisted domain
        domain = parsed.netloc.split(':')[0]
        if domain not in ALLOWED_RPC_DOMAINS:
            return False
        
        # No localhost in production
        if domain in ["localhost", "127.0.0.1"]:
            return False
        
        return True
        
    except Exception:
        return False


def get_allowed_rpc_domains() -> List[str]:
    """
    Get list of allowed RPC domains
    
    Returns:
        List of allowed domain names
    """
    return ALLOWED_RPC_DOMAINS.copy()


def add_allowed_rpc_domain(domain: str) -> bool:
    """
    Add a domain to the RPC whitelist (for custom deployments)
    
    Args:
        domain: Domain name to add (e.g., "custom-rpc.example.com")
        
    Returns:
        True if domain was added, False if invalid
    """
    if not domain or not isinstance(domain, str):
        return False
    
    # Basic validation
    if not re.match(r"^[a-zA-Z0-9.-]+$", domain):
        return False
    
    if domain not in ALLOWED_RPC_DOMAINS:
        ALLOWED_RPC_DOMAINS.append(domain)
    
    return True

