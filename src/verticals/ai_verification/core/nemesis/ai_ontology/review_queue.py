"""
Human-in-the-Loop Review Queue
Entities with confidence 0.80-0.94 require human approval before graph insertion
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ReviewStatus(Enum):
    """Review status for entities"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ReviewItem:
    """Item in the review queue"""
    entity_id: str
    entity_type: str
    entity_data: Dict[str, Any]
    source_id: str
    extraction_method: str
    confidence: float
    submitted_at: datetime
    status: ReviewStatus = ReviewStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class ReviewQueue:
    """
    Human-in-the-loop review system for medium-confidence entities
    Entities with confidence 0.80-0.94 require approval before graph insertion
    """
    
    def __init__(self):
        self.queue: Dict[str, ReviewItem] = {}
        self.reviewed_items: Dict[str, ReviewItem] = {}
    
    def add_to_queue(
        self,
        entity_id: str,
        entity_type: str,
        entity_data: Dict[str, Any],
        source_id: str,
        extraction_method: str,
        confidence: float
    ) -> ReviewItem:
        """
        Add entity to review queue
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity
            entity_data: Full entity data
            source_id: Source document ID
            extraction_method: How entity was extracted
            confidence: Confidence score (should be 0.80-0.94)
        
        Returns:
            ReviewItem added to queue
        """
        review_item = ReviewItem(
            entity_id=entity_id,
            entity_type=entity_type,
            entity_data=entity_data,
            source_id=source_id,
            extraction_method=extraction_method,
            confidence=confidence,
            submitted_at=datetime.now(),
            status=ReviewStatus.PENDING
        )
        
        self.queue[entity_id] = review_item
        return review_item
    
    def get_pending_items(self) -> List[ReviewItem]:
        """Get all pending review items"""
        return [
            item for item in self.queue.values()
            if item.status == ReviewStatus.PENDING
        ]
    
    def get_item(self, entity_id: str) -> Optional[ReviewItem]:
        """Get review item by entity ID"""
        return self.queue.get(entity_id) or self.reviewed_items.get(entity_id)
    
    def approve(
        self,
        entity_id: str,
        reviewer_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Approve entity for graph insertion
        
        Args:
            entity_id: Entity ID to approve
            reviewer_id: ID of human reviewer
            notes: Optional review notes
        
        Returns:
            True if approved, False if not found
        """
        if entity_id not in self.queue:
            return False
        
        item = self.queue[entity_id]
        item.status = ReviewStatus.APPROVED
        item.reviewed_by = reviewer_id
        item.reviewed_at = datetime.now()
        item.review_notes = notes
        
        # Move to reviewed items
        self.reviewed_items[entity_id] = item
        del self.queue[entity_id]
        
        return True
    
    def reject(
        self,
        entity_id: str,
        reviewer_id: str,
        reason: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Reject entity (will not be inserted into graph)
        
        Args:
            entity_id: Entity ID to reject
            reviewer_id: ID of human reviewer
            reason: Reason for rejection
            notes: Optional review notes
        
        Returns:
            True if rejected, False if not found
        """
        if entity_id not in self.queue:
            return False
        
        item = self.queue[entity_id]
        item.status = ReviewStatus.REJECTED
        item.reviewed_by = reviewer_id
        item.reviewed_at = datetime.now()
        item.rejection_reason = reason
        item.review_notes = notes
        
        # Move to reviewed items
        self.reviewed_items[entity_id] = item
        del self.queue[entity_id]
        
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """Get review queue statistics"""
        return {
            "pending": len([item for item in self.queue.values() if item.status == ReviewStatus.PENDING]),
            "approved": len([item for item in self.reviewed_items.values() if item.status == ReviewStatus.APPROVED]),
            "rejected": len([item for item in self.reviewed_items.values() if item.status == ReviewStatus.REJECTED]),
            "total": len(self.queue) + len(self.reviewed_items)
        }

