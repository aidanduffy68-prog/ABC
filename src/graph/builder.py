"""
Graph Builder
Simple NetworkX graph manipulation for threat intelligence relationships

Copyright (c) 2026 GH Systems. All rights reserved.
"""

from typing import List, Dict, Any, Optional, Tuple
import networkx as nx
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GraphNode:
    """Graph node representation"""
    node_id: str
    node_type: str  # actor, event, pattern, etc.
    attributes: Dict[str, Any]


@dataclass
class GraphEdge:
    """Graph edge representation"""
    source_id: str
    target_id: str
    relationship_type: str  # COORDINATES_WITH, CONTROLS, etc.
    weight: float = 1.0
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


class ThreatIntelligenceGraph:
    """
    NetworkX-based graph for threat intelligence relationships
    Demonstrates graph data structure manipulation
    """
    
    def __init__(self):
        """Initialize empty graph"""
        self.graph = nx.DiGraph()  # Directed graph
        self.node_metadata: Dict[str, GraphNode] = {}
        self.edge_metadata: Dict[Tuple[str, str], GraphEdge] = {}
    
    def add_node(
        self,
        node_id: str,
        node_type: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add node to graph
        
        Args:
            node_id: Unique node identifier
            node_type: Type of node (actor, event, pattern, etc.)
            attributes: Node attributes
        """
        if attributes is None:
            attributes = {}
        
        # Store node metadata
        node = GraphNode(
            node_id=node_id,
            node_type=node_type,
            attributes=attributes
        )
        self.node_metadata[node_id] = node
        
        # Add to NetworkX graph
        self.graph.add_node(node_id, node_type=node_type, **attributes)
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        weight: float = 1.0,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add edge (relationship) between two nodes
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship_type: Type of relationship (COORDINATES_WITH, CONTROLS, etc.)
            weight: Edge weight (default 1.0)
            attributes: Edge attributes
        """
        # Ensure nodes exist
        if source_id not in self.graph:
            raise ValueError(f"Source node {source_id} does not exist")
        if target_id not in self.graph:
            raise ValueError(f"Target node {target_id} does not exist")
        
        if attributes is None:
            attributes = {}
        
        # Store edge metadata
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            weight=weight,
            attributes=attributes
        )
        self.edge_metadata[(source_id, target_id)] = edge
        
        # Add to NetworkX graph
        self.graph.add_edge(
            source_id,
            target_id,
            relationship_type=relationship_type,
            weight=weight,
            **attributes
        )
    
    def link_nodes(
        self,
        node1_id: str,
        node2_id: str,
        relationship_type: str = "RELATED_TO",
        weight: float = 1.0
    ) -> None:
        """
        Link two nodes with a relationship
        
        Simple helper method to demonstrate graph manipulation
        
        Args:
            node1_id: First node ID
            node2_id: Second node ID
            relationship_type: Type of relationship
            weight: Relationship weight
        """
        self.add_edge(node1_id, node2_id, relationship_type, weight)
    
    def get_node_neighbors(self, node_id: str) -> List[str]:
        """
        Get all neighbors of a node
        
        Args:
            node_id: Node ID
        
        Returns:
            List of neighbor node IDs
        """
        if node_id not in self.graph:
            raise ValueError(f"Node {node_id} does not exist")
        
        return list(self.graph.neighbors(node_id))
    
    def get_node_relationships(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Get all relationships for a node
        
        Args:
            node_id: Node ID
        
        Returns:
            List of relationship dictionaries
        """
        if node_id not in self.graph:
            raise ValueError(f"Node {node_id} does not exist")
        
        relationships = []
        
        # Outgoing edges
        for target_id in self.graph.successors(node_id):
            edge_data = self.graph[node_id][target_id]
            relationships.append({
                "source": node_id,
                "target": target_id,
                "direction": "outgoing",
                "relationship_type": edge_data.get("relationship_type"),
                "weight": edge_data.get("weight", 1.0)
            })
        
        # Incoming edges
        for source_id in self.graph.predecessors(node_id):
            edge_data = self.graph[source_id][node_id]
            relationships.append({
                "source": source_id,
                "target": node_id,
                "direction": "incoming",
                "relationship_type": edge_data.get("relationship_type"),
                "weight": edge_data.get("weight", 1.0)
            })
        
        return relationships
    
    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """
        Find shortest path between two nodes
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
        
        Returns:
            List of node IDs in path, or None if no path exists
        """
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get graph statistics
        
        Returns:
            Dictionary with graph statistics
        """
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "is_connected": nx.is_weakly_connected(self.graph),
            "density": nx.density(self.graph),
            "average_clustering": nx.average_clustering(self.graph.to_undirected()) if self.graph.number_of_nodes() > 0 else 0.0
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export graph to dictionary format
        
        Returns:
            Dictionary representation of graph
        """
        nodes = []
        for node_id, node in self.node_metadata.items():
            nodes.append({
                "node_id": node_id,
                "node_type": node.node_type,
                "attributes": node.attributes
            })
        
        edges = []
        for (source_id, target_id), edge in self.edge_metadata.items():
            edges.append({
                "source_id": source_id,
                "target_id": target_id,
                "relationship_type": edge.relationship_type,
                "weight": edge.weight,
                "attributes": edge.attributes
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": self.get_graph_stats()
        }


# Example usage
if __name__ == "__main__":
    # Create graph
    graph = ThreatIntelligenceGraph()
    
    # Add nodes
    graph.add_node("ALPHA_47", "actor", {"risk_score": 0.95})
    graph.add_node("BETA_12", "actor", {"risk_score": 0.87})
    graph.add_node("TORNADO_CASH", "service", {"type": "mixer"})
    
    # Link nodes
    graph.link_nodes("ALPHA_47", "BETA_12", "COORDINATES_WITH", weight=0.9)
    graph.link_nodes("ALPHA_47", "TORNADO_CASH", "USES", weight=0.8)
    
    # Get relationships
    relationships = graph.get_node_relationships("ALPHA_47")
    print(f"ALPHA_47 relationships: {len(relationships)}")
    
    # Get stats
    stats = graph.get_graph_stats()
    print(f"Graph stats: {stats}")

