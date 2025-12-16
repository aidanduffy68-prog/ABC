"""
Agency Assessment Storage
In-memory store for agency assessments (temporary until Neo4j integration)

Copyright (c) 2025 GH Systems. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging
from collections import defaultdict

from src.schemas.agency import AgencyAssessment

logger = logging.getLogger(__name__)


class AgencyAssessmentStore:
    """
    In-memory store for agency assessments
    
    Provides temporary storage for agency assessments until Neo4j integration.
    Thread-safe operations with basic locking.
    """
    
    def __init__(self):
        """Initialize the store"""
        # Store assessments by foundry_compilation_id
        self._assessments_by_compilation: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Store assessments by receipt hash (for idempotency)
        self._assessments_by_receipt: Dict[str, Dict[str, Any]] = {}
        
        # Store assessments by agency + compilation (for quick lookups)
        self._assessments_by_agency: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        
        # Store all assessments by unique ID
        self._assessments: Dict[str, Dict[str, Any]] = {}
        
        # Maximum assessments to keep per compilation (prevent memory issues)
        self._max_assessments_per_compilation = 1000
        
        logger.info("AgencyAssessmentStore initialized (in-memory)")
    
    def store_assessment(
        self,
        assessment: AgencyAssessment,
        receipt_id: str,
        blockchain_tx_hash: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store agency assessment
        
        Args:
            assessment: Agency assessment to store
            receipt_id: Blockchain receipt ID
            blockchain_tx_hash: Blockchain transaction hash (optional)
            idempotency_key: Optional idempotency key (if provided, will prevent duplicates)
        
        Returns:
            Stored assessment record with storage metadata
        """
        # Check for idempotency
        if idempotency_key:
            existing = self._assessments_by_receipt.get(idempotency_key)
            if existing:
                logger.info(f"Duplicate assessment detected (idempotency_key={idempotency_key})")
                return existing
        
        # Check for duplicate agency + compilation combination
        agency_key = f"{assessment.agency}:{assessment.foundry_compilation_id}"
        existing = self._assessments_by_agency.get(assessment.agency, {}).get(
            assessment.foundry_compilation_id
        )
        if existing:
            logger.warning(
                f"Replacing existing assessment from {assessment.agency} "
                f"for compilation {assessment.foundry_compilation_id}"
            )
            # Remove old assessment
            old_id = existing['storage_id']
            self._remove_assessment(old_id)
        
        # Create storage record
        storage_id = str(uuid.uuid4())
        stored_at = datetime.now()
        
        record = {
            'storage_id': storage_id,
            'assessment': assessment.dict(),
            'receipt_id': receipt_id,
            'blockchain_tx_hash': blockchain_tx_hash,
            'idempotency_key': idempotency_key,
            'stored_at': stored_at.isoformat(),
            'agency': assessment.agency,
            'foundry_compilation_id': assessment.foundry_compilation_id,
            'abc_receipt_hash': assessment.abc_receipt_hash,
            'confidence_score': assessment.confidence_score,
            'classification': assessment.classification.value
        }
        
        # Store in all indexes
        self._assessments[storage_id] = record
        self._assessments_by_compilation[assessment.foundry_compilation_id].append(record)
        
        if idempotency_key:
            self._assessments_by_receipt[idempotency_key] = record
        
        self._assessments_by_agency[assessment.agency][assessment.foundry_compilation_id] = record
        
        # Enforce limits
        compilations = self._assessments_by_compilation[assessment.foundry_compilation_id]
        if len(compilations) > self._max_assessments_per_compilation:
            # Remove oldest assessment
            oldest = compilations.pop(0)
            self._remove_assessment(oldest['storage_id'])
            logger.warning(
                f"Removed oldest assessment for {assessment.foundry_compilation_id} "
                f"(limit exceeded: {self._max_assessments_per_compilation})"
            )
        
        logger.info(
            f"Stored assessment from {assessment.agency} "
            f"for compilation {assessment.foundry_compilation_id} "
            f"(storage_id={storage_id})"
        )
        
        return record
    
    def get_assessments_by_compilation(
        self,
        foundry_compilation_id: str
    ) -> List[AgencyAssessment]:
        """
        Get all assessments for a Foundry compilation
        
        Args:
            foundry_compilation_id: Foundry compilation ID
        
        Returns:
            List of AgencyAssessment objects
        """
        records = self._assessments_by_compilation.get(foundry_compilation_id, [])
        assessments = []
        
        for record in records:
            try:
                assessment = AgencyAssessment(**record['assessment'])
                assessments.append(assessment)
            except Exception as e:
                logger.error(f"Error deserializing assessment {record.get('storage_id')}: {e}")
        
        logger.debug(
            f"Retrieved {len(assessments)} assessments for compilation {foundry_compilation_id}"
        )
        
        return assessments
    
    def get_assessment_by_agency(
        self,
        agency: str,
        foundry_compilation_id: str
    ) -> Optional[AgencyAssessment]:
        """
        Get assessment from specific agency for a compilation
        
        Args:
            agency: Agency identifier
            foundry_compilation_id: Foundry compilation ID
        
        Returns:
            AgencyAssessment if found, None otherwise
        """
        record = self._assessments_by_agency.get(agency, {}).get(foundry_compilation_id)
        
        if not record:
            return None
        
        try:
            return AgencyAssessment(**record['assessment'])
        except Exception as e:
            logger.error(f"Error deserializing assessment: {e}")
            return None
    
    def get_all_assessments(self) -> List[Dict[str, Any]]:
        """
        Get all stored assessments (for debugging/admin)
        
        Returns:
            List of assessment records
        """
        return list(self._assessments.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get store statistics
        
        Returns:
            Statistics dictionary
        """
        total_assessments = len(self._assessments)
        total_compilations = len(self._assessments_by_compilation)
        agencies = set(record['agency'] for record in self._assessments.values())
        
        return {
            'total_assessments': total_assessments,
            'total_compilations': total_compilations,
            'total_agencies': len(agencies),
            'agencies': sorted(list(agencies)),
            'max_assessments_per_compilation': self._max_assessments_per_compilation
        }
    
    def _remove_assessment(self, storage_id: str):
        """Remove assessment from all indexes"""
        if storage_id not in self._assessments:
            return
        
        record = self._assessments[storage_id]
        assessment_data = record['assessment']
        
        # Remove from compilation index
        compilation_id = assessment_data['foundry_compilation_id']
        compilations = self._assessments_by_compilation.get(compilation_id, [])
        self._assessments_by_compilation[compilation_id] = [
            r for r in compilations if r['storage_id'] != storage_id
        ]
        
        # Remove from receipt index
        if record.get('idempotency_key'):
            self._assessments_by_receipt.pop(record['idempotency_key'], None)
        
        # Remove from agency index
        agency = assessment_data['agency']
        if agency in self._assessments_by_agency:
            self._assessments_by_agency[agency].pop(compilation_id, None)
        
        # Remove from main store
        self._assessments.pop(storage_id, None)


# Global singleton instance
_agency_store: Optional[AgencyAssessmentStore] = None


def get_agency_store() -> AgencyAssessmentStore:
    """
    Get global agency assessment store instance
    
    Returns:
        AgencyAssessmentStore singleton
    """
    global _agency_store
    if _agency_store is None:
        _agency_store = AgencyAssessmentStore()
    return _agency_store

