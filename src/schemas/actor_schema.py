"""
Strict Type Definitions for Threat Actors
Pydantic models for compiler validation

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ActorType(str, Enum):
    """Actor type enumeration"""
    WALLET = "wallet"
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    NATION_STATE = "nation_state"
    SERVICE_PROVIDER = "service_provider"


class RiskBand(str, Enum):
    """Risk band classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Actor(BaseModel):
    """
    Threat Actor entity schema
    Strict typing for compiler validation
    """
    actor_id: str = Field(..., description="Unique actor identifier")
    name: str = Field(..., description="Actor name")
    type: ActorType = Field(..., description="Actor type")
    
    # Optional fields
    source_ids: List[str] = Field(default_factory=list, description="Source system identifiers")
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Risk score (0-1)")
    risk_band: Optional[RiskBand] = Field(None, description="Risk classification")
    behavioral_signatures: Dict[str, Any] = Field(default_factory=dict, description="Behavioral fingerprints")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction")
    hades_profile_ref: Optional[str] = Field(None, description="Reference to Hades profile")
    address: Optional[str] = Field(None, description="Wallet address (if type is wallet)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")
    
    # Provenance tracking
    source_id: Optional[str] = Field(None, description="Source document ID")
    extraction_method: Optional[str] = Field(None, description="Extraction method")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    review_status: Optional[str] = Field(None, description="Review status")
    
    @validator('actor_id')
    def validate_actor_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("actor_id cannot be empty")
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("name cannot be empty")
        return v.strip()
    
    @validator('address')
    def validate_wallet_address(cls, v, values):
        if v and values.get('type') == ActorType.WALLET:
            # Basic format validation
            if not (v.startswith('0x') and len(v) == 42) and not (len(v) >= 26 and len(v) <= 35):
                raise ValueError(f"Invalid wallet address format: {v}")
        return v
    
    class Config:
        use_enum_values = True
        extra = "forbid"  # Reject extra fields


class Event(BaseModel):
    """
    Event entity schema
    """
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Event type")
    timestamp: datetime = Field(..., description="Event timestamp")
    
    # Optional fields
    chain: Optional[str] = Field(None, description="Blockchain network")
    tx_hash: Optional[str] = Field(None, description="Transaction hash")
    value_usd: Optional[float] = Field(None, description="Value in USD")
    participants: List[str] = Field(default_factory=list, description="Actor IDs involved")
    nemesis_assessment_ref: Optional[str] = Field(None, description="Reference to Nemesis assessment")
    evidence_objects: List[str] = Field(default_factory=list, description="Linked evidence IDs")
    
    class Config:
        extra = "forbid"


class Pattern(BaseModel):
    """
    Pattern entity schema
    """
    pattern_id: str = Field(..., description="Unique pattern identifier")
    category: str = Field(..., description="Pattern category")
    description: str = Field(..., description="Human-readable description")
    
    # Optional fields
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence IDs")
    echo_cluster_ref: Optional[str] = Field(None, description="Reference to Echo cluster")
    detection_rules: List[str] = Field(default_factory=list, description="Detection rules")
    version: Optional[str] = Field(None, description="Pattern version")
    
    class Config:
        extra = "forbid"


class TargetingPackage(BaseModel):
    """
    Targeting Package schema
    """
    package_id: str = Field(..., description="Unique package identifier")
    package_type: str = Field(..., description="Package type")
    status: str = Field(..., description="Package status (draft/active/executed)")
    
    # Optional fields
    generated_by_nemesis_ref: Optional[str] = Field(None, description="Nemesis generation reference")
    target_actors: List[str] = Field(default_factory=list, description="Target actor IDs")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended countermeasures")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence")
    evidence_objects: List[str] = Field(default_factory=list, description="Supporting evidence IDs")
    
    class Config:
        extra = "forbid"

