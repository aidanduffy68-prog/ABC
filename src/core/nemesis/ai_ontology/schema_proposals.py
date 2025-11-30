"""
Schema Proposals System - Human-Gated Schema Evolution
AI proposes schema changes, human approves (prevents auto-modification crashes)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ProposalStatus(Enum):
    """Status of schema proposal"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


@dataclass
class SchemaProposal:
    """Proposed schema change"""
    proposal_id: str
    proposal_type: str  # new_entity_type, new_relationship, updated_field, etc.
    description: str
    proposed_schema: Dict[str, Any]
    evidence: List[str]  # Why this change is needed
    confidence: float  # 0-1, AI confidence in proposal
    impact_analysis: Dict[str, Any]  # Which APIs/queries affected
    proposed_by: str = "ai_system"
    proposed_at: datetime = None
    status: ProposalStatus = ProposalStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    implemented_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.proposed_at is None:
            self.proposed_at = datetime.now()


class SchemaProposalSystem:
    """
    Human-gated schema evolution system
    AI proposes changes, human reviews and approves
    Prevents automatic schema modification that would crash downstream systems
    """
    
    def __init__(self):
        self.proposals: Dict[str, SchemaProposal] = {}
        self.implemented_proposals: Dict[str, SchemaProposal] = {}
    
    def propose_schema_change(
        self,
        proposal_type: str,
        description: str,
        proposed_schema: Dict[str, Any],
        evidence: List[str],
        confidence: float,
        impact_analysis: Optional[Dict[str, Any]] = None
    ) -> SchemaProposal:
        """
        Propose a schema change (AI-generated)
        
        Args:
            proposal_type: Type of change (new_entity_type, new_relationship, etc.)
            description: Human-readable description
            proposed_schema: Proposed schema structure
            evidence: Evidence supporting the change
            confidence: AI confidence (0-1)
            impact_analysis: Analysis of which systems would be affected
        
        Returns:
            SchemaProposal object
        """
        import uuid
        proposal_id = f"proposal_{uuid.uuid4().hex[:16]}"
        
        proposal = SchemaProposal(
            proposal_id=proposal_id,
            proposal_type=proposal_type,
            description=description,
            proposed_schema=proposed_schema,
            evidence=evidence,
            confidence=confidence,
            impact_analysis=impact_analysis or {},
            proposed_at=datetime.now()
        )
        
        self.proposals[proposal_id] = proposal
        return proposal
    
    def get_pending_proposals(self) -> List[SchemaProposal]:
        """Get all pending proposals awaiting review"""
        return [
            proposal for proposal in self.proposals.values()
            if proposal.status == ProposalStatus.PENDING
        ]
    
    def get_proposal(self, proposal_id: str) -> Optional[SchemaProposal]:
        """Get proposal by ID"""
        return self.proposals.get(proposal_id) or self.implemented_proposals.get(proposal_id)
    
    def approve_proposal(
        self,
        proposal_id: str,
        reviewer_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Approve schema proposal (human review)
        
        Args:
            proposal_id: Proposal ID to approve
            reviewer_id: ID of human reviewer
            notes: Optional review notes
        
        Returns:
            True if approved, False if not found
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        proposal.status = ProposalStatus.APPROVED
        proposal.reviewed_by = reviewer_id
        proposal.reviewed_at = datetime.now()
        proposal.review_notes = notes
        
        return True
    
    def reject_proposal(
        self,
        proposal_id: str,
        reviewer_id: str,
        reason: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Reject schema proposal
        
        Args:
            proposal_id: Proposal ID to reject
            reviewer_id: ID of human reviewer
            reason: Reason for rejection
            notes: Optional review notes
        
        Returns:
            True if rejected, False if not found
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        proposal.status = ProposalStatus.REJECTED
        proposal.reviewed_by = reviewer_id
        proposal.reviewed_at = datetime.now()
        proposal.rejection_reason = reason
        proposal.review_notes = notes
        
        return True
    
    def implement_proposal(self, proposal_id: str) -> bool:
        """
        Implement approved proposal (executes schema change)
        
        Args:
            proposal_id: Proposal ID to implement
        
        Returns:
            True if implemented, False if not found or not approved
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if proposal.status != ProposalStatus.APPROVED:
            return False  # Can only implement approved proposals
        
        # TODO: Execute actual schema migration
        # This would update the graph schema, API definitions, etc.
        
        proposal.status = ProposalStatus.IMPLEMENTED
        proposal.implemented_at = datetime.now()
        
        # Move to implemented proposals
        self.implemented_proposals[proposal_id] = proposal
        del self.proposals[proposal_id]
        
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """Get proposal statistics"""
        return {
            "pending": len([p for p in self.proposals.values() if p.status == ProposalStatus.PENDING]),
            "approved": len([p for p in self.proposals.values() if p.status == ProposalStatus.APPROVED]),
            "rejected": len([p for p in self.proposals.values() if p.status == ProposalStatus.REJECTED]),
            "implemented": len(self.implemented_proposals),
            "total": len(self.proposals) + len(self.implemented_proposals)
        }

