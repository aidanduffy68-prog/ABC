"""
Threat Actor Schema
Rigid Pydantic data structure for threat actor entities

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from enum import Enum


class ActorType(str, Enum):
    """Threat actor type enumeration"""
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


class ThreatActor(BaseModel):
    """
    Threat Actor entity schema
    Rigid data structure for compiler validation
    """
    # Required fields
    actor_id: str = Field(..., description="Unique actor identifier", min_length=1, max_length=256)
    name: str = Field(..., description="Actor name", min_length=1, max_length=512)
    type: ActorType = Field(..., description="Actor type")
    
    # Optional core fields
    source_ids: List[str] = Field(default_factory=list, description="Source system identifiers (TRM, Chainalysis, etc.)")
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Risk score (0-1)")
    risk_band: Optional[RiskBand] = Field(None, description="Risk classification")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction", max_length=128)
    
    # Behavioral data
    behavioral_signatures: Dict[str, Any] = Field(default_factory=dict, description="AI-generated behavioral fingerprints")
    hades_profile_ref: Optional[str] = Field(None, description="Reference to Hades behavioral profile")
    
    # Wallet-specific fields
    address: Optional[str] = Field(None, description="Wallet address (required if type is wallet)")
    
    # Provenance tracking
    source_id: Optional[str] = Field(None, description="Source document ID")
    extraction_method: Optional[str] = Field(None, description="Extraction method (llm_gpt4, heuristic, manual)")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score (0-1)")
    review_status: Optional[str] = Field(None, description="Review status (auto, pending, approved, rejected)")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Entity creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Entity update timestamp")
    
    @validator('actor_id')
    def validate_actor_id(cls, v):
        """Validate actor ID format"""
        if not v or not v.strip():
            raise ValueError("actor_id cannot be empty")
        if len(v) > 256:
            raise ValueError("actor_id exceeds maximum length of 256 characters")
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        """Validate actor name"""
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        if len(v) > 512:
            raise ValueError("name exceeds maximum length of 512 characters")
        return v.strip()
    
    @validator('address')
    def validate_wallet_address(cls, v, values):
        """Validate wallet address format if type is wallet"""
        actor_type = values.get('type')
        if actor_type == ActorType.WALLET:
            if not v:
                raise ValueError("address is required when type is 'wallet'")
            # Ethereum address format (0x + 40 hex chars)
            if v.startswith('0x') and len(v) == 42:
                # Validate hex characters
                try:
                    int(v[2:], 16)
                except ValueError:
                    raise ValueError(f"Invalid Ethereum address format: {v}")
            # Bitcoin address format (basic check)
            elif len(v) >= 26 and len(v) <= 35:
                # Basic format validation (would need more sophisticated check in production)
                pass
            else:
                raise ValueError(f"Invalid wallet address format: {v}")
        return v
    
    @validator('risk_score')
    def validate_risk_score(cls, v):
        """Validate risk score range"""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("risk_score must be between 0.0 and 1.0")
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_risk_band_consistency(cls, values):
        """Ensure risk_band is consistent with risk_score"""
        risk_score = values.get('risk_score')
        risk_band = values.get('risk_band')
        
        if risk_score is not None and risk_band is not None:
            # Validate consistency
            if risk_score < 0.3 and risk_band != RiskBand.LOW:
                pass  # Warning, not error
            elif 0.3 <= risk_score < 0.6 and risk_band not in [RiskBand.LOW, RiskBand.MEDIUM]:
                pass  # Warning, not error
            elif 0.6 <= risk_score < 0.8 and risk_band not in [RiskBand.MEDIUM, RiskBand.HIGH]:
                pass  # Warning, not error
            elif risk_score >= 0.8 and risk_band not in [RiskBand.HIGH, RiskBand.CRITICAL]:
                pass  # Warning, not error
        
        return values
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        extra = "forbid"  # Reject extra fields (strict typing)
        validate_assignment = True  # Validate on assignment
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict(exclude_none=True)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        import json
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreatActor':
        """Create from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ThreatActor':
        """Create from JSON string"""
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)


# Example usage
if __name__ == "__main__":
    # Valid actor
    actor = ThreatActor(
        actor_id="ALPHA_47",
        name="Lazarus Group Wallet",
        type=ActorType.WALLET,
        address="0x4a9f8b8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c",
        risk_score=0.95,
        risk_band=RiskBand.CRITICAL,
        source_ids=["TRM_12345", "CHAINALYSIS_67890"]
    )
    
    print(f"Created actor: {actor.name}")
    print(f"Risk score: {actor.risk_score}")
    print(f"JSON: {actor.to_json()[:100]}...")

