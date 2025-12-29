"""
Heuristic Rules - Fast, deterministic relationship detection
Runs before GNNs for speed and reliability
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class HeuristicRelationship:
    """Relationship detected by heuristic rules"""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float  # 0-1, typically high for deterministic rules
    evidence: List[str]
    reasoning: str
    detected_by: str = "heuristic_rule"


class HeuristicRulesEngine:
    """
    Fast, deterministic relationship detection
    Runs synchronously for API responses (<500ms)
    GNNs supplement these rules, not replace them
    """
    
    def __init__(self):
        self.relationship_types = [
            "COORDINATES_WITH",
            "CONTROLS",
            "BEHAVES_LIKE",
            "CLUSTERS_WITH",
            "SANCTIONED_BY",
            "SUSPECTED_OF"
        ]
    
    def detect_relationships(
        self,
        entities: List[Dict[str, Any]],
        transactions: Optional[List[Dict[str, Any]]] = None
    ) -> List[HeuristicRelationship]:
        """
        Detect relationships using deterministic heuristic rules
        
        Args:
            entities: List of entities to analyze
            transactions: Optional transaction data for timing analysis
        
        Returns:
            List of detected relationships
        """
        relationships = []
        
        # Rule 1: Same contract interaction (within same block)
        if transactions:
            coord_rels = self._detect_same_contract_interaction(entities, transactions)
            relationships.extend(coord_rels)
        
        # Rule 2: Direct funding relationships
        funding_rels = self._detect_funding_relationships(entities, transactions)
        relationships.extend(funding_rels)
        
        # Rule 3: Sequential transaction patterns
        if transactions:
            sequential_rels = self._detect_sequential_patterns(entities, transactions)
            relationships.extend(sequential_rels)
        
        # Rule 4: Same exchange usage
        exchange_rels = self._detect_same_exchange_usage(entities, transactions)
        relationships.extend(exchange_rels)
        
        # Rule 5: Sanction list matching
        sanction_rels = self._detect_sanction_matches(entities)
        relationships.extend(sanction_rels)
        
        return relationships
    
    def _detect_same_contract_interaction(
        self,
        entities: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]]
    ) -> List[HeuristicRelationship]:
        """
        Rule: If Wallet A and Wallet B interact with Contract C within same block 5 times → COORDINATES_WITH
        """
        relationships = []
        
        # Group transactions by block
        block_transactions: Dict[int, List[Dict]] = {}
        for tx in transactions:
            block_num = tx.get("block_number")
            if block_num:
                if block_num not in block_transactions:
                    block_transactions[block_num] = []
                block_transactions[block_num].append(tx)
        
        # Find entities that interact with same contracts in same blocks
        entity_contracts: Dict[str, Dict[str, int]] = {}  # entity_id -> {contract: block_count}
        
        for entity in entities:
            entity_id = entity.get("entity_id")
            if not entity_id:
                continue
            
            entity_contracts[entity_id] = {}
            
            for block_num, block_txs in block_transactions.items():
                for tx in block_txs:
                    from_addr = tx.get("from_address", "").lower()
                    to_addr = tx.get("to_address", "").lower()
                    contract_addr = tx.get("contract_address", "").lower()
                    
                    # Check if entity is involved in this transaction
                    entity_addr = entity.get("address", "").lower()
                    if entity_addr and (entity_addr == from_addr or entity_addr == to_addr):
                        if contract_addr:
                            contract_key = f"{block_num}_{contract_addr}"
                            entity_contracts[entity_id][contract_key] = \
                                entity_contracts[entity_id].get(contract_key, 0) + 1
        
        # Find pairs that interact with same contract in same block multiple times
        entity_list = list(entity_contracts.keys())
        for i, entity1_id in enumerate(entity_list):
            for entity2_id in entity_list[i+1:]:
                common_contracts = set(entity_contracts[entity1_id].keys()) & \
                                 set(entity_contracts[entity2_id].keys())
                
                if len(common_contracts) >= 5:  # Threshold: 5 same-block interactions
                    relationships.append(HeuristicRelationship(
                        source_entity_id=entity1_id,
                        target_entity_id=entity2_id,
                        relationship_type="COORDINATES_WITH",
                        confidence=0.90,  # High confidence for deterministic rule
                        evidence=[f"{len(common_contracts)} same-block contract interactions"],
                        reasoning=f"Entities interacted with same contracts in same blocks {len(common_contracts)} times, indicating coordination"
                    ))
        
        return relationships
    
    def _detect_funding_relationships(
        self,
        entities: List[Dict[str, Any]],
        transactions: Optional[List[Dict[str, Any]]]
    ) -> List[HeuristicRelationship]:
        """
        Rule: If Entity A sends funds to Entity B multiple times → CONTROLS
        """
        relationships = []
        
        if not transactions:
            return relationships
        
        # Track funding flows
        funding_flows: Dict[str, Dict[str, int]] = {}  # from_entity -> {to_entity: count}
        
        for tx in transactions:
            from_addr = tx.get("from_address", "").lower()
            to_addr = tx.get("to_address", "").lower()
            value = tx.get("value", 0)
            
            if not from_addr or not to_addr or value == 0:
                continue
            
            # Find entities matching addresses
            from_entity = self._find_entity_by_address(entities, from_addr)
            to_entity = self._find_entity_by_address(entities, to_addr)
            
            if from_entity and to_entity and from_entity != to_entity:
                from_id = from_entity.get("entity_id")
                to_id = to_entity.get("entity_id")
                
                if from_id not in funding_flows:
                    funding_flows[from_id] = {}
                
                funding_flows[from_id][to_id] = funding_flows[from_id].get(to_id, 0) + 1
        
        # Detect control relationships (multiple funding transactions)
        for from_id, to_entities in funding_flows.items():
            for to_id, count in to_entities.items():
                if count >= 3:  # Threshold: 3+ funding transactions
                    relationships.append(HeuristicRelationship(
                        source_entity_id=from_id,
                        target_entity_id=to_id,
                        relationship_type="CONTROLS",
                        confidence=0.85,
                        evidence=[f"{count} funding transactions"],
                        reasoning=f"Entity {from_id} funded {to_id} {count} times, indicating control structure"
                    ))
        
        return relationships
    
    def _detect_sequential_patterns(
        self,
        entities: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]]
    ) -> List[HeuristicRelationship]:
        """
        Rule: If Entity A sends to Entity B, then B sends to Entity C in sequence → COORDINATES_WITH
        """
        relationships = []
        
        # Sort transactions by timestamp
        sorted_txs = sorted(transactions, key=lambda x: x.get("timestamp", 0))
        
        # Track sequential patterns
        for i in range(len(sorted_txs) - 1):
            tx1 = sorted_txs[i]
            tx2 = sorted_txs[i + 1]
            
            # Check if tx1.to == tx2.from (sequential flow)
            if tx1.get("to_address", "").lower() == tx2.get("from_address", "").lower():
                entity1 = self._find_entity_by_address(entities, tx1.get("from_address", "").lower())
                entity2 = self._find_entity_by_address(entities, tx2.get("to_address", "").lower())
                
                if entity1 and entity2 and entity1 != entity2:
                    entity1_id = entity1.get("entity_id")
                    entity2_id = entity2.get("entity_id")
                    
                    # Check timing (within 1 hour)
                    time_diff = abs(tx2.get("timestamp", 0) - tx1.get("timestamp", 0))
                    if time_diff < 3600:  # 1 hour
                        relationships.append(HeuristicRelationship(
                            source_entity_id=entity1_id,
                            target_entity_id=entity2_id,
                            relationship_type="COORDINATES_WITH",
                            confidence=0.80,
                            evidence=["sequential transaction pattern"],
                            reasoning=f"Sequential transaction flow from {entity1_id} to {entity2_id} within 1 hour"
                        ))
        
        return relationships
    
    def _detect_same_exchange_usage(
        self,
        entities: List[Dict[str, Any]],
        transactions: Optional[List[Dict[str, Any]]]
    ) -> List[HeuristicRelationship]:
        """
        Rule: If multiple entities use same exchange addresses → CLUSTERS_WITH
        """
        relationships = []
        
        if not transactions:
            return relationships
        
        # Known exchange addresses (would come from external list)
        exchange_addresses = {
            "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be",  # Binance
            "0xd551234ae421e3bcba99a0da6d736074f22192ff",  # Binance 2
            # Add more exchange addresses
        }
        
        # Track which entities interact with exchanges
        entity_exchanges: Dict[str, set] = {}
        
        for tx in transactions:
            from_addr = tx.get("from_address", "").lower()
            to_addr = tx.get("to_address", "").lower()
            
            # Check if transaction involves exchange
            exchange_addr = None
            if from_addr in exchange_addresses:
                exchange_addr = from_addr
            elif to_addr in exchange_addresses:
                exchange_addr = to_addr
            
            if exchange_addr:
                # Find entity
                entity = self._find_entity_by_address(entities, from_addr) or \
                        self._find_entity_by_address(entities, to_addr)
                
                if entity:
                    entity_id = entity.get("entity_id")
                    if entity_id not in entity_exchanges:
                        entity_exchanges[entity_id] = set()
                    entity_exchanges[entity_id].add(exchange_addr)
        
        # Find entities using same exchanges
        entity_list = list(entity_exchanges.keys())
        for i, entity1_id in enumerate(entity_list):
            for entity2_id in entity_list[i+1:]:
                common_exchanges = entity_exchanges[entity1_id] & entity_exchanges[entity2_id]
                
                if len(common_exchanges) >= 2:  # Threshold: 2+ common exchanges
                    relationships.append(HeuristicRelationship(
                        source_entity_id=entity1_id,
                        target_entity_id=entity2_id,
                        relationship_type="CLUSTERS_WITH",
                        confidence=0.75,
                        evidence=[f"{len(common_exchanges)} common exchange interactions"],
                        reasoning=f"Entities used {len(common_exchanges)} common exchanges, indicating clustering"
                    ))
        
        return relationships
    
    def _detect_sanction_matches(self, entities: List[Dict[str, Any]]) -> List[HeuristicRelationship]:
        """
        Rule: If entity matches sanctioned address → SANCTIONED_BY
        """
        relationships = []
        
        # Known sanctioned addresses (would come from OFAC list)
        sanctioned_addresses = {
            "0x098b716b8aaf21512996dc57eb0615e2383e2f96",  # Example
            # Would load from actual OFAC list
        }
        
        for entity in entities:
            entity_id = entity.get("entity_id")
            address = entity.get("address", "").lower()
            
            if address in sanctioned_addresses:
                relationships.append(HeuristicRelationship(
                    source_entity_id=entity_id,
                    target_entity_id="OFAC_SANCTIONS",
                    relationship_type="SANCTIONED_BY",
                    confidence=1.0,  # 100% confidence for deterministic match
                    evidence=["OFAC sanctions list match"],
                    reasoning=f"Entity address matches OFAC sanctioned address"
                ))
        
        return relationships
    
    def _find_entity_by_address(
        self,
        entities: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """Find entity by wallet address"""
        address_lower = address.lower()
        for entity in entities:
            entity_address = entity.get("address", "").lower()
            if entity_address == address_lower:
                return entity
        return None

