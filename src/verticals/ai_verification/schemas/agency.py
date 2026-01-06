"""
Agency Assessment Schema
Pydantic models for agency AI assessment submissions and consensus calculations

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ClassificationLevel(str, Enum):
    """Classification level enumeration"""
    UNCLASSIFIED = "UNCLASSIFIED"
    SBU = "SBU"
    SECRET = "SECRET"
    TOP_SECRET = "TOP_SECRET"


class AgencyAssessment(BaseModel):
    """Agency AI assessment submission"""
    
    agency: str = Field(..., description="Agency identifier (CIA, DHS, Treasury, etc.)")
    foundry_compilation_id: str = Field(..., description="Foundry compilation ID")
    abc_receipt_hash: str = Field(..., description="ABC blockchain receipt hash")
    assessment_hash: str = Field(..., description="SHA256 hash of agency's assessment")
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence 0-100")
    classification: ClassificationLevel = Field(..., description="Classification level")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    submitted_at: datetime = Field(default_factory=datetime.now, description="Submission timestamp")
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        """Validate confidence score is in range 0-100"""
        if not 0 <= v <= 100:
            raise ValueError('Confidence must be 0-100')
        return v
    
    @validator('agency')
    def validate_agency(cls, v):
        """Validate agency identifier is not empty"""
        if not v or not v.strip():
            raise ValueError("agency cannot be empty")
        return v.strip().upper()
    
    @validator('foundry_compilation_id')
    def validate_foundry_compilation_id(cls, v):
        """Validate Foundry compilation ID is not empty"""
        if not v or not v.strip():
            raise ValueError("foundry_compilation_id cannot be empty")
        return v.strip()
    
    @validator('abc_receipt_hash')
    def validate_abc_receipt_hash(cls, v):
        """Validate ABC receipt hash format"""
        if not v or not v.strip():
            raise ValueError("abc_receipt_hash cannot be empty")
        # Basic hash format validation (should start with hash prefix or be hex)
        v = v.strip()
        if not (v.startswith('sha256:') or all(c in '0123456789abcdefABCDEF' for c in v)):
            raise ValueError("abc_receipt_hash must be a valid hash format")
        return v
    
    @validator('assessment_hash')
    def validate_assessment_hash(cls, v):
        """Validate assessment hash format"""
        if not v or not v.strip():
            raise ValueError("assessment_hash cannot be empty")
        # Basic hash format validation
        v = v.strip()
        if not (v.startswith('sha256:') or all(c in '0123456789abcdefABCDEF' for c in v)):
            raise ValueError("assessment_hash must be a valid SHA256 hash format")
        return v
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'AgencyAssessment':
        """Create from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgencyAssessment':
        """Create from JSON string"""
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)


class ConsensusResult(BaseModel):
    """Multi-agency consensus calculation"""
    
    foundry_compilation_id: str = Field(..., description="Foundry compilation ID")
    abc_baseline_confidence: float = Field(..., ge=0, le=100, description="ABC baseline confidence 0-100")
    agency_assessments: List[Dict[str, Any]] = Field(..., description="List of agency assessment data")
    consensus_metrics: Dict[str, Any] = Field(..., description="Consensus metrics (mean, std_dev, outliers)")
    recommendation: str = Field(..., description="Consensus recommendation")
    verified: bool = Field(..., description="Whether consensus is verified")
    
    @validator('foundry_compilation_id')
    def validate_foundry_compilation_id(cls, v):
        """Validate Foundry compilation ID is not empty"""
        if not v or not v.strip():
            raise ValueError("foundry_compilation_id cannot be empty")
        return v.strip()
    
    @validator('abc_baseline_confidence')
    def validate_abc_baseline_confidence(cls, v):
        """Validate ABC baseline confidence is in range 0-100"""
        if not 0 <= v <= 100:
            raise ValueError('abc_baseline_confidence must be 0-100')
        return v
    
    @validator('agency_assessments')
    def validate_agency_assessments(cls, v):
        """Validate agency assessments list is not empty"""
        if not v or len(v) == 0:
            raise ValueError("agency_assessments cannot be empty")
        return v
    
    @validator('consensus_metrics')
    def validate_consensus_metrics(cls, v):
        """Validate consensus metrics contains expected fields"""
        if not v:
            raise ValueError("consensus_metrics cannot be empty")
        # Optionally validate structure (mean, std_dev, outliers)
        expected_keys = ['mean', 'std_dev', 'outliers']
        if not any(key in v for key in expected_keys):
            raise ValueError(f"consensus_metrics should contain at least one of: {expected_keys}")
        return v
    
    @validator('recommendation')
    def validate_recommendation(cls, v):
        """Validate recommendation is not empty"""
        if not v or not v.strip():
            raise ValueError("recommendation cannot be empty")
        return v.strip()
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsensusResult':
        """Create from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ConsensusResult':
        """Create from JSON string"""
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)

