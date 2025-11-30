"""
Data Lake Layer - Staging area for extracted entities before graph insertion
Enables rollback if validation fails
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import uuid


@dataclass
class StagedEntity:
    """Entity staged in data lake before graph insertion"""
    entity_id: str
    entity_type: str
    entity_data: Dict[str, Any]
    source_id: str
    extraction_method: str
    confidence: float
    staged_at: datetime
    validation_status: str = "pending"  # pending, validated, rejected
    validation_errors: List[str] = None
    graph_inserted: bool = False
    graph_inserted_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


class DataLake:
    """
    Staging area for extracted entities
    Prevents bad data from entering the graph
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data_lake"
        self.staged_entities: Dict[str, StagedEntity] = {}
        self._load_staged_entities()
    
    def stage_entity(
        self,
        entity_id: str,
        entity_type: str,
        entity_data: Dict[str, Any],
        source_id: str,
        extraction_method: str,
        confidence: float
    ) -> StagedEntity:
        """
        Stage an entity in the data lake
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity (actor, event, pattern, etc.)
            entity_data: Full entity data
            source_id: Source document/report ID
            extraction_method: How entity was extracted (llm_gpt4, heuristic, manual)
            confidence: Confidence score (0-1)
        
        Returns:
            StagedEntity object
        """
        staged = StagedEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            entity_data=entity_data,
            source_id=source_id,
            extraction_method=extraction_method,
            confidence=confidence,
            staged_at=datetime.now()
        )
        
        self.staged_entities[entity_id] = staged
        self._save_staged_entities()
        
        return staged
    
    def get_staged_entity(self, entity_id: str) -> Optional[StagedEntity]:
        """Get staged entity by ID"""
        return self.staged_entities.get(entity_id)
    
    def get_staged_by_source(self, source_id: str) -> List[StagedEntity]:
        """Get all entities staged from a specific source"""
        return [
            entity for entity in self.staged_entities.values()
            if entity.source_id == source_id
        ]
    
    def get_pending_entities(self) -> List[StagedEntity]:
        """Get all entities pending validation"""
        return [
            entity for entity in self.staged_entities.values()
            if entity.validation_status == "pending"
        ]
    
    def mark_validated(self, entity_id: str):
        """Mark entity as validated (ready for graph insertion)"""
        if entity_id in self.staged_entities:
            self.staged_entities[entity_id].validation_status = "validated"
            self._save_staged_entities()
    
    def mark_rejected(self, entity_id: str, errors: List[str]):
        """Mark entity as rejected (validation failed)"""
        if entity_id in self.staged_entities:
            self.staged_entities[entity_id].validation_status = "rejected"
            self.staged_entities[entity_id].validation_errors = errors
            self._save_staged_entities()
    
    def mark_graph_inserted(self, entity_id: str):
        """Mark entity as inserted into graph"""
        if entity_id in self.staged_entities:
            self.staged_entities[entity_id].graph_inserted = True
            self.staged_entities[entity_id].graph_inserted_at = datetime.now()
            self._save_staged_entities()
    
    def delete_by_source(self, source_id: str) -> int:
        """
        Delete all entities from a specific source (cascade delete)
        Used when hallucination detected in source
        
        Returns:
            Number of entities deleted
        """
        to_delete = [
            entity_id for entity_id, entity in self.staged_entities.items()
            if entity.source_id == source_id
        ]
        
        for entity_id in to_delete:
            del self.staged_entities[entity_id]
        
        self._save_staged_entities()
        return len(to_delete)
    
    def _load_staged_entities(self):
        """Load staged entities from storage (if persistence enabled)"""
        # TODO: Implement persistence if storage_path provided
        pass
    
    def _save_staged_entities(self):
        """Save staged entities to storage (if persistence enabled)"""
        # TODO: Implement persistence if storage_path provided
        pass

