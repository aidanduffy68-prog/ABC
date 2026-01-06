"""
Merkle Tree for Cryptographic Receipts
Allows revealing part of intelligence without revealing the whole tree

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any, Optional
import hashlib
import json


class MerkleNode:
    """Merkle tree node"""
    def __init__(self, hash_value: str, left: Optional['MerkleNode'] = None, right: Optional['MerkleNode'] = None, data: Optional[Dict[str, Any]] = None):
        self.hash = hash_value
        self.left = left
        self.right = right
        self.data = data  # Only leaf nodes have data
        self.parent: Optional['MerkleNode'] = None  # Parent pointer for proof generation


class MerkleTree:
    """
    Merkle tree for cryptographic receipts
    Enables selective disclosure: reveal "We knew about Wallet X" without revealing "We also know about Wallet Y"
    """
    
    def __init__(self, receipts: List[Dict[str, Any]]):
        """
        Initialize Merkle tree from receipts
        
        Args:
            receipts: List of receipt dictionaries (must have 'intelligence_hash' field)
        """
        self.receipts = receipts
        self.leaf_nodes: List[MerkleNode] = []  # Initialize before _build_tree
        self.root = self._build_tree(receipts)
    
    def _build_tree(self, receipts: List[Dict[str, Any]]) -> Optional[MerkleNode]:
        """
        Build Merkle tree from receipts
        
        SECURITY FIXES:
        - Deterministic sorting: Sort receipts by hash for consistent tree structure
        - Proper padding: Duplicate last leaf when odd number (prevents second preimage attacks)
        - Parent pointers: Maintain parent references for proof generation
        """
        if not receipts:
            return None
        
        # SECURITY FIX: Sort receipts deterministically by hash
        # This ensures same receipts always produce same tree structure
        def get_receipt_hash(receipt: Dict[str, Any]) -> str:
            intelligence_hash = receipt.get('intelligence_hash', '')
            if not intelligence_hash:
                intelligence_hash = self._hash_receipt(receipt)
            return intelligence_hash
        
        # Sort receipts by hash for deterministic tree structure
        sorted_receipts = sorted(receipts, key=get_receipt_hash)
        
        # Create leaf nodes (one per receipt)
        leaves = []
        for receipt in sorted_receipts:
            intelligence_hash = get_receipt_hash(receipt)
            
            leaf = MerkleNode(
                hash_value=intelligence_hash,
                data=receipt
            )
            leaves.append(leaf)
            self.leaf_nodes.append(leaf)
        
        # Build tree bottom-up with parent pointers
        nodes = leaves
        while len(nodes) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else None
                
                if right:
                    # Combine hashes with position information
                    combined_hash = self._hash_pair(left.hash, right.hash)
                    parent = MerkleNode(combined_hash, left, right)
                    # Maintain parent pointers for proof generation
                    left.parent = parent
                    right.parent = parent
                else:
                    # SECURITY FIX: Duplicate last leaf when odd number
                    # This prevents second preimage attacks
                    # Don't promote left directly - duplicate it
                    duplicated_hash = self._hash_pair(left.hash, left.hash)
                    parent = MerkleNode(duplicated_hash, left, left)
                    left.parent = parent
                
                next_level.append(parent)
            
            nodes = next_level
        
        return nodes[0] if nodes else None
    
    def _hash_pair(self, hash1: str, hash2: str) -> str:
        """
        Hash two hashes together with position information
        
        SECURITY FIX: Include position markers to prevent second preimage attacks
        """
        # Include position markers: "L" for left, "R" for right
        # This prevents attacker from swapping left/right to create same hash
        combined = f"L{hash1}R{hash2}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()
    
    def _hash_receipt(self, receipt: Dict[str, Any]) -> str:
        """Hash receipt using canonical JSON"""
        receipt_json = json.dumps(
            receipt,
            sort_keys=True,
            ensure_ascii=False,
            separators=(',', ':')
        )
        return hashlib.sha256(receipt_json.encode('utf-8')).hexdigest()
    
    def get_root_hash(self) -> Optional[str]:
        """Get root hash of Merkle tree"""
        return self.root.hash if self.root else None
    
    def generate_proof(self, receipt_index: int) -> Optional[Dict[str, Any]]:
        """
        Generate Merkle proof for a specific receipt
        
        Allows proving receipt is in tree without revealing other receipts
        
        Args:
            receipt_index: Index of receipt in original list
        
        Returns:
            Proof dictionary with path and hashes
        """
        if receipt_index < 0 or receipt_index >= len(self.leaf_nodes):
            return None
        
        leaf = self.leaf_nodes[receipt_index]
        proof_path = []
        current = leaf
        
        # Traverse up to root, collecting sibling hashes
        while current and current != self.root:
            parent = self._find_parent(current)
            if not parent:
                break
            
            if parent.left == current:
                # Current is left child, include right sibling
                if parent.right:
                    proof_path.append({
                        "position": "left",
                        "sibling_hash": parent.right.hash
                    })
            else:
                # Current is right child, include left sibling
                if parent.left:
                    proof_path.append({
                        "position": "right",
                        "sibling_hash": parent.left.hash
                    })
            
            current = parent
        
        return {
            "receipt_index": receipt_index,
            "receipt_hash": leaf.hash,
            "root_hash": self.root.hash if self.root else None,
            "proof_path": proof_path
        }
    
    def _find_parent(self, node: MerkleNode) -> Optional[MerkleNode]:
        """
        Find parent of a node (helper for proof generation)
        
        SECURITY FIX: Now uses parent pointers maintained during tree construction
        """
        return node.parent
    
    def verify_proof(
        self,
        receipt_hash: str,
        root_hash: str,
        proof_path: List[Dict[str, str]]
    ) -> bool:
        """
        Verify Merkle proof
        
        Args:
            receipt_hash: Hash of receipt to verify
            root_hash: Root hash of tree
            proof_path: Proof path from generate_proof()
        
        Returns:
            True if proof is valid
        """
        current_hash = receipt_hash
        
        for step in proof_path:
            sibling_hash = step["sibling_hash"]
            position = step["position"]
            
            if position == "left":
                # Current is left, sibling is right
                current_hash = self._hash_pair(current_hash, sibling_hash)
            else:
                # Current is right, sibling is left
                current_hash = self._hash_pair(sibling_hash, current_hash)
        
        # SECURITY FIX: Use constant-time comparison to prevent timing attacks
        import secrets
        return secrets.compare_digest(
            current_hash.encode() if isinstance(current_hash, str) else current_hash,
            root_hash.encode() if isinstance(root_hash, str) else root_hash
        )
    
    def reveal_receipt(self, receipt_index: int) -> Optional[Dict[str, Any]]:
        """
        Reveal specific receipt with proof
        
        Allows selective disclosure: "We knew about Wallet X" without revealing other wallets
        
        Args:
            receipt_index: Index of receipt to reveal
        
        Returns:
            Receipt data with Merkle proof
        """
        if receipt_index < 0 or receipt_index >= len(self.leaf_nodes):
            return None
        
        receipt = self.leaf_nodes[receipt_index].data
        proof = self.generate_proof(receipt_index)
        
        if not proof:
            return None
        
        return {
            "receipt": receipt,
            "proof": proof,
            "root_hash": self.root.hash if self.root else None
        }


def create_receipt_merkle_tree(receipts: List[Dict[str, Any]]) -> MerkleTree:
    """
    Convenience function to create Merkle tree from receipts
    
    Usage:
        tree = create_receipt_merkle_tree([receipt1, receipt2, receipt3])
        root_hash = tree.get_root_hash()
        proof = tree.generate_proof(0)  # Proof for first receipt
    """
    return MerkleTree(receipts)

